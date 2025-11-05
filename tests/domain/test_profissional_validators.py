"""
Testes dos validadores do ProfissionalSolicitante usando model_validate()
"""
import pytest
from pydantic import ValidationError
from src.domain.profissional import ProfissionalSolicitante


class TestProfissionalNomeValidator:
    """Testes do validador de nome"""
    
    def test_nome_valido_simples(self):
        """Nome simples capitalizado"""
        data = {
            "nome": "joao silva",
            "conselho": "CRM",
            "uf": "SP",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.nome == "Joao Silva"
    
    def test_nome_valido_composto(self):
        """Nome composto com acentos"""
        data = {
            "nome": "maria josé da silva",
            "conselho": "COREN",
            "uf": "RJ",
            "numero_conselho": "123456",
            "conselho_especialidade": "Pediatria",
            "numero_conselho_especialidade": "RQE456"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.nome == "Maria José Da Silva"
    
    def test_nome_com_apostrofo(self):
        """Nome com apóstrofo"""
        data = {
            "nome": "joão d'angelo",
            "conselho": "CRM",
            "uf": "MG",
            "numero_conselho": "789012",
            "conselho_especialidade": "Ortopedia",
            "numero_conselho_especialidade": "RQE789"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.nome == "João D'Angelo"
    
    def test_nome_muito_curto_rejeitado(self):
        """Nome com menos de 3 caracteres deve ser rejeitado"""
        data = {
            "nome": "AB",
            "conselho": "CRM",
            "uf": "SP",
            "numero_conselho": "123456",
            "conselho_especialidade": "Clinica Geral",
            "numero_conselho_especialidade": "RQE123"
        }
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante.model_validate(data)
        assert "3 caracteres" in str(exc_info.value)
    
    def test_nome_com_numeros_rejeitado(self):
        """Nome com números deve ser rejeitado"""
        data = {
            "nome": "João Silva 123",
            "conselho": "CRM",
            "uf": "SP",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante.model_validate(data)
        assert "inválidos" in str(exc_info.value).lower()


class TestProfissionalConselhoValidator:
    """Testes do validador de conselho"""
    
    def test_conselho_crm_valido(self):
        """CRM deve ser aceito"""
        data = {
            "nome": "Dr João Silva",
            "conselho": "crm",
            "uf": "SP",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.conselho == "CRM"
    
    def test_conselho_coren_valido(self):
        """COREN deve ser aceito"""
        data = {
            "nome": "Maria Santos",
            "conselho": "COREN",
            "uf": "RJ",
            "numero_conselho": "654321",
            "conselho_especialidade": "Enfermagem",
            "numero_conselho_especialidade": "ESP321"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.conselho == "COREN"
    
    def test_conselho_cro_valido(self):
        """CRO deve ser aceito"""
        data = {
            "nome": "Ana Paula",
            "conselho": "cro",
            "uf": "MG",
            "numero_conselho": "111222",
            "conselho_especialidade": "Odontologia",
            "numero_conselho_especialidade": "ESP111"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.conselho == "CRO"
    
    def test_conselho_crefito_valido(self):
        """CREFITO deve ser aceito"""
        data = {
            "nome": "Carlos Eduardo",
            "conselho": "CREFITO",
            "uf": "PR",
            "numero_conselho": "333444",
            "conselho_especialidade": "Fisioterapia",
            "numero_conselho_especialidade": "ESP333"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.conselho == "CREFITO"
    
    def test_conselho_invalido_rejeitado(self):
        """Conselho inválido deve ser rejeitado"""
        data = {
            "nome": "João Silva",
            "conselho": "ABC",
            "uf": "SP",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante.model_validate(data)
        assert "Conselho deve ser" in str(exc_info.value)


class TestProfissionalUFValidator:
    """Testes do validador de UF"""
    
    def test_uf_sp_valida(self):
        """UF SP deve ser aceita"""
        data = {
            "nome": "João Silva",
            "conselho": "CRM",
            "uf": "sp",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.uf == "SP"
    
    def test_uf_rj_valida(self):
        """UF RJ deve ser aceita"""
        data = {
            "nome": "Maria Santos",
            "conselho": "COREN",
            "uf": "RJ",
            "numero_conselho": "654321",
            "conselho_especialidade": "Enfermagem",
            "numero_conselho_especialidade": "ESP321"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.uf == "RJ"
    
    def test_uf_todas_27_validas(self):
        """Todas as 27 UFs devem ser aceitas"""
        ufs = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        for uf in ufs:
            data = {
                "nome": "João Silva",
                "conselho": "CRM",
                "uf": uf.lower(),
                "numero_conselho": "123456",
                "conselho_especialidade": "Cardiologia",
                "numero_conselho_especialidade": "RQE123"
            }
            prof = ProfissionalSolicitante.model_validate(data)
            assert prof.uf == uf
    
    def test_uf_invalida_rejeitada(self):
        """UF inválida deve ser rejeitada"""
        data = {
            "nome": "João Silva",
            "conselho": "CRM",
            "uf": "XX",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante.model_validate(data)
        assert "UF inválida" in str(exc_info.value)


class TestProfissionalNumeroConselhoValidator:
    """Testes do validador de número do conselho"""
    
    def test_numero_conselho_numerico_valido(self):
        """Número apenas numérico deve ser aceito"""
        data = {
            "nome": "João Silva",
            "conselho": "CRM",
            "uf": "SP",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.numero_conselho == "123456"
    
    def test_numero_conselho_alfanumerico_valido(self):
        """Número alfanumérico deve ser aceito"""
        data = {
            "nome": "Maria Santos",
            "conselho": "COREN",
            "uf": "RJ",
            "numero_conselho": "ABC-123",
            "conselho_especialidade": "Enfermagem",
            "numero_conselho_especialidade": "ESP321"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.numero_conselho == "ABC-123"
    
    def test_numero_conselho_com_barra_valido(self):
        """Número com barra deve ser aceito"""
        data = {
            "nome": "Carlos Eduardo",
            "conselho": "CRF",
            "uf": "MG",
            "numero_conselho": "12345/SP",
            "conselho_especialidade": "Farmacia",
            "numero_conselho_especialidade": "ESP456"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.numero_conselho == "12345/SP"
    
    def test_numero_conselho_muito_curto_rejeitado(self):
        """Número com menos de 3 caracteres deve ser rejeitado"""
        data = {
            "nome": "João Silva",
            "conselho": "CRM",
            "uf": "SP",
            "numero_conselho": "12",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE123"
        }
        with pytest.raises(ValidationError) as exc_info:
            ProfissionalSolicitante.model_validate(data)
        assert "3 caracteres" in str(exc_info.value)


class TestProfissionalCompleto:
    """Testes de profissionais completos"""
    
    def test_medico_completo_valido(self):
        """Médico com todos os campos válidos"""
        data = {
            "nome": "dr. joão pedro da silva",
            "conselho": "crm",
            "uf": "sp",
            "numero_conselho": "123456",
            "conselho_especialidade": "Cardiologia",
            "numero_conselho_especialidade": "RQE-12345"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.nome == "Dr. João Pedro Da Silva"
        assert prof.conselho == "CRM"
        assert prof.uf == "SP"
        assert prof.numero_conselho == "123456"
    
    def test_enfermeira_completa_valida(self):
        """Enfermeira com todos os campos válidos"""
        data = {
            "nome": "maria josé santos",
            "conselho": "coren",
            "uf": "rj",
            "numero_conselho": "654321-RJ",
            "conselho_especialidade": "Pediatria",
            "numero_conselho_especialidade": "ESP-654"
        }
        prof = ProfissionalSolicitante.model_validate(data)
        assert prof.nome == "Maria José Santos"
        assert prof.conselho == "COREN"
        assert prof.uf == "RJ"
        assert prof.numero_conselho == "654321-RJ"
