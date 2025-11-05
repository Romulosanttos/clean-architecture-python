from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from pydantic import field_validator, model_validator
import re


class Fatura(SQLModel, table=True):
    """
    Fatura gerada pelo prestador para cobrança de procedimentos
    """

    __tablename__: str = "fatura"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    numero_fatura: str = Field(min_length=1, max_length=100, unique=True)
    data_emissao: datetime = Field(default_factory=lambda: datetime.now())
    data_vencimento: Optional[datetime] = Field(default=None)
    periodo_inicio: datetime
    periodo_fim: datetime
    prestador_id: int = Field(foreign_key="prestador.id", nullable=False)
    status: str = Field(
        default="pendente", min_length=1, max_length=50
    )  # pendente, aprovada, paga, rejeitada
    valor_total: Decimal = Field(
        default=Decimal("0.00"), decimal_places=2, max_digits=12
    )
    observacoes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("numero_fatura")
    @classmethod
    def validar_numero_fatura(cls, v: str) -> str:
        """Valida formato do número da fatura."""
        if not v or not v.strip():
            raise ValueError("Número da fatura não pode ser vazio")
        
        v = v.strip().upper()
        
        # Mínimo 5 caracteres
        if len(v) < 5:
            raise ValueError("Número da fatura deve ter no mínimo 5 caracteres")
        
        # Formato alfanumérico com hífen e barra
        if not re.match(r'^[A-Z0-9\-\/]+$', v):
            raise ValueError("Número da fatura deve ser alfanumérico (A-Z, 0-9, -, /)")
        
        return v
    
    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida status da fatura."""
        v = v.lower().strip()
        
        status_validos = [
            "pendente",
            "em_analise",
            "aprovada",
            "aprovada_parcial",
            "paga",
            "paga_parcial",
            "rejeitada",
            "cancelada"
        ]
        
        if v not in status_validos:
            raise ValueError(
                f"Status deve ser um de: {', '.join(status_validos)}"
            )
        
        return v
    
    @field_validator("valor_total")
    @classmethod
    def validar_valor_total(cls, v: Decimal) -> Decimal:
        """Valida valor total da fatura."""
        if v < 0:
            raise ValueError("Valor total não pode ser negativo")
        
        if v > Decimal("9999999.99"):
            raise ValueError("Valor total excede limite máximo (R$ 9.999.999,99)")
        
        return v
    
    @field_validator("data_emissao")
    @classmethod
    def validar_data_emissao(cls, v: datetime) -> datetime:
        """Valida data de emissão."""
        hoje = datetime.now()
        
        # Não pode ser no futuro
        if v > hoje:
            raise ValueError("Data de emissão não pode ser no futuro")
        
        # Não pode ser muito antiga (máximo 1 ano)
        if (hoje - v).days > 365:
            raise ValueError("Data de emissão não pode ser mais de 1 ano no passado")
        
        return v
    
    @field_validator("data_vencimento")
    @classmethod
    def validar_data_vencimento(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida data de vencimento."""
        if v is None:
            return v
        
        hoje = datetime.now()
        
        # Deve ser no futuro (ou hoje)
        if v < hoje.replace(hour=0, minute=0, second=0, microsecond=0):
            # Vencida
            pass  # Permitir faturas vencidas
        
        # Máximo 1 ano no futuro
        if (v - hoje).days > 365:
            raise ValueError("Data de vencimento não pode ser mais de 1 ano no futuro")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência entre campos."""
        # 1. Período fim deve ser após período início
        if self.periodo_fim <= self.periodo_inicio:
            raise ValueError("Período fim deve ser após período início")
        
        # 2. Período não pode ser muito longo (máximo 3 meses)
        dias_periodo = (self.periodo_fim - self.periodo_inicio).days
        if dias_periodo > 90:
            raise ValueError("Período de faturamento não pode exceder 90 dias")
        
        # 3. Data de vencimento deve ser após emissão
        if self.data_vencimento:
            if self.data_vencimento < self.data_emissao:
                raise ValueError("Data de vencimento deve ser após data de emissão")
            
            # Prazo mínimo: 5 dias
            if (self.data_vencimento - self.data_emissao).days < 5:
                raise ValueError("Prazo de vencimento deve ser no mínimo 5 dias após emissão")
        
        # 4. Data de emissão deve estar dentro ou após o período faturado
        if self.data_emissao < self.periodo_inicio:
            raise ValueError("Data de emissão não pode ser antes do período faturado")
        
        # Máximo 30 dias após fim do período
        if (self.data_emissao - self.periodo_fim).days > 30:
            raise ValueError("Data de emissão deve ser até 30 dias após fim do período")
        
        # 5. Faturas pagas devem ter valor > 0
        if self.status in ["paga", "paga_parcial", "aprovada"]:
            if self.valor_total == 0:
                raise ValueError(f"Fatura com status '{self.status}' deve ter valor > 0")
        
        return self

