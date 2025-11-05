"""
Controllers para health checks endpoints.
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.infrastructure.health import (
    liveness_probe,
    readiness_probe,
    startup_probe,
)
from src.infrastructure.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/health",
    summary="Basic health check",
    description="Retorna status básico da aplicação (alias para /health/live)",
    tags=["Health"]
)
async def health_check():
    """
    Health check básico - compatibilidade com /health tradicional.
    """
    result = await liveness_probe()
    return result


@router.get(
    "/health/live",
    summary="Liveness probe",
    description="Indica se aplicação está viva (Kubernetes liveness probe)",
    tags=["Health"],
    status_code=status.HTTP_200_OK
)
async def liveness():
    """
    Liveness probe - Kubernetes reinicia pod se falhar.
    
    - Retorna 200 se aplicação está rodando
    - Deve ser RÁPIDO (< 100ms)
    - Não verifica dependências externas
    """
    result = await liveness_probe()
    return result


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="Indica se aplicação está pronta para tráfego (Kubernetes readiness probe)",
    tags=["Health"]
)
async def readiness():
    """
    Readiness probe - Load balancer roteia tráfego se retornar 200.
    
    - Retorna 200 se pode receber requests
    - Retorna 503 se dependências estão down
    - Verifica: DB, cache, filas, etc
    """
    result = await readiness_probe()
    
    if result["status"] == "not_ready":
        logger.warning("Readiness probe failed", extra=result)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result
        )
    
    return result


@router.get(
    "/health/startup",
    summary="Startup probe",
    description="Indica se aplicação terminou inicialização (Kubernetes startup probe)",
    tags=["Health"]
)
async def startup():
    """
    Startup probe - Kubernetes aguarda startup antes de checar liveness.
    
    - Retorna 200 quando inicialização completa
    - Retorna 503 enquanto iniciando
    - Útil para apps com startup lento (migrations, warm-up)
    """
    result = await startup_probe()
    
    if result["status"] == "starting":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result
        )
    
    return result

