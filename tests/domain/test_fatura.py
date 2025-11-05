"""Testes para validações do domínio Fatura."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError
from src.domain.fatura import Fatura


class TestFaturaValidations:
    """Testes de validações da Fatura."""
    
    def test_criar_fatura_valida(self):
        """Testa criação de fatura válida."""
        hoje = datetime.now()
        fatura = Fatura(
            numero_fatura="FAT-2024-001",
            prestador_id=1,
            data_emissao=hoje,
            periodo_inicio=hoje - timedelta(days=30),
            periodo_fim=hoje - timedelta(days=1),
            data_vencimento=hoje + timedelta(days=30),
            valor_total=Decimal("5000.00"),
            status="pendente"
        )
        assert fatura.numero_fatura == "FAT-2024-001"
        assert fatura.status == "pendente"
    
    def test_numero_fatura_menos_5_caracteres(self):
        """Testa número de fatura com menos de 5 caracteres."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="F001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=30),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("5000.00"),
                status="pendente"
            )
        assert "5 caracteres" in str(exc_info.value)
    
    def test_status_invalido(self):
        """Testa status inválido."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=30),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("5000.00"),
                status="invalido"
            )
        assert "Status deve ser" in str(exc_info.value)
    
    def test_valor_total_negativo(self):
        """Testa valor total negativo."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=30),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("-1000.00"),
                status="pendente"
            )
        assert "negativo" in str(exc_info.value).lower()
    
    def test_data_emissao_futura(self):
        """Testa data de emissão no futuro."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje + timedelta(days=2),
                periodo_inicio=hoje - timedelta(days=30),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("5000.00"),
                status="pendente"
            )
        assert "futuro" in str(exc_info.value).lower()
    
    def test_periodo_fim_antes_inicio(self):
        """Testa período fim antes do início."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=1),
                periodo_fim=hoje - timedelta(days=30),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("5000.00"),
                status="pendente"
            )
        assert "período fim deve ser após período início" in str(exc_info.value).lower()
    
    def test_periodo_acima_90_dias(self):
        """Testa período acima de 90 dias."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=100),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("5000.00"),
                status="pendente"
            )
        assert "90 dias" in str(exc_info.value)
    
    def test_vencimento_antes_emissao(self):
        """Testa vencimento antes da emissão."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=30),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje - timedelta(days=5),
                valor_total=Decimal("5000.00"),
                status="pendente"
            )
        assert "vencimento" in str(exc_info.value).lower()
    
    def test_paga_sem_valor(self):
        """Testa fatura paga sem valor."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Fatura(
                numero_fatura="FAT-2024-001",
                prestador_id=1,
                data_emissao=hoje,
                periodo_inicio=hoje - timedelta(days=30),
                periodo_fim=hoje - timedelta(days=1),
                data_vencimento=hoje + timedelta(days=30),
                valor_total=Decimal("0.00"),
                status="paga"
            )
        assert "valor total maior que zero" in str(exc_info.value).lower()
