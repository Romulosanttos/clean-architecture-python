from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel, Index
from pydantic import field_validator, model_validator


class Procedimento(SQLModel, table=True):
    """
    Procedimento médico realizado
    
    Representa um procedimento específico executado em uma guia.
    Suporta diferentes tabelas: TUSS (ANS), SIGTAP (SUS), etc.
    """

    __tablename__: str = "procedimento"
    __table_args__ = (
        Index("idx_procedimento_guia", "guia_id"),
        Index("idx_procedimento_codigo", "codigo", "tipo_tabela"),
        Index("idx_procedimento_data", "data_realizacao"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    guia_id: int = Field(
        foreign_key="guia.id", nullable=False
    )  # Procedimento pertence a UMA guia
    codigo: str = Field(min_length=1, max_length=20)
    tipo_tabela: str = Field(
        min_length=1, max_length=20
    )  # TUSS, SIGTAP, SIMPRO, BRASINDICE, etc
    descricao: str = Field(min_length=1, max_length=500)
    categoria: str = Field(
        min_length=1, max_length=100
    )  # consulta, cirurgia, exame, internacao, etc
    data_realizacao: Optional[datetime] = Field(default=None)
    prestador_executante_id: Optional[int] = Field(
        default=None, foreign_key="prestador.id"
    )
    quantidade: int = Field(default=1, ge=1)  # quantas vezes foi feito
    valor_unitario: Decimal = Field(
        default=Decimal("0.00"), decimal_places=2, max_digits=10
    )

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """Valida formato do código do procedimento."""
        if not v or not v.strip():
            raise ValueError("Código do procedimento não pode ser vazio")
        
        v = v.strip().upper()
        
        # Código deve ter entre 6 e 20 caracteres
        if len(v) < 6:
            raise ValueError("Código do procedimento deve ter no mínimo 6 caracteres")
        
        # Deve ser alfanumérico
        import re
        if not re.match(r'^[A-Z0-9\.\-]+$', v):
            raise ValueError("Código deve ser alfanumérico (A-Z, 0-9, ., -)")
        
        return v
    
    @field_validator("tipo_tabela")
    @classmethod
    def validar_tipo_tabela(cls, v: str) -> str:
        """Valida tipo de tabela de referência."""
        v = v.upper().strip()
        
        tabelas_validas = [
            "TUSS",      # ANS - Terminologia Unificada da Saúde Suplementar
            "SIGTAP",    # SUS - Sistema de Gerenciamento da Tabela de Procedimentos
            "SIMPRO",    # Materiais
            "BRASINDICE", # Materiais
            "CBHPM"      # Classificação Brasileira Hierarquizada de Procedimentos Médicos
        ]
        
        if v not in tabelas_validas:
            raise ValueError(
                f"Tipo de tabela deve ser um de: {', '.join(tabelas_validas)}"
            )
        
        return v
    
    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, v: str) -> str:
        """Valida categoria do procedimento."""
        v = v.lower().strip()
        
        categorias_validas = [
            "consulta",
            "exame",
            "cirurgia",
            "internacao",
            "procedimento ambulatorial",
            "terapia",
            "diagnostico",
            "urgencia"
        ]
        
        if v not in categorias_validas:
            raise ValueError(
                f"Categoria deve ser uma de: {', '.join(categorias_validas)}"
            )
        
        return v
    
    @field_validator("quantidade")
    @classmethod
    def validar_quantidade(cls, v: int) -> int:
        """Valida quantidade do procedimento."""
        if v < 1:
            raise ValueError("Quantidade deve ser no mínimo 1")
        
        if v > 100:
            raise ValueError("Quantidade máxima é 100 (verificar se correto)")
        
        return v
    
    @field_validator("valor_unitario")
    @classmethod
    def validar_valor_unitario(cls, v: Decimal) -> Decimal:
        """Valida valor unitário."""
        if v < 0:
            raise ValueError("Valor unitário não pode ser negativo")
        
        if v == 0:
            raise ValueError("Valor unitário deve ser maior que zero")
        
        if v > Decimal("999999.99"):
            raise ValueError("Valor unitário excede limite máximo")
        
        return v
    
    @field_validator("data_realizacao")
    @classmethod
    def validar_data_realizacao(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida data de realização."""
        if v is None:
            return v
        
        hoje = datetime.now()
        
        # Não pode ser no futuro
        if v > hoje:
            raise ValueError("Data de realização não pode ser no futuro")
        
        # Não pode ser muito antiga (máximo 2 anos)
        if (hoje - v).days > 730:
            raise ValueError("Data de realização não pode ser mais de 2 anos no passado")
        
        return v
    
    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, v: str) -> str:
        """Valida descrição do procedimento."""
        if not v or not v.strip():
            raise ValueError("Descrição não pode ser vazia")
        
        v = v.strip()
        
        if len(v) < 10:
            raise ValueError("Descrição deve ter no mínimo 10 caracteres")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência entre campos."""
        # Se tem data de realização, deve ter prestador executante
        if self.data_realizacao and not self.prestador_executante_id:
            raise ValueError(
                "Procedimento realizado deve ter prestador executante"
            )
        
        # Cirurgias devem ter valor mínimo
        if self.categoria == "cirurgia":
            if self.valor_unitario < Decimal("100.00"):
                raise ValueError(
                    "Cirurgia deve ter valor mínimo de R$ 100,00"
                )
        
        # Validação específica por tipo de tabela
        if self.tipo_tabela == "SIGTAP":
            # Códigos SIGTAP seguem padrão específico
            if not self.codigo.startswith(("01", "02", "03", "04")):
                raise ValueError(
                    "Código SIGTAP deve começar com grupo válido (01-04)"
                )
        
        return self

    observacoes: Optional[str] = Field(default=None, max_length=1000)
    valor_unitario: Decimal = Field(
        default=Decimal("0.00"), decimal_places=2, max_digits=10
    )
