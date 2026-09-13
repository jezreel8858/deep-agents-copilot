# Incident Recorder & Learning Engine — Persistência e Aprendizado de Workflows

Mecanismo de captura, persistência e aprendizado contínuo com erros enfrentados por agentes de IA durante a execução dos 8 Workflows Canônicos do `deep-agents-copilot`.

Adota o padrão arquitetural **Local-First Outbox Pattern**:
- **Gravação Primária Local:** Banco SQLite embutido em modo WAL com escrita ultrarrápida (<5ms) e isolamento transacional ACID em `.workflow-db/incidents.db`.
- **Sincronização Remota com Baixo Custo:** Sincronização em lote assíncrona com **Supabase (PostgreSQL JSONB)** via API REST nativa (PostgREST), sem adicionar dependências externas ao projeto.
- **Aprendizado Contínuo com Erros:** Pareamento de erro com a solução bem-sucedida (`rootCause`, `successfulPatch`, `lessonLearned`) e busca preventiva (`find_lessons`) para impedir repetição de falhas.
- **Liberação de Espaço (Storage Pruning):** Expurgo de logs brutos pesados pós-resolução com `DELETE` remoto no Supabase e `VACUUM` no SQLite local, mantendo o armazenamento 100% dentro do Free Tier gratuito.

---

## 📁 Estrutura de Arquivos

```text
tools/incident_recorder/
├── incident_model.py       # Modelo canônico tipado com validação contra workflow-incident.schema.json
├── secret_scrubber.py      # Sanitizador automático de segredos (JWT, API keys, tokens, senhas)
├── sqlite_sink.py          # Repositório SQLite local (WAL, DDL, resolve_incident, find_lessons, purge)
├── supabase_formatter.py   # Mapeador relacional + JSONB para PostgREST e formatador de DELETE
├── supabase_sync.py        # CLI e worker de sincronização e expurgo (utiliza urllib nativo)
├── schema_supabase.sql     # Script DDL pronto para o SQL Editor do Supabase
└── README.md               # Esta documentação
```

---

## 🚀 Como Configurar e Usar

### 1. Configurar o Supabase
1. No [Supabase Dashboard](https://supabase.com), acesse o **SQL Editor**.
2. Execute o conteúdo de [`schema_supabase.sql`](schema_supabase.sql) para criar a tabela `workflow_incidents` e o índice GIN.
3. Copie a **Project URL** e a **API Key** (Service Role ou Anon) em **Project Settings > API**.

### 2. Configurar o Arquivo `.env`
Crie ou edite o `.env` na raiz do repositório:
```env
SUPABASE_URL=https://<seu-projeto>.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Comandos do CLI de Sincronização (`supabase_sync.py`)

O worker foi desenvolvido utilizando exclusivamente módulos padrão do Python (`urllib`), não exigindo nenhum `pip install`:

```bash
# Verificar status da conexão e quantidade de incidentes pendentes
python -m tools.incident_recorder.supabase_sync --status

# Sincronizar incidentes pendentes do SQLite para o Supabase
python -m tools.incident_recorder.supabase_sync --sync

# Purgar incidentes resolvidos para liberar espaço no SQLite e no Supabase
python -m tools.incident_recorder.supabase_sync --purge
```

---

## 💻 Uso Programático nos Agentes

### Registrar um Erro / Incidente:
```python
from tools.incident_recorder.incident_model import WorkflowIncident
from tools.incident_recorder.sqlite_sink import SqliteIncidentSink

sink = SqliteIncidentSink()

incident = WorkflowIncident(
    workflow_id="WF-BUG-2026-001",
    workflow_name="WORKFLOW-BUG-FIX",
    agent_id="spring-boot-bug-fixer",
    step_index=4,
    step_name="Correção Cirúrgica",
    severity="HIGH",
    category="TOOL_FAILURE",
    symptom="Falha de compilação: package javax.persistence não encontrado",
    error_type="CompilationError",
    error_message="package javax.persistence does not exist",
    target_project="sistema-legado",
    active_skill="spring-boot-implementation-patterns",
)

sink.record_incident(incident)
```

### Resolver o Incidente com Lição Aprendida:
```python
sink.resolve_incident(
    incident_id=incident.incident_id,
    root_cause="Spring Boot 3 descontinuou javax.* e migrou para jakarta.*",
    successful_patch="Substituído javax.persistence por jakarta.persistence",
    lesson_learned="No Spring Boot 3+, use sempre jakarta.persistence.* para anotações JPA.",
)
```

### Busca Preventiva de Lições Antes de Executar uma Tarefa:
```python
# Consulta se já ocorreram erros similares nesta stack
lessons = sink.find_lessons(
    workflow_name="WORKFLOW-BUG-FIX",
    keyword="persistence"
)

for l in lessons:
    print(f"Atenção: {l['lesson_learned']}")
```

---

## 🧪 Validação Automatizada

Para rodar a suíte completa de testes do módulo de persistência:
```bash
pytest tests/governance_audit/test_workflow_incident_persistence.py -v
```

