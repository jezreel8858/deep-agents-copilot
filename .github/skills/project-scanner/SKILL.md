---
name: project-scanner-governance
description: "Define diretrizes e padrões para boas práticas para análise automática de repositórios e detecção de stack, frameworks, estrutura, codestyle e arquitetura. Essencial para customização de adapters e descoberta de convenções reais do projeto. Use quando atuar em scan project, detectar stack, analisar repositório. Não use para tarefas fora do escopo de project-scanner ou implementação direta de código de negócio não relacionado."
tier: 2
related_agents:
  - "adapter-generator"
related_skills:
  - "context-mode"
  - "agent-contracts"

category: tooling
triggers:
  - "scan project"
  - "detectar stack"
  - "analisar repositório"
  - "identificar framework"
  - "descobrir convenções"
source_docs:
  - .github/instructions/README.md
  - .github/agents/adapter-generator.agent.md
  - .github/prompts/add-project-context.prompt.md
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: ['read_file', 'list_dir', 'grep_search', 'file_search', '--']

# Project Scanner Governance

Diretrizes consolidadas para **scan automático de projetos** e descoberta de stack técnico, frameworks, padrões arquiteturais e convenções de codestyle.

## Quando Usar

- Ativação em cenários de scan project, detectar stack, analisar repositório.

## Quando NÃO Usar

- Não usar para demandas fora do domínio de `project-scanner` ou quando outra skill específica cobrir integralmente o escopo.

## Diretrizes e Padrões Canônicos

- Seguir estritamente as regras, invariantes e fluxos descritos nas seções abaixo.

## 1) Objetivo

Automaticamente **detectar características técnicas reais de um projeto** a partir de artefatos presentes no repositório, sem análise de código complexa. Resultado: **project_profile** estruturado que customiza geração de adapters.

---

## 2) Artefatos Essenciais — Checklist de Scan

- **2.1 Linguagem & Runtime**: inspecionar manifestos raiz (`pom.xml`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`).
- **2.2 Framework & Ecossistema**: detectar Spring Boot, Angular, React, FastAPI, NestJS e dependências core.
- **2.3 a 2.5 Estrutura, Codestyle & Type Safety**: mapear arquitetura de pastas, linters (`eslint`, `ruff`, `checkstyle`) e `tsconfig`/`mypy`.
- **2.6 a 2.8 Testing, CI/CD & Database**: identificar runners (`vitest`, `jest`, `pytest`, `junit`), pipelines (`.github/workflows`) e migrações (`Flyway`, `Liquibase`, `Alembic`).
- Tabelas completas de artefatos por categoria (2.1–2.8) em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

### 2.9) Detecção de Segredos/Credenciais (Redação Obrigatória — R-010 / OWASP LLM02:2025)

Prioridade: **P1 (Bloqueante — nunca percentual, qualquer reprodução literal é falha crítica)**

> Fundamento: OWASP LLM02:2025 (Sensitive Information Disclosure) — trata segredos/config como "potencialmente expostos", nunca como seguros por padrão. O scanner **detecta a existência** do padrão, mas **nunca reproduz o valor literal** no `project_profile` ou no adapter gerado.

| Sinal | Padrão comum | Ação |
|---|---|---|
| `.env` / `.env.local` / `.env.*` | Qualquer `CHAVE=valor` | Reportar apenas: "usa `.env` para configuração sensível" — nunca listar chave nem valor |
| `application.yml` / `application.properties` (Spring) | `password:`, `secret:`, `api-key:`, connection strings JDBC com credencial embutida | Reportar apenas: "usa arquivo de config para credenciais de BD/API" |
| `package.json` / lockfiles | Tokens de registry privado (`_authToken`, `//registry.npmjs.org/:_authToken=`) | Nunca reproduzir o token — reportar apenas "usa registry privado autenticado" |
| Padrão de chave AWS (`AKIA[0-9A-Z]{16}`) | Chave de acesso AWS hardcoded | Reportar como achado de risco (não como convenção) — nunca reproduzir a chave |
| Blocos `-----BEGIN ... PRIVATE KEY-----` | Chave privada embutida no repositório | Reportar como achado de risco crítico — nunca reproduzir o conteúdo |
| `docker-compose.yml` com `environment:` | Variáveis com valores literais de credencial | Reportar apenas a existência do padrão, nunca o valor |

**Regra de saída**: o `project_profile` e qualquer adapter gerado a partir dele descrevem **o mecanismo** ("projeto usa variáveis de ambiente para segredos"), nunca **o conteúdo** (valor da variável). Violação é bloqueante — 0% de tolerância, não é meta percentual.

---

### 2.10) Detecção de Local de Armazenamento do Token (`token_storage` — opcional, Emenda B)

Prioridade: **P3** — somente frontend com autenticação. Detecta a **categoria** por grep, sem identificar projeto, chave ou valor do token.

| Sinal (grep no código-fonte) | `token_storage` |
|---|---|
| `sessionStorage.setItem` | `sessionStorage` |
| `localStorage.setItem`, `localStorageSync` | `localStorage` |
| `document.cookie`, `withCredentials`, `Set-Cookie` | `cookie` |
| `indexedDB.open` | `indexeddb` |

Regra de saída: reportar apenas a categoria (múltiplos sinais → listar todos e pedir confirmação); nunca reproduzir nome de chave, valor ou caminho de arquivo identificável (R-010/R-044). Estratégia de auth derivada: `playwright-mcp/SKILL.md` § 7.4.

## 3) Resultado: Project Profile

- O scanner consolida os metadados detectados no contrato `project_profile` (linguagem, build tool, frameworks, arquitetura, testes, CI/CD e segurança).
- Exemplo completo do `project_profile` YAML em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

## 4) Uso no Adapter Generator

Quando `adapter-generator` é disparado:

1. **Executa scanner** no `projeto_path` (P6)
2. **Consolida project_profile**
3. **Gera frontmatter** com `detected_stack`:
   ```yaml
   ---
   applyTo: ["src/app/**/*.ts"]
   detected_stack: "TypeScript + Angular 21 (strict)"
   detected_frameworks: ["Angular", "RxJS"]
   detected_language: "TypeScript"
   detected_testing: "Jasmine/Karma + Playwright"
   detected_architecture: "component-based"
   source: "adapter-generator-scanner"
   scan_timestamp: "2026-06-11T14:30:00Z"
   ---
   ```
4. **Customiza template** seções LI, II, III conforme profile.

---

## 5) Boas Práticas

### ✅ DO

- Usar `grep`, `file_search`, `list_dir` para detecção.
- Priorizar P1 (linguagem) antes de P2 (framework).
- Consolidar resultado em YAML estruturado.
- Incluir `scan_timestamp` para auditoria.
- Reportar confiança: "Scanner encontrou N|N+1 sinais → confiança X%".
- Aplicar estratégia `keep-existing` por padrão (nomenclatura de mercado — [Nx generators](https://nx.dev/docs/kb/creating-files)): gerar só se o arquivo ainda não existir, nunca sobrescrever silenciosamente.
- Reportar apenas a **existência/tipo** de mecanismo de segredo detectado (§2.9) — nunca o valor literal (OWASP LLM02:2025).

### ❌ DON'T

- Analisar código-fonte em busca de padrões (muito caro).
- Assumir stack por nome de pasta ou documento.
- Falhar silenciosamente — sempre reportar o que foi encontrado.
- Misturar resultados de múltiplos projetos em um único profile.
- Sobrescrever adapters existentes sem confirmação explícita (estratégia `overwrite` — equivalente a flag `--force`, nunca padrão).
- Reproduzir valor literal de segredo/credencial detectado (viola R-010/OWASP LLM02:2025 — ver §2.9).

---

## 6) Exemplo: Fluxo Completo

- Executar varredura em lote (P1: linguagem/framework, P2: estrutura/codestyle, P3: testes/CI) via `ctx_batch`.
- Script completo de exemplo em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

## 7) Fontes de Mercado Consolidadas (Pesquisa Externa — R-019, 2026-09-01)

> Pesquisa `@deep-search`/Tavily validando que este checklist de scan está alinhado com práticas de mercado 2025-2026.

| Tema | Fonte |
|---|---|
| `.github/instructions/NAME.instructions.md` + `applyTo` glob é o mecanismo oficial do GitHub Copilot | [docs.github.com](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) |
| `AGENTS.md` — padrão aberto cross-tool consolidado (Copilot, Cursor, Codex, Windsurf, Zed, Jules), mantido pela Agentic AI Foundation (Linux Foundation) | [agents.md](https://agents.md) |
| Cursor `.cursor/rules/*.mdc` — 4 modos de ativação (`alwaysApply`, `description`-based, `globs`-based, manual) | [Cursor Docs — Rules](https://cursor.com/docs/rules) |
| Ferramentas de mercado que já fazem "scan repo → gera instructions" automaticamente (`npx ai-setup`, `npx agentseed init`, Copilot CLI `/init`) | [Reddit r/GithubCopilot](https://www.reddit.com/r/GithubCopilot/comments/1s6ppan/), [github/copilot-cli-for-beginners](https://github.com/github/copilot-cli-for-beginners) |
| `OverwriteStrategy` (`Overwrite`/`KeepExisting`/`ThrowIfExisting`) — nomenclatura de mercado para geração idempotente de arquivo | [Nx — Creating Files with a Generator](https://nx.dev/docs/kb/creating-files) |
| OWASP LLM Top 10 2025 (LLM02 Sensitive Information Disclosure, LLM06 Excessive Agency) | [Aembit](https://aembit.io/blog/owasp-top-10-llm-risks-explained) |
| OWASP Top 10 for Agentic Applications (ASI02 Tool Misuse, ASI03 Identity/Privilege Abuse) | [Promptfoo](https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai) |

---

## 8) Referências

- `.github/agents/adapter-generator.agent.md` — implementação
- `binding-initializer.agent.md` — P6 coleta projeto_path
- `catalog.yaml` — binding context com projeto_path

