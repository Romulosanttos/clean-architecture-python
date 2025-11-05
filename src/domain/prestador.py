from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator
import re


class Prestador(SQLModel, table=True):
    """
    Prestador de serviços de saúde
    """

    __tablename__: str = "prestador"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    nome: str = Field(min_length=1, max_length=255)
    cnpj: str = Field(min_length=14, max_length=18)
    endereco: Optional[str] = Field(default=None, max_length=500)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        """Valida nome do prestador."""
        if not v or not v.strip():
            raise ValueError("Nome do prestador não pode ser vazio")
        
        v = v.strip()
        
        if len(v) < 3:
            raise ValueError("Nome deve ter no mínimo 3 caracteres")
        
        return v
    
    @field_validator("cnpj")
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        """
        Valida CNPJ (formato e dígitos verificadores).
        
        Aceita formatos:
        - 12.345.678/0001-90
        - 12345678000190
        """
        if not v or not v.strip():
            raise ValueError("CNPJ não pode ser vazio")
        
        # Remove pontuação
        cnpj = re.sub(r'[^\d]', '', v)
        
        # Deve ter 14 dígitos
        if len(cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        
        # Verifica se todos os dígitos são iguais (CNPJ inválido)
        if cnpj == cnpj[0] * 14:
            raise ValueError("CNPJ inválido: todos os dígitos são iguais")
        
        # Validação dos dígitos verificadores
        def calcular_digito(cnpj_parcial: str, pesos: list) -> int:
            soma = sum(int(cnpj_parcial[i]) * pesos[i] for i in range(len(pesos)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito verificador
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito1 = calcular_digito(cnpj[:12], pesos1)
        
        if int(cnpj[12]) != digito1:
            raise ValueError("CNPJ inválido: primeiro dígito verificador incorreto")
        
        # Segundo dígito verificador
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito2 = calcular_digito(cnpj[:13], pesos2)
        
        if int(cnpj[13]) != digito2:
            raise ValueError("CNPJ inválido: segundo dígito verificador incorreto")
        
        # Retorna formatado
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    
    @field_validator("endereco")
    @classmethod
    def validar_endereco(cls, v: Optional[str]) -> Optional[str]:
        """Valida endereço."""
        if v is None:
            return v
        
        v = v.strip()
        
        if len(v) > 0 and len(v) < 10:
            raise ValueError("Endereço deve ter no mínimo 10 caracteres se preenchido")
        
        return v

