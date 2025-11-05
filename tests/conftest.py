"""Configuração de fixtures compartilhadas para os testes."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="engine")
def engine_fixture():
    """Cria engine in-memory para testes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Cria sessão de banco de dados para testes."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture():
    """Cria client HTTP para testes."""
    from src.application.saude import app
    
    with TestClient(app) as client:
        yield client
