"""Testes para pagination."""
from src.infrastructure.paginations.pagination import Page


def test_page_default():
    """Testa parâmetros de paginação padrão."""
    page = Page()
    assert page.page == 1
    assert page.per_page == 30


def test_page_custom():
    """Testa parâmetros de paginação customizados."""
    page = Page(page=2, per_page=25)
    assert page.page == 2
    assert page.per_page == 25
    assert page.offset == 25  # (page - 1) * per_page


def test_page_offset_calculation():
    """Testa cálculo do offset."""
    page = Page(page=3, per_page=20)
    assert page.offset == 40  # (3 - 1) * 20


def test_page_total_pages():
    """Testa cálculo de total de páginas."""
    page = Page(page=1, per_page=10, total=100)
    assert page.total_pages == 10


def test_page_total_pages_incompleto():
    """Testa total de páginas com última página incompleta."""
    page = Page(page=1, per_page=10, total=95)
    assert page.total_pages == 10  # ceil(95/10) = 10


def test_page_primeira_pagina():
    """Testa primeira página."""
    page = Page(page=1, per_page=20)
    assert page.offset == 0


def test_page_sem_total():
    """Testa página sem total definido."""
    page = Page(page=2, per_page=10)
    assert page.total is None
    assert page.total_pages is None
