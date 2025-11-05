from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel, Index
from pydantic import BaseModel, field_validator, model_validator


class Guia(SQLModel, table=True):
    """
    Guia de solicitação de procedimentos
    """

    __tablename__: str = "guia"
    __table_args__ = (
        Index("idx_guia_beneficiario", "beneficiario_id"),
        Index("idx_guia_status", "status"),
        Index("idx_guia_data_solicitacao", "data_solicitacao"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, description="ID único da guia")
    id: Optional[int] = Field(default=None, primary_key=True, description="ID único da guia")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(), 
        description="Data e hora de criação do registro"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Data e hora da última atualização"
    )
    numero_guia: str = Field(
        min_length=1, max_length=100, unique=True,
        description="Número único da guia"
    )
    data_solicitacao: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Data de solicitação da guia"
    )
    indicacao_clinica: Optional[str] = Field(
        default=None, max_length=1000,
        description="Indicação clínica para o procedimento"
    )
    tipo_atendimento: str = Field(
        min_length=1, max_length=50,
        description="Tipo de atendimento: eletivo, urgencia, emergencia"
    )
    beneficiario_id: int = Field(
        foreign_key="beneficiario.id", nullable=False,
        description="ID do beneficiário (deve existir na tabela beneficiario)"
    )
    solicitante_id: Optional[int] = Field(
        default=None, foreign_key="profissional_solicitante.id",
        description="ID do profissional solicitante"
    )
    status: str = Field(
        default="solicitada", min_length=1, max_length=50,
        description="Status da guia: solicitada, autorizada, realizada, faturada, paga"
    )
    valor_total: Decimal = Field(
        default=Decimal("0.00"), decimal_places=2, max_digits=10,
        description="Valor total dos procedimentos da guia"
    )

    @field_validator("numero_guia")
    @classmethod
    def validar_numero_guia(cls, v: str) -> str:
        """Valida formato do número da guia."""
        if not v or not v.strip():
            raise ValueError("Número da guia não pode ser vazio")
        
        v = v.strip().upper()
        
        # Mínimo 5 caracteres
        if len(v) < 5:
            raise ValueError("Número da guia deve ter no mínimo 5 caracteres")
        
        # Aceita alfanumérico com hífen
        import re
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError("Número da guia deve ser alfanumérico (A-Z, 0-9, -)")
        
        return v
    
    @field_validator("tipo_atendimento")
    @classmethod
    def validar_tipo_atendimento(cls, v: str) -> str:
        """Valida tipo de atendimento."""
        v = v.lower().strip()
        
        tipos_validos = ["eletivo", "urgencia", "emergencia"]
        
        if v not in tipos_validos:
            raise ValueError(
                f"Tipo de atendimento deve ser um de: {', '.join(tipos_validos)}"
            )
        
        return v
    
    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida status da guia."""
        v = v.lower().strip()
        
        status_validos = [
            "solicitada",
            "autorizada", 
            "realizada",
            "faturada",
            "paga",
            "cancelada",
            "negada"
        ]
        
        if v not in status_validos:
            raise ValueError(
                f"Status deve ser um de: {', '.join(status_validos)}"
            )
        
        return v
    
    @field_validator("valor_total")
    @classmethod
    def validar_valor_total(cls, v: Decimal) -> Decimal:
        """Valida se valor total é não-negativo."""
        if v < 0:
            raise ValueError("Valor total não pode ser negativo")
        
        if v > Decimal("999999.99"):
            raise ValueError("Valor total excede limite máximo (R$ 999.999,99)")
        
        return v
    
    @field_validator("indicacao_clinica")
    @classmethod
    def validar_indicacao_clinica(cls, v: Optional[str]) -> Optional[str]:
        """Valida indicação clínica."""
        if v is None:
            return v
        
        v = v.strip()
        
        if len(v) < 10:
            raise ValueError("Indicação clínica deve ter no mínimo 10 caracteres")
        
        return v
    
    @field_validator("data_solicitacao")
    @classmethod
    def validar_data_solicitacao(cls, v: datetime) -> datetime:
        """Valida data de solicitação."""
        hoje = datetime.now()
        
        # Não pode ser muito no futuro (máximo 7 dias)
        if v > hoje:
            dias_futuro = (v - hoje).days
            if dias_futuro > 7:
                raise ValueError("Data de solicitação não pode ser mais de 7 dias no futuro")
        
        # Não pode ser muito antiga (máximo 1 ano)
        if v < hoje:
            dias_passado = (hoje - v).days
            if dias_passado > 365:
                raise ValueError("Data de solicitação não pode ser mais de 1 ano no passado")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência entre campos."""
        # Emergência/Urgência deveria ter indicação clínica
        if self.tipo_atendimento in ["urgencia", "emergencia"]:
            if not self.indicacao_clinica or len(self.indicacao_clinica.strip()) < 10:
                raise ValueError(
                    f"Guia de {self.tipo_atendimento} requer indicação clínica detalhada"
                )
        
        # Status 'autorizada' ou superior deveria ter solicitante
        status_com_solicitante = ["autorizada", "realizada", "faturada", "paga"]
        if self.status in status_com_solicitante and not self.solicitante_id:
            raise ValueError(
                f"Guia com status '{self.status}' requer profissional solicitante"
            )
        
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "created_at": "2025-11-05T10:00:00",
                "updated_at": "2025-11-05T10:00:00", 
                "numero_guia": "GUIA-2025-001",
                "data_solicitacao": "2025-11-05T10:00:00",
                "indicacao_clinica": "Consulta de rotina preventiva",
                "tipo_atendimento": "eletivo",
                "beneficiario_id": 1,
                "solicitante_id": 1,
                "status": "solicitada",
                "valor_total": 150.00
            }
        }
    }
