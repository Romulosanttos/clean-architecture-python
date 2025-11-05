import json
import hashlib
import os
from typing import Any, Optional, Dict
from src.infrastructure.logging_config import get_logger
from src.infrastructure.config.settings import Settings
import redis.asyncio as aioredis

logger = get_logger(__name__)


class Cache:
    """
    Singleton para conexão com Redis.
    
    Environment variables:
        REDIS_URL: redis://localhost:6379/0 (development)
                   redis://redis-service:6379/0 (kubernetes)
                   redis://10.x.x.x:6379/0 (GCP Memorystore)
    
    Casos de uso:
    - Cache de queries de banco (TTL: 5-30 min)
    - Sessões de usuário (TTL: 24h)
    - Rate limiting (TTL: 1h)
    - Pub/Sub para eventos entre microserviços
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Retorna instância singleton do Redis client."""
        if cls._instance is None:
            
            redis_url = Settings().redis_url
            
            try:
                cls._instance = aioredis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info(f"Redis connected: {redis_url}")
                
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                raise
            
        return cls._instance


class CacheManager:
    """
    Gerenciador centralizado de cache para repositórios.
    
    Responsabilidades:
    - Geração consistente de chaves de cache
    - Serialização/deserialização de dados
    - Controle de TTL e invalidação
    - Logging e estatísticas de cache
    """
    
    def __init__(self, enable_cache: bool = False, expire_after_seconds: int = 3600):
        self._enable_cache = enable_cache
        self._expire_after_seconds = expire_after_seconds
        self._cache_client = Cache.get_instance() if enable_cache else None
        
        # Estatísticas de cache
        self._hits = 0
        self._misses = 0
    
    def generate_cache_key(self, repository_name: str, model_class_name: str, operation: str, *args, **kwargs) -> str:
        """
        Gera chave de cache consistente seguindo o padrão:
        nome_repositorio:class_model:operacao:hash(args+kwargs)
        
        Args:
            repository_name: Nome do repositório 
            model_class_name: Nome da classe do modelo 
            operation: Nome da operação 
            *args, **kwargs: Argumentos da função para hash
            
        Returns:
            str: Chave de cache única e consistente
        """
        # Serializa argumentos para gerar hash consistente
        args_str = str(args) if args else ""
        kwargs_str = str(sorted(kwargs.items())) if kwargs else ""
        combined_args = f"{args_str}:{kwargs_str}"

        # Gera hash SHA256 dos argumentos
        args_hash = hashlib.sha256(combined_args.encode()).hexdigest()
        
        # Formato: repository:model:operation:hash
        return f"{repository_name}:{model_class_name}:{operation}:{args_hash}"
    
    async def get(self, cache_key: str) -> Optional[Any]:
        """
        Recupera dados do cache com tratamento de erro e estatísticas.
        
        Args:
            cache_key: Chave do cache
            
        Returns:
            Dados deserializados ou None se não encontrado/erro
        """
        if not self._enable_cache or not self._cache_client:
            return None
            
        try:
            cached_data = await self._cache_client.get(cache_key)
            if cached_data:
                self._hits += 1
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(cached_data)
            else:
                self._misses += 1
                logger.debug(f"Cache MISS: {cache_key}")
                return None
        except Exception as e:
            logger.warning(f"Erro ao acessar cache {cache_key}: {e}")
            return None
    
    async def set(self, cache_key: str, data: Any, ttl_override: Optional[int] = None) -> None:
        """
        Armazena dados no cache com serialização automática.
        
        Args:
            cache_key: Chave do cache
            data: Dados para armazenar (será serializado em JSON)
            ttl_override: TTL customizado, se não informado usa o padrão
        """
        if not self._enable_cache or not self._cache_client:
            return
            
        try:
            ttl = ttl_override if ttl_override is not None else self._expire_after_seconds
            
            # Serializa dados (trata objetos SQLAlchemy)
            if hasattr(data, '__dict__'):
                # Objeto SQLAlchemy - usar to_dict() se disponível
                if hasattr(data, 'to_dict'):
                    serialized_data = json.dumps(data.to_dict(), default=str)
                else:
                    # Fallback: serializa __dict__ removendo campos internos
                    obj_dict = data.__dict__.copy()
                    obj_dict.pop('_sa_instance_state', None)
                    serialized_data = json.dumps(obj_dict, default=str)
            elif isinstance(data, list):
                # Lista de objetos - serializa cada item
                list_data = []
                for item in data:
                    if hasattr(item, 'to_dict'):
                        list_data.append(item.to_dict())
                    elif hasattr(item, '__dict__'):
                        item_dict = item.__dict__.copy()
                        item_dict.pop('_sa_instance_state', None)
                        list_data.append(item_dict)
                    else:
                        list_data.append(item)
                serialized_data = json.dumps(list_data, default=str)
            else:
                # Dados primitivos
                serialized_data = json.dumps(data, default=str)
            
            await self._cache_client.set(cache_key, serialized_data, ex=ttl)
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            
        except Exception as e:
            logger.warning(f"Erro ao armazenar no cache {cache_key}: {e}")
    
    async def delete(self, cache_key: str) -> None:
        """Remove uma chave específica do cache"""
        if not self._enable_cache or not self._cache_client:
            return
            
        try:
            await self._cache_client.delete(cache_key)
            logger.debug(f"Cache DELETE: {cache_key}")
        except Exception as e:
            logger.warning(f"Erro ao deletar cache {cache_key}: {e}")
    
    async def delete_pattern(self, pattern: str) -> None:
        """
        Remove múltiplas chaves que correspondem ao padrão.
        Nota: Redis suporta SCAN + DEL para pattern matching.
        """
        if not self._enable_cache or not self._cache_client:
            return
        
        logger.warning(f"Pattern delete: {pattern} (implementar SCAN + DEL para Redis)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache para monitoramento"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": self._enable_cache,
            "ttl_seconds": self._expire_after_seconds,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "redis_available": self._cache_client is not None
        }
    
    def reset_stats(self) -> None:
        """Reseta estatísticas de cache"""
        self._hits = 0
        self._misses = 0
        logger.info("Cache stats resetadas")
    
    def is_enabled(self) -> bool:
        """Verifica se o cache está habilitado"""
        return self._enable_cache and self._cache_client is not None