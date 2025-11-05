from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status, Query, Request
from src.infrastructure.database import get_session, PageNumber, PageSize
from src.infrastructure.paginations import PagedList
from src.domain.fatura import Fatura
from src.use_cases.fatura import FaturaUseCases

router = APIRouter()


@router.get("/")
async def list_faturas(
    request: Request,
    session: AsyncSession = Depends(get_session),
    fatura_id: int = Query(None, description="ID da fatura para buscar específica"),
    page: PageNumber = 1,
    per_page: PageSize = 2048,
):
    """
    Lista faturas com paginação ou busca uma fatura específica por ID.
    
    - Se `fatura_id` for informado: retorna apenas essa fatura
    - Senão: retorna lista paginada com headers GitHub
    """
    use_case = FaturaUseCases(session)
    
    # Busca específica por ID
    if fatura_id is not None:
        fatura = await use_case.read(fatura_id)
        return fatura
    
    # Lista paginada
    items, pagination = await use_case.list(page=page, per_page=per_page)
    
    return PagedList(
        items=items,
        page=pagination,
        base_url=str(request.base_url).rstrip('/'),
        endpoint="api/v1/fatura"
    ).to_response()


@router.post("/", response_model=Fatura, status_code=status.HTTP_201_CREATED)
async def create_fatura(fatura: Fatura, session: AsyncSession = Depends(get_session)):
    use_case = FaturaUseCases(session)
    return await use_case.create(fatura)
