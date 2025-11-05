# Sistema de Processamento de Guias Médicas

Sistema de estudo explorando arquitetura limpa e processamento assíncrono no domínio de saúde.

## Stack Implementado

- **FastAPI** + **SQLModel** + **PostgreSQL**
- **Docker** + **Kubernetes** (deployment configs)
- **Pytest** (120+ testes, 37% domain coverage)
- **Structured Logging** + Exception Handling

## Arquitetura

```
application/      # FastAPI app + lifespan
use_cases/        # Business logic
domain/           # Entities (9 tables)
infrastructure/   # DB, Controllers, Exceptions
```

**Fluxo:**  
`Client → Controller → UseCase → Domain → Repository → DB`

## Domínio

Guia médica com ciclo completo:
- **Guia** → **Procedimento** → **Material** (solicitado → autorizado → utilizado)
- **Autorização** (procedimento/OPME)
- **Fatura** (agregação de guias)
- Detecção de glosas (quantidade_utilizada > quantidade_autorizada)

Ver [MODELAGEM.md](./MODELAGEM.md) para diagrama completo.

## Quick Start

```bash
docker-compose up -d
curl http://localhost:8000/docs
```

## Testing

```bash
pytest tests/ -v --cov
```

## Padrões Implementados

- **Clean Architecture** (4 layers isoladas)
- **Repository Pattern** (abstração de persistência)
- **Dependency Injection** (FastAPI Depends)
- **Domain-Driven Design** (9 entidades com validações)
- **Health Checks** (Kubernetes-ready: startup/liveness/readiness)

## Observabilidade

```python
# Logs estruturados
logger.info("Guia processed", extra={"guia_id": 123, "score": 45})

# Exception handlers customizados (5 tipos)
- AppException
- RequestValidationError  
- IntegrityError
- SQLAlchemyError
- Generic Exception
```

## Aprendizados

1. **Validação multi-layer** (Pydantic field/model validators → DB constraints)
2. **Async/await patterns** (AsyncSession, async endpoints, lifespan context)
3. **Complex domain modeling** (9 entidades, N:M relations, lifecycle states)
4. **Testing discipline** (120+ tests, model_validate() pattern for validators)
5. **Kubernetes deployment** (probes, resource limits, replicas)

---

## 📊 Evidências de Padrões no Código

### 🏛️ Clean Architecture (4 Layers)

```
src/
├── domain/              # ← LAYER 1: Entidades puras (zero dependências externas)
│   └── guia.py
├── use_cases/           # ← LAYER 2: Lógica de negócio
│   └── guia.py
├── infrastructure/      # ← LAYER 3: Detalhes técnicos (DB, HTTP)
│   ├── database/
│   │   └── repository_base.py
│   └── controllers/
│       └── guia.py
└── application/         # ← LAYER 4: Entry point (FastAPI app)
    └── saude.py
```

**Direção das dependências:**
```
application → use_cases → domain ← infrastructure
                ↑                       ↑
                └───────────────────────┘
         (infrastructure depende de domain, nunca o contrário)
```

**Exemplo - Domain Layer puro:**
```python
# src/domain/guia.py
from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import field_validator

class Guia(SQLModel, table=True):
    """Entidade pura - só regras de negócio, SEM imports de infra"""
    numero_guia: str
    status: str
    
    @field_validator("status")
    def validar_status(cls, v: str):
        status_validos = ["solicitada", "autorizada", "realizada"]
        if v not in status_validos:
            raise ValueError("Status inválido")
        return v
```

---

### 🎯 SOLID Principles

#### **S - Single Responsibility Principle**
```python
# Cada classe tem UMA responsabilidade

# src/domain/guia.py
class Guia(SQLModel):
    """RESPONSABILIDADE: Representar entidade + validações de negócio"""
    # NÃO faz: persistência, logging, HTTP handling

# src/use_cases/guia.py
class GuiaUseCases:
    """RESPONSABILIDADE: Orquestrar operações de negócio"""
    # NÃO faz: validação de domínio, detalhes de SQL

# src/infrastructure/controllers/guia.py
@router.get("/")
async def list_guias():
    """RESPONSABILIDADE: HTTP request/response"""
    # NÃO faz: lógica de negócio, validação
```

#### **O - Open/Closed Principle**
```python
# src/infrastructure/database/repository_base.py
class RepositoryBase(Generic[T]):  # ← ABERTO para extensão
    """Base genérica - pode ser estendida sem modificar código"""
    
    async def create(self, data: T) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        return instance

# src/use_cases/guia.py
class GuiaUseCases(RepositoryBase[Guia]):  # ← FECHADO para modificação
    """Especialização - herda comportamento sem alterar base"""
    def __init__(self, session: AsyncSession):
        super().__init__(Guia, session)
```

#### **L - Liskov Substitution Principle**
```python
# Qualquer subclasse de RepositoryBase pode substituir a base
use_case: RepositoryBase = GuiaUseCases(session)     # ← É um RepositoryBase
use_case: RepositoryBase = FaturaUseCases(session)   # ← Também é um RepositoryBase
# Ambos funcionam: create(), read(), list()
```

#### **I - Interface Segregation Principle**
```python
# Clientes usam só os métodos que precisam
class RepositoryBase(Generic[T]):
    async def create(self, data: T) -> T: ...
    async def read(self, id: int) -> Optional[T]: ...
    async def list(self, ...) -> tuple[list[T], Page]: ...

# Controller GET só chama list()
# Controller POST só chama create()
# Não é forçado a implementar tudo
```

#### **D - Dependency Inversion Principle**
```python
# src/infrastructure/controllers/guia.py
async def list_guias(
    session: AsyncSession = Depends(get_session),  # ← Injeção de dependência
):
    use_case = GuiaUseCases(session)  # ← Depende de abstração (AsyncSession)
    items, pagination = await use_case.list()
    
# Controller não instancia DB connection diretamente
# Depende de get_session() (abstração injetada pelo FastAPI)
```

---

### 🗄️ Repository Pattern

```python
# src/infrastructure/database/repository_base.py
class RepositoryBase(Generic[T]):
    """
    Abstrai persistência - Controllers não sabem que é PostgreSQL
    Poderia ser MongoDB, Redis, arquivo... interface continua igual
    """
    
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model      # ← Modelo de domínio
        self.session = session  # ← Mecanismo de persistência (abstrato)
    
    async def create(self, data: T) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        return instance

# Uso:
class GuiaUseCases(RepositoryBase[Guia]):
    """Repository específico - herda operações CRUD"""
    pass
```

---

### 💉 Dependency Injection

```python
# src/infrastructure/controllers/guia.py
from fastapi import Depends

@router.get("/")
async def list_guias(
    session: AsyncSession = Depends(get_session),  # ← DI
):
    """
    FastAPI injeta AsyncSession automaticamente
    - Controller não cria conexão DB
    - Fácil de mockar em testes
    """
    use_case = GuiaUseCases(session)
    return await use_case.list()
```

