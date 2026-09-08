---
name: project-scanner-governance
description: |
  Boas práticas para análise automática de repositórios e detecção de stack,
  frameworks, estrutura, codestyle e arquitetura. Essencial para customização
  de adapters e descoberta de convenções reais do projeto.
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
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/adapter-generator.agent.md"
  - ".github/prompts/add-project-context.prompt.md"
  - "docs/ai-context/catalog.yaml"
tools:
  - "read_file"
  - "list_dir"
  - "grep_search"
  - "file_search"
---

# Project Scanner Governance

Diretrizes consolidadas para **scan automático de projetos** e descoberta de stack técnico, frameworks, padrões arquiteturais e convenções de codestyle.

## 1) Objetivo

Automaticamente **detectar características técnicas reais de um projeto** a partir de artefatos presentes no repositório, sem análise de código complexa. Resultado: **project_profile** estruturado que customiza geração de adapters.

---

## 2) Artefatos Essenciais — Checklist de Scan

### 2.1) Detecção de Linguagem & Runtime

Prioridade: **P1 (Crítica)**

| Arquivo | Indicador | Language | Priority |
|---------|-----------|----------|----------|
| `package.json` | Presença | Node.js / TypeScript / JavaScript | P1 |
| `pom.xml` | `<modelVersion>` | Java + Maven | P1 |
| `build.gradle` | Presença | Kotlin / Java + Gradle | P1 |
| `build.gradle.kts` | Presença | Kotlin / Java + Gradle (Kotlin DSL) | P1 |
| `requirements.txt` | Presença | Python + pip | P1 |
| `Pipfile` / `Pipfile.lock` | Presença | Python + Pipenv | P1 |
| `.swift-version` | Presença | Swift | P1 |
| `Cargo.toml` | Presença | Rust | P1 |
| `go.mod` | Presença | Go | P1 |
| `Gemfile` | Presença | Ruby | P1 |
| `Dockerfile` | `FROM <image>` | Container runtime | P2 |

**Lógica**: Se `package.json` existe → Node ecosystem. Se `pom.xml` → Java/Maven. Etc.

```json
{
  "language": "TypeScript",
  "runtime": "Node.js 20+",
  "package_manager": "npm | yarn | pnpm"
}
```

---

### 2.2) Detecção de Framework & Ecossistema

Prioridade: **P1 (Crítica)**

#### Frontend Frameworks

| Framework | Detection Signal | applyTo Pattern |
|-----------|-----------------|-----------------|
| **Angular** | `angular.json` + `"@angular/core"` in `package.json` | `src/app/**/*.ts` |
| **React** | `"react"`, `"react-dom"` in `package.json` | `src/**/*.{ts,tsx}` |
| **Vue** | `"vue"` in `package.json` + `vue.config.js` | `src/**/*.vue` |
| **Next.js** | `"next"` in `package.json` + `next.config.js` | `pages/**/*.{ts,tsx}` |
| **Svelte** | `"svelte"` in `package.json` | `src/**/*.svelte` |
| **NuxtJS** | `"nuxt"` in `package.json` + `nuxt.config.js` | `pages/**/*.vue` |

#### Backend Frameworks

| Framework | Detection Signal | Language |
|-----------|-----------------|----------|
| **Spring Boot** | `spring-boot-starter-*` in `pom.xml` / `build.gradle` | Java / Kotlin |
| **Nest.js** | `"@nestjs/core"` in `package.json` | TypeScript |
| **Express** | `"express"` in `package.json` | JavaScript / TypeScript |
| **Django** | `Django` in `requirements.txt` | Python |
| **FastAPI** | `fastapi` in `requirements.txt` | Python |
| **Flask** | `Flask` in `requirements.txt` | Python |
| **Gin** | `github.com/gin-gonic/gin` in `go.mod` | Go |
| **Echo** | `github.com/labstack/echo` in `go.mod` | Go |

```yaml
frameworks:
  primary: "Angular 21"
  secondary:
    - "RxJS 7"
    - "Material Design"
  supported_versions: [21]
```

---

### 2.3) Detecção de Estrutura & Arquitetura

Prioridade: **P2 (Alta)**

| Pattern | Detection Signal | Meaning |
|---------|-----------------|---------|
| **Monorepo** | `lerna.json` / `nx.json` / `"workspaces"` in `package.json` | Multiple projects in same repo |
| **Modular** | Subfolders: `src/module-a/`, `src/module-b/` | Organization by feature/domain |
| **Layered** | Folders: `/controllers`, `/services`, `/repositories`, `/models` | N-tier architecture |
| **Component-Based** | `/components`, `/pages`, `@Component` decorators | UI component pattern |
| **Microservices** | Multiple `docker-compose.yml` / Kubernetes manifests | Service-oriented architecture |
| **Monolithic** | Single `src/` folder, no clear separation | Single large application |

```yaml
structure:
  type: "component-based"  # ou layered, modular, etc
  organization: "by-feature"
  examples:
    - "src/app/components/"
    - "src/app/pages/"
    - "src/app/services/"
```

---

### 2.4) Detecção de Codestyle & Linting

Prioridade: **P2 (Alta)**

| Config File | Defines | Example |
|-------------|---------|---------|
| `.eslintrc.json` / `.eslintrc.js` | ESLint rules (JavaScript/TypeScript) | `"extends": "eslint:recommended"` |
| `.prettierrc` / `prettier.config.js` | Code formatting | `"printWidth": 80`, `"semi": true` |
| `tsconfig.json` | TypeScript compiler options | `"strict": true`, `"target": "ES2020"` |
| `.editorconfig` | Editor conventions | `indent_style = space`, `indent_size = 2` |
| `.checkstyle.xml` (Java) | Checkstyle rules | Google / Sun coding standards |
| `sonar-project.properties` | SonarQube config | `sonar.sources=src`, `sonar.exclusions=**/*Test.java` |
| `.stylelintrc` | CSS/SCSS linting | Ordering, naming conventions |

```yaml
codestyle:
  linter: "eslint"
  formatter: "prettier"
  linter_config:
    extends: "eslint:recommended"
    rules:
      semi: true
      quotes: "single"
  formatter_config:
    printWidth: 100
    semiColons: true
  type_safety: "strict"  # from tsconfig.strict=true
```

---

### 2.5) Detecção de Type Safety & Compilação

Prioridade: **P2 (Alta)**

| Signal | Meaning | Detection |
|--------|---------|-----------|
| `tsconfig.json` with `"strict": true` | Strict type checking enabled | `grep -o '"strict":\s*true' tsconfig.json` |
| `"noImplicitAny": false` | Allow implicit any types | Inverse of strict |
| `"strictNullChecks": true` | Null safety enforced | Subset of strict |
| `@deprecated` in JSDoc | Code quality signalling | Comment analysis |
| `// @ts-expect-error` | Intentional type bypass | Comment analysis |

```yaml
type_safety:
  enabled: true
  strict_mode: true
  implicit_any_allowed: false
  null_checks_enabled: true
```

---

### 2.6) Detecção de Testing & Coverage

Prioridade: **P2 (Alta)**

| Artifact | Testing Framework | E2E Framework |
|----------|-------------------|---------------|
| `jest.config.js` | Jest (unit) | Jest + puppeteer optional |
| `karma.conf.js` | Karma + Jasmine | Separate (Protractor/Cypress/Playwright) |
| `cypress.config.js` | - | Cypress (E2E) |
| `playwright.config.ts` | - | Playwright (E2E) |
| `protractor.conf.js` | - | Protractor (deprecated) |
| `/test` or `/tests` folder | Convention-based | - |
| `coverage/` | Coverage report | - |
| `.nycrc` / `.nyc_output` | NYC coverage | - |
| `pom.xml` with `maven-surefire-plugin` | Maven test runner | - |

```yaml
testing:
  unit_testing_framework: "jasmine"
  unit_test_runner: "karma"
  e2e_testing_framework: "playwright"
  e2e_runner: "playwright"
  has_coverage: true
  coverage_threshold: 80
  test_folder: "/test"
```

---

### 2.7) Detecção de CI/CD & Deployment

Prioridade: **P3 (Média)**

| File | CI/CD Tool | Signals |
|------|-----------|---------|
| `.github/workflows/*.yml` | GitHub Actions | `on: push`, `runs-on:` |
| `.gitlab-ci.yml` | GitLab CI | `stages:`, `jobs:` |
| `Jenkinsfile` | Jenkins | `pipeline {}` or `node {}` |
| `azure-pipelines.yml` | Azure Pipelines | `trigger:`, `jobs:` |
| `.travis.yml` | Travis CI | `language:`, `script:` |
| `docker-compose.yml` | Docker Compose | Local dev/test orchestration |
| `values-*.yaml` | Helm | Kubernetes deployments |
| `Dockerfile` | Container build | `FROM`, `RUN`, `CMD` |

```yaml
ci_cd:
  provider: "github-actions"
  workflows:
    - "test.yml"
    - "deploy.yml"
  deployment:
    - "docker"
    - "kubernetes"
```

---

### 2.8) Detecção de Banco de Dados & API Docs

Prioridade: **P3 (Média)**

| Signal | Technology |
|--------|-----------|
| `@Controller`, `@RequestMapping` + Swagger annotations | OpenAPI / Swagger |
| `@Endpoint`, `@Operation` (Jakarta REST) | OpenAPI 3.0 |
| Comments: `/**\n * @swagger` | Swagger 2.0 |
| `oas3-definition.yml` / `openapi.json` | OpenAPI file |
| `@Entity`, `@Table` in code | JPA/Hibernate (Java) |
| `@Column`, `@OneToMany` | ORM persistence |
| `db/schema.sql` / `migrations/` | Database schema |

```yaml
database:
  type: "PostgreSQL"  # or null if not detected
  orm: "Hibernate"   # JPA/ORM
  schema_location: "db/schema.sql"

api_documentation:
  format: "openapi"
  version: "3.0"
  spec_file: "docs/openapi.yaml"
```

---

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

## 3) Resultado: Project Profile

Consolidar scanner em um objeto estruturado (`project_profile`):

```yaml
# Exemplo output do scanner
project_profile:
  name: "exemplo"
  base_path: "."  # from P6
  
  # Seção P1
  language: "TypeScript"
  runtime: "Node.js 20+"
  package_manager: "npm"
  
  # Seção P1
  frameworks:
    primary: "Angular 21"
    secondary:
      - "RxJS 7"
      - "@ngrx/store"
    versions:
      angular: "21.0.0"
  
  # Seção P2
  architecture:
    structure: "component-based"
    patterns:
      - "service-locator"
      - "dependency-injection"
    organization: "by-feature"
  
  # Seção P2
  code_style:
    linter: "eslint"
    formatter: "prettier"
    type_safety:
      enabled: true
      strict: true
    config_files:
      - ".eslintrc.json"
      - ".prettierrc"
      - "tsconfig.json"
  
  # Seção P2-P3
  testing:
    unit:
      framework: "jasmine"
      runner: "karma"
    e2e:
      framework: "playwright"
      runner: "playwright"
    coverage: true
    test_dir: "src/"
    coverage_threshold: 80
  
  # Seção P3
  ci_cd:
    provider: "github-actions"
    workflows: ["test.yml", "deploy.yml"]
  
  # Seção P3
  deployment:
    container: "docker"
    orchestration: "kubernetes"
  
  # Seção P3
  api_docs:
    format: "openapi"
    version: "3.0"
    spec_file: "docs/openapi.yaml"

  # Metadata
  scan_timestamp: "2026-06-11T14:30:00Z"
  scanner_version: "1.0"
```

---

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

**Input:**
```
projeto_path: "."
catalog.yml: projetos=[exemplo], adapters=[frontend, backend]
```

**Execução Scanner:**
```bash
# P1: Detectar linguagem
ls -la package.json        # Encontrado → Node.js
ls -la pom.xml             # Não encontrado → skip Maven

# P1: Detectar frameworks
grep "@angular/core" package.json     # Encontrado → Angular
grep "spring-boot" pom.xml            # Não encontrado → skip Spring

# P2: Detectar estrutura
ls -la src/app/components  # Encontrado → component-based
ls -la src/app/pages       # Encontrado → feature-based org

# P2: Detectar codestyle
cat .eslintrc.json         # Lido → ESLint rules
cat tsconfig.json          # Lido → TypeScript strict=true
cat .prettierrc             # Lido → Prettier config

# P3: Detectar testing
cat karma.conf.js          # Encontrado → Karma
cat playwright.config.ts   # Encontrado → Playwright
ls -la src/                # coverage threshold
```

**Output Profile:**
```yaml
project_profile:
  language: "TypeScript"
  frameworks:
    primary: "Angular 21"
  code_style:
    linter: "eslint"
    formatter: "prettier"
    type_safety: "strict"
  testing:
    unit: "jasmine/karma"
    e2e: "playwright"
  architecture: "component-based"
```

---

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

