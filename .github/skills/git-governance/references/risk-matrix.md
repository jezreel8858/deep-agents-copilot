# Matriz de Risco e Blast Radius (Nível 3 — git-governance)

## 1) Critérios

| Nível | Critério |
|---|---|
| **Baixo** | Docs, testes, estilo, refactor interno coberto por testes; sem path sensível; reversível por simples revert |
| **Médio** | Mudança funcional localizada; novas dependências minor/patch; alteração em módulo compartilhado com cobertura |
| **Alto** | Toca path sensível, contrato público, dados persistidos, ou é difícil de reverter |

## 2) Paths Sensíveis (elevam o risco)

| Categoria | Exemplos de path/padrão | Mínimo |
|---|---|---|
| Autenticação/autorização | `auth/`, `security/`, `**/*Jwt*`, `**/*Permission*` | Alto |
| Migrations/schema | `migrations/`, `db/`, `*.sql`, `flyway/`, `liquibase/` | Alto |
| CI/CD | `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml` | Alto |
| API pública/contratos | `openapi*.yaml`, `*.proto`, controllers/DTOs públicos | Médio→Alto se breaking |
| Dependências | `pom.xml`, `package.json`, lockfiles, `requirements*.txt` | Médio (major → Alto) |
| Infra/containers | `Dockerfile`, `docker-compose*`, `terraform/`, `k8s/` | Médio→Alto |
| Configuração/segredos | `.env*`, `application*.yml`, `*.pem` | Alto |

## 3) Blast Radius

Estimar por: nº de módulos/consumidores afetados, reversibilidade (revert limpo?), impacto em dados, janela de exposição. Maior fator determina o nível final.

## 4) Mitigações Esperadas

| Nível | Mitigação mínima |
|---|---|
| Baixo | Testes existentes passando |
| Médio | Testes novos + Plano de Rollback descrito |
| Alto | Testes + rollback verificável + revisão adicional + feature flag/deploy gradual quando viável |

Linha da matriz sempre baseada em evidência do diff — nunca presumida.
