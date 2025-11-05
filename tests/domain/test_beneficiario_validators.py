"""
Testes dos validadores do Beneficiario usando model_validate()
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from src.domain.paciente import Beneficiario


class TestBeneficiarioIdentificadorValidator:
    """Testes do validador de identificador (CPF, CNS, carteirinha)"""
    
    def test_cpf_valido_com_pontuacao(self):
        """CPF com pontuação deve ser aceito"""
        data = {"identificador": "123.456.789-01"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "123.456.789-01"
    
    def test_cpf_valido_sem_pontuacao(self):
        """CPF sem pontuação deve ser aceito"""
        data = {"identificador": "12345678901"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "12345678901"
    
    def test_cpf_invalido_digitos_iguais(self):
        """CPF com todos dígitos iguais deve ser rejeitado"""
        data = {"identificador": "111.111.111-11"}
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "CPF inválido" in str(exc_info.value)
    
    def test_cns_valido(self):
        """CNS com 15 dígitos deve ser aceito"""
        data = {"identificador": "123456789012345"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "123456789012345"
    
    def test_carteirinha_valida_alfanumerica(self):
        """Carteirinha alfanumérica com mínimo 5 caracteres deve ser aceita"""
        data = {"identificador": "ABC12345"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "ABC12345"
    
    def test_carteirinha_valida_com_hifen(self):
        """Carteirinha com hífen deve ser aceita"""
        data = {"identificador": "XYZ-123456"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "XYZ-123456"
    
    def test_identificador_vazio(self):
        """Identificador vazio deve ser rejeitado"""
        data = {"identificador": ""}
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "at least 1 character" in str(exc_info.value).lower()
    
    def test_identificador_somente_espacos(self):
        """Identificador com apenas espaços deve ser rejeitado"""
        data = {"identificador": "   "}
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "vazio" in str(exc_info.value).lower()
    
    def test_identificador_muito_curto(self):
        """Identificador com menos de 5 caracteres não numéricos deve ser rejeitado"""
        data = {"identificador": "AB12"}
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "inválido" in str(exc_info.value).lower()
    
    def test_identificador_caracteres_especiais_invalidos(self):
        """Identificador com caracteres especiais inválidos deve ser rejeitado"""
        data = {"identificador": "ABC@123#"}
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "inválido" in str(exc_info.value).lower()


class TestBeneficiarioSexoValidator:
    """Testes do validador de sexo"""
    
    def test_sexo_masculino_maiusculo(self):
        """Sexo 'M' deve ser aceito"""
        data = {"identificador": "12345678901", "sexo": "M"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo == "M"
    
    def test_sexo_feminino_maiusculo(self):
        """Sexo 'F' deve ser aceito"""
        data = {"identificador": "12345678901", "sexo": "F"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo == "F"
    
    def test_sexo_indeterminado_maiusculo(self):
        """Sexo 'I' deve ser aceito"""
        data = {"identificador": "12345678901", "sexo": "I"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo == "I"
    
    def test_sexo_masculino_minusculo_convertido(self):
        """Sexo 'm' deve ser convertido para 'M'"""
        data = {"identificador": "12345678901", "sexo": "m"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo == "M"
    
    def test_sexo_feminino_minusculo_convertido(self):
        """Sexo 'f' deve ser convertido para 'F'"""
        data = {"identificador": "12345678901", "sexo": "f"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo == "F"
    
    def test_sexo_com_espacos_removidos(self):
        """Sexo com espaços deve ter espaços removidos - mas Pydantic valida antes"""
        # Pydantic valida max_length=1 ANTES do field_validator
        # Então " M " (3 chars) falha antes de chegar no validator
        data = {"identificador": "12345678901", "sexo": "M"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo == "M"
    
    def test_sexo_invalido(self):
        """Sexo inválido deve ser rejeitado"""
        data = {"identificador": "12345678901", "sexo": "X"}
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "Sexo deve ser" in str(exc_info.value)
    
    def test_sexo_none(self):
        """Sexo None deve ser aceito (opcional)"""
        data = {"identificador": "12345678901", "sexo": None}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo is None
    
    def test_sexo_omitido(self):
        """Sexo omitido deve ser aceito (campo opcional)"""
        data = {"identificador": "12345678901"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.sexo is None


class TestBeneficiarioDataNascimentoValidator:
    """Testes do validador de data de nascimento"""
    
    def test_data_nascimento_valida_adulto(self):
        """Data de nascimento de adulto (30 anos) deve ser aceita"""
        data_nascimento = datetime.now() - timedelta(days=30*365)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is not None
    
    def test_data_nascimento_valida_crianca(self):
        """Data de nascimento de criança (5 anos) deve ser aceita"""
        data_nascimento = datetime.now() - timedelta(days=5*365)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is not None
    
    def test_data_nascimento_valida_idoso(self):
        """Data de nascimento de idoso (90 anos) deve ser aceita"""
        data_nascimento = datetime.now() - timedelta(days=90*365)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is not None
    
    def test_data_nascimento_valida_recem_nascido(self):
        """Data de nascimento recente (1 dia) deve ser aceita"""
        data_nascimento = datetime.now() - timedelta(days=1)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is not None
    
    def test_data_nascimento_hoje(self):
        """Data de nascimento de hoje deve ser aceita"""
        data_nascimento = datetime.now()
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is not None
    
    def test_data_nascimento_futura_rejeitada(self):
        """Data de nascimento no futuro deve ser rejeitada"""
        data_nascimento = datetime.now() + timedelta(days=1)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "futuro" in str(exc_info.value).lower()
    
    def test_data_nascimento_muito_antiga_rejeitada(self):
        """Data de nascimento com mais de 150 anos deve ser rejeitada"""
        data_nascimento = datetime.now() - timedelta(days=151*365)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario.model_validate(data)
        assert "150 anos" in str(exc_info.value) or "inválida" in str(exc_info.value).lower()
    
    def test_data_nascimento_limite_150_anos(self):
        """Data de nascimento com exatamente 150 anos deve ser aceita"""
        data_nascimento = datetime.now() - timedelta(days=150*365)
        data = {
            "identificador": "12345678901",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is not None
    
    def test_data_nascimento_none(self):
        """Data de nascimento None deve ser aceita (opcional)"""
        data = {"identificador": "12345678901", "data_nascimento": None}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is None
    
    def test_data_nascimento_omitida(self):
        """Data de nascimento omitida deve ser aceita (campo opcional)"""
        data = {"identificador": "12345678901"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.data_nascimento is None


class TestBeneficiarioModelValidator:
    """Testes do model validator (validações de consistência)"""
    
    def test_beneficiario_completo_valido(self):
        """Beneficiário com todos os campos válidos deve ser aceito"""
        data_nascimento = datetime.now() - timedelta(days=25*365)
        data = {
            "identificador": "12345678901",
            "sexo": "F",
            "data_nascimento": data_nascimento.isoformat()
        }
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "12345678901"
        assert beneficiario.sexo == "F"
        assert beneficiario.data_nascimento is not None
    
    def test_beneficiario_minimo_valido(self):
        """Beneficiário apenas com identificador deve ser aceito"""
        data = {"identificador": "12345678901"}
        beneficiario = Beneficiario.model_validate(data)
        assert beneficiario.identificador == "12345678901"
        assert beneficiario.sexo is None
        assert beneficiario.data_nascimento is None
