"""Paginação simplificada com suporte a GitHub headers (RFC 5988)."""
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar, Annotated
from urllib.parse import urlencode
import math
from fastapi import Query
from fastapi.responses import JSONResponse

T = TypeVar("T")

# Anotações reutilizáveis para paginação (sem default)
PageNumber = Annotated[int, Query(ge=1, description="Página atual")]
PageSize = Annotated[int, Query(ge=1, le=2048, description="Itens por página")]


@dataclass
class Page:
    """Parâmetros de paginação (query + response)."""
    page: int = 1
    per_page: int = 30
    total: Optional[int] = None

    @property
    def offset(self) -> int:
        """Offset SQL: (page - 1) * per_page"""
        return (self.page - 1) * self.per_page

    @property
    def total_pages(self) -> Optional[int]:
        return math.ceil(self.total / self.per_page) if self.total and self.per_page > 0 else None

    @property
    def has_next(self) -> bool:
        return self.total_pages is not None and self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }

    def headers(self, base_url: str = "", endpoint: str = "", **filters) -> dict:
        """GitHub pagination headers: X-Total-Count + Link"""
        links = [f'<{self._url(base_url, endpoint, self.page, **filters)}>; rel="self"']
        
        if self.has_next:
            links.append(f'<{self._url(base_url, endpoint, self.page + 1, **filters)}>; rel="next"')
        if self.has_prev:
            links.append(f'<{self._url(base_url, endpoint, self.page - 1, **filters)}>; rel="prev"')
            links.append(f'<{self._url(base_url, endpoint, 1, **filters)}>; rel="first"')
        if self.has_next and self.total_pages:
            links.append(f'<{self._url(base_url, endpoint, self.total_pages, **filters)}>; rel="last"')
        
        return {
            "X-Total-Count": str(self.total or 0),
            "Link": ", ".join(links)
        }

    def _url(self, base: str, endpoint: str, page: int, **filters) -> str:
        params = {"page": page, "per_page": self.per_page, **filters}
        return f"{base.rstrip('/')}/{endpoint.lstrip('/')}?{urlencode(params, doseq=True)}"


class PagedList(Generic[T]):
    """Lista paginada com headers automáticos e resposta JSON."""
    def __init__(self, items: List[T], page: Page, base_url: str = "", endpoint: str = "", **filters):
        self.items = items
        self.page = page
        self.headers = page.headers(base_url, endpoint, **filters)

    def to_dict(self) -> dict:
        """Retorna dicionário com items e paginação."""
        return {"items": self.items, "pagination": self.page.to_dict()}
    
    def to_response(self) -> JSONResponse:
        """Retorna JSONResponse com headers HTTP."""
        return JSONResponse(
            content=self.to_dict(),
            headers=self.headers
        )


__all__ = ["Page", "PagedList", "PageNumber", "PageSize"]
