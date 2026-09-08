# Context Insight Visualizer

Dashboard visualizador standalone (HTML/CSS/JS puro + gerador Python) para telemetria local e análise de métricas do **Context Mode MCP**.

Desenvolvido para operar **100% offline**, com zero dependências npm no runtime e zero lock-in em serviços SaaS na nuvem, seguindo a linguagem visual e design tokens do **Angular Material 3** (Dark Theme).

---

## 🎯 Objetivo

Analisar os dados de telemetria gravados localmente pelo Context Mode (`~/.claude/context-mode/sessions/` ou `~/.config/JetBrains/**/context-mode/`) e fornecer uma suíte analítica completa com **5 visões profissionais** através do menu lateral Angular Material 3:

1. **Dashboard**: Top KPIs (Sessões, R:W Ratio, Compact Rate, Error Rate, Prompts/Session), Heatmap 24h ("When You Code"), Volume temporal, distribuição de ferramentas e cards de Insights & Ações determinísticos (`Nice`, `Heads up`, `Fix this`, `FYI`).
2. **Knowledge Base**: Catálogo de fontes indexadas agrupadas por recência (*Hoje, Ontem, Esta Semana, Anteriores*), proporção de código vs texto e modal de inspeção de chunks com preview.
3. **Sessions & Decisions**: Auditoria cronológica de sessões com duração média, tabela filtrável e **Diário de Decisões Técnicas** com exportação direta para Markdown (`.md`).
4. **Search**: Mecanismo de busca unificado na memória local (pesquisa instantânea com highlight sobre fontes, decisões técnicas e sessões).
5. **Enterprise**: Painel executivo com matriz de personas de liderança (CTO, Engineering Manager, DevEx Lead, Security/CISO, QA Lead, Developer) calculando ROI, economia financeira e impacto.

---

## 🏗️ Arquitetura

O módulo replica a arquitetura modular e validada de `tools/codegraph-visualizer/`:

```
tools/context-insight-visualizer/
├── dist/                          # Artefatos gerados (gitignored)
│   └── context-insight.html       # Arquivo HTML standalone único (file://)
├── generator/                     # Motor de extração e compilação em Python
│   ├── extractor.py               # Leitor multi-DB SQLite e JSONs locais
│   ├── insights_engine.py         # Motor de regras determinísticas, KPIs e personas
│   ├── template_bundler.py        # Compilador modular (HTML + CSS + JS)
│   └── generate.py                # CLI de execução e servidor local
├── schemas/                       # Contratos formais de dados
│   └── insight-data.schema.json   # JSON Schema (Draft 2020-12)
├── template/                      # Template modular Angular Material 3
│   ├── index.html                 # Shell com Sidebar M3 e os 5 containers de visão
│   ├── styles/                    # Folhas de estilo modulares
│   │   ├── tokens.css             # Tokens de cor e elevação M3
│   │   ├── main.css               # Estrutura base, app bar e chips
│   │   ├── views.css              # Layout sidebar M3, cards de visão e dialogs
│   │   ├── cards.css              # KPI cards e Insight cards
│   │   ├── charts.css             # Gráficos SVG, heatmap e barras
│   │   └── table.css              # Tabela de dados, busca e paginação
│   └── scripts/                   # Lógica JavaScript client-side
│       ├── state.js               # Estado reativo e dados injetados
│       ├── charts.js              # Renderizador SVG e heatmap
│       ├── insights.js            # Filtro e renderização dos cards
│       ├── knowledge.js           # Catálogo de fontes e modal de chunks
│       ├── sessions-view.js       # Timeline de sessões e diário de decisões (.md)
│       ├── search-view.js         # Busca instantânea na memória com highlight
│       ├── executive.js           # Painel executivo de personas de liderança
│       ├── table.js               # Paginação e busca de sessões
│       └── app.js                 # Roteador SPA (switchView) e exportação
├── .gitignore
├── PLAN.md
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+ (sem necessidade de instalar pacotes externos além da biblioteca padrão; `jsonschema` opcional para validação formal de schema).

### 1. Gerar o Dashboard Standalone

A partir da raiz do repositório:

```bash
python tools/context-insight-visualizer/generator/generate.py
```

O comando irá extrair automaticamente as métricas locais e gerar o arquivo standalone em:
`tools/context-insight-visualizer/dist/context-insight.html`

### 2. Abrir Diretamente no Navegador (Offline)

Você pode abrir o arquivo HTML diretamente via protocolo `file://`:

```bash
# No Windows PowerShell:
Start-Process "tools/context-insight-visualizer/dist/context-insight.html"

# No Linux / macOS:
open tools/context-insight-visualizer/dist/context-insight.html
# ou: xdg-open tools/context-insight-visualizer/dist/context-insight.html
```

### 3. Iniciar Servidor Local Embutido

Para servir o arquivo via HTTP local na porta `4747` e abrir o navegador automaticamente:

```bash
python tools/context-insight-visualizer/generator/generate.py --serve --open
```

Opções de linha de comando disponíveis:
- `--sessions-dir <path>`: Especifica um caminho customizado para o diretório de sessões do context-mode.
- `--content-dir <path>`: Especifica um caminho customizado para a pasta de bases de conteúdo.
- `--output <path>` ou `-o`: Define o arquivo de saída gerado.
- `--port <number>` ou `-p`: Define a porta do servidor web local (padrão: 4747).

---

## 📊 Fontes de Dados Locais

O extrator descobre e agrega automaticamente:
1. **Bancos de Sess��o SQLite** (`~/.claude/context-mode/sessions/*.db`):
   - Tabelas `session_meta`, `session_events`, `tool_calls`.
2. **Snapshots de Processo** (`stats-pid-*.json`):
   - Tokens economizados em sandbox, bytes mantidos fora da conversa e chamadas por ferramenta.
3. **Bancos de Conteúdo** (`~/.claude/context-mode/content/*.db`):
   - Metadados de chunks e fontes indexadas.

### Fallbacks Automáticos de Plataforma
Se a pasta padrão `~/.claude/context-mode/` não for encontrada, o extrator busca nos diretórios de configuração do JetBrains (`~/.config/JetBrains/` e `AppData/Roaming/JetBrains/`). Caso nenhuma base esteja presente na máquina, o extrator emite um aviso no `meta.warnings` e gera o dashboard sem quebras, suportando execução parcial e fixtures sintéticas.

---

## 📡 Telemetria Nativa OTel (Copilot/Claude Code) — Opcional

Fonte adicional **opt-in por máquina**, complementar (não substitui) a extração por heurística de regex.

### Habilitar
1. `python tools/context-insight-visualizer/otel-collector/receiver.py` (mantenha rodando em background).
2. JetBrains: `Settings > Tools > GitHub Copilot > Chat > Open Telemetry`:
   - `Enable OpenTelemetry export`: ✅
   - `Exporter type`: `otlp-http`
   - `OTLP protocol`: `http/json`
   - `OTLP endpoint`: `http://localhost:4318`
   - `Capture prompt/response content`: **manter desligado** (R-044 — evita PII em `logs/otel-spans.jsonl`)

### Limitação conhecida
Cobre spans dos agentes **Copilot** e **Claude Code** dentro do JetBrains (ambos exigem o endpoint OTLP — o "Output file" nativo da IDE não cobre o agente Claude Code). Formato de atributos ainda não documentado oficialmente 1:1 para o plugin JetBrains — parser é *best-effort* com fallback silencioso.

### Privacidade
`logs/otel-spans.jsonl` é gitignored. Nunca habilite `Capture prompt/response content` neste repositório.

---

## 🔒 Governança e Privacidade (R-038 e R-044)

- **Anonimização Ativa**: Caminhos absolutos do sistema operacional e identificadores de usuário são higienizados na extração, exibindo apenas o nome base dos diretórios de projeto.
- **Zero Lock-in**: Não requer conta, login, token de API ou acesso à internet.
- **Artefatos Distribuíveis**: O diretório `dist/` e artefatos de dados locais permanecem isolados e ignorados via `.gitignore`.

