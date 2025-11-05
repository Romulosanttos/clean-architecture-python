"""Testes para módulo de exceções."""
import pytest
from src.infrastructure.exceptions import (
    AppException,
    NotFoundException,
    ValidationException,
    DatabaseException,
    DuplicateException
)


def test_app_exception():
    """Testa exceção base AppException."""
    exc = AppException("Erro geral", 500)
    assert exc.message == "Erro geral"
    assert exc.status_code == 500


def test_not_found_exception():
    """Testa NotFoundException."""
    exc = NotFoundException("User", 123)
    assert "User" in exc.message
    assert "123" in exc.message
    assert exc.status_code == 404


def test_validation_exception():
    """Testa ValidationException."""
    exc = ValidationException("Dados inválidos")
    assert exc.message == "Dados inválidos"
    assert exc.status_code == 400


def test_database_exception():
    """Testa DatabaseException."""
    exc = DatabaseException("Erro de conexão")
    assert exc.message == "Erro de conexão"
    assert exc.status_code == 500


def test_duplicate_exception():
    """Testa DuplicateException."""
    exc = DuplicateException("User", "email", "test@example.com")
    assert "User" in exc.message
    assert "email" in exc.message
    assert "test@example.com" in exc.message
    assert exc.status_code == 409


def test_app_exception_inheritance():
    """Testa herança de Exception."""
    exc = AppException("Test")
    assert isinstance(exc, Exception)


def test_exception_message_attribute():
    """Testa atributo message."""
    exc = ValidationException("Teste de validação")
    assert hasattr(exc, 'message')
    assert hasattr(exc, 'status_code')
