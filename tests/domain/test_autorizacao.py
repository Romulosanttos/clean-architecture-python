"""Testes para validações do domínio Autorização."""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from src.domain.autorizacao import Autorizacao


class TestAutorizacaoValidations:
    """Testes de validações da Autorização."""
    
    def test_criar_autorizacao_valida_procedimento(self):
        """Testa criação de autorização válida para procedimento."""
        hoje = datetime.now()
        autorizacao = Autorizacao(
            numero_autorizacao="AUTH12345",
            data_autorizacao=hoje,
            data_validade=hoje + timedelta(days=30),
            tipo_autorizacao="procedimento",
            procedimento_id=1,
            status="pendente"
        )
        assert autorizacao.numero_autorizacao == "AUTH12345"
        assert autorizacao.tipo_autorizacao == "procedimento"
    
    def test_criar_autorizacao_valida_opme(self):
        """Testa criação de autorização válida para OPME."""
        hoje = datetime.now()
        autorizacao = Autorizacao(
            numero_autorizacao="AUTH12345",
            data_autorizacao=hoje,
            data_validade=hoje + timedelta(days=30),
            tipo_autorizacao="opme",
            material_id=1,
            status="pendente",
            observacoes="Prótese de joelho necessária para cirurgia eletiva"
        )
        assert autorizacao.tipo_autorizacao == "opme"
    
    def test_numero_autorizacao_menos_5_caracteres(self):
        """Testa número de autorização com menos de 5 caracteres."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="procedimento",
                procedimento_id=1,
                status="pendente"
            )
        assert "5 caracteres" in str(exc_info.value)
    
    def test_tipo_autorizacao_invalido(self):
        """Testa tipo de autorização inválido."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="invalido",
                procedimento_id=1,
                status="pendente"
            )
        assert "procedimento" in str(exc_info.value).lower()
    
    def test_status_invalido(self):
        """Testa status inválido."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="procedimento",
                procedimento_id=1,
                status="invalido"
            )
        assert "Status deve ser" in str(exc_info.value)
    
    def test_sem_procedimento_nem_material(self):
        """Testa autorização sem procedimento nem material."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="procedimento",
                status="pendente"
            )
        assert "procedimento OU" in str(exc_info.value).lower() or "material" in str(exc_info.value).lower()
    
    def test_procedimento_e_material_simultaneos(self):
        """Testa autorização com procedimento E material."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="procedimento",
                procedimento_id=1,
                material_id=1,
                status="pendente"
            )
        assert "simultaneamente" in str(exc_info.value).lower()
    
    def test_data_validade_antes_autorizacao(self):
        """Testa data de validade antes da autorização."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje - timedelta(days=1),
                tipo_autorizacao="procedimento",
                procedimento_id=1,
                status="pendente"
            )
        assert "após" in str(exc_info.value).lower()
    
    def test_aprovada_sem_prestador(self):
        """Testa autorização aprovada sem prestador."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="procedimento",
                procedimento_id=1,
                status="aprovada"
            )
        assert "prestador" in str(exc_info.value).lower()
    
    def test_negada_sem_motivo(self):
        """Testa autorização negada sem motivo."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="procedimento",
                procedimento_id=1,
                status="negada"
            )
        assert "motivo" in str(exc_info.value).lower()
    
    def test_opme_sem_justificativa(self):
        """Testa OPME sem justificativa."""
        hoje = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Autorizacao(
                numero_autorizacao="AUTH12345",
                data_autorizacao=hoje,
                data_validade=hoje + timedelta(days=30),
                tipo_autorizacao="opme",
                material_id=1,
                status="pendente"
            )
        assert "justificativa" in str(exc_info.value).lower() or "observações" in str(exc_info.value).lower()
