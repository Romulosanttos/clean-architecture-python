"""Testes para validações do domínio Guia."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError
from src.domain.guia import Guia


class TestGuiaValidations:
    """Testes de validações da Guia."""
    
    def test_criar_guia_valida(self):
        """Testa criação de guia válida."""
        guia = Guia(
            numero_guia="GUIA12345",
            tipo_atendimento="eletivo",
            data_solicitacao=datetime.now(),
            status="pendente",
            valor_total=Decimal("1500.50"),
            beneficiario_id=1
        )
        assert guia.numero_guia == "GUIA12345"
        assert guia.status == "pendente"
    
    def test_numero_guia_menos_5_caracteres(self):
        """Testa número de guia com menos de 5 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="G123",
                tipo_atendimento="eletivo",
                data_solicitacao=datetime.now(),
                status="pendente",
                valor_total=Decimal("1500.50"),
                beneficiario_id=1
            )
        assert "5 caracteres" in str(exc_info.value)
    
    def test_tipo_atendimento_invalido(self):
        """Testa tipo de atendimento inválido."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="consulta",
                data_solicitacao=datetime.now(),
                status="pendente",
                valor_total=Decimal("1500.50"),
                beneficiario_id=1
            )
        assert "eletivo" in str(exc_info.value).lower()
    
    def test_status_invalido(self):
        """Testa status inválido."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="eletivo",
                data_solicitacao=datetime.now(),
                status="invalido",
                valor_total=Decimal("1500.50"),
                beneficiario_id=1
            )
        assert "Status deve ser um de" in str(exc_info.value)
    
    def test_valor_total_negativo(self):
        """Testa valor total negativo."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="eletivo",
                data_solicitacao=datetime.now(),
                status="pendente",
                valor_total=Decimal("-100.00"),
                beneficiario_id=1
            )
        assert "negativo" in str(exc_info.value).lower()
    
    def test_valor_total_acima_limite(self):
        """Testa valor total acima do limite."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="eletivo",
                data_solicitacao=datetime.now(),
                status="pendente",
                valor_total=Decimal("1000000.00"),
                beneficiario_id=1
            )
        assert "999,999.99" in str(exc_info.value)
    
    def test_data_solicitacao_muito_futura(self):
        """Testa data de solicitação muito no futuro."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="eletivo",
                data_solicitacao=datetime.now() + timedelta(days=10),
                status="pendente",
                valor_total=Decimal("1500.50"),
                beneficiario_id=1
            )
        assert "7 dias" in str(exc_info.value)
    
    def test_urgencia_sem_indicacao_clinica(self):
        """Testa urgência sem indicação clínica."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="urgencia",
                data_solicitacao=datetime.now(),
                status="pendente",
                valor_total=Decimal("1500.50"),
                beneficiario_id=1
            )
        assert "indicação clínica" in str(exc_info.value).lower()
    
    def test_autorizada_sem_solicitante(self):
        """Testa guia autorizada sem solicitante."""
        with pytest.raises(ValidationError) as exc_info:
            Guia(
                numero_guia="GUIA12345",
                tipo_atendimento="eletivo",
                data_solicitacao=datetime.now(),
                status="autorizada",
                valor_total=Decimal("1500.50"),
                beneficiario_id=1
            )
        assert "solicitante" in str(exc_info.value).lower()
    
    def test_urgencia_com_indicacao_valida(self):
        """Testa urgência com indicação clínica válida."""
        guia = Guia(
            numero_guia="GUIA12345",
            tipo_atendimento="urgencia",
            data_solicitacao=datetime.now(),
            status="pendente",
            valor_total=Decimal("1500.50"),
            beneficiario_id=1,
            indicacao_clinica="Dor abdominal aguda com sinais de peritonite"
        )
        assert guia.tipo_atendimento == "urgencia"
