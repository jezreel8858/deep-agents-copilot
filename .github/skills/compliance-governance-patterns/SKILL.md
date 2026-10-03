---
name: compliance-governance-patterns
description: >
  Diretrizes consolidadas de compliance/governança regulatória para código de
  aplicação — SOC 2 (Type I/II), GDPR, HIPAA, ISO 27001, trilhas de auditoria,
  políticas de retenção de dados e evidências de controle. Distinto de
  agent-safety-guardrails (que cobre segurança do próprio agent de IA).
tier: 2
category: security
triggers:
  - "compliance"
  - "auditoria"
  - "soc 2"
  - "gdpr"
  - "lgpd"
  - "hipaa"
  - "iso 27001"
  - "audit trail"
  - "trilha de auditoria"
  - "retenção de dados"
  - "política de acesso"
  - "least privilege"
  - "controle de acesso"
  - "evidência de controle"
source_docs:
  - .github/skills/agent-safety-guardrails/SKILL.md
  - .github/skills/security-review-patterns/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Compliance Governance Patterns

> Base de conhecimento para agents que avaliam **conformidade regulatória da aplicação** (SOC 2, GDPR, HIPAA, ISO 27001) — diferente de `agent-safety-guardrails`, que cobre segurança do **próprio agent de IA** (prompt injection, blast radius de tools do Copilot).

## Quando Usar

- Ao revisar código que lida com dados pessoais (PII) sujeitos a GDPR/LGPD.
- Ao avaliar se uma mudança introduz gap de auditoria (ação sem log rastreável).
- Ao preparar evidências para auditoria SOC 2 Type II (observação contínua).
- Ao revisar política de acesso/permissão (least privilege).

## 1) Frameworks Consolidados (2026)

| Framework | Escopo | Evidência Necessária |
|---|---|---|
| **SOC 2 Type I** | Design de controles em ponto único no tempo | Screenshots, políticas, descrição de sistema |
| **SOC 2 Type II** | Design + efetividade operacional ao longo de 3-12 meses | Logs contínuos, registros de revisão de acesso, trilhas de ticket, evidência de MFA |
| **GDPR** (UE) / **LGPD** (Brasil) | Proteção de dados pessoais | RoPA (Record of Processing Activities), consentimento, direito ao esquecimento |
| **HIPAA** (EUA, saúde) | Dados de saúde (PHI) | Criptografia, controle de acesso, BAA (Business Associate Agreement) |
| **ISO 27001** | Gestão de segurança da informação | SGSI documentado, análise de risco, plano de continuidade |

## 2) Findings Mais Comuns em Auditorias (2026)

| # | Achado | Frequência | Severidade |
|---|---|---|---|
| 1 | Desprovisionamento de acesso incompleto/atrasado | 30-40% | Alta |
| 2 | Revisão trimestral de acesso ausente/incompleta | 25-35% | Média-Alta |
| 3 | Deploy sem code review documentado | 20-30% | Média-Alta |
| 4 | Treinamento de segurança incompleto | 20-30% | Média |
| 5 | Logging de evento de segurança insuficiente | 15-25% | Média |
| 6 | Avaliação de risco ausente/incompleta | 15-25% | Média |
| 7 | MFA não obrigatório para todo tipo de acesso | 10-20% | Alta |
| 8 | Gap política-prática (política escrita ≠ comportamento real) | 10-20% | Média |

## 3) Checklist de Auditoria/Trilha (Aplicável ao Código)

### Audit Logging
- [ ] Toda ação sensível (criação/alteração/exclusão de dado protegido) gera log estruturado.
- [ ] Log inclui: quem (identidade), o quê (ação), quando (timestamp), onde (recurso afetado).
- [ ] Logs são **append-only** (imutáveis) — nunca sobrescritos ou deletáveis por usuário comum.
- [ ] Retenção de log conforme política (mínimo 1 ano para SOC 2 Type II).

### Least Privilege / RBAC
- [ ] Toda rota/endpoint valida permissão explícita, nunca "acesso implícito por autenticação".
- [ ] Credenciais/tokens têm escopo mínimo necessário e expiração definida.
- [ ] Revisão de acesso (quem tem o quê) é auditável e periódica.

### Dados Pessoais (GDPR/LGPD/HIPAA)
- [ ] Dado sensível identificado e classificado (PII, PHI, financeiro).
- [ ] Criptografia em repouso e em trânsito para dado classificado.
- [ ] Mecanismo de exclusão/anonimização sob solicitação do titular (direito ao esquecimento).
- [ ] Nenhum dado sensível em log de aplicação sem mascaramento.

### Gestão de Mudança
- [ ] Toda mudança em produção passou por code review documentado.
- [ ] Deploy tem trilha rastreável (commit → PR → aprovação → deploy).

## 4) Padrão de Policy Enforcement (Aplicação)

```
Ação proposta → validação de política → log de decisão → execução ou bloqueio
```

- **Antes da ação**: verificar permissão (RBAC), verificar política aplicável.
- **Durante**: aplicar princípio de menor privilégio — escopo mínimo necessário.
- **Depois**: registrar decisão em audit log append-only, independente de aprovação ou rejeição.

## 5) Anti-Padrões (Achados Recorrentes de Auditoria)

- ❌ Política escrita descrevendo processo que "ninguém segue" — inconsistência é achado automático.
- ❌ Boilerplate genérico não removido (ex.: seção de segurança física para empresa 100% cloud).
- ❌ Conta de serviço/usuário offboardado ainda com acesso ativo (drift de controle de acesso).
- ❌ Log de auditoria mutável ou sem timestamp confiável.
- ❌ Confundir compliance de aplicação (este skill) com segurança de agent de IA (`agent-safety-guardrails`).

## Checklist de Saída

- [ ] Framework(s) aplicável(is) identificado(s) (SOC 2, GDPR, HIPAA, ISO 27001).
- [ ] Gap de auditoria classificado por categoria (§3) com evidência de código/config.
- [ ] Recomendação de controle concreta (não apenas "adicionar log").
- [ ] Nenhum dado sensível real reproduzido no relatório de achados.

## Referências

- SOC 2 Compliance Statistics 2026 — findings mais comuns por frequência/severidade.
- OWASP ASVS 5.0 — requisitos de verificação mapeáveis a controles de auditoria.
- Padrões de mercado (Vanta, Drata, Strac Comply) — evidência contínua vs. pontual (Type I vs Type II).
- GDPR Art. 5, 25, 28, 30, 32 — accountability e demonstrable records.

