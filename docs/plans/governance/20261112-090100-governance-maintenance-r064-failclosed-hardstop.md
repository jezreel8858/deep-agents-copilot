---
status: COMPLETED
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-12"
date: "2026-11-12"
related-planning-doc: "docs/plans/governance/20261112-090200-governance-maintenance-universal-plan-materialization.md"
workflow: "WORKFLOW-GOVERNANCE-MAINTENANCE"
allowed_files:
  - "docs/plans/governance/**"
  - "CLAUDE.md"
  - ".github/agents/workflows.md"
  - ".github/agents/workflows/invariantes-e-protocolos.md"
  - ".github/agents/agent-router.agent.md"
  - ".github/agents/agent-auditor.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/prompt-structuring.agent.md"
  - ".github/agents/templates/**"
  - ".github/prompts/craft-prompt.prompt.md"
  - "tests/governance_audit/**"
---

# Plano de Manutenção de Governança — Fechamento Fail-Closed e Hard-Stop Universal da Regra R-064

## 1. Contexto e Diagnóstico de Causa Raiz (RCA — 5 Porquês)

Na execução anterior do `WORKFLOW-GOVERNANCE-MAINTENANCE` (padronização da ferramenta `ask_questions` sob R-027), as mutações nos 21 artefatos da malha de governança foram aplicadas diretamente após o checkpoint humano em chat, **sem a prévia materialização física do arquivo de plano em `docs/plans/governance/`**.

A análise de causa raiz (5 Porquês) identificou 5 fatores sistêmicos concorrentes que permitiram o contorno (*bypass*) silencioso da regra R-064:

1. **Brecha semântica na isenção § 10.3(b) de `.github/agents/workflows/invariantes-e-protocolos.md`**: A cláusula isentava da R-064 *"alterações restritas a arquivos Markdown (`*.md`) ou configurações declarativas sem impacto comportamental"*, sem excluir explicitamente os diretórios críticos da malha (`.github/**`, `tools/**`, `tests/**`, `CLAUDE.md`). Como prompts e contratos de agentes são escritos em `*.md`, demandas de manutenção de governança eram falsamente classificadas como `isencao_r064: docs_only`.
2. **Notação implícita entre colchetes e ordem invertida em `.github/agents/workflows.md:134`**: O fluxo `WORKFLOW-GOVERNANCE-MAINTENANCE` estava declarado como `1. Diagnóstico (@agent-auditor) -> 2. Checkpoint Humano (R-034) -> [Plano de Governança R-064] -> 3. Execução (@governance-maintainer)`. Posicionar `[Plano de Governança R-064]` *após* o Checkpoint Humano, entre colchetes e sem agente executor responsável pela escrita em disco, induziu o salto direto da aprovação em chat para a mutação dos arquivos.
3. **Contradição estrutural e cláusula *fail-open* em `.github/agents/workflows/invariantes-e-protocolos.md:421`**: O texto da seção de governança referenciava erroneamente `docs/plans/implementation/` em vez de `docs/plans/governance/` e continha a instrução explícita *"o fluxo nunca é bloqueado por ausência de artefato intermediário"*, instituindo comportamento *fail-open* diametralmente oposto ao contrato *fail-closed* de R-064.
4. **Ausência de Gate 2-G no `@agent-router` e de Hard-Stop no `@governance-maintainer`**: O `@agent-router` ainda mencionava o caminho legado `docs/implementation-plans/` (linha 51), não exigia a materialização física prévia do plano de governança antes do HITL e aceitava `isencao_r064: docs_only` sem validar escopo. Simultaneamente, o `@governance-maintainer` aceitou o handoff de mutação em lote sem verificar a existência física de `plan_ref` em `docs/plans/governance/` com `approved: true`.
5. **Instrução restritiva ambígua em `prompt-structuring.agent.md` e `craft-prompt.prompt.md`**: A diretriz *"NÃO criar documento avulso de estudo/especificação em `docs/` quando não solicitado"* não distinguia "documentos avulsos de estudo" dos "planos obrigatórios de workflow R-064 em `docs/plans/<tipo>/`", induzindo o estruturador de prompt a omitir a etapa de persistência física em `docs/plans/governance/`.

---

## 2. Mapa de Gaps Diagnosticados (G1 a G11)

| ID | Smell / Categoria | Localização Exata | Severidade | Impacto Operacional | Remediação Canônica |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **G1** | Ambiguidade de Escopo (Isenção `docs_only`) | `.github/agents/workflows/invariantes-e-protocolos.md` (§ 10.3.b) | CRÍTICA | Permite classificar alterações em `.github/agents/*.md` e `CLAUDE.md` como simples documentação isenta de plano R-064. | Vedar explicitamente a isenção `docs_only` quando houver qualquer arquivo em `.github/**`, `CLAUDE.md`, `AGENTS.md`, `tools/**` ou `tests/**`. |
| **G2** | Sequenciamento Invertido de Workflow | `.github/agents/workflows.md` (linha 134 — `WORKFLOW-GOVERNANCE-MAINTENANCE`) | CRÍTICA | Coloca `[Plano de Governança R-064]` após o Checkpoint Humano e sem executor de persistência física definido. | Redefinir sequência: `1. Diagnóstico (@agent-auditor) -> 2. Materialização Física do Plano DRAFT em docs/plans/governance/ (@docs-engineer ou @governance-maintainer) -> 3. Gate de Aprovação Humana (R-034 / R-064) -> 4. Execução (@governance-maintainer)`. |
| **G3** | Cláusula Fail-Open e Diretório Incorreto | `.github/agents/workflows/invariantes-e-protocolos.md` (linha 421) | CRÍTICA | Aponta para `docs/plans/implementation/` no fluxo de governança e afirma que o fluxo nunca é bloqueado por ausência de plano. | Corrigir caminho para `docs/plans/governance/` e substituir a cláusula *fail-open* por bloqueio *fail-closed* estrito (R-064). |
| **G4** | Referência Legada de Diretório | `.github/agents/agent-router.agent.md` (linha 51) | ALTA | Cita `docs/implementation-plans/` (diretório extinto), gerando deriva de roteamento na verificação de planos. | Substituir por `docs/plans/<tipo>/` com listagem explícita das 8 subpastas canônicas de R-064. |
| **G5** | Ausência de Gate 2-G no Router | `.github/agents/agent-router.agent.md` | CRÍTICA | O router delega para `@governance-maintainer` sem exigir `plan_ref` físico aprovado em `docs/plans/governance/`. | Instituir Gate 2-G obrigatório: bloquear handoff de execução sem `plan_ref` físico aprovado e auditar `isencao_r064`. |
| **G6** | Ausência de Delegação de Persistência no Auditor | `.github/agents/agent-auditor.agent.md` | ALTA | Como `@agent-auditor` é 100% Read-Only (R-025), emite o plano apenas em texto no chat e aciona aprovação sem gravar arquivo. | Exigir que o diagnóstico estruturado pelo `@agent-auditor` seja materializado em `docs/plans/governance/` (via `@docs-engineer` ou `@governance-maintainer` em modo draft-only) **antes** do Gate Humano. |
| **G7** | Ausência de Hard-Stop no Executor de Governança | `.github/agents/governance-maintainer.agent.md` | CRÍTICA | Executa mutações em `.github/**` sem checar a existência física e aprovação do plano em `docs/plans/governance/`. | Adicionar Hard-Stop Fail-Closed: recusar mutação da malha se `plan_ref` não existir fisicamente em `docs/plans/governance/` com `approved: true` (exceto quando acionado exclusivamente para criar o arquivo `DRAFT` do plano ou atualizar seu frontmatter pós-aprovação). |
| **G8** | Supressão Induzida pelo Prompt Structuring | `.github/agents/prompt-structuring.agent.md` | ALTA | Regra "NÃO criar documento avulso em `docs/`" suprime a geração do plano obrigatório em `docs/plans/<tipo>/`. | Explicitar que a proibição de documentos avulsos NUNCA suspende a materialização física obrigatória R-064 em `docs/plans/<tipo>/`. |
| **G9** | Supressão Induzida pelo Craft Prompt | `.github/prompts/craft-prompt.prompt.md` | ALTA | Mesma ambiguidade de G8 no template de comando `/craft-prompt`, gerando prompts otimizados que pulam a etapa de persistência R-064. | Incluir diretriz obrigatória de preservação do passo de materialização física em `docs/plans/<tipo>/` antes do Gate HITL. |
| **G10** | Desalinhamento em Templates de Agentes (Q2) | `.github/agents/templates/**` e `CLAUDE.md` | MÉDIA | Templates e índice central não refletem a restrição estrita da isenção § 10.3(b) nem o Gate 2-G fail-closed. | Sincronizar `CLAUDE.md` e templates de governança com a regra fail-closed de R-064 (Simetria Q1+Q2 — R-055). |
| **G11** | Lacuna de Cobertura em Testes Determinísticos (Q3) | `tests/governance_audit/test_universal_plan_materialization_governance.py` | ALTA | A suíte atual valida a existência das 8 pastas, mas não testa a ordem de `workflows.md:134`, a ausência de `docs/implementation-plans/`, a proibição de fail-open nem o Hard-Stop em `@governance-maintainer`. | Expandir a suíte pytest com asserções determinísticas cobrindo G1 a G9 (Tríade Q1+Q2+Q3 — R-055). |

---

## 3. Escopo, Critérios de Aceitação (CA-01 a CA-06) e Regras Impactadas

### 3.1 Regras de Governança Impactadas
- **R-050 (Prevenção e Tratamento de Erros / Fail-Closed)**: Eliminação de cláusulas *fail-open* na verificação de artefatos obrigatórios de planejamento.
- **R-055 (Integridade Sistêmica Universal — Tríade Q1+Q2+Q3)**: Sincronização simultânea entre documentação/contratos (Q1), templates/prompts (Q2) e suíte determinística de auditoria pytest (Q3).
- **R-064 (Persistência Física Universal de Planos em `docs/plans/<tipo>/`)**: Fechamento de brechas de isenção, correção da ordem do workflow de governança e instituição de Hard-Stop nos agentes roteador e executor.

### 3.2 Critérios de Aceitação
- **CA-01 (Fechamento da Isenção § 10.3.b e Fim do Fail-Open)**: `.github/agents/workflows/invariantes-e-protocolos.md` deve proibir expressamente o uso da isenção `docs_only` para qualquer arquivo sob `.github/**`, `CLAUDE.md`, `AGENTS.md`, `tools/**` ou `tests/**`, além de substituir a cláusula *fail-open* da linha 421 por bloqueio *fail-closed* apontando para `docs/plans/governance/`.
- **CA-02 (Sequência Canônica no Workflow de Governança)**: `.github/agents/workflows.md` deve declarar explicitamente a etapa de materialização física do plano `DRAFT` em `docs/plans/governance/` **antes** do Checkpoint Humano (R-034 / R-064) no `WORKFLOW-GOVERNANCE-MAINTENANCE`.
- **CA-03 (Gate 2-G e Hard-Stop nos Agentes)**: `agent-router.agent.md` (sem referências legadas a `docs/implementation-plans/`), `agent-auditor.agent.md` e `governance-maintainer.agent.md` devem conter travas *fail-closed* exigindo arquivo físico em `docs/plans/governance/` antes da aprovação humana e `approved: true` antes da mutação dos alvos da malha.
- **CA-04 (Distinção em Prompt Structuring)**: `prompt-structuring.agent.md` e `craft-prompt.prompt.md` devem distinguir explicitamente a proibição de criar estudos avulsos em `docs/` da obrigação inegociável de materializar planos R-064 em `docs/plans/<tipo>/`.
- **CA-05 (Rastreabilidade Retroativa 100%)**: O plano referente à entrega anterior de padronização de `ask_questions` deve estar fisicamente materializado em `docs/plans/governance/20261112-090000-governance-maintenance-ask-questions-ux-standardization.md` com `status: COMPLETED` e `approved: true`.
- **CA-06 (Validação Determinística Pytest — Q3)**: `tests/governance_audit/test_universal_plan_materialization_governance.py` deve conter testes automatizados validando CA-01 a CA-05, passando integralmente (`pytest` 100% verde).

---

## 4. Plano de Execução em Lotes (R-046 / R-059)

### Lote 1 — Contratos Canônicos de Workflow e Invariantes (Q1)
- **Alvos**:
  - `.github/agents/workflows/invariantes-e-protocolos.md`
  - `.github/agents/workflows.md`
  - `CLAUDE.md`
- **Ações**:
  1. Restringir a isenção § 10.3(b) em `invariantes-e-protocolos.md`: alterações em `.github/**`, `CLAUDE.md`, `AGENTS.md`, `tools/**` ou `tests/**` **jamais** qualificam como `docs_only` e exigem plano físico em `docs/plans/governance/`.
  2. Corrigir a seção de governança em `invariantes-e-protocolos.md:421`, substituindo `docs/plans/implementation/` por `docs/plans/governance/` e removendo a cláusula *fail-open*.
  3. Atualizar `workflows.md` no `WORKFLOW-GOVERNANCE-MAINTENANCE` para: `1. Diagnóstico (@agent-auditor) -> 2. Persistência Física do Plano DRAFT em docs/plans/governance/ (@docs-engineer / @governance-maintainer) -> 3. Checkpoint Humano (R-034 / R-064) -> 4. Execução em Lotes (@governance-maintainer)`.
  4. Sincronizar o resumo da R-064 em `CLAUDE.md`.

### Lote 2 — Hard-Stop nos Agentes de Governança e Estruturação de Prompts (Q1 + Q2)
- **Alvos**:
  - `.github/agents/agent-router.agent.md`
  - `.github/agents/agent-auditor.agent.md`
  - `.github/agents/governance-maintainer.agent.md`
  - `.github/agents/prompt-structuring.agent.md`
  - `.github/prompts/craft-prompt.prompt.md`
- **Ações**:
  1. Em `agent-router.agent.md`: eliminar a referência legada a `docs/implementation-plans/`, exigir verificação física em `docs/plans/<tipo>/` e vedar `isencao_r064: docs_only` para arquivos da malha de governança.
  2. Em `agent-auditor.agent.md`: determinar que todo diagnóstico de manutenção de governança deve ser sucedido pela delegação de persistência física do plano `DRAFT` em `docs/plans/governance/` antes de acionar `ask_questions` para aprovação do plano.
  3. Em `governance-maintainer.agent.md`: instituir **Hard-Stop R-064** — bloquear qualquer mutação na malha se o arquivo `plan_ref` não existir fisicamente em `docs/plans/governance/` com `approved: true` (permitindo apenas a operação estrita de criação inicial do arquivo `DRAFT` em `docs/plans/governance/` ou atualização do seu frontmatter pós-aprovação humana).
  4. Em `prompt-structuring.agent.md` e `craft-prompt.prompt.md`: adicionar ressalva explícita de que a regra contra criação de documentos avulsos em `docs/` não se aplica aos planos canônicos de workflow em `docs/plans/<tipo>/` (R-064), cujo passo de materialização física antes do Gate Humano deve ser obrigatoriamente incluído nos prompts estruturados.

### Lote 3 — Sincronização de Templates (Q2) e Testes de Auditoria Determinística (Q3)
- **Alvos**:
  - `.github/agents/templates/**` (se aplicável à regra R-064)
  - `tests/governance_audit/test_universal_plan_materialization_governance.py`
- **Ações**:
  1. Adicionar testes em `test_universal_plan_materialization_governance.py` verificando:
     - Ausência da string legada `docs/implementation-plans/` em `.github/agents/agent-router.agent.md`;
     - Ausência da cláusula fail-open *"nunca é bloqueado por ausência"* associada a planos em `invariantes-e-protocolos.md`;
     - Presença da restrição explícita contra `.github/**` na isenção § 10.3(b);
     - Presença do Hard-Stop de verificação de `docs/plans/governance/` em `governance-maintainer.agent.md`;
     - Presença da ressalva R-064 em `prompt-structuring.agent.md` e `craft-prompt.prompt.md`.
  2. Executar a suíte `pytest tests/governance_audit/` e `get_errors` para certificação final.

---

## 5. Modelagem de Ameaças (Shift-Left), Riscos e Estratégia de Rollback

| Risco / Ameaça | Probabilidade | Impacto | Mitigação Shift-Left |
| :--- | :--- | :--- | :--- |
| **Deadlock de Persistência (Ovo e a Galinha)**: `@agent-auditor` é Read-Only e não pode gravar o plano, enquanto `@governance-maintainer` exige plano aprovado para agir. | Alta (se mal especificado) | Alto | O Hard-Stop de `@governance-maintainer` autoriza explicitamente o modo **Materialização de Draft** (escrita exclusiva em `docs/plans/governance/*.md` com `status: DRAFT, approved: false`), ou a delegação ao `@docs-engineer`, bloqueando apenas a mutação dos demais arquivos da malha antes de `approved: true`. |
| **Falso Positivo em Edições Simples de README de Aplicação**: Bloquear edições triviais em READMEs fora da malha de governança. | Baixa | Médio | A exclusão da isenção § 10.3(b) é cirúrgica: aplica-se apenas a `.github/**`, `CLAUDE.md`, `AGENTS.md`, `tools/**` e `tests/**`, preservando a isenção para documentação pura de usuário final quando solicitada isoladamente. |
| **Quebra de Testes Existentes na Suíte de Governança**: Regex ou invariantes de tamanho de arquivo excedidos. | Baixa | Médio | Execução integral de `pytest tests/governance_audit/` no Lote 3 antes do encerramento do turno. |

### Estratégia de Rollback
- Todas as alterações são declarativas em arquivos versionados via Git. Em caso de regressão na suíte `tests/governance_audit/`, reverter atomicamente os lotes via `git checkout -- <arquivos_do_lote>` sem impacto em dados persistentes de runtime.
