"""
DTOs simples para criação completa de guia - abordagem limpa e direta.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


# ========================================
# DTOs simples - BaseModel puro para evitar conflitos SQLModel
# ========================================

class BeneficiarioDTO(BaseModel):
    """DTO do beneficiário - remove campos de controle (id, timestamps)."""
    # Campos principais do beneficiário
    identificador: str = Field(min_length=11, max_length=11, description="CPF do beneficiário")
    sexo: str = Field(min_length=1, max_length=1, description="M ou F")
    data_nascimento: datetime = Field(description="Data de nascimento")
    
    # Campos opcionais de controle (removidos para criação)
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


class ProfissionalSolicitanteDTO(BaseModel):
    """DTO do profissional - remove campos de controle (id, timestamps)."""
    # Campos principais do profissional
    nome: str = Field(min_length=1, max_length=200, description="Nome do profissional")
    conselho: str = Field(min_length=1, max_length=10, description="CRM, CRO, etc")
    numero_conselho: str = Field(min_length=1, max_length=20, description="Número do conselho")
    uf: str = Field(min_length=2, max_length=2, description="UF do conselho")
    conselho_especialidade: Optional[str] = Field(None, max_length=50, description="Conselho da especialidade")
    numero_conselho_especialidade: Optional[str] = Field(None, max_length=20, description="RQE, etc")
    
    # Campos opcionais de controle
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


class AutorizacaoDTO(BaseModel):
    """DTO da autorização - remove campos de controle e FKs."""
    # Campos principais da autorização
    numero_autorizacao: str = Field(min_length=1, max_length=50, description="Número da autorização")
    data_validade: datetime = Field(description="Data de validade da autorização")
    tipo_autorizacao: str = Field(min_length=1, max_length=50, description="Tipo: procedimento, material, etc")
    status: str = Field(default="pendente", min_length=1, max_length=20, description="Status da autorização")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")
    
    # Campos opcionais de controle
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


class MaterialDTO(BaseModel):
    """DTO do material - remove campos de controle e FKs."""
    # Campos principais do material
    codigo_material: str = Field(min_length=1, max_length=20, description="Código do material")
    descricao: str = Field(min_length=1, max_length=500, description="Descrição do material")
    tipo_tabela: str = Field(min_length=1, max_length=20, description="SIMPRO, BRASINDICE, etc")
    quantidade_solicitada: int = Field(ge=1, description="Quantidade solicitada")
    valor_unitario: Decimal = Field(decimal_places=2, max_digits=10, description="Valor unitário")
    status: str = Field(default="solicitado", min_length=1, max_length=20, description="Status do material")
    
    # Campos opcionais de controle
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


class ProcedimentoDTO(BaseModel):
    """DTO do procedimento - remove campos de controle e FKs, adiciona relacionamentos."""
    # Campos principais do procedimento
    codigo: str = Field(min_length=1, max_length=20, description="Código do procedimento")
    tipo_tabela: str = Field(min_length=1, max_length=20, description="TUSS, SIGTAP, SIMPRO, etc")
    descricao: str = Field(min_length=1, max_length=500, description="Descrição do procedimento")
    categoria: str = Field(min_length=1, max_length=100, description="consulta, cirurgia, exame, etc")
    quantidade: int = Field(default=1, ge=1, description="Quantidade de vezes")
    valor_unitario: Decimal = Field(decimal_places=2, max_digits=10, description="Valor unitário")
    data_realizacao: Optional[datetime] = Field(None, description="Data de realização")
    
    # Campos opcionais de controle
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


class GuiaDTO(BaseModel):
    """DTO da guia - remove campos de controle e FKs."""
    # Campos principais da guia
    numero_guia: str = Field(min_length=1, max_length=50, description="Número da guia")
    data_solicitacao: datetime = Field(description="Data de solicitação")
    indicacao_clinica: str = Field(min_length=1, max_length=1000, description="Indicação clínica")
    tipo_atendimento: str = Field(min_length=1, max_length=50, description="eletivo, urgencia, etc")
    status: str = Field(default="solicitada", min_length=1, max_length=20, description="Status da guia")
    valor_total: Decimal = Field(decimal_places=2, max_digits=12, description="Valor total da guia")
    
    # Campos opcionais de controle
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



