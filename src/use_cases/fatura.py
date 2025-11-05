from src.domain.fatura import Fatura
from src.infrastructure.database.repository_base import RepositoryBase
from sqlmodel.ext.asyncio.session import AsyncSession

class FaturaUseCases(RepositoryBase[Fatura]):
    def __init__(self, session: AsyncSession):
        super().__init__(Fatura, session)