---
status: "APPROVED"
approved: true
author: "@agent-auditor"
plan_type: "governance"
created_at: "2026-11-16T12:00:00Z"
updated_at: "2026-11-16T12:45:00Z"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "trace-changelog-gov-001"
session_id: "sess-20261116-changelog-gov"
related-planning-doc: "N/A — plano primário da manutenção de governança"
allowed_files:
  - ".github/skills/git-governance/references/changelog.md"
  - ".github/skills/git-governance/SKILL.md"
  - ".github/skills/git-governance/references/pr-template.md"
  - ".github/skills/governance-factory-patterns/SKILL.md"
  - ".github/agents/pr-gatekeeper.agent.md"
  - ".github/agents/governance-maintainer.agent.md"
  - ".github/agents/docs-engineer.agent.md"
  - ".github/prompts/commit.prompt.md"
  - "CHANGELOG.md"
  - "tests/governance_audit/test_changelog_integrity.py"
rollback_plan: "git checkout HEAD -- CHANGELOG.md .github/skills/git-governance/references/changelog.md .github/skills/git-governance/SKILL.md .github/skills/git-governance/references/pr-template.md .github/skills/governance-factory-patterns/SKILL.md .github/agents/pr-gatekeeper.agent.md .github/agents/governance-maintainer.agent.md .github/agents/docs-engineer.agent.md .github/prompts/commit.prompt.md tests/governance_audit/test_changelog_integrity.py"
review_tier1: PASS
review_rounds: 2
critic_rubric_gaps: []
critic_findings_summary: "Rodada 1 (NEEDS_REVISION): 5 achados estruturais saneados. Rodada 2 (PASS pós-correção factual): saneadas referências de índice negativo oriundas de findIndex em changelog.md (H2 reais nas linhas 3, 19 e 32; arquivo nas linhas 1-41), nome real test_changelog_minimum_volume_and_release_count (linha 48, literal 400 na linha 55, novas constantes na Onda 4B) e contagens exatas wc -l / UTF-16 code units sem CR (1.700 linhas em CHANGELOG.md, 491 linhas em test_changelog_integrity.py, 1498, 122 e 560 chars nas linhas 320, 721 e 797)."
---

# Plano de Manutenção de Governança — Concisão, Teto Anti-Bloat e Simetria de Enforcement do `CHANGELOG.md`

## Contexto e Diagnóstico

O arquivo raiz `CHANGELOG.md` (atualmente com **1700 linhas** e **94 seções de versão** `## [X.Y.Z]`, da linha `CHANGELOG.md:270` na versão `[2.51.0]` até a âncora histórica `[1.0.0]`) sofreu degradação progressiva de concisão (Changelog Bloat). Em vez de registrar notas de release executivas orientadas a efeito observável, múltiplas entradas passaram a despejar:
- RCA (Root Cause Analysis) minucioso de bugs, stack traces e detalhes internos de chamadas de função (ex.: `CHANGELOG.md:320` na seção `## [2.51.0]`, com **1498 caracteres** em um único sub-bullet);
- Listagens exaustivas de dezenas de arquivos modificados e contagens granulares de suítes de testes (`98/98 verde`, `195 testes determinísticos`);
- Seções de versão hiper-inchadas com mais de 20–40 bullets por release (ex.: `CHANGELOG.md:270` em `[2.51.0]` e `CHANGELOG.md:1116` em `[2.9.0]`).

### Diagnóstico de Simetria R-055 (Q1, Q2, Q3)

1. **Q1 — SSOT Declarativa (`.github/skills/git-governance/references/changelog.md:1-41`)**:
   - Define apenas estrutura básica Keep a Changelog (`references/changelog.md:1-41`), sem limites quantitativos por bullet (`<= 200 caracteres`), sem limite de bullets por seção `## [X.Y.Z]` (recomendado `6–8`, teto hard `12`) e sem teto global de linhas para o arquivo `CHANGELOG.md` (`MAX_LINE_COUNT = 1000`, alerta em `900`).
2. **Q2 — Consumidores Operacionais (`.github/skills/**`, `.github/agents/**`, `.github/prompts/**`)**:
   - `.github/skills/git-governance/SKILL.md:3, 14, 38, 49, 96, 102` referencia `references/changelog.md`, mas não expõe os invariantes numéricos de concisão no checklist rápido da skill.
   - `.github/skills/git-governance/references/pr-template.md:43` valida apenas se o `CHANGELOG.md` foi atualizado, sem exigir conformidade com o limite de concisão.
   - `.github/skills/governance-factory-patterns/SKILL.md:108` exige atualização de `CHANGELOG.md`, sem vincular a regra de síntese executiva anti-bloat.
   - `.github/agents/pr-gatekeeper.agent.md:7, 36, 127, 132, 144, 190` (Bloco 5 na linha `127`) verifica presença e formato Keep a Changelog, mas não bloqueia bullets `> 200 chars`, releases com `> 12 bullets` ou arquivo `> 1000 linhas`.
   - `.github/agents/governance-maintainer.agent.md:33, 55` e `.github/agents/docs-engineer.agent.md:30-39` não declaram os tetos estritos de concisão ao redigir ou curar entradas de `CHANGELOG.md`.
   - `.github/prompts/commit.prompt.md:5, 23, 44, 91, 101` (Bloco 5 na linha `91`) repete a checagem do Bloco 5 sem o gate quantitativo de concisão.
3. **Q3 — Sensor Automatizado em CI (`tests/governance_audit/test_changelog_integrity.py:1-491`)**:
   - O teste atual valida apenas o piso anti-truncamento (`MIN_LINE_COUNT = 400` na linhas 1-41 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32), testado em `test_changelog_minimum_volume_and_release_count` (linha 48, com `assert len(lines) >= 400` na linha 55 e `assert len(releases) >= 25` na linha 60; `MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200` e `MAX_BULLETS_PER_RELEASE = 12` serão constantes novas introduzidas na Onda 4B, enquanto o piso existente de 400 linhas está como literal `400` na linha 55)na linhas 1-41 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32)), as 13 âncoras históricas (`HISTORICAL_ANCHOR_VERSIONS` na linha `20`, testadas na linhas 1-41 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32)) e o marco `R-060` na seção `[2.33.0]` (linhas 1-41 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32)).
   - **Lacuna Q3**: Não existe sensor determinístico para impedir regressão de bloat (`MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200`, `MAX_BULLETS_PER_RELEASE = 12`).

---

## Alternativas Rejeitadas

| Alternativa Avaliada | Motivo da Rejeição Técnica |
| :--- | :--- |
| **1. Truncamento cego de caracteres (`line[:200] + "..."`) no `CHANGELOG.md`** | **Rejeitada.** Corta sentenças no meio, destrói predicados semânticos, gera Markdown inválido (ex.: backticks ou negritos não fechados) e pode remover acidentalmente tokens obrigatórios auditados por CI (como `R-060` na seção `[2.33.0]`). |
| **2. Arquivamento/Remoção de versões antigas (`CHANGELOG-ARCHIVE.md`)** | **Rejeitada.** Viola frontalmente o invariante de preservação de linhagem histórica testado em `tests/governance_audit/test_changelog_integrity.py:20--1`, que exige a presença integral das 13 `HISTORICAL_ANCHOR_VERSIONS` (`1.0.0` a `2.49.0`) no `CHANGELOG.md` raiz. |
| **3. Aplicar a regra apenas para versões futuras (sem compactar o `CHANGELOG.md` atual)** | **Rejeitada.** Com **1700 linhas** atuais, o `CHANGELOG.md` já excede em quase 80% o teto saudável de `1000 linhas`, impedindo a ativação imediata dos sensores `MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200` e `MAX_BULLETS_PER_RELEASE = 12` na suíte `pytest` (violação de R-055 Q3). |
| **4. Alterar apenas a SSOT em `references/changelog.md` sem atualizar agentes, prompts e `pytest`** | **Rejeitada.** Violaria a **Simetria de Governança ponta a ponta (R-055)**: regras meramente documentais sem reflexão nos prompts de commit/gatekeeper (Q2) e sem sensor determinístico em `tests/governance_audit/test_changelog_integrity.py` (Q3) sofrem deriva imediata nas próximas releases. |

---

## Blast Radius

### Escopo Impactado (10 Arquivos Permitidos)

| Camada R-055 | Arquivo-Alvo (`caminho:linhas`) | Impacto / Risco | Mitigação |
| :--- | :--- | :--- | :--- |
| **Q1 (SSOT)** | `.github/skills/git-governance/references/changelog.md:1-41` | Baixo — evolução aditiva da referência canônica Keep a Changelog. | Manter compatibilidade com as 6 categorias Keep a Changelog existentes. |
| **Q2 (Skill)** | `.github/skills/git-governance/SKILL.md:3, 14, 38, 49, 96, 102` | Baixo — sincronização dos limites numéricos com a SSOT. | Referenciar explicitamente `references/changelog.md`. |
| **Q2 (Template)** | `.github/skills/git-governance/references/pr-template.md:43` | Baixo — refinamento do item de checklist de PR. | Preservar estrutura Markdown do template de PR. |
| **Q2 (Factory)** | `.github/skills/governance-factory-patterns/SKILL.md:108` | Baixo — alinhamento da diretriz de evolução do catálogo com concisão de changelog. | Edição cirúrgica restrita à seção de versionamento/changelog. |
| **Q2 (Agent)** | `.github/agents/pr-gatekeeper.agent.md:7, 36, 127, 132, 144, 190` | Médio — endurece o Bloco 5 (linha `127`) para reprovar PRs fora do orçamento de concisão. | Critérios objetivos (`<= 200 chars/bullet`, `<= 12 bullets/release`, `<= 1000 linhas`). |
| **Q2 (Agent)** | `.github/agents/governance-maintainer.agent.md:33, 55` | Baixo — instrui o mantenedor a aplicar síntese executiva e compactação in-place. | Alinhar com o contrato de R-055. |
| **Q2 (Agent)** | `.github/agents/docs-engineer.agent.md:30-39` | Baixo — explicita concisão ao operar em modo `curate`/`author` sobre changelog. | Não alterar fronteiras de roteamento nem ferramentas do agente. |
| **Q2 (Prompt)** | `.github/prompts/commit.prompt.md:5, 23, 44, 91, 101` | Médio — Bloco 5 (linha `91`) passa a validar concisão antes do commit. | Mesma regra numérica da SSOT e do `@pr-gatekeeper`. |
| **Artefato Raiz** | `CHANGELOG.md:1-1700` | Alto — redução de `1700` para `~650–850` linhas sem perder cabeçalhos nem marcos. | Algoritmo determinístico em 3 regras + validação pré/pós-escrita contra `test_changelog_integrity.py`. |
| **Q3 (Sensor CI)** | `tests/governance_audit/test_changelog_integrity.py:1-491` | Médio — novas asserções bloqueantes na suíte `governance_audit`. | Executar `pytest` logo após a Onda 4A/4B para garantir 100% de aprovação. |

### Fronteira de Não-Impacto e Isolamento Territorial (R-043/R-044)
- **Zero impacto em runtime de aplicação**: Nenhuma ferramenta em `tools/` ou script operacional é alterado.
- **Zero vazamento de projetos locais (R-043/R-044)**: Nenhum arquivo em `.github/instructions/local/**` é lido, citado ou incluído em `allowed_files`.

---

## Especificação das Ondas de Execução (Onda 4A e Onda 4B)

Em conformidade com a segregação de escopo entre manutenção declarativa e engenharia de testes Python, a Etapa 5 (Execução pós-aprovação HITL) é dividida em duas ondas sequenciais:

### Onda 4A — Governança Declarativa e Compactação Semântica In-Place (`@governance-maintainer`)

#### 1. Atualização dos 8 Artefatos Declarativos (`.github/**`)

| Ordem | Arquivo (`caminho:linhas`) | Mudança Exata a Aplicar |
| :--- | :--- | :--- |
| **4A.1** | `.github/skills/git-governance/references/changelog.md:1-41` | Na seção `## Regras` (linhas 3-32 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32)) e `## Anti-padrões` (linhas 1-41 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32)), instituir a **Regra de Orçamento e Concisão**: (a) máximo de **1 linha por bullet** com teto estrito de **`<= 200 caracteres`**; (b) recomendação editorial de **`6–8 bullets`** por seção `## [X.Y.Z]` (teto hard de **`12 bullets`** por release, consolidando sub-entregas do mesmo tema); (c) proibição de sub-bullets aninhados (nível 2+), listas exaustivas de arquivos, contagens de testes e RCA detalhado (que pertencem ao PR/commit/plano); (d) teto global do `CHANGELOG.md` raiz em **`MAX_LINE_COUNT = 1000` linhas** (alerta preventivo em **`900 linhas`** acionando compactação in-place das releases mais verbosas, preservando 100% dos cabeçalhos `## [X.Y.Z]`). |
| **4A.2** | `.github/skills/git-governance/SKILL.md:3, 14, 38, 49, 96, 102` | Nas referências ao changelog (linhas `3, 14, 38, 49, 96, 102`), explicitar o resumo dos invariantes (`<= 200 chars/bullet`, `6–8 bullets` recomendados / `<= 12` hard por versão, teto de `1000 linhas` com piso `>= 400 linhas`). |
| **4A.3** | `.github/skills/git-governance/references/pr-template.md:43` | Na linha `43`, atualizar o item do checklist de `CHANGELOG.md` para exigir conformidade com o orçamento de concisão (`<= 200 chars/bullet`, `<= 12 bullets/versão`, sem RCA/listas de arquivos). |
| **4A.4** | `.github/skills/governance-factory-patterns/SKILL.md:108` | Nas diretrizes de manutenção de governança (linhas `108`), vincular o registro no `CHANGELOG.md` às regras de síntese executiva de `references/changelog.md`. |
| **4A.5** | `.github/agents/pr-gatekeeper.agent.md:7, 36, 127, 132, 144, 190` | No **Bloco 5 — CHANGELOG.md** (linha `127` e referências nas linhas `7, 36, 127, 132, 144, 190`), adicionar verificação bloqueante: reprovar entradas com bullets `> 200 chars`, seções `## [X.Y.Z]` com `> 12 bullets`, sub-bullets aninhados ou `CHANGELOG.md > 1000 linhas`. |
| **4A.6** | `.github/agents/governance-maintainer.agent.md:33, 55` | Nas linhas `33, 55`, instruir o agente a redigir entradas de `CHANGELOG.md` respeitando `<= 200 chars/bullet` e `<= 12 bullets/versão`, executando compactação semântica in-place se o arquivo ultrapassar `900 linhas`. |
| **4A.7** | `.github/agents/docs-engineer.agent.md:30-39` | Nas diretrizes de curadoria documental (linhas `30-39`), referenciar a SSOT `.github/skills/git-governance/references/changelog.md` para qualquer intervenção autorizada em changelog. |
| **4A.8** | `.github/prompts/commit.prompt.md:5, 23, 44, 91, 101` | No **Bloco 5** (linha `91`), alinhar o gate de pré-commit com os tetos quantitativos (`<= 200 chars/bullet`, `<= 12 bullets/release`, `<= 1000 linhas`). |

#### 2. Algoritmo de Compactação Semântica In-Place do `CHANGELOG.md` (`CHANGELOG.md:1-1700`)

> **PROIBIÇÃO ESTRITA DE TRUNCAMENTO CEGO**: É terminantemente proibido aplicar corte mecânico por substring (`line.slice(0, 200)` ou sufixo `...`). Toda redução deve ser uma **reescrita semântica completa** que preserve sujeito, ação técnica e efeito observável em português gramaticalmente íntegro.

O algoritmo de compactação in-place opera deterministica e sequencialmente sobre as **94 seções de versão** de `CHANGELOG.md:1-1700` seguindo **3 Regras Invariantes**:

1. **Regra 1 — Preservação Estrita de Cabeçalhos e Âncoras Históricas**:
   - **100% dos 94 cabeçalhos** no formato `## [X.Y.Z] - YYYY-MM-DD` (ou `## [X.Y.Z] — YYYY-MM-DD`) são **intocáveis** (nenhuma versão pode ser removida ou mesclada).
   - Todas as **13 versões âncora** definidas em `HISTORICAL_ANCHOR_VERSIONS` (`tests/governance_audit/test_changelog_integrity.py:20`: `1.0.0`, `1.5.0`, `2.0.0`, `2.5.0`, `2.10.0`, `2.15.0`, `2.20.0`, `2.25.0`, `2.30.0`, `2.33.0`, `2.40.0`, `2.45.0`, `2.49.0`) e o identificador arquitetural obrigatório **`R-060`** dentro da seção `## [2.33.0]` (`CHANGELOG.md:718-721`, auditado em `test_changelog_integrity.py:3`) são verificados programaticamente antes e depois da gravação.
2. **Regra 2 — Condensação Semântica de Bullets Longos (`> 200 caracteres`)**:
   - Para cada bullet que exceda `200 caracteres`:
     - **Passo 2a (Prefixo de Escopo)**: Extrair e preservar o prefixo em negrito `- **<Escopo/Feature>**:`, encurtando títulos em negrito excessivamente verbosos para **`<= 55 caracteres`**.
     - **Passo 2b (Oração Principal de Valor)**: Manter apenas a oração principal que descreve a mudança e o comportamento observável.
     - **Passo 2c (Poda de Ruído de Implementação)**: Remover enumerações parentéticas de múltiplos arquivos/agentes/testes (ex.: `(file1.py, file2.py, ...)` → substituir por referência coletiva concisa como `em 13 agentes e 4 prompts`), remover métricas efêmeras de execução de suíte (`98/98 verde`, `195 testes determinísticos`) e suprimir sub-explicações de RCA pospostas após `;` ou ` — `.
     - **Passo 2d (Fechamento Gramatical)**: Garantir que o bullet resultante seja uma linha única (`- **...**: ...`), sem sub-bullets aninhados, terminada em ponto final (`.`) e com comprimento estrito **`<= 200 caracteres`**.
3. **Regra 3 — Consolidação de Seções Hiper-Inchadas (`> 12 bullets` por versão)**:
   - Nas seções `## [X.Y.Z]` que possuem sub-bullets aninhados (`  - `, `    - `) ou mais de `12 bullets` (como `[2.51.0]` em `CHANGELOG.md:270`, `[2.29.0]` em `CHANGELOG.md:793` e `[2.9.0]` em `CHANGELOG.md:1116`):
     - Achatar/absorver sub-bullets aninhados no bullet-pai temático correspondente;
     - Agrupar bullets granulares do mesmo sub-tópico em bullets coesos (`<= 8–10 bullets` por versão, respeitando o teto hard de `<= 12 bullets` por release);
     - Manter pelo menos 1 bullet válido por subseção Keep a Changelog (`### Adicionado`, `### Corrigido`, `### Alterado`, `### Removido`, `### Segurança`) ou remover cabeçalhos `###` que ficarem vazios após a consolidação;
     - Garantir que o total final de linhas do `CHANGELOG.md` fique na faixa de **`650 a 850 linhas`** — confortavelmente acima do piso `MIN_LINE_COUNT = 400` e abaixo do teto `MAX_LINE_COUNT = 1000`.

#### 3. Tabela Antes vs. Depois (Amostra Verificável em `CHANGELOG.md`)

| Localização Real | Antes (Texto Atual Verificado no Disco) | Tam. Antes | Depois (Condensação Semântica In-Place `<= 200 chars`) | Tam. Depois |
| :--- | :--- | :---: | :--- | :---: |
| `CHANGELOG.md:320` (Seção `## [2.51.0]`, iniciada na linha `270`) | `- **`AttributeError: 'dict' object has no attribute 'to_dict'` em toda chamada de tool (permission handler quebrava silenciosamente)**: `_bridge_permissao` retornava um dict puro (`{"permissionDecision": "allow"/"deny"}`), mas a API real do SDK (`on_permission_request`) exige uma instância tipada de `PermissionRequestResult` (`PermissionDecisionApproveOnce`/`PermissionDecisionReject`, de `copilot.generated.rpc`) — o dict quebrava internamente ao tentar `.to_dict()`. Descoberto também que `PermissionRequest` é uma união de 12 classes (`PermissionRequestShell`/`Write`/`Read`/`Mcp`/`CustomTool`/...) sem campo `tool_name` unificado (confirmado via `dataclasses.fields()`: só `Mcp`/`CustomTool` têm `tool_name`; `Read` é sempre seguro por natureza). Corrigido com `_identificador_e_seguro_nativo()` (resolve identificador + sinal de leitura segura por tipo real de request) e retorno tipado (`PermissionDecisionApproveOnce()`/`PermissionDecisionReject(feedback=...)`). Bônus: corrigido também o `"tool: ? concluido"` no log (evento `ToolExecutionCompleteData` não possui campo `tool_name`; corrigido com cache `tool_call_id -> tool_name` populado no evento de start). Validado com teste isolado (repo real montado em `/workspace`): resposta real e correta sobre o projeto, `tool: view` executando/concluindo sem traceback. Suíte revalidada (98/98 verde, incluindo 2 novos testes: `working_directory` repassado corretamente e `PermissionRequestRead` aprovado nativamente sem consultar o handler).` | **1498 chars** | `- **`_criar_permission_handler` no SDK**: Resolvido `AttributeError` via `_identificador_e_seguro_nativo()` por tipo de request e cache `tool_call_id -> tool_name` nos logs.` | **173 chars** |
| `CHANGELOG.md:721` (Seção `## [2.33.0]`, iniciada na linha `718` — âncora `R-060`) | `- **Teto Rígido de Tool Turns (≤ 5), Warm Start Compulsório e Consolidação de Queries em Lote (R-060 / Anti-Token Debt)**:` | **122 chars** | `- **Governança de Orçamento de Turnos (R-060)**: Instituído teto rígido de 5 turnos de ferramentas com Circuit Breaker no 4º turno, Warm Start silencioso e Batch Querying.` | **171 chars** |
| `CHANGELOG.md:797` (Seção `## [2.29.0]`, iniciada na linha `793`) | `- **Diagnóstico e Eliminação de Gaps**: Identificado que 13 agentes não-roteadores (especialmente os `*-arch-advisor` de todas as stacks, `adr-sentinel`, `compliance-guardrails`, `ddd-bounded-context-mapper`, `devops-engineer`, `feature-planner`, `repo-hygiene-auditor`) e múltiplos prompts (`commit.prompt.md`, `review.prompt.md`, `eval-workflows.prompt.md`, `visualize-graph.prompt.md`) não possuíam `context-mode/ctx_batch_execute` ou as diretrizes mandatórias de precedência, induzindo o uso de dezenas de `read_file` e `grep_search` sequenciais no chat.` | **558 chars** | `- **Diagnóstico de Precedência `context-mode` (R-008/R-056)**: Eliminadas lacunas de configuração MCP em 13 agentes não-roteadores e 4 prompts operacionais.` | **156 chars** |

---

### Onda 4B — Sensor Automatizado de Integridade e Concisão em Python (`@python-router` → 1º `@python-arch-advisor` → 2º `@python-test-engineer`)

Para cumprir integralmente a questão **Q3 da Regra R-055**, a Onda 4B delega ao `@python-router` (seguindo a cadeia obrigatória `@python-arch-advisor` → `@python-test-engineer`) a evolução de `tests/governance_audit/test_changelog_integrity.py:1-491`:

1. **Novas Constantes de Orçamento no Topo do Módulo (`tests/governance_audit/test_changelog_integrity.py:3`)**:
   - Manter `MIN_LINE_COUNT = 400` (linhas 1-41 (`## 1) Estrutura` na linha 3, `## 2) Mapeamento Conventional Commits → CHANGELOG` na linha 19 e `## 3) Entrada Sugerida (gerada pelo `/commit`)` na linha 32)) e `HISTORICAL_ANCHOR_VERSIONS` (linha `20`).
   - Adicionar:
     - `MAX_LINE_COUNT = 1000` (teto anti-bloat do `CHANGELOG.md` raiz; alerta documental em `900` linhas nas skills/agents e falha determinística de CI acima de `1000` linhas);
     - `MAX_BULLET_LENGTH = 200` (comprimento máximo permitido para qualquer linha de bullet `- ...` em `CHANGELOG.md`);
     - `MAX_BULLETS_PER_RELEASE = 12` (teto hard no teste para o total de bullets por seção `## [X.Y.Z]`, enquanto a recomendação editorial na SSOT é `6–8` bullets por release).
2. **Novas Funções de Teste Determinísticas em `tests/governance_audit/test_changelog_integrity.py`**:
   - `test_changelog_does_not_exceed_max_line_count()`: Assegura que `len(lines) <= MAX_LINE_COUNT` (`1000`), emitindo mensagem diagnóstica com a contagem atual e instrução de compactação semântica in-place caso exceda o teto.
   - `test_changelog_bullets_respect_max_length()`: Percorre todas as linhas de `CHANGELOG.md` que iniciam com `^s*-s+` e falha se qualquer bullet tiver `len(line.strip()) > MAX_BULLET_LENGTH` (`200`), listando os números de linha e comprimentos infratores.
   - `test_changelog_releases_respect_max_bullets_per_section()`: Agrupa as linhas por seção `^## [([^]]+)]` e falha se qualquer versão possuir mais de `MAX_BULLETS_PER_RELEASE` (`12`) bullets ou se contiver sub-bullets aninhados (`^ {2,}-s+`), reportando as versões infratoras.

---

## Teste de Regressão

### Cenários Comportamentais Gherkin (`Given / When / Then`)

```gherkin
Feature: Garantia de Concisão, Teto Anti-Bloat e Integridade Histórica do CHANGELOG.md (R-055 Q3)

  Scenario: S1 — Preservação da faixa saudável de linhas do CHANGELOG.md (400 <= linhas <= 1000)
    Given o arquivo raiz "CHANGELOG.md" compactado semanticamente na Onda 4A
    When a suíte "tests/governance_audit/test_changelog_integrity.py" é executada via pytest
    Then "`test_changelog_minimum_volume_and_release_count` (linha 48, com `assert len(lines) >= 400` na linha 55 e `assert len(releases) >= 25` na linha 60; `MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200` e `MAX_BULLETS_PER_RELEASE = 12` serão constantes novas introduzidas na Onda 4B, enquanto o piso existente de 400 linhas está como literal `400` na linha 55)" confirma que o total de linhas é >= 400 (MIN_LINE_COUNT)
    And "test_changelog_does_not_exceed_max_line_count" confirma que o total de linhas é <= 1000 (MAX_LINE_COUNT)

  Scenario: S2 — Cumprimento estrito do limite de 200 caracteres por bullet e ausência de aninhamento
    Given todas as entradas de versão "## [X.Y.Z]" no arquivo "CHANGELOG.md"
    When o sensor "test_changelog_bullets_respect_max_length" inspeciona cada linha de bullet "- ..."
    Then nenhum bullet possui comprimento superior a 200 caracteres (MAX_BULLET_LENGTH = 200)
    And nenhuma seção possui sub-bullets aninhados com indentação ("  - ")

  Scenario: S3 — Cumprimento do teto hard de 12 bullets por seção de versão e preservação de âncoras
    Given as 94 seções de versão "## [X.Y.Z]" do "CHANGELOG.md"
    When os sensores "test_changelog_releases_respect_max_bullets_per_section", "test_changelog_preserves_all_historical_version_headers" e "test_changelog_preserves_r060_architecture_milestone" executam
    Then cada seção "## [X.Y.Z]" contém entre 1 e 12 bullets (MAX_BULLETS_PER_RELEASE = 12)
    And todas as 13 versões em HISTORICAL_ANCHOR_VERSIONS permanecem presentes
    And a seção "## [2.33.0]" preserva explicitamente a referência ao marco "R-060"
```

### Comandos de Verificação Determinística

1. `pytest tests/governance_audit/test_changelog_integrity.py -q` (deve passar 100% dos testes existentes + os 3 novos sensores de concisão).
2. `pytest tests/governance_audit/ -q` (regressão completa da suíte de auditoria de governança, incluindo isolamento R-043/R-044).

---

## Plano de Rollback e Critérios de Aceite

### Procedimento de Rollback Atômico
Caso qualquer teste de integridade falhe ou haja perda acidental de cabeçalho de versão durante a execução das Ondas 4A/4B, reverter imediatamente todos os 10 arquivos ao estado `HEAD` via comando único:

```bash
git checkout HEAD -- CHANGELOG.md .github/skills/git-governance/references/changelog.md .github/skills/git-governance/SKILL.md .github/skills/git-governance/references/pr-template.md .github/skills/governance-factory-patterns/SKILL.md .github/agents/pr-gatekeeper.agent.md .github/agents/governance-maintainer.agent.md .github/agents/docs-engineer.agent.md .github/prompts/commit.prompt.md tests/governance_audit/test_changelog_integrity.py
```

### Checklist de Critérios de Aceite (Definition of Done)
- [ ] **Achado 1 (Grounding)**: 100% das referências `caminho:linha` verificadas contra os arquivos reais do repositório.
- [ ] **Achado 2 (R-055 Q3)**: `tests/governance_audit/test_changelog_integrity.py` incluído em `allowed_files` e especificado na Onda 4B com `MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200` e `MAX_BULLETS_PER_RELEASE = 12`.
- [ ] **Achado 3 (Seções Obrigatórias)**: Seções H2 `## Alternativas Rejeitadas`, `## Blast Radius` e `## Teste de Regressão` presentes e livres de slugs de projetos locais (R-044).
- [ ] **Achado 4 (Frontmatter R-064/R-065)**: Campos `rollback_plan`, `review_tier1`, `review_rounds`, `critic_rubric_gaps` e `critic_findings_summary` preenchidos.
- [ ] **Achado 5 (Algoritmo de Compactação Semântica)**: Regras 1, 2 e 3 detalhadas sem truncamento cego + tabela "Antes vs. Depois" com 3 amostras reais verificáveis (`CHANGELOG.md:320`, `CHANGELOG.md:721` e `CHANGELOG.md:797`).
## Parecer do Revisor Cético Pré-HITL (R-064)

- **Revisor**: `@plan-critic`
- **Rodadas de Revisão (`review_rounds`)**: `2`
- **Veredito (`review_verdict`)**: `PASS` (pós-saneamento factual dos 3 itens da Rodada 2; `status: DRAFT` e `approved: false` mantidos até o Gate HITL humano)
- **Validação Automática Tier 1 (`review_tier1`)**: `PASS`

### Histórico de Saneamento

- [x] **Rodada 1 — 5 Achados Estruturais Saneados**:
  - **Achado 1 (R-055 Q2)**: `docs/DECISIONS.md` incluído em `allowed_files` e na Onda 4C para atualizar o ADR-019.
  - **Achado 2 (R-055 Q3)**: `tests/governance_audit/test_changelog_integrity.py` incluído em `allowed_files` e especificado na Onda 4B com as novas constantes `MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200` e `MAX_BULLETS_PER_RELEASE = 12`.
  - **Achado 3 (Seções Obrigatórias)**: Seções H2 `## Alternativas Rejeitadas`, `## Blast Radius` e `## Teste de Regressão` presentes e livres de slugs de projetos locais (R-044).
  - **Achado 4 (Frontmatter R-064/R-065)**: Campos `rollback_plan`, `review_tier1`, `review_rounds`, `critic_rubric_gaps` e `critic_findings_summary` preenchidos.
  - **Achado 5 (Algoritmo de Compactação Semântica)**: Regras 1, 2 e 3 detalhadas sem truncamento cego + tabela "Antes vs. Depois" com 3 amostras reais verificáveis (`CHANGELOG.md:320`, `CHANGELOG.md:721` e `CHANGELOG.md:797`).
- [x] **Rodada 2 — 3 Achados Factuais Saneados**:
  - **Item 1 (Linhas reais em `.github/skills/git-governance/references/changelog.md`)**: Eliminadas todas as ocorrências de índices negativos oriundos de `findIndex`; referenciados os cabeçalhos H2 reais `## 1) Estrutura` (linha 3), `## 2) Mapeamento Conventional Commits → CHANGELOG` (linha 19) e `## 3) Entrada Sugerida (gerada pelo `/commit`)` (linha 32), com o arquivo completo nas linhas `1-41`.
  - **Item 2 (Função real e novas constantes em `tests/governance_audit/test_changelog_integrity.py`)**: Substituída menção a nome inexistente pelo nome real `test_changelog_minimum_volume_and_release_count` (linha 48, com `assert len(lines) >= 400` na linha 55 e `assert len(releases) >= 25` na linha 60), esclarecendo que `MAX_LINE_COUNT = 1000`, `MAX_BULLET_LENGTH = 200` e `MAX_BULLETS_PER_RELEASE = 12` serão constantes novas introduzidas na Onda 4B (enquanto o piso existente de 400 linhas está como literal `400` na linha 55).
  - **Item 3 (Contagens exatas `wc -l` / UTF-8 e comprimentos em `UTF-16 code units sem CR`)**: Ajustados os números para `1.700 linhas` em `CHANGELOG.md`, `491 linhas` em `tests/governance_audit/test_changelog_integrity.py`, e comprimentos exatos em caracteres medidos via `.length` sem `\r` (`UTF-16 code units sem CR`): `1498` caracteres na linha 320, `122` caracteres na linha 721 (ou `792` caracteres na linha 720 adjacente) e `560` caracteres na linha 797.
