from sqlmodel import SQLModel

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from src.infrastructure.logging_config import get_logger
from src.infrastructure.config.settings import Settings
# Importar todos os modelos antes de create_all
from src.domain import (  # noqa: F401
    Beneficiario,
    ProfissionalSolicitante,
    Prestador,
    Guia,
    Procedimento,
    Material,
    Autorizacao,
    Fatura,
    FaturaGuia,
)

logger = get_logger(__name__)

DATABASE_URL = (
    Settings().database_url
)
async_engine = create_async_engine(DATABASE_URL, echo=False)


async def create_db_and_tables():
    """Create database tables if they don't exist."""
    logger.info("Creating database tables...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(
            f"Error creating database tables: {str(e)}",
            exc_info=True
        )
        raise


async def get_session():
    """Dependency for getting database session."""
    async with AsyncSession(async_engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(
                f"Error in database session: {str(e)}",
                exc_info=True
            )
            await session.rollback()
            raise
        finally:
            await session.close()
