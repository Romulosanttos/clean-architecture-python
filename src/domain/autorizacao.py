from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Index
from pydantic import field_validator, model_validator
import re


class Autorizacao(SQLModel, table=True):
    """
    Autorização para um procedimento específico ou material (OPME).
    
    Tipos:
    - 'procedimento': Autoriza a realização do procedimento
    - 'opme': Autoriza material de alto custo (Órtese, Prótese, Material Especial)
    - 'material': Autoriza material comum
    """

    __tablename__: str = "autorizacao"
    __table_args__ = (
        Index("idx_autorizacao_procedimento", "procedimento_id"),
        Index("idx_autorizacao_material", "material_id"),
        Index("idx_autorizacao_status", "status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    numero_autorizacao: str = Field(
        min_length=1, max_length=50, unique=True
    )
    data_autorizacao: datetime = Field(
        default_factory=lambda: datetime.now()
    )
    data_validade: datetime
    
    # Autorização pode ser para procedimento OU material
    procedimento_id: Optional[int] = Field(
        default=None, foreign_key="procedimento.id"
    )
    material_id: Optional[int] = Field(
        default=None, foreign_key="material.id"
    )
    
    tipo_autorizacao: str = Field(
        min_length=1, max_length=20
    )  # procedimento, opme, material
    
    prestador_executante_id: Optional[int] = Field(
        default=None, foreign_key="prestador.id"
    )
    aprovador_identificador: Optional[str] = Field(
        default=None, max_length=255
    )
    status: str = Field(
        default="pendente", min_length=1, max_length=50
    )  # pendente, aprovada, negada, expirada
    motivo_negacao: Optional[str] = Field(
        default=None, max_length=1000
    )  # Se status = negada
    observacoes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("numero_autorizacao")
    @classmethod
    def validar_numero_autorizacao(cls, v: str) -> str:
        """Valida número da autorização."""
        if not v or not v.strip():
            raise ValueError("Número da autorização não pode ser vazio")
        
        v = v.strip().upper()
        
        if len(v) < 5:
            raise ValueError("Número da autorização deve ter no mínimo 5 caracteres")
        
        # Formato alfanumérico
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError("Número deve ser alfanumérico (A-Z, 0-9, -)")
        
        return v
    
    @field_validator("tipo_autorizacao")
    @classmethod
    def validar_tipo_autorizacao(cls, v: str) -> str:
        """Valida tipo de autorização."""
        v = v.lower().strip()
        
        tipos_validos = ["procedimento", "opme", "material"]
        
        if v not in tipos_validos:
            raise ValueError(
                f"Tipo de autorização deve ser um de: {', '.join(tipos_validos)}"
            )
        
        return v
    
    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida status da autorização."""
        v = v.lower().strip()
        
        status_validos = ["pendente", "aprovada", "negada", "expirada", "cancelada"]
        
        if v not in status_validos:
            raise ValueError(
                f"Status deve ser um de: {', '.join(status_validos)}"
            )
        
        return v
    
    @field_validator("data_autorizacao")
    @classmethod
    def validar_data_autorizacao(cls, v: datetime) -> datetime:
        """Valida data de autorização."""
        hoje = datetime.now()
        
        # Não pode ser no futuro
        if v > hoje:
            raise ValueError("Data de autorização não pode ser no futuro")
        
        # Não pode ser muito antiga (máximo 6 meses)
        if (hoje - v).days > 180:
            raise ValueError("Data de autorização não pode ser mais de 6 meses no passado")
        
        return v
    
    @field_validator("data_validade")
    @classmethod
    def validar_data_validade(cls, v: datetime) -> datetime:
        """Valida data de validade."""
        hoje = datetime.now()
        
        # Deve ser no futuro (ou pelo menos hoje)
        if v < hoje.replace(hour=0, minute=0, second=0, microsecond=0):
            # Permite autorizações expiradas (para histórico)
            pass
        
        # Máximo 1 ano de validade
        if (v - hoje).days > 365:
            raise ValueError("Validade máxima é 1 ano")
        
        return v
    
    @field_validator("motivo_negacao")
    @classmethod
    def validar_motivo_negacao(cls, v: Optional[str]) -> Optional[str]:
        """Valida motivo de negação."""
        if v is None:
            return v
        
        v = v.strip()
        
        if len(v) < 10:
            raise ValueError("Motivo de negação deve ter no mínimo 10 caracteres")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência entre campos."""
        # 1. Deve autorizar procedimento OU material (XOR)
        tem_procedimento = self.procedimento_id is not None
        tem_material = self.material_id is not None
        
        if not tem_procedimento and not tem_material:
            raise ValueError(
                "Autorização deve referenciar um procedimento OU um material"
            )
        
        if tem_procedimento and tem_material:
            raise ValueError(
                "Autorização não pode referenciar procedimento E material simultaneamente"
            )
        
        # 2. Tipo deve corresponder ao que está sendo autorizado
        if tem_procedimento and self.tipo_autorizacao != "procedimento":
            raise ValueError(
                "Tipo deve ser 'procedimento' quando procedimento_id está preenchido"
            )
        
        if tem_material and self.tipo_autorizacao not in ["opme", "material"]:
            raise ValueError(
                "Tipo deve ser 'opme' ou 'material' quando material_id está preenchido"
            )
        
        # 3. Data de validade deve ser após data de autorização
        if self.data_validade <= self.data_autorizacao:
            raise ValueError("Data de validade deve ser após data de autorização")
        
        # 4. Validade mínima: 1 dia
        dias_validade = (self.data_validade - self.data_autorizacao).days
        if dias_validade < 1:
            raise ValueError("Autorização deve ter validade mínima de 1 dia")
        
        # 5. Status 'aprovada' requer prestador executante
        if self.status == "aprovada":
            if not self.prestador_executante_id:
                raise ValueError(
                    "Autorização aprovada deve ter prestador executante"
                )
        
        # 6. Status 'negada' requer motivo
        if self.status == "negada":
            if not self.motivo_negacao or len(self.motivo_negacao.strip()) < 10:
                raise ValueError(
                    "Autorização negada deve ter motivo detalhado (mínimo 10 caracteres)"
                )
        
        # 7. OPME deve ter observações/justificativa
        if self.tipo_autorizacao == "opme":
            if not self.observacoes or len(self.observacoes.strip()) < 20:
                raise ValueError(
                    "Autorização de OPME requer justificativa detalhada"
                )
        
        # 8. Validar se autorização está expirada
        if self.status == "aprovada":
            hoje = datetime.now()
            if self.data_validade < hoje:
                raise ValueError(
                    "Autorização expirada não pode ter status 'aprovada'. "
                    "Use status 'expirada'."
                )
        
        return self

