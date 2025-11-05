from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.infrastructure.logging_config import setup_logging, get_logger
from src.infrastructure.database import create_db_and_tables
from src.infrastructure.controllers.fatura import router as fatura_router
from src.infrastructure.controllers.guia import router as guia_router
from src.infrastructure.controllers.health import router as health_router
from src.infrastructure.exceptions import AppException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from src.infrastructure.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
    generic_exception_handler,
)

# Setup logging
setup_logging("INFO")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    try:
        await create_db_and_tables()
        logger.info("Database tables created/verified successfully")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Application shutdown initiated")


app = FastAPI()
app = FastAPI(
    lifespan=lifespan,
    title="POC saude API",
    description="API with FastAPI, SQLModel and PostgreSQL",
    version="1.0.0",
)


# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)


app.include_router(router=health_router, tags=["Health"])
app.include_router(prefix="/api/v1/guia", router=guia_router, tags=["Guias"])
app.include_router(prefix="/api/v1/faturas", router=fatura_router, tags=["Faturas"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
