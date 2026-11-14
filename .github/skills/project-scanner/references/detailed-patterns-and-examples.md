# Project Scanner — Tabelas de Detecção, Profile Schema e Exemplos

## 2) Tabelas Detalhadas de Detecção (2.1 a 2.8)

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

## 3) Schema Completo — Project Profile YAML

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
  # Detecção de automação UI & Playwright MCP (T14 / R-043 / Plan frontend consolidation)
  ui_automation:
    ui_url: "http://localhost:<dev-port>"            # porta inferida de angular.json / package.json / vite.config
    auth_strategy: "storage_state"                   # storage_state | user_data_dir | none
    auth_env_var: "<PROJETO>_STORAGE_STATE_PATH"     # apenas o NOME da variável de ambiente, nunca o valor
    token_storage: "localStorage"                    # opcional: cookie | localStorage | sessionStorage | indexeddb
  
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

## 6) Exemplo: Fluxo Completo de Scan

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
