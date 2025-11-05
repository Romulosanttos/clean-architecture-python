"""Testes para validações do domínio Material."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError
from src.domain.material import Material


class TestMaterialValidations:
    """Testes de validações do Material."""
    
    def test_criar_material_valido(self):
        """Testa criação de material válido."""
        material = Material(
            codigo_material="MAT12345",
            descricao="Prótese de joelho",
            tipo_tabela="simpro",
            valor_unitario=Decimal("5000.00"),
            quantidade_solicitada=1,
            guia_id=1
        )
        assert material.codigo_material == "MAT12345"
        assert material.tipo_tabela == "simpro"
    
    def test_codigo_material_menos_4_caracteres(self):
        """Testa código de material com menos de 4 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="M12",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=1,
                guia_id=1
            )
        assert "4 caracteres" in str(exc_info.value)
    
    def test_tipo_tabela_invalido(self):
        """Testa tipo de tabela inválido."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="tuss",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=1,
                guia_id=1
            )
        assert "SIMPRO, BRASINDICE ou ANVISA" in str(exc_info.value)
    
    def test_quantidade_acima_limite(self):
        """Testa quantidade acima do limite."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=1001,
                guia_id=1
            )
        assert "1000" in str(exc_info.value)
    
    def test_valor_unitario_zero(self):
        """Testa valor unitário zero."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("0.00"),
                quantidade_solicitada=1,
                guia_id=1
            )
        assert "maior que zero" in str(exc_info.value).lower()
    
    def test_glosa_automatica(self):
        """Testa detecção automática de glosa."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=10,
                quantidade_autorizada=5,
                quantidade_utilizada=8,
                status="autorizado",
                guia_id=1
            )
        assert "glosado" in str(exc_info.value).lower()
    
    def test_material_alto_custo_sem_justificativa(self):
        """Testa material de alto custo sem justificativa."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("2000.00"),
                quantidade_solicitada=1,
                guia_id=1
            )
        assert "justificativa" in str(exc_info.value).lower()
    
    def test_autorizado_sem_quantidade(self):
        """Testa status autorizado sem quantidade autorizada."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=5,
                quantidade_autorizada=0,
                status="autorizado",
                guia_id=1
            )
        assert "autorizada" in str(exc_info.value).lower()
    
    def test_glosado_sem_motivo(self):
        """Testa status glosado sem motivo."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=5,
                quantidade_autorizada=3,
                quantidade_utilizada=5,
                status="glosado",
                guia_id=1
            )
        assert "motivo_glosa" in str(exc_info.value).lower()
    
    def test_data_validade_expirada(self):
        """Testa data de validade expirada."""
        with pytest.raises(ValidationError) as exc_info:
            Material(
                codigo_material="MAT12345",
                descricao="Teste",
                tipo_tabela="simpro",
                valor_unitario=Decimal("100.00"),
                quantidade_solicitada=1,
                lote="LOTE123",
                data_validade_lote=datetime.now() - timedelta(days=1),
                guia_id=1
            )
        assert "expirado" in str(exc_info.value).lower() or "vencido" in str(exc_info.value).lower()
