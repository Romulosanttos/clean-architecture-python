"""
Testes dos validadores de Guia usando model_validate()
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError
from src.domain.guia import Guia


class TestGuiaNumeroGuiaValidator:
    """Testes do validador de número da guia"""
    
    def test_numero_guia_valido_simples(self):
        """Número da guia simples válido"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.numero_guia == "GUIA12345"
    
    def test_numero_guia_valido_com_hifen(self):
        """Número da guia com hífen"""
        data = {
            "numero_guia": "GUIA-2024-001",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.numero_guia == "GUIA-2024-001"
    
    def test_numero_guia_minusculo_convertido(self):
        """Número em minúsculo deve ser convertido para maiúsculo"""
        data = {
            "numero_guia": "guia12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.numero_guia == "GUIA12345"
    
    def test_numero_guia_muito_curto_rejeitado(self):
        """Número com menos de 5 caracteres deve ser rejeitado"""
        data = {
            "numero_guia": "G123",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "5 caracteres" in str(exc_info.value)
    
    def test_numero_guia_caracteres_invalidos_rejeitado(self):
        """Número com caracteres especiais inválidos deve ser rejeitado"""
        data = {
            "numero_guia": "GUIA@12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "alfanumérico" in str(exc_info.value).lower()


class TestGuiaTipoAtendimentoValidator:
    """Testes do validador de tipo de atendimento"""
    
    def test_tipo_eletivo_valido(self):
        """Tipo eletivo deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.tipo_atendimento == "eletivo"
    
    def test_tipo_urgencia_valido(self):
        """Tipo urgência deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "urgencia",
            "beneficiario_id": 1,
            "indicacao_clinica": "Paciente com dor intensa no abdômen há 6 horas"
        }
        guia = Guia.model_validate(data)
        assert guia.tipo_atendimento == "urgencia"
    
    def test_tipo_emergencia_valido(self):
        """Tipo emergência deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "emergencia",
            "beneficiario_id": 1,
            "indicacao_clinica": "Paciente apresentando infarto agudo do miocárdio"
        }
        guia = Guia.model_validate(data)
        assert guia.tipo_atendimento == "emergencia"
    
    def test_tipo_maiusculo_convertido(self):
        """Tipo em maiúsculo deve ser convertido para minúsculo"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "ELETIVO",
            "beneficiario_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.tipo_atendimento == "eletivo"
    
    def test_tipo_invalido_rejeitado(self):
        """Tipo inválido deve ser rejeitado"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "ambulatorial",
            "beneficiario_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "eletivo" in str(exc_info.value).lower()


class TestGuiaStatusValidator:
    """Testes do validador de status"""
    
    def test_status_solicitada_valido(self):
        """Status solicitada deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "solicitada"
        }
        guia = Guia.model_validate(data)
        assert guia.status == "solicitada"
    
    def test_status_autorizada_valido(self):
        """Status autorizada deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "autorizada",
            "solicitante_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.status == "autorizada"
    
    def test_status_realizada_valido(self):
        """Status realizada deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "realizada",
            "solicitante_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.status == "realizada"
    
    def test_status_cancelada_valido(self):
        """Status cancelada deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "cancelada"
        }
        guia = Guia.model_validate(data)
        assert guia.status == "cancelada"
    
    def test_status_maiusculo_convertido(self):
        """Status em maiúsculo deve ser convertido"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "SOLICITADA"
        }
        guia = Guia.model_validate(data)
        assert guia.status == "solicitada"
    
    def test_status_invalido_rejeitado(self):
        """Status inválido deve ser rejeitado"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "em_analise"
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "Status deve ser" in str(exc_info.value)


class TestGuiaValorTotalValidator:
    """Testes do validador de valor total"""
    
    def test_valor_zero_valido(self):
        """Valor zero deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "valor_total": "0.00"
        }
        guia = Guia.model_validate(data)
        assert guia.valor_total == Decimal("0.00")
    
    def test_valor_positivo_valido(self):
        """Valor positivo deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "valor_total": "1500.50"
        }
        guia = Guia.model_validate(data)
        assert guia.valor_total == Decimal("1500.50")
    
    def test_valor_maximo_valido(self):
        """Valor máximo deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "valor_total": "999999.99"
        }
        guia = Guia.model_validate(data)
        assert guia.valor_total == Decimal("999999.99")
    
    def test_valor_negativo_rejeitado(self):
        """Valor negativo deve ser rejeitado"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "valor_total": "-100.00"
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "negativo" in str(exc_info.value).lower()
    
    def test_valor_acima_limite_rejeitado(self):
        """Valor acima do limite deve ser rejeitado"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "valor_total": "1000000.00"
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "limite" in str(exc_info.value).lower()


class TestGuiaIndicacaoClinicaValidator:
    """Testes do validador de indicação clínica"""
    
    def test_indicacao_none_valida(self):
        """Indicação None deve ser aceita"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "indicacao_clinica": None
        }
        guia = Guia.model_validate(data)
        assert guia.indicacao_clinica is None
    
    def test_indicacao_valida_minima(self):
        """Indicação com 10 caracteres deve ser aceita"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "indicacao_clinica": "Dor crônica"
        }
        guia = Guia.model_validate(data)
        assert guia.indicacao_clinica == "Dor crônica"
    
    def test_indicacao_muito_curta_rejeitada(self):
        """Indicação com menos de 10 caracteres deve ser rejeitada"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "indicacao_clinica": "Dor"
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "10 caracteres" in str(exc_info.value)


class TestGuiaDataSolicitacaoValidator:
    """Testes do validador de data de solicitação"""
    
    def test_data_hoje_valida(self):
        """Data de hoje deve ser aceita"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "data_solicitacao": datetime.now().isoformat()
        }
        guia = Guia.model_validate(data)
        assert guia.data_solicitacao is not None
    
    def test_data_7_dias_futuro_valida(self):
        """Data até 7 dias no futuro deve ser aceita"""
        data_futura = datetime.now() + timedelta(days=7)
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "data_solicitacao": data_futura.isoformat()
        }
        guia = Guia.model_validate(data)
        assert guia.data_solicitacao is not None
    
    def test_data_365_dias_passado_valida(self):
        """Data até 1 ano no passado deve ser aceita"""
        data_passada = datetime.now() - timedelta(days=365)
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "data_solicitacao": data_passada.isoformat()
        }
        guia = Guia.model_validate(data)
        assert guia.data_solicitacao is not None
    
    def test_data_muito_futura_rejeitada(self):
        """Data mais de 7 dias no futuro deve ser rejeitada"""
        data_futura = datetime.now() + timedelta(days=10)
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "data_solicitacao": data_futura.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "7 dias" in str(exc_info.value)
    
    def test_data_muito_antiga_rejeitada(self):
        """Data mais de 1 ano no passado deve ser rejeitada"""
        data_passada = datetime.now() - timedelta(days=366)
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "data_solicitacao": data_passada.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "1 ano" in str(exc_info.value)


class TestGuiaModelValidator:
    """Testes do model validator (validações de consistência)"""
    
    def test_urgencia_com_indicacao_valida(self):
        """Urgência com indicação clínica deve ser aceita"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "urgencia",
            "beneficiario_id": 1,
            "indicacao_clinica": "Paciente com dor abdominal aguda há 12 horas"
        }
        guia = Guia.model_validate(data)
        assert guia.tipo_atendimento == "urgencia"
    
    def test_emergencia_com_indicacao_valida(self):
        """Emergência com indicação clínica deve ser aceita"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "emergencia",
            "beneficiario_id": 1,
            "indicacao_clinica": "Paciente com suspeita de AVC - paralisia facial e fala arrastada"
        }
        guia = Guia.model_validate(data)
        assert guia.tipo_atendimento == "emergencia"
    
    def test_urgencia_sem_indicacao_rejeitada(self):
        """Urgência sem indicação clínica deve ser rejeitada"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "urgencia",
            "beneficiario_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "indicação clínica" in str(exc_info.value).lower()
    
    def test_autorizada_com_solicitante_valida(self):
        """Status autorizada com solicitante deve ser aceita"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "autorizada",
            "solicitante_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.status == "autorizada"
    
    def test_autorizada_sem_solicitante_rejeitada(self):
        """Status autorizada sem solicitante deve ser rejeitada"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1,
            "status": "autorizada"
        }
        with pytest.raises(ValidationError) as exc_info:
            Guia.model_validate(data)
        assert "solicitante" in str(exc_info.value).lower()
    
    def test_eletivo_sem_indicacao_valido(self):
        """Eletivo sem indicação clínica deve ser aceito"""
        data = {
            "numero_guia": "GUIA12345",
            "tipo_atendimento": "eletivo",
            "beneficiario_id": 1
        }
        guia = Guia.model_validate(data)
        assert guia.indicacao_clinica is None
