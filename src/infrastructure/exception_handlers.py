"""
Exception handlers para FastAPI.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.infrastructure.exceptions import AppException
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__)


async def app_exception_handler(
    request: Request,
    exc: AppException
) -> JSONResponse:
    """Handler para exceções customizadas da aplicação."""
    logger.warning(
        f"App exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": request.url.path
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handler para erros de validação do Pydantic."""
    logger.warning(
        "Validation error",
        extra={
            "errors": exc.errors(),
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": exc.errors(),
            "path": request.url.path
        }
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError
) -> JSONResponse:
    """Handler para erros de integridade do banco de dados."""
    logger.error(
        f"Database integrity error: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )
    
    # Parse common integrity errors
    error_msg = str(exc.orig)
    if "duplicate key" in error_msg.lower():
        message = "Resource already exists"
        status_code = status.HTTP_409_CONFLICT
    elif "foreign key" in error_msg.lower():
        message = "Referenced resource does not exist"
        status_code = status.HTTP_400_BAD_REQUEST
    elif "not null" in error_msg.lower():
        message = "Required field is missing"
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        message = "Database constraint violation"
        status_code = status.HTTP_400_BAD_REQUEST
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "IntegrityError",
            "message": message,
            "path": request.url.path
        }
    )


async def sqlalchemy_error_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handler para erros gerais do SQLAlchemy."""
    logger.error(
        f"Database error: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "message": "An error occurred while processing your request",
            "path": request.url.path
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handler para exceções não tratadas."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": request.url.path
        }
    )
