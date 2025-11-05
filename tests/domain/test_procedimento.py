"""Testes para validações do domínio Procedimento."""
import pytest
from decimal import Decimal
from pydantic import ValidationError
from src.domain.procedimento import Procedimento


class TestProcedimentoValidations:
    """Testes de validações do Procedimento."""
    
    def test_criar_procedimento_valido(self):
        """Testa criação de procedimento válido."""
        proc = Procedimento(
            codigo="0206010079",
            descricao="Cirurgia de apendicite",
            tipo_tabela="tuss",
            categoria="cirurgia",
            quantidade=1,
            valor_unitario=Decimal("2500.00"),
            guia_id=1
        )
        assert proc.codigo == "0206010079"
        assert proc.tipo_tabela == "tuss"
    
    def test_codigo_menos_6_caracteres(self):
        """Testa código com menos de 6 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="12345",
                descricao="Teste",
                tipo_tabela="tuss",
                categoria="exame",
                quantidade=1,
                valor_unitario=Decimal("100.00"),
                guia_id=1
            )
        assert "6 caracteres" in str(exc_info.value)
    
    def test_tipo_tabela_invalido(self):
        """Testa tipo de tabela inválido."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="123456",
                descricao="Teste",
                tipo_tabela="invalid",
                categoria="exame",
                quantidade=1,
                valor_unitario=Decimal("100.00"),
                guia_id=1
            )
        assert "TUSS" in str(exc_info.value)
    
    def test_categoria_invalida(self):
        """Testa categoria inválida."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="123456",
                descricao="Teste",
                tipo_tabela="tuss",
                categoria="invalida",
                quantidade=1,
                valor_unitario=Decimal("100.00"),
                guia_id=1
            )
        assert "Categoria deve ser" in str(exc_info.value)
    
    def test_quantidade_zero(self):
        """Testa quantidade zero."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="123456",
                descricao="Teste",
                tipo_tabela="tuss",
                categoria="exame",
                quantidade=0,
                valor_unitario=Decimal("100.00"),
                guia_id=1
            )
        assert "1 e 100" in str(exc_info.value)
    
    def test_valor_unitario_zero(self):
        """Testa valor unitário zero."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="123456",
                descricao="Teste",
                tipo_tabela="tuss",
                categoria="exame",
                quantidade=1,
                valor_unitario=Decimal("0.00"),
                guia_id=1
            )
        assert "maior que zero" in str(exc_info.value).lower()
    
    def test_cirurgia_valor_minimo(self):
        """Testa cirurgia com valor abaixo do mínimo."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="123456",
                descricao="Teste",
                tipo_tabela="tuss",
                categoria="cirurgia",
                quantidade=1,
                valor_unitario=Decimal("50.00"),
                guia_id=1
            )
        assert "100" in str(exc_info.value)
    
    def test_realizado_sem_prestador(self):
        """Testa procedimento realizado sem prestador."""
        with pytest.raises(ValidationError) as exc_info:
            Procedimento(
                codigo="123456",
                descricao="Teste",
                tipo_tabela="tuss",
                categoria="exame",
                quantidade=1,
                valor_unitario=Decimal("100.00"),
                status="realizado",
                guia_id=1
            )
        assert "prestador" in str(exc_info.value).lower()
