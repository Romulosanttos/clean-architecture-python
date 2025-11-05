from src.domain.guia import Guia
from src.infrastructure.database.repository_base import RepositoryBase
from sqlmodel.ext.asyncio.session import AsyncSession

class GuiaUseCases(RepositoryBase[Guia]):
    def __init__(self, session: AsyncSession):
        super().__init__(Guia, session)