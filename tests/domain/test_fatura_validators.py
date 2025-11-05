"""
Testes dos validadores de Fatura usando model_validate()
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError
from src.domain.fatura import Fatura


class TestFaturaNumeroFaturaValidator:
    """Testes do validador de número da fatura"""
    
    def test_numero_fatura_valido_simples(self):
        """Número da fatura simples válido"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        fatura = Fatura.model_validate(data)
        assert fatura.numero_fatura == "FAT12345"
    
    def test_numero_fatura_com_barra_hifen(self):
        """Número da fatura com barra e hífen"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT-2024/001",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        fatura = Fatura.model_validate(data)
        assert fatura.numero_fatura == "FAT-2024/001"
    
    def test_numero_fatura_minusculo_convertido(self):
        """Número em minúsculo deve ser convertido para maiúsculo"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "fat12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        fatura = Fatura.model_validate(data)
        assert fatura.numero_fatura == "FAT12345"
    
    def test_numero_fatura_muito_curto_rejeitado(self):
        """Número com menos de 5 caracteres deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "F123",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "5 caracteres" in str(exc_info.value)


class TestFaturaStatusValidator:
    """Testes do validador de status"""
    
    def test_status_pendente_valido(self):
        """Status pendente deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "pendente"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.status == "pendente"
    
    def test_status_em_analise_valido(self):
        """Status em_analise deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "em_analise"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.status == "em_analise"
    
    def test_status_aprovada_valido(self):
        """Status aprovada deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "aprovada",
            "valor_total": "1000.00"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.status == "aprovada"
    
    def test_status_paga_valido(self):
        """Status paga deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "paga",
            "valor_total": "1500.50"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.status == "paga"
    
    def test_status_maiusculo_convertido(self):
        """Status em maiúsculo deve ser convertido"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "PENDENTE"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.status == "pendente"
    
    def test_status_invalido_rejeitado(self):
        """Status inválido deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "processando"
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "Status deve ser" in str(exc_info.value)


class TestFaturaValorTotalValidator:
    """Testes do validador de valor total"""
    
    def test_valor_zero_valido(self):
        """Valor zero deve ser aceito para status pendente"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "valor_total": "0.00"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.valor_total == Decimal("0.00")
    
    def test_valor_positivo_valido(self):
        """Valor positivo deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "valor_total": "25000.50"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.valor_total == Decimal("25000.50")
    
    def test_valor_maximo_valido(self):
        """Valor máximo deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "valor_total": "9999999.99"
        }
        fatura = Fatura.model_validate(data)
        assert fatura.valor_total == Decimal("9999999.99")
    
    def test_valor_negativo_rejeitado(self):
        """Valor negativo deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "valor_total": "-1000.00"
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "negativo" in str(exc_info.value).lower()
    
    def test_valor_acima_limite_rejeitado(self):
        """Valor acima do limite deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "valor_total": "10000000.00"
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "limite" in str(exc_info.value).lower()


class TestFaturaDataEmissaoValidator:
    """Testes do validador de data de emissão"""
    
    def test_data_emissao_hoje_valida(self):
        """Data de emissão de hoje deve ser aceita"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": hoje.isoformat()
        }
        fatura = Fatura.model_validate(data)
        assert fatura.data_emissao is not None
    
    def test_data_emissao_passado_recente_valida(self):
        """Data de emissão no passado recente deve ser aceita"""
        hoje = datetime.now()
        data_emissao = hoje - timedelta(days=10)
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=40)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=11)).isoformat(),
            "prestador_id": 1,
            "data_emissao": data_emissao.isoformat()
        }
        fatura = Fatura.model_validate(data)
        assert fatura.data_emissao is not None
    
    def test_data_emissao_futura_rejeitada(self):
        """Data de emissão no futuro deve ser rejeitada"""
        hoje = datetime.now()
        data_futura = hoje + timedelta(days=1)
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": data_futura.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "futuro" in str(exc_info.value).lower()
    
    def test_data_emissao_muito_antiga_rejeitada(self):
        """Data de emissão muito antiga deve ser rejeitada"""
        hoje = datetime.now()
        data_antiga = hoje - timedelta(days=366)
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (data_antiga - timedelta(days=30)).isoformat(),
            "periodo_fim": (data_antiga - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": data_antiga.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "1 ano" in str(exc_info.value)


class TestFaturaModelValidator:
    """Testes do model validator (validações de consistência)"""
    
    def test_periodo_fim_apos_inicio_valido(self):
        """Período fim após início deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        fatura = Fatura.model_validate(data)
        assert fatura.periodo_fim > fatura.periodo_inicio
    
    def test_periodo_fim_antes_inicio_rejeitado(self):
        """Período fim antes do início deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=1)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=30)).isoformat(),
            "prestador_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "após período início" in str(exc_info.value)
    
    def test_periodo_90_dias_valido(self):
        """Período de 90 dias deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=90)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        fatura = Fatura.model_validate(data)
        dias = (fatura.periodo_fim - fatura.periodo_inicio).days
        assert dias <= 90
    
    def test_periodo_acima_90_dias_rejeitado(self):
        """Período acima de 90 dias deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=100)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "90 dias" in str(exc_info.value)
    
    def test_vencimento_apos_emissao_valido(self):
        """Vencimento após emissão com prazo mínimo de 5 dias deve ser aceito"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": hoje.isoformat(),
            "data_vencimento": (hoje + timedelta(days=30)).isoformat()
        }
        fatura = Fatura.model_validate(data)
        assert fatura.data_vencimento > fatura.data_emissao
    
    def test_vencimento_antes_emissao_rejeitado(self):
        """Vencimento antes da emissão deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": hoje.isoformat(),
            "data_vencimento": (hoje - timedelta(days=1)).isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "após data de emissão" in str(exc_info.value)
    
    def test_prazo_muito_curto_rejeitado(self):
        """Prazo menor que 5 dias deve ser rejeitado"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": hoje.isoformat(),
            "data_vencimento": (hoje + timedelta(days=3)).isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "5 dias" in str(exc_info.value)
    
    def test_fatura_paga_com_valor_zero_rejeitada(self):
        """Fatura com status paga e valor zero deve ser rejeitada"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "status": "paga",
            "valor_total": "0.00"
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "valor > 0" in str(exc_info.value)
    
    def test_emissao_antes_periodo_rejeitada(self):
        """Emissão antes do período deve ser rejeitada"""
        hoje = datetime.now()
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (hoje - timedelta(days=30)).isoformat(),
            "periodo_fim": (hoje - timedelta(days=1)).isoformat(),
            "prestador_id": 1,
            "data_emissao": (hoje - timedelta(days=31)).isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "antes do período" in str(exc_info.value)
    
    def test_emissao_muito_depois_periodo_rejeitada(self):
        """Emissão mais de 30 dias após período deve ser rejeitada"""
        hoje = datetime.now()
        periodo_fim = hoje - timedelta(days=31)
        data = {
            "numero_fatura": "FAT12345",
            "periodo_inicio": (periodo_fim - timedelta(days=30)).isoformat(),
            "periodo_fim": periodo_fim.isoformat(),
            "prestador_id": 1,
            "data_emissao": hoje.isoformat()
        }
        with pytest.raises(ValidationError) as exc_info:
            Fatura.model_validate(data)
        assert "30 dias" in str(exc_info.value)
