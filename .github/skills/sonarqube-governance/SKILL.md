---
name: sonarqube-governance
description: >
  Boas práticas para uso de SonarQube em métricas de qualidade, security hotspots,
  quality gates, análise de PR e integração CI/CD. Baseado em SonarQube 10+ e
  metodologia Clean as You Code (2025).
tier: 2
category: quality
triggers:
  - "sonarqube"
  - "sonar"
  - "qualidade de código"
  - "vulnerabilidades"
  - "cobertura sonar"
  - "quality gate"
  - "hotspot"
  - "code smell"
  - "sonarcloud"
  - "clean as you code"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# SonarQube Governance

## 1) Metodologia: Clean as You Code

**Princípio central** (SonarQube 10+): foque na **qualidade do código novo**, não em resolver o passado inteiro de uma vez.

```
Código novo/alterado → Quality Gate estrito
Código legado      → visibility only (não bloquear)
```

**Por que?** Bloquear merges por issues em código de 5 anos desestimula adoção e cria ruído. A estratégia correta é garantir que *nada novo* degrade qualidade.

---

## 2) Quality Gate — Configuração Recomendada

### Para Código Novo (PR / branch)

```yaml
quality_gate_new_code:
  cobertura_nova: ">= 80%"           # linhas novas cobertas
  duplications: "< 3%"               # duplicação em código novo
  maintainability_rating: "A"        # code smells: dívida/tamanho ≤ 5%
  reliability_rating: "A"            # 0 bugs no código novo
  security_rating: "A"               # 0 vulnerabilidades no código novo
  security_hotspots_reviewed: "100%" # todos hotspots revisados
```

### Para Código Geral (baseline)

```yaml
quality_gate_overall:
  cobertura_geral: ">= 70%"         # threshold de projeto consolidado
  duplications: "< 10%"
  reliability_rating: ">= B"        # bugs existentes aceitáveis
  security_rating: ">= B"
```

> **Evitar**: thresholds muito agressivos em código legado — criam tickets falsos e bloqueiam times.

---

## 3) Security Hotspots — Fluxo de Revisão

Hotspots **não são vulnerabilidades confirmadas** — são trechos que precisam de revisão humana.

```
Workflow correto:

1. Identificar → listar hotspots de alta prioridade primeiro
2. Revisar → entender o risco (está realmente exposto?)
3. Decidir:
   - "Fixed"    → código foi corrigido
   - "Safe"     → revisão confirmou que não é risco real
   - "Kept"     → risco conhecido, aceito e documentado
4. Documentar → adicionar comentário com justificativa

❌ NÃO reportar hotspots como "vulnerabilidades confirmadas" para gestão
   sem revisão — isso infla severity e destrói confiança.
```

---

## 4) Integração CI/CD

### GitLab CI

```yaml
sonarqube-check:
  stage: test
  image: sonarsource/sonar-scanner-cli:latest
  variables:
    SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar"
    GIT_DEPTH: "0"
  script:
    - sonar-scanner
      -Dsonar.projectKey=$CI_PROJECT_NAME
      -Dsonar.host.url=$SONAR_HOST_URL
      -Dsonar.token=$SONAR_TOKEN
      -Dsonar.qualitygate.wait=true   # aguardar resultado do QG
  allow_failure: false
  only:
    - merge_requests
    - main
```

### GitHub Actions

```yaml
- name: SonarQube Scan
  uses: SonarSource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
  with:
    args: >
      -Dsonar.qualitygate.wait=true
```

### sonar-project.properties

```properties
sonar.projectKey=meu-projeto
sonar.projectName=Meu Projeto
sonar.sources=src/main
sonar.tests=src/test
sonar.java.binaries=target/classes
sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
sonar.exclusions=**/generated/**,**/*Config.java
```

---

## 5) Operações Recomendadas

### Fluxo IDE → PR → Main

```
1. SonarLint (IDE): feedback em tempo real enquanto o dev codifica
2. PR analysis: QG em novo código — bloquear se falhar
3. Hotspot review: parte do processo de code review
4. Main branch trending: acompanhar tendência de dívida técnica
5. Debt program: líderes planejam refatorações baseadas em métricas
```

### Métricas a Monitorar

| Métrica | Threshold OK | Alerta |
|---|---|---|
| Coverage (novo código) | ≥ 80% | < 70% |
| Security Vulnerabilities | 0 | ≥ 1 Critical |
| Bugs (novo código) | 0 | ≥ 1 |
| Debt Ratio | < 5% | > 15% |
| Duplications (novo) | < 3% | > 10% |

---

## 6) Anti-padrões

- ❌ Ignorar SonarQube (apenas rodar, nunca agir nos resultados) — "screenshot program"
- ❌ Tratar todos os hotspots como vulnerabilidades confirmadas (infla severidade)
- ❌ Configurar QG muito restritivo em legado (bloqueia sem valor)
- ❌ Habilitar muitas regras de baixa precisão em caminhos bloqueantes
- ❌ Não usar SonarLint localmente (só descobrir issues no CI é tarde demais)
- ❌ Excluir código problemático das análises em vez de corrigir

---

## 7) Referências

- SonarQube Docs: https://docs.sonarsource.com/sonarqube/
- Clean as You Code: https://docs.sonarsource.com/sonarqube/latest/user-guide/clean-as-you-code/
- Security Hotspots: https://www.product-security.expert/05-application-security/sonarqube-modern-practical-guide-quality-gates-hotspots-and-review-workflows.html
- CI/CD Integration 2025: https://medium.com/@lamjed.gaidi070/sonarqube-in-2025-the-ultimate-guide-to-code-quality-ci-cd-integration-alerting-43e96018d36f
