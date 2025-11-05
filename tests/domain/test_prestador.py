"""Testes para validações do domínio Prestador."""
import pytest
from pydantic import ValidationError
from src.domain.prestador import Prestador


class TestPrestadorValidations:
    """Testes de validações do Prestador."""
    
    def test_criar_prestador_valido(self):
        """Testa criação de prestador válido com CNPJ."""
        prestador = Prestador(
            nome="Hospital São Lucas",
            cnpj="12345678000190"
        )
        assert prestador.nome == "Hospital São Lucas"
        # CNPJ deve ser formatado
        assert "-" in prestador.cnpj or len(prestador.cnpj) == 14
    
    def test_nome_menos_3_caracteres(self):
        """Testa nome com menos de 3 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            Prestador(
                nome="AB",
                cnpj="12345678000190"
            )
        assert "3 caracteres" in str(exc_info.value)
    
    def test_cnpj_menos_14_digitos(self):
        """Testa CNPJ com menos de 14 dígitos."""
        with pytest.raises(ValidationError) as exc_info:
            Prestador(
                nome="Hospital",
                cnpj="1234567800019"
            )
        assert "14 dígitos" in str(exc_info.value)
    
    def test_cnpj_todos_digitos_iguais(self):
        """Testa CNPJ com todos os dígitos iguais."""
        with pytest.raises(ValidationError) as exc_info:
            Prestador(
                nome="Hospital",
                cnpj="11111111111111"
            )
        assert "dígitos iguais" in str(exc_info.value).lower() or "inválido" in str(exc_info.value).lower()
    
    def test_endereco_menos_10_caracteres(self):
        """Testa endereço com menos de 10 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            Prestador(
                nome="Hospital São Lucas",
                cnpj="12345678000190",
                endereco="Rua 1"
            )
        assert "10 caracteres" in str(exc_info.value)
    
    def test_prestador_com_endereco_valido(self):
        """Testa prestador com endereço válido."""
        prestador = Prestador(
            nome="Hospital São Lucas",
            cnpj="12345678000190",
            endereco="Rua das Flores, 123, Centro"
        )
        assert prestador.endereco == "Rua das Flores, 123, Centro"
