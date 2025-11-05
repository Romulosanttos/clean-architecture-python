"""Testes para validações do domínio Profissional Solicitante."""
import pytest
from pydantic import ValidationError
from src.domain.profissional import ProfissionalSolicitante


class TestProfissionalSolicitanteValidations:
    """Testes de validações do Profissional Solicitante."""
    
    def test_criar_profissional_valido(self):
        """Testa criação de profissional válido."""
        profissional = ProfissionalSolicitante(
            nome="João da Silva",
            conselho="CRM",
            numero_conselho="12345",
            uf="SP"
        )
        assert profissional.nome == "João Da Silva"  # Title case
        assert profissional.conselho == "crm"
    
    def test_nome_menos_3_caracteres(self):
        """Testa nome com menos de 3 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante(
                nome="Jo",
                conselho="CRM",
                numero_conselho="12345",
                uf="SP"
            )
        assert "3 caracteres" in str(exc_info.value)
    
    def test_conselho_invalido(self):
        """Testa conselho inválido."""
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante(
                nome="João da Silva",
                conselho="INVALID",
                numero_conselho="12345",
                uf="SP"
            )
        assert "CRM" in str(exc_info.value)
    
    def test_uf_invalida(self):
        """Testa UF inválida."""
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante(
                nome="João da Silva",
                conselho="CRM",
                numero_conselho="12345",
                uf="XX"
            )
        assert "UF" in str(exc_info.value) or "estado" in str(exc_info.value).lower()
    
    def test_numero_conselho_menos_3_caracteres(self):
        """Testa número de conselho com menos de 3 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante(
                nome="João da Silva",
                conselho="CRM",
                numero_conselho="12",
                uf="SP"
            )
        assert "3 caracteres" in str(exc_info.value)
    
    def test_profissional_com_especialidade(self):
        """Testa profissional com especialidade."""
        profissional = ProfissionalSolicitante(
            nome="João da Silva",
            conselho="CRM",
            numero_conselho="12345",
            uf="SP",
            conselho_especialidade="CREMEC",
            numero_conselho_especialidade="67890"
        )
        assert profissional.conselho_especialidade == "cremec"
