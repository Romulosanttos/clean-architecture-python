from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, model_validator
import re


class ProfissionalSolicitante(SQLModel, table=True):
    """
    Profissional de saúde solicitante do procedimento
    """

    __tablename__: str = "profissional_solicitante"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    nome: str = Field(min_length=1, max_length=255)
    conselho: str = Field(min_length=1, max_length=50)
    conselho_especialidade: str = Field(min_length=1, max_length=100)
    uf: str = Field(min_length=2, max_length=2)
    numero_conselho: str = Field(min_length=1, max_length=20)
    numero_conselho_especialidade: str = Field(min_length=1, max_length=20)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        """Valida nome do profissional."""
        if not v or not v.strip():
            raise ValueError("Nome não pode ser vazio")
        
        v = v.strip()
        
        if len(v) < 3:
            raise ValueError("Nome deve ter no mínimo 3 caracteres")
        
        # Deve conter apenas letras, espaços e caracteres especiais de nomes
        if not re.match(r'^[A-Za-zÀ-ÿ\s\'-\.]+$', v):
            raise ValueError("Nome contém caracteres inválidos")
        
        return v.title()  # Capitaliza cada palavra
    
    @field_validator("conselho")
    @classmethod
    def validar_conselho(cls, v: str) -> str:
        """Valida tipo de conselho profissional."""
        v = v.upper().strip()
        
        conselhos_validos = [
            "CRM",   # Medicina
            "CRO",   # Odontologia
            "COREN", # Enfermagem
            "CRF",   # Farmácia
            "CREFITO", # Fisioterapia
            "CRP",   # Psicologia
            "CRN",   # Nutrição
            "CRFA",  # Fonoaudiologia
            "CRBM",  # Biomedicina
            "COFFITO", # Fisioterapia e Terapia Ocupacional
        ]
        
        if v not in conselhos_validos:
            raise ValueError(
                f"Conselho deve ser um de: {', '.join(conselhos_validos)}"
            )
        
        return v
    
    @field_validator("uf")
    @classmethod
    def validar_uf(cls, v: str) -> str:
        """Valida UF (estado brasileiro)."""
        v = v.upper().strip()
        
        ufs_validas = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        
        if v not in ufs_validas:
            raise ValueError(f"UF inválida. Use sigla de estado brasileiro (ex: SP, RJ)")
        
        return v
    
    @field_validator("numero_conselho")
    @classmethod
    def validar_numero_conselho(cls, v: str) -> str:
        """Valida número do conselho."""
        if not v or not v.strip():
            raise ValueError("Número do conselho não pode ser vazio")
        
        v = v.strip().upper()
        
        # Deve ter pelo menos 3 caracteres
        if len(v) < 3:
            raise ValueError("Número do conselho deve ter no mínimo 3 caracteres")
        
        # Aceita números e letras (alguns conselhos têm letras)
        if not re.match(r'^[A-Z0-9\-\/]+$', v):
            raise ValueError("Número do conselho deve ser alfanumérico")
        
        return v
    
    @field_validator("numero_conselho_especialidade")
    @classmethod
    def validar_numero_conselho_especialidade(cls, v: str) -> str:
        """Valida número do RQE/especialidade."""
        if not v or not v.strip():
            raise ValueError("Número do conselho de especialidade não pode ser vazio")
        
        v = v.strip().upper()
        
        if len(v) < 3:
            raise ValueError("Número deve ter no mínimo 3 caracteres")
        
        if not re.match(r'^[A-Z0-9\-\/]+$', v):
            raise ValueError("Número deve ser alfanumérico")
        
        return v
    
    @field_validator("conselho_especialidade")
    @classmethod
    def validar_conselho_especialidade(cls, v: str) -> str:
        """Valida nome da especialidade."""
        if not v or not v.strip():
            raise ValueError("Especialidade não pode ser vazia")
        
        v = v.strip().title()
        
        if len(v) < 3:
            raise ValueError("Especialidade deve ter no mínimo 3 caracteres")
        
        return v
    
    @model_validator(mode="after")
    def validar_consistencia(self):
        """Validações de consistência."""
        # Médicos (CRM) devem ter especialidade médica válida
        if self.conselho == "CRM":
            especialidades_medicas = [
                "cardiologia", "ortopedia", "pediatria", "ginecologia",
                "cirurgia geral", "clinica geral", "neurologia"
            ]
            
            # Validação suave - apenas avisa se não encontrar
            especialidade_lower = self.conselho_especialidade.lower()
            if not any(esp in especialidade_lower for esp in especialidades_medicas):
                # Não bloqueia, mas poderia logar um warning
                pass
        
        return self

