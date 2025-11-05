"""Testes para validações do domínio Beneficiario (Paciente)."""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from src.domain.paciente import Beneficiario


class TestBeneficiarioValidations:
    """Testes de validações do Beneficiario."""
    
    def test_criar_beneficiario_valido_cpf(self):
        """Testa criação de beneficiário válido com CPF."""
        beneficiario = Beneficiario(
            identificador="12345678901",
            data_nascimento=datetime(1990, 1, 1),
            sexo="M"
        )
        assert beneficiario.identificador == "12345678901"
        assert beneficiario.sexo == "m"
    
    def test_criar_beneficiario_valido_cns(self):
        """Testa criação de beneficiário válido com CNS."""
        beneficiario = Beneficiario(
            identificador="123456789012345",
            data_nascimento=datetime(1985, 5, 15),
            sexo="F"
        )
        assert beneficiario.identificador == "123456789012345"
    
    def test_cpf_invalido_menos_11_digitos(self):
        """Testa CPF com menos de 11 dígitos."""
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario(
                identificador="1234567890",
                data_nascimento=datetime(1990, 1, 1),
                sexo="M"
            )
        assert "11 dígitos" in str(exc_info.value)
    
    def test_cpf_com_digitos_iguais(self):
        """Testa CPF com todos os dígitos iguais."""
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario(
                identificador="11111111111",
                data_nascimento=datetime(1990, 1, 1),
                sexo="M"
            )
        assert "dígitos iguais" in str(exc_info.value).lower()
    
    def test_cns_invalido_menos_15_digitos(self):
        """Testa CNS com menos de 15 dígitos."""
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario(
                identificador="12345678901234",
                data_nascimento=datetime(1990, 1, 1),
                sexo="M"
            )
        assert "15 dígitos" in str(exc_info.value)
    
    def test_sexo_invalido(self):
        """Testa sexo inválido."""
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario(
                identificador="12345678901",
                data_nascimento=datetime(1990, 1, 1),
                sexo="X"
            )
        assert "M, F ou I" in str(exc_info.value)
    
    def test_data_nascimento_futura(self):
        """Testa data de nascimento no futuro."""
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario(
                identificador="12345678901",
                data_nascimento=datetime.now() + timedelta(days=1),
                sexo="M"
            )
        assert "futuro" in str(exc_info.value).lower()
    
    def test_idade_acima_150_anos(self):
        """Testa idade acima de 150 anos."""
        with pytest.raises(ValidationError) as exc_info:
            Beneficiario(
                identificador="12345678901",
                data_nascimento=datetime(1800, 1, 1),
                sexo="M"
            )
        assert "150 anos" in str(exc_info.value)
