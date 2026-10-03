---
name: devops-agent-patterns
description: >
  Diretrizes consolidadas para revisão especializada de artefatos DevOps —
  Dockerfile, Kubernetes manifests, GitHub Actions/CI pipelines e
  Infrastructure-as-Code. Complementa o adapter genérico devops.instructions.md
  com critérios de revisão acionáveis por um agent especialista.
tier: 2
category: quality
triggers:
  - "revisar dockerfile"
  - "revisar kubernetes"
  - "revisar pipeline"
  - "revisar ci/cd"
  - "infrastructure as code"
  - "terraform"
  - "helm chart"
  - "github actions"
  - "deployment strategy"
source_docs:
  - .github/instructions/devops.instructions.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# DevOps Agent Patterns

> Base de conhecimento para agent especialista que **revisa/recomenda** artefatos DevOps — Dockerfile, Kubernetes, CI/CD, IaC. Complementa `devops.instructions.md` (convenções genéricas de código) com **critérios de revisão** acionáveis.

## Quando Usar

- Ao revisar Dockerfile novo ou alterado.
- Ao avaliar manifests Kubernetes (Deployment, Service, Ingress).
- Ao revisar pipeline de CI/CD (GitHub Actions, GitLab CI).
- Ao avaliar estratégia de deployment (blue-green, canary, rolling).

## 1) Checklist de Revisão — Dockerfile

| Item | Critério de Bloqueio |
|---|---|
| Imagem base | Versão explícita (`node:20-alpine`), nunca `:latest` → 🟠 Alta se `:latest` |
| Multi-stage build | Build e runtime separados para imagens não-triviais → 🟡 Sugestão se ausente |
| Usuário não-root | Container roda como `USER nonroot` → 🔴 Bloqueador se root em produção |
| `.dockerignore` | Presente, excluindo `node_modules`/`.git`/`target` → 🟡 Sugestão |
| Secrets no build | Nenhum secret via `ARG`/`ENV` hardcoded → 🔴 Bloqueador |
| Camadas otimizadas | `COPY package*.json` antes de `COPY .` para cache de layer → 🟡 Sugestão |

## 2) Checklist de Revisão — Kubernetes

| Item | Critério de Bloqueio |
|---|---|
| `resources.requests/limits` | Declarado em todo container → 🔴 Bloqueador se ausente (risco de OOM/noisy neighbor) |
| `livenessProbe`/`readinessProbe` | Presente em todo Deployment → 🟠 Alta se ausente |
| Secrets via K8s Secret | Nunca em ConfigMap ou env plaintext → 🔴 Bloqueador |
| Namespace por ambiente | Separação dev/homolog/prod → 🟡 Sugestão |
| Labels obrigatórias | `app`, `version`, `environment` presentes → 🟡 Sugestão |
| `imagePullPolicy` | `Always` para tag mutável, `IfNotPresent` para tag imutável | 🟡 Sugestão |

## 3) Checklist de Revisão — CI/CD Pipeline

| Item | Critério de Bloqueio |
|---|---|
| Ordem de stages | `lint → test → build → security-scan → deploy` → 🟠 Alta se deploy antes de test |
| Credenciais | Via secrets do CI, nunca hardcoded no YAML → 🔴 Bloqueador |
| Branch protegida | Build/push de imagem apenas em main/tag → 🟠 Alta se ausente |
| Cache de dependências | Configurado para acelerar pipeline → 🟡 Sugestão |
| Security scan | Trivy/Snyk/SAST no pipeline antes de deploy → 🟠 Alta se ausente |
| Rollback | Estratégia de rollback documentada/automatizada → 🟡 Sugestão |

## 4) Estratégias de Deployment

| Estratégia | Quando Usar | Risco |
|---|---|---|
| **Rolling Update** | Padrão para a maioria dos casos | Baixo — K8s nativo |
| **Blue-Green** | Rollback instantâneo necessário | Médio — dobra de recursos temporário |
| **Canary** | Validação gradual com tráfego real | Médio — requer observabilidade robusta |
| **Feature Flag** | Desacoplar deploy de release | Baixo — requer infraestrutura de flags |

## 5) Infrastructure-as-Code (Terraform/Helm)

- [ ] Estado remoto (backend S3/GCS) com lock — nunca state local em produção.
- [ ] Variáveis sensíveis via secret manager, nunca em `.tfvars` commitado.
- [ ] `terraform plan` revisado antes de `apply` — nunca apply direto sem plan.
- [ ] Módulos versionados (não `HEAD`/branch mutável).

## 6) Anti-Padrões

- ❌ Aprovar Dockerfile com `USER root` implícito (ausência de `USER` = root).
- ❌ Pipeline sem security scan antes de deploy em produção.
- ❌ Deployment sem `resources.limits` (risco de esgotar nó).
- ❌ Sugerir mudança de infraestrutura sem considerar custo/complexidade operacional.

## Checklist de Saída

- [ ] Artefato identificado (Dockerfile/K8s/Pipeline/IaC).
- [ ] Cada achado com severidade e critério de bloqueio objetivo (§1-3).
- [ ] Recomendação concreta, não apenas "melhorar segurança".
- [ ] Referência ao adapter `devops.instructions.md` para convenções de nomenclatura/estrutura.

## Referências

- Docker Best Practices — https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Kubernetes Patterns — https://kubernetes.io/docs/concepts/workloads/pods/
- `.github/instructions/devops.instructions.md` (adapter genérico deste projeto).

