from __future__ import annotations

from datetime import datetime
from typing import Type, TypeVar, Generic, Optional, Any, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
from src.infrastructure.logging_config import get_logger
from sqlalchemy import select, func
from sqlalchemy.sql import Select
from src.infrastructure.paginations import Page
from src.infrastructure.database.cache_manager import CacheManager

T = TypeVar("T")
logger = get_logger(__name__)


def _convert_datetime_strings(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte strings de data ISO para objetos datetime.
    Procura por campos que terminam com '_at' ou contêm 'data_' e são strings.
    """
    converted = data_dict.copy()
    
    # Campos que devem ser convertidos para datetime
    datetime_fields = [key for key in data_dict.keys() 
                      if key.endswith('_at') or key.startswith('data_')]
    
    for key in datetime_fields:
        value = data_dict.get(key)
        if isinstance(value, str):
            try:
                # Remove 'Z' do final se presente
                if value.endswith('Z'):
                    value_clean = value[:-1]
                else:
                    value_clean = value
                
                # Converte para datetime
                converted[key] = datetime.fromisoformat(value_clean)
                logger.debug(f"Converted {key}: {value} -> {converted[key]}")
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to convert {key}={value} to datetime: {e}")
                # Mantém o valor original se não conseguir converter
                pass
    
    return converted


class RepositoryBase(Generic[T]):
    def __init__(
        self, 
        model: Type[T], 
        session: AsyncSession,
        enable_cache: bool = True,
        expire_after_seconds: int = 1800
    ):
        self.model = model
        self.session = session
        
        # Cache Manager centralizado
        self.cache_manager = CacheManager(
            enable_cache=enable_cache,
            expire_after_seconds=expire_after_seconds
        )
        
        # Nome do repositório para chaves de cache
        self._repository_name = self.__class__.__name__
        self._model_name = model.__name__
        
        logger.debug(f"RepositoryBase initialized for model: {model.__name__} (cache: {enable_cache})")
    
    def _generate_cache_key(self, operation: str, *args, **kwargs) -> str:
        """Gera chave de cache usando o CacheManager"""
        return self.cache_manager.generate_cache_key(
            self._repository_name,
            self._model_name,
            operation,
            *args,
            **kwargs
        )
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Recupera dados do cache"""
        return await self.cache_manager.get(cache_key)
    
    async def _set_cache(self, cache_key: str, data: Any, ttl_override: Optional[int] = None) -> None:
        """Armazena dados no cache"""
        await self.cache_manager.set(cache_key, data, ttl_override)
    
    async def _delete_cache(self, cache_key: str) -> None:
        """Remove dados do cache"""
        await self.cache_manager.delete(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache do repositório"""
        return self.cache_manager.get_stats()

    async def _paginate_params(
        self,
        page: Optional[int],
        per_page: Optional[int],
        stmt: Select,
        session: AsyncSession,
    ) -> Page:
        """Calcula metadados de paginação baseado na query fornecida."""
        # Normaliza valores de entrada
        current_page = max(1, page or 1)
        items_per_page = max(1, min(per_page or 30, 2048))
        
        # Conta total de registros usando scalar para extrair o valor int
        count_query = select(func.count()).select_from(stmt)
        result = await session.exec(count_query)
        total_records = result.scalar_one() if result else 0
        
        # Força conversão para int caso venha outro tipo
        total_records = int(total_records) if total_records is not None else 0
        
        return Page(
            page=current_page,
            per_page=items_per_page,
            total=total_records,
        )

    async def create(self, data: T) -> T:
        """Persiste nova entidade no banco e invalida cache."""
        logger.info(f"Creating {self.model.__name__}", extra={"data": data})
        try:
            # Se data é uma instância do modelo, converte campos datetime se necessário
            if isinstance(data, self.model):
                # Verifica se há campos datetime como string que precisam ser convertidos
                instance_dict = data.model_dump() if hasattr(data, 'model_dump') else data.dict()
                converted_dict = _convert_datetime_strings(instance_dict)
                
                # Se houve conversões, cria nova instância com dados convertidos
                if converted_dict != instance_dict:
                    logger.debug(f"Converting datetime fields for {self.model.__name__}")
                    instance = self.model(**converted_dict)
                else:
                    instance = data
            else:
                # Converte para dict usando model_dump se disponível
                if hasattr(data, 'model_dump'):
                    data_dict = data.model_dump()
                elif hasattr(data, 'dict'):
                    data_dict = data.dict()
                elif isinstance(data, dict):
                    data_dict = data
                else:
                    # Fallback: usa __dict__
                    data_dict = data.__dict__ if hasattr(data, '__dict__') else data
                
                # Converte strings de data para objetos datetime
                data_dict = _convert_datetime_strings(data_dict)
                
                # Cria nova instância do modelo
                instance = self.model(**data_dict)
            
            self.session.add(instance)
            await self.session.commit()
            await self.session.refresh(instance)
            logger.info(f"{self.model.__name__} saved", extra={"id": getattr(instance, "id", None)})
            
            # Invalida cache de listas após criação
            list_cache_key = self._generate_cache_key("list")
            await self._delete_cache(list_cache_key)
            
            return instance
        except Exception as e:
            logger.error(f"Create failed for {self.model.__name__}: {e}", exc_info=True)
            raise

    async def read(self, id: int) -> Optional[T]:
        """Recupera entidade por identificador único (com cache)."""
        # Tenta recuperar do cache primeiro
        cache_key = self._generate_cache_key("read", id=id)
        cached_data = await self._get_from_cache(cache_key)
        
        if cached_data:
            logger.debug(f"Cache HIT: {self.model.__name__} id={id}")
            return cached_data
        
        logger.debug(f"Fetching {self.model.__name__} id={id}")
        try:
            instance = await self.session.get(self.model, id)
            if instance:
                logger.info(f"{self.model.__name__} retrieved: {id}")
                # Armazena no cache
                await self._set_cache(cache_key, instance)
            else:
                logger.warning(f"{self.model.__name__} not found: {id}")
            return instance
        except Exception as e:
            logger.error(f"Read error {self.model.__name__}: {e}", exc_info=True)
            raise

    async def list(
        self, page: Optional[int] = 1, per_page: Optional[int] = 2048
    ) -> tuple[list[T], Optional[Page]]:
        """Retorna coleção paginada de entidades (com cache)."""
        # Tenta recuperar do cache
        cache_key = self._generate_cache_key("list", page=page, per_page=per_page)
        cached_data = await self._get_from_cache(cache_key)
        
        if cached_data:
            logger.debug(f"Cache HIT: {self.model.__name__} list page={page}")
            return cached_data.get("items", []), cached_data.get("pagination")
        
        logger.debug(f"Listing {self.model.__name__}", extra={"page": page, "per_page": per_page})
        try:
            query = select(self.model)
            pagination = await self._paginate_params(page, per_page, query.subquery(), self.session)
            
            # Aplica limitação e deslocamento
            paginated_query = query.offset(pagination.offset).limit(pagination.per_page)
            result = await self.session.exec(paginated_query)
            items = list(result.all())
            
            # Armazena no cache
            cache_data = {"items": items, "pagination": pagination}
            await self._set_cache(cache_key, cache_data, ttl_override=300)  # 5 min para listas
            
            return items, pagination
        except Exception as e:
            logger.error(f"List error {self.model.__name__}: {e}", exc_info=True)
            raise

    async def search(
        self, filters: dict, page: Optional[int] = None, per_page: Optional[int] = None
    ) -> tuple[list[T], Optional[Page]]:
        """Busca entidades aplicando filtros dinâmicos (com cache)."""
        # Tenta recuperar do cache
        cache_key = self._generate_cache_key("search", filters=filters, page=page, per_page=per_page)
        cached_data = await self._get_from_cache(cache_key)
        
        if cached_data:
            logger.debug(f"Cache HIT: {self.model.__name__} search filters={filters}")
            return cached_data.get("items", []), cached_data.get("pagination")
        
        logger.debug(f"Searching {self.model.__name__}", extra={"filters": filters, "page": page, "per_page": per_page})
        try:
            query = select(self.model)
            
            # Aplica cada filtro dinamicamente
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
            
            # Sem paginação: retorna tudo
            if page is None and per_page is None:
                result = await self.session.exec(query)
                items = list(result.all())
                logger.info(f"Found {len(items)} {self.model.__name__} (unpaginated)", extra={"filters": filters})
                
                # Cache por 5 minutos
                cache_data = {"items": items, "pagination": None}
                await self._set_cache(cache_key, cache_data, ttl_override=300)
                
                return items, None
            
            # Com paginação
            pagination = await self._paginate_params(page, per_page, query.subquery(), self.session)
            paginated_query = query.offset(pagination.offset).limit(pagination.per_page)
            result = await self.session.exec(paginated_query)
            items = list(result.all())
            
            # Cache por 5 minutos
            cache_data = {"items": items, "pagination": pagination}
            await self._set_cache(cache_key, cache_data, ttl_override=300)
            
            return items, pagination
        except Exception as e:
            logger.error(f"Search error {self.model.__name__}: {e}", exc_info=True)
            raise

    async def update(self, id: int, data: T) -> Optional[T]:
        """Atualiza campos de entidade existente e invalida cache."""
        logger.info(f"Updating {self.model.__name__} id={id}", extra={"data": data})
        try:
            instance = await self.session.get(self.model, id)
            if not instance:
                logger.warning(f"{self.model.__name__} not found for update: {id}")
                return None
            
            for field, value in data.items():
                setattr(instance, field, value)
            
            self.session.add(instance)
            await self.session.commit()
            await self.session.refresh(instance)
            logger.info(f"{self.model.__name__} updated")
            
            # Invalida cache do item e listas
            read_cache_key = self._generate_cache_key("read", id=id)
            await self._delete_cache(read_cache_key)
            list_cache_key = self._generate_cache_key("list")
            await self._delete_cache(list_cache_key)
            
            return instance
        except Exception as e:
            logger.error(f"Update error {self.model.__name__}: {e}", exc_info=True)
            raise

    async def delete(self, id: int) -> bool:
        """Remove entidade e invalida cache."""
        logger.info(f"Deleting {self.model.__name__} with id: {id}")
        try:
            instance = await self.session.get(self.model, id)
            if instance:
                await self.session.delete(instance)
                await self.session.commit()
                logger.info(f"{self.model.__name__} deleted successfully")
                
                # Invalida cache do item e listas
                read_cache_key = self._generate_cache_key("read", id=id)
                await self._delete_cache(read_cache_key)
                list_cache_key = self._generate_cache_key("list")
                await self._delete_cache(list_cache_key)
                
                return True
            else:
                logger.warning(f"{self.model.__name__} not found for deletion: {id}")
            return False
        except Exception as e:
            logger.error(
                f"Error deleting {self.model.__name__}: {str(e)}", exc_info=True
            )
            raise
