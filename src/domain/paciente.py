from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, model_validator
import re


class Beneficiario(SQLModel, table=True):
    """
    Paciente/Beneficiário que receberá o procedimento
    """

    __tablename__: str = "beneficiario"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    identificador: str = Field(
        min_length=1, max_length=255, unique=True
    )  # CPF, CNS ou número de carteirinha
    sexo: Optional[str] = Field(default=None, min_length=1, max_length=1)
    data_nascimento: Optional[datetime] = Field(default=None)

    @field_validator("identificador")
    @classmethod
    def validar_identificador(cls, v: str) -> str:
        """
        Valida formato do identificador (CPF ou CNS).
        
        Aceita:
        - CPF: 11 dígitos (com ou sem pontuação)
        - CNS: 15 dígitos
        - Carteirinha: alfanumérico (min 5 caracteres)
        """
        if not v or not v.strip():
            raise ValueError("Identificador não pode ser vazio")
        
        v = v.strip()
        
        # Remove pontuação para validação
        apenas_numeros = re.sub(r'[^\d]', '', v)
        
        # CPF: 11 dígitos
        if len(apenas_numeros) == 11:
            # Validação básica de CPF
            if apenas_numeros == apenas_numeros[0] * 11:
                raise ValueError("CPF inválido: todos os dígitos são iguais")
            return v
        
        # CNS: 15 dígitos
        if len(apenas_numeros) == 15:
            return v
        
        # Carteirinha: pelo menos 5 caracteres alfanuméricos
        if len(v) >= 5 and re.match(r'^[A-Za-z0-9\-]+$', v):
            return v
        
        raise ValueError(
            "Identificador inválido. Use CPF (11 dígitos), "
            "CNS (15 dígitos) ou carteirinha (mínimo 5 caracteres)"
        )
    
    @field_validator("sexo")
    @classmethod
    def validar_sexo(cls, v: Optional[str]) -> Optional[str]:
        """Valida se sexo é M, F ou I (indeterminado)."""
        if v is None:
            return v
        
        v = v.upper().strip()
        
        if v not in ["M", "F", "I"]:
            raise ValueError("Sexo deve ser 'M' (masculino), 'F' (feminino) ou 'I' (indeterminado)")
        
        return v
    
    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida se data de nascimento é válida."""
        if v is None:
            return v
        
        hoje = datetime.now()
        
        # Não pode ser no futuro
        if v > hoje:
            raise ValueError("Data de nascimento não pode ser no futuro")
        
        # Idade mínima: 0 anos (recém-nascido)
        # Idade máxima: 150 anos (razoável)
        idade_anos = (hoje - v).days / 365.25
        
        if idade_anos < 0:
            raise ValueError("Data de nascimento inválida")
        
        if idade_anos > 150:
            raise ValueError("Data de nascimento inválida: idade máxima 150 anos")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência entre campos."""
        # Se tem data de nascimento e sexo, validar regras de negócio
        if self.data_nascimento and self.sexo:
            hoje = datetime.now()
            idade_anos = (hoje - self.data_nascimento).days / 365.25
            
            # Exemplo: certos procedimentos têm restrição de idade/sexo
            # (isso seria validado no procedimento, mas aqui é um exemplo)
            pass
        
        return self
