> **Fonte de verdade operacional:** [`CLAUDE.md`](../../../CLAUDE.md) § R-050, R-041 e R-042.  
> **Índice completo:** [`.github/agents/workflows.md`](../workflows.md).

---

### 3.4 WORKFLOW 4: `WORKFLOW-FEATURE-DEVELOPMENT` (Nova Feature e Evolução Funcional E2E)

- **Objetivo**: Elicitar requisitos, conceber arquitetura técnica, desenhar contratos de API (OpenAPI), definir matriz de testes por risco, aprovar blueprint com desenvolvedor e implementar sob workflow TDD estrito com validação de segurança OWASP.
- **Gatilhos**: `"criar feature"`, `"nova funcionalidade"`, `"implementar endpoint"`, `"adicionar tela"`, `"novo módulo"`, `"evoluir fluxo"`.
- **Política R-041**: **Ativação Obrigatória** de `@prompt-structuring` caso a solicitação seja de alto nível ou ambígua. Bypassa caso venha de Fast-Chaining pós-diagnóstico com proposta aprovada.

```mermaid

flowchart TD
    Start(["🚀 Solicitação de Feature Nova"]) --> CheckAmbiguity{"Pedido aberto<br/>ou ambíguo?"}

    CheckAmbiguity -- "Sim" --> Struct["<b>1. Prompt Structuring</b><br/>Agente: @prompt-structuring<br/>Ação: Refinamento canônico (loop máx 5x)"]
    CheckAmbiguity -- "Não (Já Estruturado/Fast-Chaining)" --> Req
    Struct --> Req["<b>2. Elicitação de Requisitos</b><br/>Agente: @requirements-analyst / @feature-planner<br/>Ação: Requisitos funcionais BDD/EARS e não-funcionais"]

    Req --> Arch["<b>3. Technical Blueprint & Contratos</b><br/>Agente: @tech-solution-architect<br/>Ação: OpenAPI v3, modelo de dados e divisão por stack"]

    Arch --> CheckScope{"Escopo da Feature"}
    CheckScope -- "Fullstack" --> SplitFull["Divisão [BACKEND_TASKS] e [FRONTEND_TASKS]"]
    CheckScope -- "Backend Only" --> SplitBack["Definição de Endpoints & Persistência"]
    CheckScope -- "Frontend Only" --> SplitFront["Definição de Telas & Mock API DTOs"]

    SplitFull & SplitBack & SplitFront --> BlueprintGate{"<b>3b. Checkpoint de Blueprint</b><br/>Aprovação humana via ask_questions"}

    BlueprintGate -- "Revisar" --> Arch
    BlueprintGate -- "Aprovado" --> TestStrat["<b>4. Estratégia de Testes por Risco</b><br/>Agente: @test-strategy<br/>Ação: Matriz de riscos, casos de borda e cobertura alvo"]

    TestStrat --> TDD["<b>5. Implementação Domain TDD & Paridade UI</b><br/>Agentes: Domain Routers & Specialists<br/>Ação: Contract-First (Red -> Green -> Refactor)<br/>Frontend: 5a Lógica/Store -> 5b Handoff UI Stylist"]

    Arch --> CheckDBFeature{"Exige novas<br/>tabelas/colunas?"}
    CheckDBFeature -- "Sim" --> DBFeature["<b>3c. Migração de Schema</b><br/>Agente: @database-specialist<br/>Ação: DDL idempotente + rollback documentado"]
    DBFeature --> CheckScope

    TDD --> SecReview["<b>6a. Gate 1: Security Review (OWASP) & Lógica</b><br/>Agente: @security-reviewer<br/>Ação: Verificação de testes, injeções, IDOR, auth"]

    SecReview --> CheckSec{"Aprovado em<br/>Gate 1?"}
    CheckSec -- "Vulnerabilidade (tentativa N/2)" --> CheckSecCap{"Tentativas<br/>remediação < 2?"}
    CheckSecCap -- "Sim" --> TDD
    CheckSecCap -- "Não (teto esgotado)" --> SecEscalate["<b>6b. Escalonamento de Segurança</b><br/>ask_questions: revisão manual pareada com dev"]
    CheckSec -- "Limpo" --> UIGate["<b>6c. Gate 2: Design System & Paridade UI</b><br/>Agentes: @angular-developer / @code-review<br/>Ação: Tokens, zero hex inline, classes diálogo/scroll"]
    UIGate --> Gate["<b>6d. PR Preparation & Quality Gate Final</b><br/>Agentes: @code-review → @pr-gatekeeper<br/>Ação: Revisão de diff e geração de PR semântico"]

    Gate --> EndFeat(["✅ Feature Concluída com Sucesso"])
    %% --- R-064 PARITY START ---
    RouterHub["<b>Hub Central: @agent-router</b><br/>Flat Delegation (R-037) & Orquestração de Gates"] --> Gate1Mat["<b>Gate 1 & Gate 2: Materialização DRAFT</b><br/>Agente: @docs-engineer (plano_materializacao_pendente)<br/>Plano de Domínio + Plano de Implementação (docs/plans/implementation/)"]
    Gate1Mat --> GateCritic{"<b>Revisão Cética Pré-HITL (@plan-critic)</b><br/>Valida rubrica R-064 nos Gates 1 e 2"}
    GateCritic -- "NEEDS_REVISION (<= 2x/3x)" --> Gate1Mat
    GateCritic -- "PASS / PASS_WITH_NITS / ESCALATED_HITL" --> GateHITL{"<b>Gate Humano Obrigatório (HITL)</b><br/>ask_questions (Duplo Gate R-064)"}
    GateHITL -- "REJECTED / Replanejar" --> GateRejected["<b>Plano REJECTED</b><br/>status: REJECTED / Retorno ao planejador via @agent-router"] --> RouterHub
    GateHITL -- "APPROVED (status: APPROVED)" --> ExecStack["<b>Execução pelos Especialistas da Stack</b><br/>Despacho mediado por @agent-router"]
    ExecStack --> Sub5a["<b>Subetapa 5a: Testes & Quality Gate</b><br/>Validação determinística da suíte e contratos"]
    Sub5a -- "Falha (Autofix 5a-CB cap rígido R-053)" --> Sub5aCB["<b>Subetapa 5a-CB: Loop de Autofix</b><br/>Retorno via @agent-router ao especialista"] --> ExecStack
    Sub5a -- "Sucesso (status: REVIEW_PENDING)" --> Sub5b["<b>Subetapa 5b: Revisão de Conformidade Pós-Execução</b><br/>Handoff: revisao_conformidade_pos_execucao via @agent-router<br/>Agentes: @code-review + @security-reviewer (R-065)"]
    Sub5b -- "PASS / PASS_WITH_WARNINGS" --> PlanCompleted(["<b>Plano COMPLETED</b><br/>Encerramento via @agent-router"])
```

#### Cadeia Sequencial e Papéis:
1. **Estado 1 — Estruturação de Prompt (`@prompt-structuring`)**: Transforma pedidos abertos no formato canônico Markdown (`## Tarefa`, `## Contexto`, `## Restrições e Não-Escopo`, `## Formato de Saída Esperado`).
2. **Estado 2 — Elicitação de Requisitos (`@requirements-analyst` / `@feature-planner` — negociação do Sprint Contract — § 1.4)**: Detalha regras funcionais (BDD/EARS) e não-funcionais com critérios de aceitação objetivos, prevenindo *solution-jumping* e persistindo a especificação oficial em `docs/plans/requirements/<AAAAMMDD-HHMMSS>-<modulo>.md` (perfil Híbrido Documental sob R-056). Os critérios de aceitação aqui definidos constituem o `sprint_contract` que o Avaliador Cético do Estado 6 usará como rubrica de corte objetiva — nenhum critério pode ser adicionado ou reinterpretado retroativamente pelo Gerador (Estado 5) sem nova negociação explícita.
3. **Estado 3 — Technical Blueprint & Contratos (`@tech-solution-architect`)**:
   - Modela contratos de integração (OpenAPI v3), esquema de banco de dados (relacional ou NoSQL/Firestore/BaaS), máquina de estados e mitigação de concorrência.
   - Particionamento de escopo: isola se a demanda é **Fullstack**, **Backend-Only**, **Frontend-Only** ou **Database-Only**.
   - *Estado 3b (Checkpoint de Blueprint)*: Apresenta o blueprint estruturado e aguarda autorização humana explícita via `ask_questions` antes de iniciar qualquer codificação.
   - *Sub-rotina 3c (Decomposição de Tarefas com `@feature-planner`)*: Após aprovação do Blueprint Técnico, se a funcionalidade contiver 3 ou mais frentes de trabalho interdependentes (ex.: modelo/store + telas/diálogos + infra/push + testes), o `@feature-planner` decompõe o plano em subtasks sequenciais `[S]` e paralelas `[P]` com Definition of Done granular, evitando que o implementador improvise a ordem de execução.
   - *⚠️ Invariante de Blueprint e Decomposição Obrigatórios (R-058 / Smell 2.27)*: É terminantemente proibido pular o Estado 3 e despachar diretamente para domain routers ou especialistas de código quando a feature envolver novo schema, máquina de estados (3+ transições), concorrência ou infraestrutura/push. É expressamente vedado ao router listar lacunas de arquitetura e deixá-las para o implementador resolver no improviso.
4. **Estado 4 — Estratégia de Testes por Risco (`@test-strategy`)**: Mapeia casos de borda, matriz de risco e cobertura recomendada (mínimo 80%) antes de codificar.
4b. **Gate 2 Mandatório — Autoria do Plano de Implementação Técnica (R-064) & Revisão Cética Pré-HITL (`@plan-critic` — § 10.7)**:
   - *Autoria e Materialização Física*: O `<stack>-arch-advisor` estrutura o Plano de Implementação (Tier Full) com arquitetura técnica detalhada e allowlist de arquivos, acionando `@docs-engineer` para persistência física como `DRAFT` em `docs/plans/implementation/` (o mesmo rito R-064 aplica-se aos planos de `docs/plans/feature/`, `docs/plans/architecture/` e `docs/plans/test-strategy/` nas etapas anteriores).
   - *Revisão Cética Pré-HITL Obrigatória (`@plan-critic` — Two-Tier Hybrid Gate, ref. `invariantes-e-protocolos.md § 10.7`)*: Todo plano `DRAFT` (no Gate 1 do Estado 3b e neste Gate 2 do Estado 4b) DEVE passar pela revisão cética do `@plan-critic` (Tier 1 determinístico + Tier 2 cético Read-Only, máx. 2 rodadas; 3 em `tier: full`) antes de invocar `ask_questions`.
   - *CHECKPOINT DE APROVAÇÃO HUMANA (R-034 / R-064)*: Somente após veredito `PASS` ou `PASS_WITH_WARNINGS` do `@plan-critic` (ou `ESCALATED_HITL`), aciona-se `ask_questions` gerando `plan_ref` com `status: APPROVED` e `approved: true` antes de qualquer linha de código no Estado 5/6.
5. **Estado 5 — Implementação Domain TDD & Paridade UI (`domain routers & specialists`)**:
   - Padrão **Contract-First**: o contrato OpenAPI / DTO é a SSOT.
   - **Backend**: Execução estrita TDD (Red -> Green -> Refactor) com diffs cirúrgicos em lote (R-046).
   - **Frontend (Modelo Test-Last com Verification Gate)**: Para eliminar gargalos de runners repetitivos e mocks prematuros de DOM, a stack frontend adota **Implementation-First / Test-Last**:
     - *Estado 5a (Lógica, Store & Services)*: O `@angular-developer` constrói componentes standalone, gerência de estado reativo (Signals/NgRx) e serviços primeiro, validando compilação limpa com `get_errors`. A criação dos testes unitários/componentes de regressão é executada ao final (`Test-Last`) pelo `@angular-test-engineer` ou `@angular-test-engineer`.
     - *Estado 5b (Handoff Mandatório de Apresentação & Paridade de UI)*: Handoff obrigatório para o `@angular-developer` para validação do protocolo "Canonical Sibling First" (inspeção prévia de componente irmão canônico homologado), auditoria de design tokens (zero hex inline), classes utilitárias de layout/scroll para diálogos e verificação estrita dos inputs de componentes compartilhados em seus arquivos `.ts` (Smell 2.21). **Agentes e tarefas de UI pura/estilização são formalmente ISENTOS de criar ou rodar testes unitários de lógica** (validação é visual via Visual Feedback Loop e compilação limpa).
6. **Estado 6 (suporta Loop de Revisão de Qualidade (§ 1.5), máx. 3 iterações) — Estado 6 — Duplo Quality Gate, Segurança & PR (`@security-reviewer`, `@angular-developer`, `@code-review` e `@pr-gatekeeper` — Papel: Avaliador Cético — § 1.4)**:
   - *Sub-rotina 6a — Gate 1: Security Review (OWASP), Lógica & Contratos*: O `@security-reviewer` audita novos endpoints contra OWASP Top 10 (SQL Injection, IDOR, Broken Authentication, sanitização); validação de testes verdes e compilação limpa (`get_errors`).
   - *Gate 2 (Design System & Paridade de UI)*: Auditoria visual estrita — proibição absoluta de cores hexadecimais inline em SCSS de feature, conferência de propriedades tipadas de componentes `shared/` contra o TypeScript real (prevenindo que atributos não mapeados passem silenciosamente), alinhamento estrutural de diálogos/seções e execução de linters/scripts de auditoria visual do projeto (ex.: `npm run material:auditar`).
   - *Rubrica de Corte contra o Sprint Contract*: O `@code-review` avalia a implementação estritamente contra os critérios de aceitação (`sprint_contract`) negociados no Estado 2, registrando veredito objetivo por critério em `avaliacao_cetica` no `workflow_state` — qualquer critério `nao_atendido` reprova a entrega, sem média compensatória com os demais critérios.
   - *Loop de Revisão de Qualidade & Guard de Severidade Arquitetural (R-065 / § 10.2)*: Se o Avaliador Cético reprovar por achados táticos não-bloqueantes (`LOW`/`MEDIUM`), aplica-se o Loop de Revisão de Qualidade (`quality_review_loop`, § 1.5), teto de 3 iterações (máx. 2 iterações táticas com o implementador antes de escalonamento humano). Pelo **Guard de Severidade Arquitetural (R-065 / `invariantes-e-protocolos.md § 10.2`)**, violações estruturais `HIGH`/`CRITICAL` (quebra do Technical Blueprint, violação de Sprint Contract ou parecer bloqueante de `*-arch-advisor` / `@security-reviewer`) bloqueiam o loop tático e retornam ao `<stack>-arch-advisor` / `@tech-solution-architect` com invalidação do Gate 2.
   - O `@code-review` realiza a revisão holística de conformidade, boas práticas e **conformidade documental viva** (verificando se o diff possui impacto em `docs/`, schemas ou READMEs).
   - **Autorreflexão Documental de DoD (R-033)**: Antes de finalizar a entrega, o pipeline avalia autonomamente se a nova funcionalidade introduziu rotas, modelos de dados, componentes compartilhados ou regras de negócio, atualizando de forma automática e atômica a documentação viva do projeto (`docs/`, `README.md`, catálogo de componentes ou ADRs) sem exigir lembrete do usuário.
   - O `@pr-gatekeeper` gera a mensagem de commit semântico, descrição estruturada de PR e atualiza o CHANGELOG.md (sem push autônomo — R-031).

#### Typed State Bag (`workflow_state`):
```yaml
workflow_state:
  feature_id: "<slug-da-feature>"
  escopo_stack: "frontend_only | backend_only | fullstack"
  requisitos_doc: "docs/plans/requirements/<AAAAMMDD-HHMMSS>-<feature>.md"
  blueprint:
    contrato_openapi: "<caminho/openapi.yaml ou inline>"
    tabelas_banco: ["<tabela_a>", "<tabela_b>"]
    exige_migracao_ddl: false
    tasks_backend:
      - descricao: "Task 1"
        stack: "spring-boot | spring-reactive | ejb"
    tasks_frontend: ["Task 1", "Task 2"]
  matriz_riscos_testes:
    casos_borda: ["Payload vazio", "Timeout", "Duplicidade"]
    casos_borda_seguranca: ["SQL injection", "IDOR", "Auth bypass"]
    threshold_aplicavel: "90 (critico) | 80 (integracao) | 70 (controller)"
  tentativas_remediacao_seguranca: 0  # teto: 2 (Estado 6b)
  status_implementacao:
    backend_concluido: true
    frontend_concluido: true
  security_gate_status: "aprovado | vulnerabilidade_detectada"
  sprint_contract:  # negociado no Estado 2 (Gerador), avaliado no Estado 6 (Avaliador Cético — § 1.4)
    criterios_aceite:
      - "<criterio de aceitacao funcional ou nao-funcional>"
    forma_verificacao: "<teste automatizado, checklist visual ou script de auditoria>"
  avaliacao_cetica:  # preenchido pelo Avaliador (@code-review) no Estado 6
    criterios_avaliados:
      - criterio: "<mesmo criterio do sprint_contract>"
        veredito: "atendido | nao_atendido"
    veredito_final: "aprovado | reprovado"
```

---

> **Diretórios Canônicos de Persistência R-064 (`docs/plans/<tipo>/`)**: Gate 1 (`plan_type: feature`) em `docs/plans/feature/` (e `docs/plans/requirements/` para requisitos, `docs/plans/architecture/` para arquitetura, `docs/plans/test-strategy/` para estratégia de testes); Gate 2 (`plan_type: implementation`) em `docs/plans/implementation/`. Agentes planejadores/advisors permanecem 100% Read-Only (com `author` preservando o autor intelectual real do plano e proibição de `@tech-solution-architect` materializar docs no `WORKFLOW-BUG-FIX`), delegando a escrita física do `.md` a `@docs-engineer` / `@governance-maintainer` antes da aprovação humana (`status: APPROVED`, `approved: true`, `allowed_files`).

- **Quality Gate Pós-Execução de Conformidade com o Plano (`plan-conformance-patterns` N1/N2/N3 — R-064 / `invariantes-e-protocolos.md § 10.9`)**: Na etapa de Revisão / Quality Gate pós-implementação (acionada via handoff `motivo: "revisao_conformidade_pos_execucao"` com o plano em `status: "REVIEW_PENDING"`), o `@code-review` (Read-Only, Agency Score 0 — em conjunto com `@security-reviewer` e `@adr-sentinel` quando aplicável) DEVE auditar obrigatoriamente o diff implementado contra o `active_plan_ref` nos níveis **N1** (respeito estrito a `allowed_files` e frontmatter R-064), **N2** (completude 1:1 da Matriz De-Para, requisitos EARS `REQ-NN` e tasks) e **N3** (aderência semântica, contratos arquiteturais e R-065). O fluxo só transiciona para `status: "COMPLETED"` mediante registro de `post_exec_review_verdict` (`PASS` ou `PASS_WITH_WARNINGS`), `post_exec_reviewer: "@code-review"` e `post_exec_reviewed_at`; em caso de `FAIL`, retorna ao developer executor via `motivo: "conformidade_reprovada_retorno_execucao"` (teto de 2 rodadas antes de escalonamento HITL via `ask_questions`).
