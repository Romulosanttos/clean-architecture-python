from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status, Request, Query
from src.infrastructure.database import get_session, PageNumber, PageSize
from src.domain.guia import Guia
from src.domain.guia_dto import GuiaFullDTO
from src.use_cases.guia import GuiaUseCases
from src.infrastructure.paginations import PagedList

router = APIRouter()

@router.get("/")
async def list_guias(
    request: Request,
    page: PageNumber = 1,
    per_page: PageSize = 2048,
    guia_status: str = Query(None, description="Status da guia", alias="status"),
    session: AsyncSession = Depends(get_session),
):
    """
    Lista guias com paginação automática (GitHub headers).

    Response headers:
    - X-Total-Count: 150
    - Link: <url?page=2>; rel="next", <url?page=1>; rel="prev", ...
    """
    use_case = GuiaUseCases(session)

    # Busca com filtros opcionais
    filters = {"status": guia_status} if guia_status else {}
    items, pagination = await use_case.search(filters, page, per_page)

    # Retorna resposta com headers
    return PagedList(
        items=items,
        page=pagination,
        base_url=str(request.base_url).rstrip('/'),
        endpoint="api/v1/guia",
        status=guia_status,  # filtros adicionais para links
    ).to_response()


@router.post("/", response_model=Guia, status_code=status.HTTP_201_CREATED)
async def create_guia(guia: Guia, session: AsyncSession = Depends(get_session)):
    """Cria uma nova guia usando o modelo básico (com IDs de FK existentes)."""
    use_case = GuiaUseCases(session)
    return await use_case.create(guia)


@router.post("/full", response_model=Guia, status_code=status.HTTP_201_CREATED)
async def create_guia_full(
    guia_data: GuiaFullDTO, 
    session: AsyncSession = Depends(get_session)
):
    """
    Cria uma nova guia com dados completos de todas as entidades relacionadas.
    
    Este endpoint permite criar uma guia informando todos os dados do beneficiário,
    profissional solicitante, procedimentos, materiais e autorizações em uma única requisição.
    
    A criação segue a ordem de dependências:
    1. Beneficiário
    2. Profissional Solicitante  
    3. Guia
    4. Procedimentos
    5. Materiais (por procedimento)
    6. Autorizações
    """
    use_case = GuiaUseCases(session)
    return await use_case.create_full(guia_data)
