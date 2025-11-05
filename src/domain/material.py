from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel, Index
from pydantic import field_validator, model_validator


class Material(SQLModel, table=True):
    """
    Material relacionado a um procedimento.
    
    Ciclo de vida:
    1. Status 'solicitado' - Prestador pede o material
    2. Status 'autorizado' - Operadora aprova (atualiza qtd_autorizada)
    3. Status 'utilizado' - Procedimento realizado (atualiza qtd_utilizada)
    4. Status 'glosado' - Negado ou divergência autorizado vs utilizado
    """

    __tablename__: str = "material"
    __table_args__ = (
        Index("idx_material_procedimento", "procedimento_id"),
        Index("idx_material_status", "status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    procedimento_id: int = Field(
        foreign_key="procedimento.id", nullable=False
    )
    codigo_material: str = Field(
        min_length=1, max_length=50
    )  # Código SIMPRO, BRASINDICE, etc
    descricao: str = Field(min_length=1, max_length=255)
    tipo_tabela: str = Field(
        min_length=1, max_length=20
    )  # SIMPRO, BRASINDICE, etc
    
    # Quantidades no ciclo de vida
    quantidade_solicitada: int = Field(ge=1)
    quantidade_autorizada: Optional[int] = Field(default=None, ge=0)
    quantidade_utilizada: Optional[int] = Field(default=None, ge=0)
    
    # Valores
    valor_unitario: Decimal = Field(
        default=Decimal("0.00"), decimal_places=2, max_digits=10
    )
    
    # Status e controle
    status: str = Field(
        default="solicitado", min_length=1, max_length=50
    )  # solicitado, autorizado, utilizado, glosado
    motivo_glosa: Optional[str] = Field(default=None, max_length=500)
    justificativa: Optional[str] = Field(default=None, max_length=1000)
    
    # Rastreabilidade (para OPME)
    lote: Optional[str] = Field(default=None, max_length=50)
    data_validade_lote: Optional[datetime] = Field(default=None)

    @field_validator("codigo_material")
    @classmethod
    def validar_codigo_material(cls, v: str) -> str:
        """Valida código do material."""
        if not v or not v.strip():
            raise ValueError("Código do material não pode ser vazio")
        
        v = v.strip().upper()
        
        # Mínimo 4 caracteres
        if len(v) < 4:
            raise ValueError("Código do material deve ter no mínimo 4 caracteres")
        
        import re
        if not re.match(r'^[A-Z0-9\.\-]+$', v):
            raise ValueError("Código deve ser alfanumérico (A-Z, 0-9, ., -)")
        
        return v
    
    @field_validator("tipo_tabela")
    @classmethod
    def validar_tipo_tabela(cls, v: str) -> str:
        """Valida tipo de tabela de materiais."""
        v = v.upper().strip()
        
        tabelas_validas = ["SIMPRO", "BRASINDICE", "ANVISA"]
        
        if v not in tabelas_validas:
            raise ValueError(
                f"Tipo de tabela deve ser um de: {', '.join(tabelas_validas)}"
            )
        
        return v
    
    @field_validator("quantidade_solicitada")
    @classmethod
    def validar_quantidade_solicitada(cls, v: int) -> int:
        """Valida quantidade solicitada."""
        if v < 1:
            raise ValueError("Quantidade solicitada deve ser no mínimo 1")
        
        if v > 1000:
            raise ValueError("Quantidade solicitada máxima é 1000 (verificar se correto)")
        
        return v
    
    @field_validator("quantidade_autorizada")
    @classmethod
    def validar_quantidade_autorizada(cls, v: Optional[int]) -> Optional[int]:
        """Valida quantidade autorizada."""
        if v is None:
            return v
        
        if v < 0:
            raise ValueError("Quantidade autorizada não pode ser negativa")
        
        if v > 1000:
            raise ValueError("Quantidade autorizada máxima é 1000")
        
        return v
    
    @field_validator("quantidade_utilizada")
    @classmethod
    def validar_quantidade_utilizada(cls, v: Optional[int]) -> Optional[int]:
        """Valida quantidade utilizada."""
        if v is None:
            return v
        
        if v < 0:
            raise ValueError("Quantidade utilizada não pode ser negativa")
        
        if v > 1000:
            raise ValueError("Quantidade utilizada máxima é 1000")
        
        return v
    
    @field_validator("valor_unitario")
    @classmethod
    def validar_valor_unitario(cls, v: Decimal) -> Decimal:
        """Valida valor unitário do material."""
        if v < 0:
            raise ValueError("Valor unitário não pode ser negativo")
        
        # Materiais de alto custo (OPME) podem ter valores muito altos
        if v > Decimal("99999.99"):
            raise ValueError("Valor unitário excede limite máximo (R$ 99.999,99)")
        
        return v
    
    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida status do material."""
        v = v.lower().strip()
        
        status_validos = ["solicitado", "autorizado", "utilizado", "glosado", "negado"]
        
        if v not in status_validos:
            raise ValueError(
                f"Status deve ser um de: {', '.join(status_validos)}"
            )
        
        return v
    
    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, v: str) -> str:
        """Valida descrição do material."""
        if not v or not v.strip():
            raise ValueError("Descrição não pode ser vazia")
        
        v = v.strip()
        
        if len(v) < 5:
            raise ValueError("Descrição deve ter no mínimo 5 caracteres")
        
        return v
    
    @field_validator("data_validade_lote")
    @classmethod
    def validar_data_validade_lote(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida data de validade do lote."""
        if v is None:
            return v
        
        hoje = datetime.now()
        
        # Não pode estar vencido
        if v < hoje:
            raise ValueError("Material com lote vencido não pode ser utilizado")
        
        # Máximo 10 anos no futuro (razoável para materiais)
        if (v - hoje).days > 3650:
            raise ValueError("Data de validade muito distante (máximo 10 anos)")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência entre campos."""
        # 1. Quantidade utilizada não pode exceder autorizada
        if self.quantidade_utilizada is not None and self.quantidade_autorizada is not None:
            if self.quantidade_utilizada > self.quantidade_autorizada:
                # Isso deve gerar glosa automática
                if self.status != "glosado":
                    raise ValueError(
                        f"Quantidade utilizada ({self.quantidade_utilizada}) "
                        f"excede autorizada ({self.quantidade_autorizada}). "
                        f"Status deve ser 'glosado'."
                    )
        
        # 2. Quantidade autorizada não pode exceder solicitada (muito)
        if self.quantidade_autorizada is not None:
            if self.quantidade_autorizada > self.quantidade_solicitada * 2:
                raise ValueError(
                    f"Quantidade autorizada ({self.quantidade_autorizada}) "
                    f"muito maior que solicitada ({self.quantidade_solicitada})"
                )
        
        # 3. Status 'autorizado' deve ter quantidade_autorizada
        if self.status == "autorizado":
            if self.quantidade_autorizada is None or self.quantidade_autorizada == 0:
                raise ValueError(
                    "Material com status 'autorizado' deve ter quantidade_autorizada > 0"
                )
        
        # 4. Status 'utilizado' deve ter quantidade_utilizada
        if self.status == "utilizado":
            if self.quantidade_utilizada is None or self.quantidade_utilizada == 0:
                raise ValueError(
                    "Material com status 'utilizado' deve ter quantidade_utilizada > 0"
                )
        
        # 5. Status 'glosado' deve ter motivo
        if self.status == "glosado":
            if not self.motivo_glosa or len(self.motivo_glosa.strip()) < 10:
                raise ValueError(
                    "Material glosado deve ter motivo da glosa (mínimo 10 caracteres)"
                )
        
        # 6. Materiais de alto custo (>R$ 1000) devem ter justificativa
        valor_total = self.valor_unitario * self.quantidade_solicitada
        if valor_total > Decimal("1000.00"):
            if not self.justificativa or len(self.justificativa.strip()) < 20:
                raise ValueError(
                    "Material de alto custo (>R$ 1.000) requer justificativa detalhada"
                )
        
        # 7. Material utilizado com lote deve ter data de validade
        if self.status == "utilizado":
            if self.lote and not self.data_validade_lote:
                raise ValueError(
                    "Material utilizado com lote deve ter data de validade"
                )
        
        return self
