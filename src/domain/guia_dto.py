"""
DTOs simples para criação completa de guia - abordagem limpa e direta.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

# Importar modelos base (SQLModel) para usar como base dos DTOs
from src.domain.guia import Guia
from src.domain.paciente import Beneficiario
from src.domain.profissional import ProfissionalSolicitante
from src.domain.procedimento import Procedimento
from src.domain.material import Material
from src.domain.autorizacao import Autorizacao


# ========================================
# DTOs simples - herdam validações dos modelos base
# ========================================

class BeneficiarioDTO(Beneficiario):
    """DTO do beneficiário - remove campos de controle (id, timestamps)."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "identificador": "12345678901",
                "sexo": "F",
                "data_nascimento": "1990-05-15T00:00:00"
            }
        }
    }


class ProfissionalSolicitanteDTO(ProfissionalSolicitante):
    """DTO do profissional - remove campos de controle (id, timestamps)."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Dr. João Silva",
                "conselho": "CRM",
                "conselho_especialidade": "Cardiologia",
                "uf": "SP",
                "numero_conselho": "123456",
                "numero_conselho_especialidade": "RQE789"
            }
        }
    }


class AutorizacaoDTO(Autorizacao):
    """DTO da autorização - remove campos de controle e FKs."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    procedimento_id: Optional[int] = None
    material_id: Optional[int] = None
    prestador_executante_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero_autorizacao": "AUTH-2024-001",
                "data_validade": "2024-12-31T23:59:59",
                "tipo_autorizacao": "procedimento",
                "status": "pendente",
                "observacoes": "Autorização para consulta cardiológica"
            }
        }
    }


class MaterialDTO(Material):
    """DTO do material - remove campos de controle e FKs."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    procedimento_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo_material": "MAT001",
                "descricao": "Gaze estéril 10x10cm",
                "tipo_tabela": "SIMPRO",
                "quantidade_solicitada": 5,
                "valor_unitario": "2.50",
                "status": "solicitado"
            }
        }
    }


class ProcedimentoDTO(Procedimento):
    """DTO do procedimento - remove campos de controle e FKs, adiciona relacionamentos."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    guia_id: Optional[int] = None
    prestador_executante_id: Optional[int] = None
    
    # Relacionamentos aninhados
    materiais: Optional[List[MaterialDTO]] = Field(None, description="Materiais do procedimento")
    autorizacao: Optional[AutorizacaoDTO] = Field(None, description="Autorização do procedimento")

    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "03.01.01.007-2",
                "tipo_tabela": "TUSS",
                "descricao": "Consulta médica em cardiologia",
                "categoria": "consulta",
                "quantidade": 1,
                "valor_unitario": "250.00",
                "data_realizacao": "2024-01-15T14:30:00",
                "materiais": [
                    {
                        "codigo_material": "MAT001",
                        "descricao": "Gaze estéril",
                        "tipo_tabela": "SIMPRO",
                        "quantidade_solicitada": 2,
                        "valor_unitario": "2.50"
                    }
                ],
                "autorizacao": {
                    "numero_autorizacao": "AUTH-PROC-001",
                    "data_validade": "2024-12-31T23:59:59",
                    "tipo_autorizacao": "procedimento",
                    "status": "pendente"
                }
            }
        }
    }


class GuiaDTO(Guia):
    """DTO da guia - remove campos de controle e FKs."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    beneficiario_id: Optional[int] = None
    solicitante_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero_guia": "GUI-2024-001",
                "data_solicitacao": "2024-01-15T10:30:00",
                "indicacao_clinica": "Paciente com dor no peito",
                "tipo_atendimento": "eletivo",
                "status": "solicitada",
                "valor_total": "250.00"
            }
        }
    }


# ========================================  
# DTO Principal - GuiaFullDTO (Composição simples)
# ========================================

class GuiaFullDTO(GuiaDTO):
    """
    DTO completo para criação de guia com todas as entidades relacionadas.
    Herda de GuiaDTO e adiciona os objetos relacionados completos.
    """
    
    # Entidades relacionadas completas (composição)
    beneficiario: BeneficiarioDTO = Field(..., description="Dados completos do beneficiário")
    profissional_solicitante: Optional[ProfissionalSolicitanteDTO] = Field(None, description="Dados do profissional solicitante")
    procedimentos: List[ProcedimentoDTO] = Field(..., min_items=1, description="Lista de procedimentos da guia")
    autorizacao_guia: Optional[AutorizacaoDTO] = Field(None, description="Autorização geral da guia")

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero_guia": "GUI-2024-001",
                "data_solicitacao": "2024-01-15T10:30:00",
                "indicacao_clinica": "Paciente com dor no peito e histórico familiar de doença cardíaca",
                "tipo_atendimento": "eletivo",
                "status": "solicitada",
                "valor_total": "250.00",
                "beneficiario": {
                    "identificador": "12345678901",
                    "sexo": "F", 
                    "data_nascimento": "1990-05-15T00:00:00"
                },
                "profissional_solicitante": {
                    "nome": "Dr. João Silva",
                    "conselho": "CRM",
                    "conselho_especialidade": "Cardiologia",
                    "uf": "SP",
                    "numero_conselho": "123456",
                    "numero_conselho_especialidade": "RQE789"
                },
                "procedimentos": [
                    {
                        "codigo": "03.01.01.007-2",
                        "tipo_tabela": "TUSS",
                        "descricao": "Consulta médica em cardiologia",
                        "categoria": "consulta",
                        "quantidade": 1,
                        "valor_unitario": "250.00",
                        "data_realizacao": "2024-01-15T14:30:00",
                        "materiais": [
                            {
                                "codigo_material": "MAT001",
                                "descricao": "Gaze estéril",
                                "tipo_tabela": "SIMPRO", 
                                "quantidade_solicitada": 2,
                                "valor_unitario": "2.50"
                            }
                        ],
                        "autorizacao": {
                            "numero_autorizacao": "AUTH-PROC-001",
                            "data_validade": "2024-12-31T23:59:59",
                            "tipo_autorizacao": "procedimento",
                            "status": "pendente"
                        }
                    }
                ],
                "autorizacao_guia": {
                    "numero_autorizacao": "AUTH-GUI-001", 
                    "data_validade": "2024-12-31T23:59:59",
                    "tipo_autorizacao": "procedimento",
                    "status": "pendente",
                    "observacoes": "Autorização geral para todos os procedimentos da guia"
                }
            }
        }
    }



