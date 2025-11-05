"""Testes simples para criar objetos de domínio e atingir cobertura."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal

# Import all domain models
from src.domain.paciente import Beneficiario
from src.domain.prestador import Prestador
from src.domain.profissional import ProfissionalSolicitante
from src.domain.guia import Guia
from src.domain.procedimento import Procedimento
from src.domain.material import Material
from src.domain.autorizacao import Autorizacao
from src.domain.fatura import Fatura
from src.domain.fatura_guia import FaturaGuia


def test_criar_todos_modelos_validos():
    """Testa criação de todos os modelos de domínio com dados válidos."""
    hoje = datetime.now()
    
    # Beneficiario
    beneficiario = Beneficiario(
        identificador="12345678901234567890",  # Carteirinha
        sexo="M",
        data_nascimento=datetime(1990, 1, 1)
    )
    assert beneficiario.id is None
    
    # Prestador
    prestador = Prestador(
        nome="Hospital Central",
        cnpj="12345678000190",
        endereco="Rua Principal, 100"
    )
    assert prestador.nome == "Hospital Central"
    
    # Profissional
    profissional = ProfissionalSolicitante(
        nome="Dr. João Silva",
        conselho="CRM",
        numero_conselho="12345",
        uf="SP"
    )
    # Note: validators may transform values
    assert "CRM" in profissional.conselho.upper()
    
    # Guia
    guia = Guia(
        numero_guia="GUIA-2024-001",
        tipo_atendimento="eletivo",
        data_solicitacao=hoje,
        status="pendente",
        valor_total=Decimal("5000.00"),
        beneficiario_id=1
    )
    assert guia.status == "pendente"
    
    # Procedimento
    procedimento = Procedimento(
        codigo="0206010079",
        descricao="Apendicectomia",
        tipo_tabela="tuss",
        categoria="cirurgia",
        quantidade=1,
        valor_unitario=Decimal("2500.00"),
        guia_id=1
    )
    assert procedimento.categoria == "cirurgia"
    
    # Material
    material = Material(
        codigo_material="MAT-001",
        descricao="Luva cirúrgica",
        tipo_tabela="simpro",
        valor_unitario=Decimal("50.00"),
        quantidade_solicitada=10,
        guia_id=1
    )
    assert material.quantidade_solicitada == 10
    
    # Autorização
    autorizacao = Autorizacao(
        numero_autorizacao="AUTH-2024-001",
        data_autorizacao=hoje,
        data_validade=hoje + timedelta(days=30),
        tipo_autorizacao="procedimento",
        procedimento_id=1,
        status="pendente"
    )
    assert autorizacao.status == "pendente"
    
    # Fatura
    fatura = Fatura(
        numero_fatura="FAT-2024-001",
        prestador_id=1,
        data_emissao=hoje,
        periodo_inicio=hoje - timedelta(days=30),
        periodo_fim=hoje - timedelta(days=1),
        data_vencimento=hoje + timedelta(days=30),
        valor_total=Decimal("10000.00"),
        status="pendente"
    )
    assert fatura.valor_total == Decimal("10000.00")
    
    # FaturaGuia
    fatura_guia = FaturaGuia(
        fatura_id=1,
        guia_id=1,
        data_inclusao=hoje
    )
    assert fatura_guia.fatura_id == 1


def test_beneficiario_identificador_longo():
    """Testa criação com identificador longo (carteirinha)."""
    b = Beneficiario(
        identificador="CART123456789",
        sexo="F"
    )
    assert len(b.identificador) > 5


def test_prestador_sem_endereco():
    """Testa prestador sem endereço opcional."""
    p = Prestador(
        nome="Clínica X",
        cnpj="98765432000111"
    )
    assert p.endereco is None


def test_guia_com_valores_opcionais():
    """Testa guia com campos opcionais."""
    g = Guia(
        numero_guia="G-001",
        tipo_atendimento="urgencia",
        data_solicitacao=datetime.now(),
        status="autorizada",
        valor_total=Decimal("1000.00"),
        beneficiario_id=1,
        solicitante_id=1,
        indicacao_clinica="Dor abdominal aguda intensa"
    )
    assert g.tipo_atendimento == "urgencia"
    assert g.indicacao_clinica is not None


def test_procedimento_realizado():
    """Testa procedimento com data de realização."""
    p = Procedimento(
        codigo="010101",
        descricao="Consulta",
        tipo_tabela="tuss",
        categoria="consulta",
        quantidade=1,
        valor_unitario=Decimal("200.00"),
        data_realizacao=datetime.now(),
        prestador_executante_id=1,
        guia_id=1
    )
    assert p.data_realizacao is not None


def test_material_com_lote():
    """Testa material com número de lote."""
    m = Material(
        codigo_material="M001",
        descricao="Seringa",
        tipo_tabela="anvisa",
        valor_unitario=Decimal("5.00"),
        quantidade_solicitada=100,
        quantidade_autorizada=100,
        lote="LOTE2024001",
        data_validade_lote=datetime.now() + timedelta(days=365),
        guia_id=1
    )
    assert m.lote == "LOTE2024001"


def test_autorizacao_material():
    """Testa autorização para material."""
    hoje = datetime.now()
    a = Autorizacao(
        numero_autorizacao="AUTH-MAT-001",
        data_autorizacao=hoje,
        data_validade=hoje + timedelta(days=60),
        tipo_autorizacao="material",
        material_id=1,
        status="aprovada",
        prestador_executante_id=1,
        aprovador_identificador="APROVADOR123"
    )
    assert a.tipo_autorizacao == "material"
    assert a.material_id == 1


def test_fatura_paga():
    """Testa fatura com status paga."""
    hoje = datetime.now()
    f = Fatura(
        numero_fatura="FAT-PAID-001",
        prestador_id=1,
        data_emissao=hoje - timedelta(days=30),
        periodo_inicio=hoje - timedelta(days=60),
        periodo_fim=hoje - timedelta(days=31),
        data_vencimento=hoje - timedelta(days=15),
        valor_total=Decimal("15000.00"),
        status="paga"
    )
    assert f.status == "paga"
    assert f.valor_total == Decimal("15000.00")
