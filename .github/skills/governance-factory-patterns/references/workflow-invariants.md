# Invariantes de Origem e Evolução de Workflows Canônicos (W-01 a W-08)

> **Escopo e Carregamento Lazy (R-050 / R-055 Q2 / R-064 / R-065 / R-066)**:
> Referência normativa obrigatória para `@governance-factory`, `@governance-maintainer` e `@agent-auditor` sempre que qualquer arquivo de workflow (`.github/agents/workflows.md`, `.github/agents/workflows/*.md` ou seção `workflows:` de `.github/agents/routing-graph.yaml`) for criado, refatorado ou auditado. Mantida como referência lazy (`< 150 linhas`) para preservar a economia de contexto estático sem introduzir um tipo `type: workflow` redundante.

---

## As 8 Regras Invariantes de Origem de Workflow (`W-01` a `W-08`)

### W-01 (Invariante 1) — Sincronia Quádrupla Obrigatória (R-050)
Todo workflow criado ou modificado deve manter paridade exata de ID, nome, contagem e numeração de etapas entre:
1. `.github/agents/workflows.md` (índice, Regra 7 da § 1.5, diagrama Mermaid e tabela § 2.1);
2. `.github/agents/workflows/workflow-<id>.md` (sub-arquivo detalhado);
3. `.github/agents/workflows/invariantes-e-protocolos.md` (contratos transversais, ex.: § 6.2 e § 10.7);
4. `.github/agents/routing-graph.yaml` (bloco `workflows:` e `metadata.total_workflows`).

### W-02 (Invariante 2) — Numeração Sequencial Monotônica de Estados
Os estados principais em `workflow-<id>.md` devem seguir numeração inteira sequencial estrita (`Estado 1`, `Estado 2`, `Estado 3`...), admitindo sufixo alfabético apenas para sub-ramificações ou gates intermediários explícitos (ex.: `Estado 2b`, `Estado 5b`) ou pré-estado inicial documentado (`Pré-Estado 0`), sendo terminantemente proibida a duplicação de números de estado (como dois itens `3. **Estado 3`).

### W-03 (Invariante 3) — Gate Cético Pré-HITL Obrigatório (`@plan-critic` / R-064 / § 10.7)
Todo workflow que materialize plano em `docs/plans/<tipo>/` via `@docs-engineer` (ou `@governance-maintainer` em governança) deve incluir explicitamente o passo de revisão cética pré-HITL pelo `@plan-critic` (`Two-Tier Hybrid Gate`, máx. 2 rodadas; 3 em `tier: full`, ref. `invariantes-e-protocolos.md § 10.7`) **antes** do Gate de Aprovação Humana (`ask_questions`). Exceção canônica única: `WORKFLOW-REQUIREMENTS-TO-CODE` na etapa de requisitos puros.

### W-04 (Invariante 4) — Guard de Severidade Arquitetural Explícito (R-065 / § 10.2)
Todo workflow que contenha etapa `quality_review_loop` deve referenciar explicitamente a regra `R-065` (bloqueio do loop tático por achados `CRITICAL`/`HIGH` de arquitetura/segurança/contratos dos consultores `*-arch-advisor`, forçando retorno ao advisor/planejador com invalidação do Gate 2, e limite tático de 2–3 iterações para achados `LOW`/`MEDIUM` antes de escalonamento humano), mantendo distinção semântica estrita em relação a `R-064` (persistência física de planos e gate `@plan-critic`, § 10.6 / § 10.7).

### W-05 (Invariante 5) — Nomenclatura Canônica de Planos sem Prefixos Legados (R-064 § 10.6)
Caminhos de artefatos em `docs/plans/<tipo>/` citados dentro de workflows devem usar exclusivamente o padrão `<AAAAMMDD-HHMMSS>-<slug>.md` (vedados prefixos legados `PLAN-` ou `REQ-` em nomes de arquivos), reservando `REQ-NN` exclusivamente para identificadores internos de requisitos de negócio EARS na Matriz De-Para ou especificação funcional.

### W-06 (Invariante 6) — Segregação de Execução Pós-HITL por Extensão de Arquivo
Quando um plano de manutenção ou evolução abranger simultaneamente arquivos declarativos de governança (`.md`, `.yaml`, `.json`) e testes automatizados (`.py`), o workflow deve particionar a execução pós-HITL em ondas separadas:
- **Onda 4A (Declarativa)**: `@governance-maintainer` / `@governance-factory` restritos a artefatos declarativos (veto absoluto a tocar em `*.py`);
- **Onda 4B (Python/Pytest)**: handoff para `@python-router` → `@python-arch-advisor` → `@python-test-engineer` para criar/editar e executar `tests/**/*.py`.

### W-07 (Invariante 7) — Atualização Atômica de Contadores e Ranges de Catálogo
Qualquer alteração no total de workflows ou no catálogo de smells deve atualizar no mesmo lote o comentário de cabeçalho e `metadata.total_workflows` em `routing-graph.yaml` (`9 workflows canônicos (+ 3.A auxiliar)`) e os ranges documentados nos sub-arquivos (ex.: `Smells 2.1 a 2.35`).

### W-08 (Invariante 8) — Rastreabilidade em Suíte de Testes de Auditoria (`pytest`)
Toda regra estrutural de workflow deve possuir cobertura automatizada correspondente em `tests/governance_audit/test_workflows_parity_and_gates.py`.

---

## Checklist Rápido Pré-Commit de Paridade Quádrupla
- [ ] **W-01**: `workflows.md`, `workflow-<id>.md`, `invariantes-e-protocolos.md` (§ 6.2) e `routing-graph.yaml` possuem a mesma contagem e semântica de etapas?
- [ ] **W-02**: Numeração de estados em `workflow-<id>.md` é monotônica crescente sem duplicatas?
- [ ] **W-03**: Passo pré-HITL do `@plan-critic` (§ 10.7) consta explicitamente antes de `ask_questions` em todos os sub-arquivos R-064?
- [ ] **W-04**: `R-065` está referenciado nos estados de `quality_review_loop` e desambiguado de `R-064`?
- [ ] **W-05**: Zero caminhos em `docs/plans/` com prefixos `PLAN-` ou `REQ-`?
- [ ] **W-06**: Mutações em `*.py` isoladas em onda separada via `@python-router`?
- [ ] **W-07 & W-08**: Ranges de smells (`2.1 a 2.35`), cabeçalho do `routing-graph.yaml` e testes em `test_workflows_parity_and_gates.py` sincronizados?
