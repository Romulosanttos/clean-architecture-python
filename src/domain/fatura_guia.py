from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Index
from pydantic import model_validator


class FaturaGuia(SQLModel, table=True):
    """
    Tabela associativa entre Fatura e Guia.
    
    Representa quais guias estão sendo cobradas em cada fatura.
    Uma fatura contém várias guias.
    Uma guia pode estar em apenas uma fatura.
    """

    __tablename__: str = "fatura_guia"
    __table_args__ = (
        Index("idx_fatura_guia_fatura", "fatura_id"),
        Index("idx_fatura_guia_guia", "guia_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    fatura_id: int = Field(foreign_key="fatura.id", nullable=False)
    guia_id: int = Field(
        foreign_key="guia.id", nullable=False, unique=True
    )  # unique: uma guia só pode estar em uma fatura
    data_inclusao: datetime = Field(
        default_factory=lambda: datetime.now()
    )  # quando foi adicionada à fatura

    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência da associação fatura-guia."""
        # 1. Validar que fatura_id e guia_id estão preenchidos
        if not self.fatura_id or self.fatura_id <= 0:
            raise ValueError("fatura_id deve ser um ID válido (> 0)")
        
        if not self.guia_id or self.guia_id <= 0:
            raise ValueError("guia_id deve ser um ID válido (> 0)")
        
        # 2. Validar data de inclusão
        hoje = datetime.now()
        
        if self.data_inclusao > hoje:
            raise ValueError("Data de inclusão não pode ser no futuro")
        
        # Não pode ser muito antiga (máximo 2 anos)
        if (hoje - self.data_inclusao).days > 730:
            raise ValueError(
                "Data de inclusão não pode ser mais de 2 anos no passado"
            )
        
        return self
