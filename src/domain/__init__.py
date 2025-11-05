# Ordem de importação: tabelas sem FK primeiro
from .paciente import Beneficiario
from .profissional import ProfissionalSolicitante
from .prestador import Prestador

# Tabelas com FK simples
from .guia import Guia
from .procedimento import Procedimento
from .material import Material

# Tabelas com FK múltiplas
from .autorizacao import Autorizacao
from .fatura import Fatura
from .fatura_guia import FaturaGuia

__all__ = [
    "Beneficiario",
    "ProfissionalSolicitante",
    "Prestador",
    "Guia",
    "Procedimento",
    "Material",
    "Autorizacao",
    "Fatura",
    "FaturaGuia",
]
