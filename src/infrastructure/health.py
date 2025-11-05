"""
Health checks para readiness e liveness probes.
"""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import text
from src.infrastructure.logging_config import get_logger
from src.infrastructure.database.connect import async_engine

logger = get_logger(__name__)


class HealthCheck:
    """Gerencia health checks da aplicação."""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """
        Verifica conectividade com PostgreSQL.
        
        Returns:
            dict: Status da conexão com tempo de resposta
        """
        try:
            start = datetime.now()
            
            async with async_engine.connect() as conn:
                # Query simples para validar conexão
                result = await conn.execute(text("SELECT 1"))
                result.scalar()
            
            elapsed = (datetime.now() - start).total_seconds()
            
            logger.debug("Database health check passed", extra={"elapsed": elapsed})
            
            return {
                "status": "healthy",
                "response_time_ms": round(elapsed * 1000, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def check_database_pool() -> Dict[str, Any]:
        """
        Verifica status do connection pool.
        
        Returns:
            dict: Métricas do pool de conexões
        """
        try:
            pool = async_engine.pool
            
            return {
                "status": "healthy",
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Pool health check failed: {str(e)}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def check_application() -> Dict[str, Any]:
        """
        Verifica saúde geral da aplicação.
        
        Returns:
            dict: Status geral e métricas da aplicação
        """
        try:
            import psutil
            import sys
            
            # Métricas de sistema
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "version": "1.0.0",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "uptime_seconds": datetime.utcnow().timestamp(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": round(memory.available / 1024 / 1024, 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except ImportError:
            # psutil não instalado, retorna info básica
            return {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Application health check failed: {str(e)}", exc_info=True)
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


async def liveness_probe() -> Dict[str, Any]:
    """
    Liveness probe - indica se aplicação está viva.
    Usado por Kubernetes para reiniciar pods travados.
    
    Returns:
        dict: Status mínimo (deve ser rápido)
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


async def readiness_probe() -> Dict[str, Any]:
    """
    Readiness probe - indica se aplicação está pronta para receber tráfego.
    Usado por load balancers para rotear requests.
    
    Returns:
        dict: Status completo com dependências
    """
    health = HealthCheck()
    
    # Verifica dependências críticas
    db_health = await health.check_database()
    
    # Se DB estiver down, não está ready
    if db_health["status"] != "healthy":
        return {
            "status": "not_ready",
            "reason": "database_unavailable",
            "database": db_health,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "status": "ready",
        "database": db_health,
        "timestamp": datetime.utcnow().isoformat()
    }


async def startup_probe() -> Dict[str, Any]:
    """
    Startup probe - indica se aplicação terminou inicialização.
    Usado por Kubernetes para aguardar startup lento.
    
    Returns:
        dict: Status de inicialização
    """
    health = HealthCheck()
    
    db_health = await health.check_database()
    
    if db_health["status"] != "healthy":
        return {
            "status": "starting",
            "reason": "waiting_for_database",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat()
    }
