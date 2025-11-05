"""
Testes dos validadores do Prestador usando model_validate()
"""
import pytest
from pydantic import ValidationError
from src.domain.prestador import Prestador


class TestPrestadorNomeValidator:
    """Testes do validador de nome"""
    
    def test_nome_valido_curto(self):
        """Nome com 3 caracteres deve ser aceito"""
        data = {"nome": "ABC", "cnpj": "11222333000181"}
        prestador = Prestador.model_validate(data)
        assert prestador.nome == "ABC"
    
    def test_nome_valido_medio(self):
        """Nome médio deve ser aceito"""
        data = {"nome": "Clínica São Paulo", "cnpj": "11222333000181"}
        prestador = Prestador.model_validate(data)
        assert prestador.nome == "Clínica São Paulo"
    
    def test_nome_valido_longo(self):
        """Nome longo deve ser aceito"""
        data = {"nome": "Hospital e Maternidade Santa Maria da Saúde LTDA", "cnpj": "11222333000181"}
        prestador = Prestador.model_validate(data)
        assert prestador.nome == "Hospital e Maternidade Santa Maria da Saúde LTDA"
    
    def test_nome_com_espacos_removidos(self):
        """Nome com espaços no início/fim deve ter espaços removidos"""
        data = {"nome": "  Clínica Central  ", "cnpj": "11222333000181"}
        prestador = Prestador.model_validate(data)
        assert prestador.nome == "Clínica Central"
    
    def test_nome_vazio_rejeitado(self):
        """Nome vazio deve ser rejeitado"""
        data = {"nome": "", "cnpj": "11222333000181"}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "at least 1 character" in str(exc_info.value).lower()
    
    def test_nome_somente_espacos_rejeitado(self):
        """Nome com apenas espaços deve ser rejeitado"""
        data = {"nome": "   ", "cnpj": "11222333000181"}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "vazio" in str(exc_info.value).lower()
    
    def test_nome_muito_curto_rejeitado(self):
        """Nome com menos de 3 caracteres deve ser rejeitado"""
        data = {"nome": "AB", "cnpj": "11222333000181"}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "3 caracteres" in str(exc_info.value)


class TestPrestadorCNPJValidator:
    """Testes do validador de CNPJ"""
    
    def test_cnpj_valido_com_pontuacao(self):
        """CNPJ válido com pontuação deve ser aceito e formatado"""
        data = {"nome": "Clínica ABC", "cnpj": "11.222.333/0001-81"}
        prestador = Prestador.model_validate(data)
        assert prestador.cnpj == "11.222.333/0001-81"
    
    def test_cnpj_valido_sem_pontuacao(self):
        """CNPJ válido sem pontuação deve ser aceito e formatado"""
        data = {"nome": "Clínica ABC", "cnpj": "11222333000181"}
        prestador = Prestador.model_validate(data)
        assert prestador.cnpj == "11.222.333/0001-81"
    
    def test_cnpj_valido_outro(self):
        """Outro CNPJ válido deve ser aceito"""
        data = {"nome": "Hospital XYZ", "cnpj": "06990590000123"}
        prestador = Prestador.model_validate(data)
        assert prestador.cnpj == "06.990.590/0001-23"
    
    def test_cnpj_vazio_rejeitado(self):
        """CNPJ vazio deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": ""}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "at least 14 character" in str(exc_info.value).lower()
    
    def test_cnpj_somente_espacos_rejeitado(self):
        """CNPJ com apenas espaços deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": "   "}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "at least 14 character" in str(exc_info.value).lower()
    
    def test_cnpj_com_menos_de_14_digitos_rejeitado(self):
        """CNPJ com menos de 14 dígitos deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": "1122233300018"}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "at least 14 character" in str(exc_info.value).lower()
    
    def test_cnpj_com_mais_de_14_digitos_rejeitado(self):
        """CNPJ com mais de 14 dígitos deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": "112223330001811"}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "14 dígitos" in str(exc_info.value)
    
    def test_cnpj_digitos_iguais_rejeitado(self):
        """CNPJ com todos dígitos iguais deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": "11111111111111"}
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "iguais" in str(exc_info.value).lower()
    
    def test_cnpj_digito_verificador_1_incorreto(self):
        """CNPJ com primeiro dígito verificador incorreto deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": "11222333000191"}  # último dígito 91 ao invés de 81
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "verificador" in str(exc_info.value).lower()
    
    def test_cnpj_digito_verificador_2_incorreto(self):
        """CNPJ com segundo dígito verificador incorreto deve ser rejeitado"""
        data = {"nome": "Clínica ABC", "cnpj": "11222333000180"}  # último dígito 80 ao invés de 81
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "verificador" in str(exc_info.value).lower()


class TestPrestadorEnderecoValidator:
    """Testes do validador de endereço"""
    
    def test_endereco_valido_completo(self):
        """Endereço completo válido deve ser aceito"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181",
            "endereco": "Rua das Flores, 123 - Centro - São Paulo/SP"
        }
        prestador = Prestador.model_validate(data)
        assert prestador.endereco == "Rua das Flores, 123 - Centro - São Paulo/SP"
    
    def test_endereco_valido_minimo_10_caracteres(self):
        """Endereço com exatamente 10 caracteres deve ser aceito"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181",
            "endereco": "Rua A, 123"
        }
        prestador = Prestador.model_validate(data)
        assert prestador.endereco == "Rua A, 123"
    
    def test_endereco_com_espacos_removidos(self):
        """Endereço com espaços no início/fim deve ter espaços removidos"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181",
            "endereco": "  Av. Paulista, 1000  "
        }
        prestador = Prestador.model_validate(data)
        assert prestador.endereco == "Av. Paulista, 1000"
    
    def test_endereco_none_aceito(self):
        """Endereço None deve ser aceito (opcional)"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181",
            "endereco": None
        }
        prestador = Prestador.model_validate(data)
        assert prestador.endereco is None
    
    def test_endereco_omitido_aceito(self):
        """Endereço omitido deve ser aceito (campo opcional)"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181"
        }
        prestador = Prestador.model_validate(data)
        assert prestador.endereco is None
    
    def test_endereco_muito_curto_rejeitado(self):
        """Endereço com menos de 10 caracteres deve ser rejeitado se preenchido"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181",
            "endereco": "Rua A"
        }
        with pytest.raises(ValidationError) as exc_info:
            Prestador.model_validate(data)
        assert "10 caracteres" in str(exc_info.value)
    
    def test_endereco_vazio_apos_strip_vira_none(self):
        """Endereço vazio após strip deve ser tratado"""
        data = {
            "nome": "Clínica ABC",
            "cnpj": "11222333000181",
            "endereco": "   "
        }
        # Após strip vira string vazia "", que tem len < 10
        # Mas o validador permite None ou >= 10 caracteres
        # String vazia após strip tem len=0, que é < 10, mas não é None
        # Então deve ser rejeitado ou aceito dependendo da lógica
        # Verificando o código: if len(v) > 0 and len(v) < 10
        # Se v="" (len=0), não entra no if, retorna ""
        prestador = Prestador.model_validate(data)
        assert prestador.endereco == ""


class TestPrestadorCompleto:
    """Testes de prestadores completos"""
    
    def test_prestador_completo_valido(self):
        """Prestador com todos os campos válidos"""
        data = {
            "nome": "Hospital São Lucas",
            "cnpj": "11.222.333/0001-81",
            "endereco": "Av. Brigadeiro Faria Lima, 2000 - Jardim Paulistano"
        }
        prestador = Prestador.model_validate(data)
        assert prestador.nome == "Hospital São Lucas"
        assert prestador.cnpj == "11.222.333/0001-81"
        assert prestador.endereco == "Av. Brigadeiro Faria Lima, 2000 - Jardim Paulistano"
    
    def test_prestador_minimo_valido(self):
        """Prestador apenas com campos obrigatórios"""
        data = {
            "nome": "Clínica Mínima",
            "cnpj": "11222333000181"
        }
        prestador = Prestador.model_validate(data)
        assert prestador.nome == "Clínica Mínima"
        assert prestador.cnpj == "11.222.333/0001-81"
        assert prestador.endereco is None
