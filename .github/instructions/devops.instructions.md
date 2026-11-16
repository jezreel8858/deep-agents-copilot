---
applyTo: ["**/Dockerfile*", "**/docker-compose*.yml", "kubernetes/**", "k8s/**", "helm/**", ".github/workflows/**", ".gitlab-ci.yml", "Jenkinsfile", "**/pipeline*.yml", "**/pipeline*.yaml", "confd/**"]
---

# Convenções de Código — DevOps / CI-CD / Containers

> Resumo consolidado das convenções de DevOps para projetos com containerização e pipelines de CI/CD. Use este documento como referência principal para padrões de infra-como-código; consulte `CLAUDE.md` e `.github/copilot-instructions.md` apenas para governança geral.
>
> **Instruções genéricas**: este arquivo é reutilizável por qualquer projeto com Docker, Kubernetes e CI/CD. Customizações específicas de plataforma (AWS EKS, GKE, Azure AKS) devem ser adicionadas via adapter próprio.

### Docker — Boas Práticas

- Usar imagens base **oficiais** e **mínimas** (Alpine, Distroless) para reduzir superfície de ataque.
- Declarar versão explícita da imagem base (`FROM node:20-alpine`, não `FROM node:latest`).
- Multi-stage builds: separar estágio de build e estágio de runtime.
- Usar `.dockerignore` para excluir `node_modules`, `target`, `*.log`, `.git`.
- `CMD` vs `ENTRYPOINT`: usar `ENTRYPOINT` para comando fixo + `CMD` para argumentos defaults.
- Aplicação deve rodar como **usuário não-root** dentro do container.

```dockerfile
# Multi-stage — build
FROM [imagem-base]:[versao] AS builder
WORKDIR /app
COPY . .
RUN [comando-de-build]

# Runtime — imagem mínima
FROM [imagem-runtime]:[versao] AS runtime
WORKDIR /app
COPY --from=builder /app/[artefato] .
USER nonroot:nonroot
EXPOSE [porta]
ENTRYPOINT ["[comando-principal]"]
```

### Docker Compose

- Declarar `version` explícita.
- Usar nomes de serviço descritivos (não genéricos como `app` ou `service1`).
- Variáveis de ambiente sensíveis via `.env` (não hardcoded no compose).
- Health checks para serviços com dependência.
- Volumes nomeados para dados persistidos.

```yaml
services:
  [nome-servico]:
    image: [imagem]:[tag]
    environment:
      - VARIAVEL=${VARIAVEL_DO_ENV}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:[porta]/health"]
      interval: 30s
      retries: 3
    depends_on:
      [dependencia]:
        condition: service_healthy
```

### Kubernetes — Padrões

- Declarar `resources.requests` e `resources.limits` em todo Deployment.
- Usar `livenessProbe` e `readinessProbe` em todos os containers.
- `Namespace` por ambiente (dev, homolog, prod) e por domínio de sistema.
- Secrets via Kubernetes Secrets (nunca em ConfigMap ou variáveis de environment diretamente no Deployment).
- Labels obrigatórias: `app`, `version`, `environment`.

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"

livenessProbe:
  httpGet:
    path: /health
    port: [porta]
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: [porta]
  initialDelaySeconds: 5
  periodSeconds: 5
```

### CI/CD — Boas Práticas

- Pipeline segue ordem: `lint → test → build → security-scan → deploy`.
- Build e push de imagem Docker apenas em branch protegida (main/master/develop) ou tag.
- Usar cache de dependências para acelerar pipeline (`cache: paths:`).
- Separar jobs de `test` e `deploy` — deploy nunca antes de tests passing.
- Artefatos de build devem ser versionados com o SHA do commit ou tag semântica.
- Nunca armazenar credenciais em arquivos de pipeline — usar secrets/variables do CI.

```yaml
# Estrutura genérica de pipeline
stages:
  - lint
  - test
  - build
  - security
  - deploy

lint:
  stage: lint
  script: [comando-lint]

test:
  stage: test
  script: [comando-teste]
  coverage: '/Coverage: \d+\.\d+%/'

build:
  stage: build
  script:
    - docker build -t [imagem]:[tag] .
  only:
    - main
    - tags
```

### Segurança

- Varredura de imagem Docker com **Trivy** ou **Snyk** antes de deploy em produção.
- Credenciais nunca em logs, variáveis de ambiente visíveis em `docker inspect`, ou arquivos versionados.
- Configuração de TLS/HTTPS obrigatória em ambientes não-localhost.
- Scan de dependências (`OWASP`, `npm audit`, `pip-audit`) integrado ao pipeline.

### Health Checks e Observabilidade

- Todo serviço deve expor `/health` (liveness) e `/ready` (readiness).
- Logs estruturados em JSON com campos: `timestamp`, `level`, `service`, `correlationId`, `message`.
- Métricas Prometheus via `/metrics` quando aplicável.

### Guardrail de Manutenção

- Manter este adapter genérico — sem referências a plataforma cloud específica (AWS, GCP, Azure) ou projeto.
- Customizações de plataforma → adapter próprio: `.github/instructions/<projeto>-devops.instructions.md`.

### Referências da convenção consolidada

- `CLAUDE.md` e `.github/copilot-instructions.md` para governança geral.
- Adapter específico do projeto para configurações de cluster, registry e pipeline da plataforma.
- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Kubernetes Patterns: https://kubernetes.io/docs/concepts/workloads/pods/

<!-- R-064/R-065: Cadeia pós-plano unificada: *-arch-advisor / planejador retorna motivo: "plano_materializacao_pendente" -> @docs-engineer (materializador único docs/plans/<tipo>/ DRAFT) -> @plan-critic (R-065) -> Gate HITL -> executor (Q&A consultivo isento). -->

