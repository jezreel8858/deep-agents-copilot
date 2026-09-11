# Instructions — Adapters por Projeto/Stack e Mecanismo de Binding

Instructions registram convenções e padrões específicos de um projeto, domínio ou stack.

> **Regras globais**: [`../../CLAUDE.md`](../../CLAUDE.md)
> **Regras operacionais**: [`../copilot-instructions.md`](../copilot-instructions.md)
> **Overlay de projetos (LOCAL, gitignored — R-043)**: [`../projects.local.yaml`](../projects.local.yaml)
> **Template rastreado de projetos**: [`../projects.local.yaml.example`](../projects.local.yaml.example)

---

## 1) Propósito

- **SSOT de Binding de Adapters**: Centralizar as instruções específicas por projeto/stack sem contaminar a governança global.
- **Descoberta Nativa do Copilot**: Facilitar discovery automático via IDE com suporte nativo ao frontmatter YAML `applyTo`.
- **Zero Duplicação (R-003)**: Regras globais vivem em `CLAUDE.md`; convenções específicas de tech/framework vivem aqui.
- **Desacoplamento Total de Projetos (R-043)**: Adapters genéricos são commitados; adapters por-projeto e registros de repositórios locais vivem em overlays gitignored.

---

## 2) Mecanismo de Binding Hierárquico (3 Camadas)

Este ecossistema adota o padrão consolidado de 3 camadas para injeção de contexto de IA:

```
┌────────────────────────────────────────────────────────┐
│ Camada 1: GLOBAL (Priority 100 — Sempre Carregada)     │
│ ├─ CLAUDE.md (regras normativas globais R-001..R-051)  │
│ └─ .github/copilot-instructions.md (operacional/rotas) │
└──────────────────────────┬─────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│ Camada 2: ADAPTER DE STACK (Priority 50 — Condicional) │
│ ├─ .github/instructions/*.instructions.md (raiz)       │
│ └─ Injeção nativa via frontmatter YAML 'applyTo' glob   │
└──────────────────────────┬─────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│ Camada 3: PROJETO LOCAL (Priority 40 — Gitignored)     │
│ ├─ .github/projects.local.yaml (overlay de projetos)   │
│ └─ .github/instructions/local/*.instructions.md        │
└────────────────────────────────────────────────────────┘
```

---

## 3) Estrutura da Pasta: Compartilhado vs. Local (R-043)

| Local | Escopo | Git | Gerado por |
|---|---|---|---|
| `.github/instructions/*.instructions.md` (raiz) | Adapters **genéricos por stack** — reutilizáveis por qualquer projeto | ✅ Commitado | Curadoria / engenharia |
| `.github/instructions/local/*.instructions.md` | Adapters **por-projeto** — customizados via scanner | ❌ Gitignored | `adapter-generator` (via `/add-project-context`) |

> ⚠️ **Regra de Confinamento (R-043)**: Nunca misture os dois: um adapter por-projeto **nunca** vai na raiz, e um adapter genérico compartilhado **nunca** vai em `local/`.

---

## 4) Instruções Convencionais (Adapters Compartilhados Ativos)

Cada arquivo de adapter declara um **frontmatter YAML nativo com `applyTo`**, lido automaticamente pelo GitHub Copilot:

| Documento | Stack | ApplyTo Glob Patterns |
|---|---|---|
| [`spring-boot-backend.instructions.md`](spring-boot-backend.instructions.md) | Java / Spring Boot (genérico) | `**/*.java` |
| [`angular-v21-frontend.instructions.md`](angular-v21-frontend.instructions.md) | Frontend Angular 21 (genérico) | `**/*.ts`, `**/*.js` |
| [`python-backend.instructions.md`](python-backend.instructions.md) | Backend Python (genérico) | `**/*.py`, `**/requirements*.txt`, `**/pyproject.toml` |
| [`database.instructions.md`](database.instructions.md) | Banco de Dados / Migrações (genérico) | `migrations/**`, `schema/**`, `**/*.sql` |
| [`devops.instructions.md`](devops.instructions.md) | DevOps / CI-CD / Containers (genérico) | `**/Dockerfile*`, `kubernetes/**`, `.github/workflows/**` |

---

## 5) Como o Binding Funciona na Prática

1. **Abertura de Arquivo**: Desenvolvedor abre `UsuarioService.java` no IDE.
2. **Camada 1 (Global)**: Copilot carrega `CLAUDE.md` e `.github/copilot-instructions.md`.
3. **Camada 2 (Stack)**: Copilot avalia os padrões glob dos adapters; `**/*.java` coincide com `spring-boot-backend.instructions.md`, injetando convenções de Java/Spring Boot.
4. **Camada 3 (Projeto)**: Se o projeto estiver registrado em `.github/projects.local.yaml` e possuir adapter customizado em `.github/instructions/local/<projeto>.instructions.md`, as instruções específicas do projeto são aplicadas em sobreposição.

---

## 6) Gerenciamento de Projetos Locais (Local Overlay)

```bash
# Setup inicial (uma única vez por clone/máquina):
cp .github/projects.local.yaml.example .github/projects.local.yaml

# Inicializar sessão e verificar saúde do binding:
/init-context

# Conectar novo projeto ao ecossistema (gera adapter em local/ e registra em projects.local.yaml):
/add-project-context <caminho-absoluto-do-projeto>

# Remover projeto desconectado:
/del-project-context <nome-do-projeto>

# Diagnóstico de integridade da governança:
/health
```

---

## 7) Suporte por IDE / Ferramenta

| IDE / Ferramenta | Mecanismo de Carregamento | Suporte a Discovery |
|---|---|---|
| **GitHub Copilot** (VS Code, JetBrains) | Carrega `copilot-instructions.md` + `*.instructions.md` via frontmatter `applyTo` | Automático nativo |
| **Cursor IDE** | Suporta `.cursor/rules/` e lê `copilot-instructions.md` | Automático + manual |
| **Claude Code** | Lê `CLAUDE.md` + `copilot-instructions.md` | Automático nativo |

---

## 8) Como Adicionar Novo Adapter Genérico (Compartilhado)

1. Criar arquivo `.github/instructions/<nome-da-stack>.instructions.md`
2. Adicionar frontmatter YAML com `applyTo`:
   ```yaml
   ---
   applyTo: ["src/**/*.ext", "**/build.file"]
   ---
   # Convenções de Código — <Stack>
   ```
3. Atualizar a tabela deste `README.md` com o novo adapter.
4. Validar via `pytest`.

---

## 9) Fonte de Verdade (SSOT)

- **Manifesto e Guia de Binding de Adapters**: Este arquivo (`.github/instructions/README.md`)
- **Adapters Genéricos**: Arquivos `.github/instructions/*.instructions.md` (com `applyTo`)
- **Adapters de Projetos Locais**: `.github/instructions/local/*.instructions.md` (gitignored)
- **Overlay Local de Projetos**: `.github/projects.local.yaml` (gitignored, R-043)
- **Template Rastreado do Overlay**: `.github/projects.local.yaml.example` (tracked, R-043)
