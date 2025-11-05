# 🏥 Modelagem Final - Sistema de Saúde

## 📊 Diagrama de Relacionamentos

```
┌─────────────────┐
│  Beneficiario   │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐      ┌──────────────────────┐
│      Guia       │◄─────│ ProfissionalSolicit. │
└────────┬────────┘ 1:1  └──────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Procedimento   │◄─────│  Autorizacao    │ 1:1 (opcional)
└────────┬────────┘      └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐      ┌─────────────────┐
│    Material     │◄─────│  Autorizacao    │ 1:1 (opcional, para OPME)
└─────────────────┘      └─────────────────┘
  (solicitado → autorizado → utilizado → glosado)

         ┌─────────────────┐
         │     Fatura      │◄──── Prestador
         └────────┬────────┘
                  │ N:M
         ┌────────▼────────┐
         │   FaturaGuia    │  (tabela associativa)
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │      Guia       │
         └─────────────────┘
```

## 🔄 Fluxo Completo Passo a Passo

### 1️⃣ **Solicitação**
```python
# Beneficiário vai ao médico
beneficiario = Beneficiario(
    identificador="12345678900",
    data_nascimento="1990-01-01"
)

# Profissional cria guia
profissional = ProfissionalSolicitante(
    nome="Dr. João Silva",
    conselho="CRM",
    numero_conselho="12345"
)

guia = Guia(
    numero_guia="G-2024-001",
    beneficiario_id=beneficiario.id,
    solicitante_id=profissional.id,
    tipo_atendimento="eletivo",
    indicacao_clinica="Cirurgia de vesícula",
    status="solicitada"
)

# Adiciona procedimento à guia
procedimento = Procedimento(
    guia_id=guia.id,
    codigo="40701042",
    tipo_tabela="SIGTAP",
    descricao="Colecistectomia videolaparoscópica",
    categoria="cirurgia",
    quantidade=1,
    valor_unitario=Decimal("3500.00")
)

# Solicita materiais necessários
material1 = Material(
    procedimento_id=procedimento.id,
    codigo_material="MAT-001",
    descricao="Grampeador cirúrgico descartável",
    tipo_tabela="SIMPRO",
    quantidade_solicitada=2,
    valor_unitario=Decimal("350.00"),
    status="solicitado",
    justificativa="Necessário para a cirurgia"
)

material2 = Material(
    procedimento_id=procedimento.id,
    codigo_material="MAT-002",
    descricao="Tela de polipropileno",
    tipo_tabela="SIMPRO",
    quantidade_solicitada=1,
    valor_unitario=Decimal("450.00"),
    status="solicitado"
)
```

### 2️⃣ **Autorização**
```python
# Operadora/SUS analisa e autoriza o PROCEDIMENTO
autorizacao_proc = Autorizacao(
    numero_autorizacao="AUT-PROC-2024-5678",
    procedimento_id=procedimento.id,
    tipo_autorizacao="procedimento",
    data_autorizacao=datetime.now(),
    data_validade=datetime.now() + timedelta(days=30),
    prestador_executante_id=prestador.id,
    status="aprovada"
)

# Autoriza materiais comuns (atualiza no registro do material)
material1.quantidade_autorizada = 2  # Aprovou os 2
material1.status = "autorizado"

# Material caro (OPME) precisa de autorização SEPARADA
autorizacao_opme = Autorizacao(
    numero_autorizacao="AUT-OPME-2024-9999",
    material_id=material2.id,
    tipo_autorizacao="opme",
    data_autorizacao=datetime.now(),
    data_validade=datetime.now() + timedelta(days=30),
    status="aprovada"
)
material2.quantidade_autorizada = 1
material2.status = "autorizado"

guia.status = "autorizada"
```

### 3️⃣ **Realização**
```python
# Prestador realiza o procedimento
prestador = Prestador(
    nome="Hospital Santa Casa",
    cnpj="12345678000190"
)

procedimento.prestador_executante_id = prestador.id
procedimento.data_realizacao = datetime.now()

# Registra materiais utilizados
material1.quantidade_utilizada = 2  # Usou os 2 autorizados
material1.lote = "LOTE-2024-A"
material1.data_validade_lote = datetime(2025, 12, 31)
material1.status = "utilizado"

material2.quantidade_utilizada = 1  # Usou 1
material2.lote = "LOTE-2024-B"
material2.status = "utilizado"

guia.status = "realizada"
```

### 4️⃣ **Faturamento**
```python
# Prestador cria fatura agrupando guias do período
fatura = Fatura(
    numero_fatura="FAT-2024-001",
    prestador_id=prestador.id,
    data_emissao=datetime.now(),
    periodo_inicio=datetime(2024, 1, 1),
    periodo_fim=datetime(2024, 1, 31),
    status="pendente"
)

# Adiciona guias à fatura
fatura_guia = FaturaGuia(
    fatura_id=fatura.id,
    guia_id=guia.id
)

# Calcula valor total da fatura
# (soma de procedimentos + materiais de todas as guias)
valor_procedimentos = 3500.00
valor_materiais = (2 * 350.00) + (1 * 450.00)  # 1150.00
fatura.valor_total = Decimal("4650.00")

guia.status = "faturada"
guia.valor_total = Decimal("4650.00")
```

### 5️⃣ **Glosa (se houver divergência)**
```python
# Exemplo: Se tivesse usado mais material que autorizado
material_extra = Material(
    procedimento_id=procedimento.id,
    codigo_material="MAT-003",
    descricao="Material extra não autorizado",
    quantidade_solicitada=0,  # Não foi solicitado
    quantidade_autorizada=0,  # Não foi autorizado
    quantidade_utilizada=1,   # Mas foi usado!
    status="glosado",
    motivo_glosa="Material não autorizado - cobrado indevidamente"
)

# Auditoria detecta:
# - Materiais com qtd_utilizada > qtd_autorizada
# - Materiais com status='glosado'
# - Valor não é pago na fatura
```

## 🗂️ **Estrutura de Tabelas**

### Principais
- **Beneficiario** - Paciente
- **ProfissionalSolicitante** - Médico que solicita
- **Prestador** - Hospital/clínica que executa
- **Guia** - Solicitação de atendimento
- **Procedimento** - Ação médica (consulta, cirurgia, exame)
- **Material** - Materiais médicos (ciclo completo)
- **Autorizacao** - Aprovação da operadora
- **Fatura** - Cobrança do prestador
- **FaturaGuia** - Relaciona faturas e guias

## 🔑 **Relacionamentos Principais**

| Tabela A | Relação | Tabela B | FK em |
|----------|---------|----------|-------|
| Beneficiario | 1:N | Guia | Guia.beneficiario_id |
| ProfissionalSolicitante | 1:N | Guia | Guia.solicitante_id |
| Guia | 1:N | Procedimento | Procedimento.guia_id |
| Procedimento | 1:1 | Autorizacao | Autorizacao.procedimento_id |
| Procedimento | 1:N | Material | Material.procedimento_id |
| Material | 1:1 | Autorizacao | Autorizacao.material_id (OPME) |
| Prestador | 1:N | Fatura | Fatura.prestador_id |
| Prestador | 1:N | Procedimento | Procedimento.prestador_executante_id |
| Fatura | N:M | Guia | FaturaGuia (associativa) |

## 📈 **Queries Comuns**

### Buscar materiais glosados de uma fatura
```sql
SELECT m.*, p.descricao as procedimento, g.numero_guia
FROM material m
JOIN procedimento p ON m.procedimento_id = p.id
JOIN guia g ON p.guia_id = g.id
JOIN fatura_guia fg ON g.id = fg.guia_id
WHERE fg.fatura_id = 1 AND m.status = 'glosado';
```

### Auditoria: materiais utilizados > autorizados
```sql
SELECT *
FROM material
WHERE quantidade_utilizada > quantidade_autorizada;
```

### Listar todas as guias de uma fatura
```sql
SELECT g.*, p.descricao as procedimento
FROM guia g
JOIN fatura_guia fg ON g.id = fg.guia_id
JOIN procedimento p ON p.guia_id = g.id
WHERE fg.fatura_id = 1;
```

## ✅ **Vantagens da Modelagem**

1. ✓ **Simples**: 9 tabelas principais (antes eram 11+)
2. ✓ **Auditável**: Histórico completo do material (solicitado → autorizado → utilizado)
3. ✓ **Flexível**: Suporta SUS (SIGTAP) e Operadoras (TUSS)
4. ✓ **Rastreável**: Lote, validade, glosas
5. ✓ **Performático**: Índices nas foreign keys e campos de busca
6. ✓ **Temporal**: created_at/updated_at em todas as tabelas
