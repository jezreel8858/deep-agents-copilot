---
status: approved
approved_by: "aprovado por humano em 2026-10-08 via ask_questions (H1–H6)"
date: 2026-10-08
autor: angular-arch-advisor
workflow: workflow-governance-maintenance (cria workflow-ui-layout)
related-planning-doc: "N/A — plano único de governança" # R-064: plano único de governança, sem doc em docs/plans aplicável
tier: full
reversibility: T2
plan_ref: docs/implementation-plans/20261008-governance-maintenance-playwright-mcp-frontend-consolidation.md
allowed_files:
  - .github/skills/playwright-mcp/SKILL.md
  - .github/skills/frontend-visual-feedback-loop/SKILL.md
  - .github/skills/frontend-visual-feedback-loop/references/**
  - .github/skills/.index.json
  - .github/agents/frontend/angular/angular-arch-advisor.agent.md
  - .github/agents/frontend/angular/angular-developer.agent.md
  - .github/agents/frontend/angular/angular-test-engineer.agent.md
  - .github/agents/frontend/angular/angular-router.agent.md
  - .github/agents/frontend/angular/angular-catalog.yaml
  - .github/agents/frontend/react/react-arch-advisor.agent.md
  - .github/agents/frontend/react/react-developer.agent.md
  - .github/agents/frontend/react/react-test-engineer.agent.md
  - .github/agents/frontend/react/react-router.agent.md
  - .github/agents/frontend/react/react-catalog.yaml
  - .github/agents/catalog.yaml
  - .github/agents/routing-graph.yaml
  - .github/agents/workflows.md
  - .github/agents/workflows/workflow-ui-layout.md
  - .a2a/agentcards/angular-developer.agentcard.json
  - .a2a/agentcards/angular-test-engineer.agentcard.json
  - .a2a/agentcards/react-developer.agentcard.json
  - .a2a/agentcards/react-test-engineer.agentcard.json
  - tools/agent_source_docs_sync/required_source_docs_rules.json
  - tests/governance_audit/test_playwright_mcp_frontend_governance.py
  - .github/projects.local.yaml
  - .github/prompts/add-project-context.prompt.md
  - .github/skills/project-scanner/SKILL.md
  - .gitignore
  - .config/idea_mcp.json
  - .github/skills/playwright-mcp/references/auth-token-storage-patterns.md
  - .github/projects.local.yaml.example
  - tests/governance_audit/test_local_project_isolation.py
  - tests/governance_audit/_helpers.py
  - tests/governance_audit/test_planning_doc_template_governance.py
  - .githooks/pre-commit
  - docs/implementation-plans/20261008-feature-development-poc-frontend-login-playwright.md
  - docs/context/setup-context-mode-intellij.md
amendments:
  - "2026-10-08: Emenda B (token_storage + hardening do teste de isolamento) aprovada por humano via chat; status permanece approved; ver secao 10"
  - "2026-10-08: Emenda C (correcao de vazamentos pre-existentes de ID-LOCAL) aprovada por humano via instrucao no chat; status permanece approved; ver secao 11"
progress: 0
---

Progresso: 0/16 tarefas concluidas

# PLAN: Consolidacao do MCP Playwright nos agents frontend (Angular + React)

## 1. Contexto e escopo
- Skills `playwright-mcp` e `frontend-visual-feedback-loop` (VFL) sao compartilhadas por Angular e React; toda mudanca exige paridade entre stacks.
- Escopo: auth login/senha para validacao de layout, ordem de ferramentas, flags, versao fixada, roteamento UI/layout, workflow dedicado, governanca (sync + testes).
- Fora de escopo: alterar codigo de aplicacoes-alvo, instalar Playwright nos projetos, tools playwright/* nos arch-advisors (permanecem read-only).
- Evidencia: os 29 arquivos da allowlist existem (verificado); referencias a `playwright` ja presentes em catalog/routing-graph/agents developer e test-engineer/agentcards/idea_mcp/rules.json. Arquivos novos: workflow-ui-layout.md, references/ do VFL, teste de governanca.
- Nota: `.github/instructions/local/{<projeto>,...}.instructions.md` citam playwright, mas sao locais/gitignored e ficam FORA da allowlist (somente leitura como insumo).

## 2. Decisao de Design Pattern (mini-ADR)
- Contexto: agentes precisam validar layout em apps autenticadas sem expor credenciais; MCP Playwright (~114k tokens por sessao tipica) vs Playwright CLI (~27k) — numeros do insumo de auditoria, a revalidar na doc oficial.
- Decisao 1 (ferramenta): MCP como padrao para loop interativo de layout (snapshot/resize/console); CLI como alternativa documentada para fluxos longos/scriptaveis e para economia de tokens. Criterio de escolha escrito na secao "MCP vs CLI" da skill. Decisao final do CLI = ponto humano H1.
- Decisao 2 (auth): usuario de teste dedicado + projeto `setup` do Playwright gravando `storageState` (playwright/.auth/*.json) + MCP com `--isolated --storage-state=<arquivo>`. SSO/MFA: `--user-data-dir` com perfil dedicado. `--extension` = alto risco, proibido por padrao. Segredos somente via variaveis de ambiente (nunca prompt, log, trace ou commit). `auth.json`, storage-state e traces no .gitignore. Flags/sintaxe VALIDAR na doc oficial do @playwright/mcp antes de escrever (tarefa T1).
- Decisao 3 (versao): fixar `@playwright/mcp@<x.y.z>` (sem `@latest`), versao escolhida na T1 e replicada em skill e idea_mcp.json; teste proibe `@latest`.
- Decisao 4 (ordem VFL): `browser_resize` -> `browser_snapshot` (padrao) -> console -> `browser_take_screenshot` apenas sob demanda; reconciliar com `--caps vision`. Fonte unica de viewports/cleanup (VFL), demais skills apenas referenciam.
- Decisao 5 (papeis): arch-advisor define estrategia e emite plano (secao UI/Layout), sem tools playwright/*; developer/test-engineer executam.
- Alternativas descartadas: `--extension` (superficie de ataque); credenciais no prompt/arquivo versionado; dar tools playwright/* aos advisors (viola read-only); `@latest` (nao reprodutivel).
- Consequencias: ganho em seguranca/reprodutibilidade/paridade; custo: mais arquivos sincronizados e manutencao de versao fixada.

## 3. Ordem e dependencias das tarefas
Onda 0 (pesquisa, bloqueante): T1.
Onda 1 (fontes): T2 (depende T1), T3 (depende T2).
Onda 2 (agents, paralelizavel apos T3): T4, T5, T6, T7, T8.
Onda 3 (workflow e governanca): T9 (apos T7/T8), T10 (apos T4-T9), T11, T12 (apos T10), T13.
Onda 4 (locais/infra, @governance-maintainer; T14-T16 independentes entre si; T14 depende do formato da T2/T9): T14, T15, T16.
Onda 5: T17 validacao final.

## 4. Checklist de Execucao Tecnica (GFM Unificado)
- [x] T1 Validar na doc oficial do @playwright/mcp: flags `--isolated`, `--storage-state`, `--user-data-dir`, `--save-trace`, `--output-dir`, `--viewport-size`, `--headless`, `--caps`; escolher versao fixa; confirmar numeros MCP vs CLI. Registrar fontes no corpo da skill. `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T2 `playwright-mcp/SKILL.md`: secao "Auth e Ambiente" (padrao storageState, SSO/MFA, extension proibida, segredos por env), flags, versao fixada, secao "MCP vs CLI", corrigir "10 agentes" para lista real (6 com tools). `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T3 `frontend-visual-feedback-loop/SKILL.md`: ordem de ferramentas, reconciliar `--caps vision`, referenciar auth da playwright-mcp, mover exemplos >8 linhas (R-026) para `references/`, remover duplicacao de viewports/cleanup (fonte unica). `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T4 `angular-arch-advisor` e `react-arch-advisor`: source_docs += playwright-mcp e VFL; sem tools playwright/*; template de plano ganha secao "UI/Layout" (auth strategy, ambiente, origens permitidas, viewports, projeto-alvo). `{paralelizavel: true, responsavel: "@governance-factory"}`
- [x] T5 `angular-developer` e `react-developer`: citar loop VFL, `browser_close`, regra de segredos; alinhar tools playwright/*. `{paralelizavel: true, responsavel: "@governance-factory"}`
- [x] T6 `angular-test-engineer` e `react-test-engineer`: Angular ganha VFL em source_docs; alinhar angular-test-engineer ao react-test-engineer (18 tools, H3); corpo: projeto setup + storageState + segredos por env. `{paralelizavel: true, responsavel: "@governance-factory"}`
- [x] T7 `angular-router` e `react-router`: regra UI/layout (arch-advisor -> developer/test-engineer); sincronizar `routing-graph.yaml`, `angular-catalog.yaml`, `react-catalog.yaml`, `catalog.yaml`. `{paralelizavel: true, responsavel: "@governance-factory"}`
- [x] T8 Sincronizar `.a2a/agentcards/{angular,react}-{developer,test-engineer}.agentcard.json` com as mudancas de tools/skills (T5, T6). `{paralelizavel: true, responsavel: "@governance-factory"}`
- [x] T9 Criar `workflows/workflow-ui-layout.md` e indexar em `workflows.md`; deve respeitar `test_catalog_agents_referenced_in_canonical_workflows` e invariantes (R-064, aprovacao humana). `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T10 `required_source_docs_rules.json`: regras de source_docs (arch-advisors, developers, test-engineers com playwright-mcp/VFL, paridade angular/react). `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T11 Rodar sync tools de `tools/agent_source_docs_sync` (modo check e depois aplicar) e regenerar `.github/skills/.index.json` pelo gerador oficial (nunca editar a mao). `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T12 Criar `tests/governance_audit/test_playwright_mcp_frontend_governance.py`: paridade tools `playwright/*` angular/react, paridade source_docs, arch-advisors sem `playwright/*`, ausencia de `@latest` (skill e idea_mcp), segredos so por env (sem valores literais). `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T13 Changelog/README de skills se exigidos por `test_changelog_integrity`; ajustar contagens se algum teste de governanca quebrar. `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] T14 `.github/projects.local.yaml` (gitignored): `ui_url`, `auth_strategy` (storage_state|user_data_dir|none), nome do env var (so o NOME, nunca o valor); alvo unico [PROJETO-ALVO] (H2; outro-projeto fora do escopo); ajustar `prompts/add-project-context.prompt.md` e `skills/project-scanner/SKILL.md` para coletar esses campos. `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [x] T15 `.gitignore`: `playwright/.auth/`, `auth.json`, `*storage-state*.json`, `test-results/`, `playwright-report/` (confirmar com `git check-ignore`). `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [x] T16 `.config/idea_mcp.json`: args do playwright alinhados a skill (versao fixada, `--isolated`, `--storage-state`, `--output-dir`; `--save-trace` inexistente na 0.0.83, trace via `--caps=devtools` se necessario); sem segredos no JSON. `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [x] T17 Validacao final consolidada (secao 5) e relatorio de conformidade. `{paralelizavel: false, responsavel: "@governance-factory"}`

Divisao de executores: @governance-factory = itens 1-7 e 11 da auditoria (T1-T13, T17); @governance-maintainer = itens 8-10 (T14-T16). Handoffs entre os dois: T14 consome o formato definido em T2; T16 consome versao/flags de T1/T2.

### Relatorio T17
- Resultado: `pytest tests/governance_audit` 629 passed / 3 skipped / 0 falhas; sync required/lazy source_docs drift 0; export_agentcards com drift pre-existente apenas no agent-router.
- Auditoria final: aprovado com ressalva de isolamento de escopo no commit.
- Desvios: `--save-trace` inexistente; 4 agents com tools playwright (nao 6); keywords de catalog.yaml/routers fora de allowlist.


## 5. Validacao
- `pytest tests/governance_audit` (suite completa; foco: test_a2a_agentcards_parity, test_a2a_agentcard_compliance, test_catalog_agents_referenced_in_canonical_workflows, test_local_project_isolation, test_changelog_integrity, test_governance_smells, novo teste T12).
- Sync tools: `tools/agent_source_docs_sync` em modo check sem divergencias; `.index.json` regenerado e sem diff residual ao reexecutar (idempotencia).
- `git check-ignore -v` para cada padrao de T15; `git grep -n "@latest" -- .github .config` sem ocorrencias de playwright.
- `git grep` por padroes de segredo/valores literais de senha nos arquivos alterados: zero achados.
- Verificacao manual: JSON valido de idea_mcp.json e agentcards; nenhum arquivo fora da allowlist em `git status`.
- Smoke opcional (H4): um login real com storageState em projeto-alvo, executado pelo humano.

## 6. Rollback
- Mudancas atomicas por onda em commits separados; reverter com `git revert` por onda (Onda 1-3 independentes da 4).
- Arquivos novos (workflow-ui-layout.md, references/, teste) removidos via revert; `.index.json` regenerado apos revert.
- `projects.local.yaml` e `idea_mcp.json` locais: manter backup `.bak` antes de editar; restaurar manualmente (nao versionados no caso do yaml).
- Se T12 ou a suite falhar sem correcao trivial: reverter a onda culpada, nao enfraquecer testes.

## 7. Riscos
- Sintaxe/flags do @playwright/mcp mudam entre versoes -> T1 bloqueante e versao fixada.
- Vazamento de credencial/storageState/traces -> .gitignore, regra de env, teste de varredura.
- Drift de paridade Angular/React e agentcards -> teste T12 + sync.
- Quebra de testes de governanca (contagem de agents, workflows canonicos, headings) ao adicionar workflow-ui-layout -> executar suite a cada onda.
- Custo de tokens do MCP (~114k) -> criterio MCP vs CLI e snapshot como padrao.
- `--extension`/perfil real do usuario expoem sessoes pessoais -> proibido por padrao.
- projects.local.yaml gitignored: mudanca nao e rastreavel nem reproduzivel por outros devs -> documentar campos no prompt/scanner.
- Pendencia R-064 resolvida: `related-planning-doc` = N/A (plano unico de governanca).

## 8. Decisoes Humanas Registradas

Status: aprovado por humano em 2026-10-08 via ask_questions (H1–H6).

- **H1**: MCP padrao (`@playwright/mcp`) + Playwright CLI como alternativa oficial documentada (criterio: MCP para exploracao interativa; CLI/`@playwright/test` para suites versionadas e menor custo de tokens).
- **H2**: apenas [PROJETO-ALVO] como projeto-alvo. Demais projetos locais removidos do escopo de `projects.local.yaml`.
- **H3**: assimetria intencional mantida. `developer` = 13 tools (11 base + `browser_fill_form` + `browser_press_key`); `react-test-engineer` = 18; `angular-test-engineer` alinhado ao react-test-engineer (18).
- **H4**: T1 valida na doc oficial a ultima versao estavel do `@playwright/mcp` e a fixa (sem `@latest`).
- **H5**: `--user-data-dir` somente para SSO/MFA, com perfil dedicado fora do repo e listado no `.gitignore`. `--extension` proibido por padrao.
- **H6**: `workflow-ui-layout` e workflow auxiliar (nao numerado), vinculado ao fluxo de feature/bug; nao altera a lista de workflows canonicos 1-9.

### 8.1 Tabela de paridade Angular x React

| Agent | Angular | React | Observacao |
|---|---|---|---|
| developer | 13 (11 + browser_fill_form + browser_press_key) | 13 (idem) | paridade; extras para formularios/teclado |
| test-engineer | 18 | 18 | Angular alinhado ao React (H3) |
| arch-advisor | consultivo | consultivo | paridade |
| router | sem tools playwright | sem tools playwright | paridade |

### 8.2 Parecer do react-arch-advisor (incorporado)

- **URL base via env**, nunca hardcoded: Vite 5173, Next 3000, Storybook 6006, vite preview 4173.
- **Storybook preferido** para validacao de layout isolado sem auth.
- **Next/RSC com auth por cookie httpOnly**: storageState captura o cookie; usar wait_for pos-hidratacao antes de snapshot; localhost != 127.0.0.1 (cookies por host; usar o mesmo host na captura e na execucao); redirect para /login = falha de auth, nao bug de UI.
- **Vitest browser mode fora do escopo do VFL** (frontend-visual-feedback-loop).
- **Ruido de console**: HMR e StrictMode (efeitos/logs duplicados em dev) nao sao erro de UI.
- **MCP vs suites**: MCP para exploracao; @playwright/test/CLI para suites versionadas e reprodutiveis.
- **Risco de vazamento de credencial** via browser_type/browser_fill_form: usar env/storageState, nunca literais; nao registrar valores em traces/logs.

## 9. Checklist Defensivo Pre-Code-Review
- [ ] Sanitizacao e validacao de inputs em todas as bordas expostas (ui_url com origens permitidas/allowlist, sem redirecionar para dominios arbitrarios)
- [ ] Ausencia de segredos, tokens ou dados sensiveis em hardcode e logging seguro sem PII (traces/storageState ignorados)
- [ ] Tratamento defensivo de excecoes e controle de autorizacao/permissoes validado (usuario de teste de menor privilegio, ambientes nao produtivos)
- [ ] Testes unitarios/integracao defensivos atendendo aos quality gates

## 10. Emenda B (2026-10-08) - token_storage e hardening do isolamento
- Aprovacao: humano, 2026-10-08, via chat. Status permanece `approved`. Executores: `@governance-factory` (B1-B7) e `@governance-maintainer` (B8). Tudo GENERICO (R-038/R-043/R-044): somente placeholders `[PROJETO-ALVO]`, `<PROJETO>_TEST_USER`, `<PROJETO>_TEST_PASSWORD`, `<PROJETO>_STORAGE_STATE_PATH`, `<rota-alvo>`, `<raiz-do-projeto>`.
- **RCA**: o teste so varria `git ls-files`; planos novos estavam untracked; e o set de identificadores depende de `projects.local.yaml` (ausente em CI).
- Plano generico da POC: `docs/implementation-plans/20261008-feature-development-poc-frontend-login-playwright.md` (substitui o plano anonimizado anterior, cujo stub deve ser removido pelo `@governance-maintainer`).

### Checklist Emenda B (GFM Unificado)
- [ ] B1 `.github/skills/playwright-mcp/SKILL.md`: matriz de decisao por local do token (cookie ou localStorage -> `storageState`; sessionStorage -> fixture com `addInitScript` lendo arquivo de sessao gitignorado; token validado/renovado no backend -> login por teste); licoes: Playwright NAO carrega `.env` sozinho (loader minimo com `readFileSync` sem sobrescrever env existente quando `@types/node` nao tipa `loadEnvFile` e nao ha `dotenv`); `waitForURL` aguarda a rota-alvo (nao "sair do login") com timeout maior em HML; setup como projeto dependente + `storageState` global impacta specs existentes (rodar smoke antes/depois); role pode mudar por viewport (ex.: sidenav handset vira dialog); gitignore completo (`.auth/`, `test-results/`, `playwright-report/`, `.playwright-mcp/`, arquivo de sessao); ordem de diagnostico (snapshot pos-falha -> codigo de auth -> causa-raiz). Secao curta com ponteiro a B2 `{paralelizavel: false, responsavel: "@governance-factory"}`
- [ ] B2 Criar `.github/skills/playwright-mcp/references/auth-token-storage-patterns.md` com templates genericos (`auth.setup`, fixture `addInitScript`, loader `.env`, gitignore) usando placeholders `<PROJETO>_*` `{paralelizavel: false, responsavel: "@governance-factory"}`
- [ ] B3 Secao "UI/Layout" de `angular-arch-advisor` e `react-arch-advisor`: campo obrigatorio `token_storage` (cookie|localStorage|sessionStorage|indexeddb) e passo "descobrir antes de planejar" (paridade Angular/React) `{paralelizavel: true, responsavel: "@governance-factory"}`
- [ ] B4 `.github/projects.local.yaml.example` e `.github/prompts/add-project-context.prompt.md`: campo opcional `token_storage`; `.github/skills/project-scanner/SKILL.md`: deteccao por grep (`sessionStorage.setItem`, `localStorage.setItem`, `localStorageSync`) sem identificar projetos `{paralelizavel: true, responsavel: "@governance-factory"}`
- [ ] B5 `angular-test-engineer`, `react-test-engineer` e `workflow-ui-layout.md`: uma linha apontando para a referencia B2 `{paralelizavel: true, responsavel: "@governance-factory"}`
- [ ] B6 `tests/governance_audit/test_playwright_mcp_frontend_governance.py`: asserir que a skill cita a matriz e que a referencia B2 existe `{paralelizavel: false, responsavel: "@governance-factory"}`
- [ ] B7 Hardening de `tests/governance_audit/test_local_project_isolation.py`: (a) varredura inclui nao rastreados e nao ignorados (`git ls-files --cached --others --exclude-standard`); (b) teste independente de `projects.local.yaml` com regex proibindo caminhos absolutos de workspace (drive Windows `[A-Za-z]:\\workspace\\` exceto o proprio repo publico, e `/workspace/` equivalente) e o padrao `<algo>_STORAGE_STATE_PATH`/`_TEST_USER` fora do placeholder `<PROJETO>`; (c) cobertura explicita de `docs/implementation-plans/`; (d) teste que falha se `get_forbidden_project_identifiers()` vier vazio com `projects.local.yaml` presente; verificar e reportar se `.githooks/pre-commit` cobre staged files `{paralelizavel: false, responsavel: "@governance-factory"}`
- [x] B8 `@governance-maintainer`: remover o plano antigo (stub), varredura final de vazamentos incluindo nao rastreados e `pytest tests/governance_audit` `{paralelizavel: false, responsavel: "@governance-maintainer"}`

### Allowlist adicional (Emenda B)
Incluida no frontmatter `allowed_files`: `references/auth-token-storage-patterns.md`, `.github/projects.local.yaml.example`, `tests/governance_audit/test_local_project_isolation.py`, `.githooks/pre-commit` (somente verificacao/reporte, edicao apenas se cobertura de staged files for insuficiente) e o plano generico da POC. Demais arquivos de B1-B6 ja constam na allowlist original.

### Riscos Emenda B
- Falso positivo da regex de caminho absoluto em docs legitimos -> excecao explicita apenas para o proprio repo publico.
- Ambiente local com `projects.local.yaml` vazio mascara o teste (d) -> teste falha explicitamente.
- Hook `pre-commit` que so le `git ls-files` ignora staged -> B7 verifica e reporta.
- Rollback: `git revert` do commit da Emenda B; nenhum codigo de aplicacao tocado.

## 11. Emenda C (2026-10-08) - correcao de vazamentos pre-existentes de ID-LOCAL

- Status: segue `approved`. Aprovacao humana: instrucao do usuario no chat em 2026-10-08 ("nenhum doc do deep-agents-copilot deve conter referencias de projetos locais").
- Motivo: o teste de isolamento endurecido (Emenda B) detectou 3 vazamentos reais pre-existentes.
- Allowlist: `.github/agents/catalog.yaml` (ja constava) e `docs/context/setup-context-mode-intellij.md` (adicionado ao frontmatter).

### Checklist Emenda C (GFM Unificado)
- [x] C1 `.github/agents/catalog.yaml` ~linha 2152: caminho absoluto de workspace em changelog -> placeholder `<workspace>/[PROJETO-EXEMPLO]` `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [x] C2 `.github/agents/catalog.yaml` ~linha 2414: mencao a pacote/caminho de ID-LOCAL -> `[PROJETO-A]/.../[MODULO-WS]/obter/...` ou equivalente generico `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [x] C3 `docs/context/setup-context-mode-intellij.md` ~linha 44: caminhos absolutos de workspace e de instalacao do node -> `<workspace>\[PROJETO-EXEMPLO]` e `<caminho-node>` `{paralelizavel: true, responsavel: "@governance-maintainer"}`
- [x] C4 Validacao: `pytest tests/governance_audit/test_local_project_isolation.py` verde; `sync tools --check` drift 0 (se o catalogo for regenerado/sincronizado, reportar) `{paralelizavel: false, responsavel: "@governance-maintainer"}`

### Riscos e Rollback Emenda C
- Correcao cirurgica (somente as 3 linhas); sem alteracao de semantica do catalogo.
- `catalog.yaml` e lido por tools: drift de sync possivel -> reportar se regenerado.
- Rollback: `git checkout -- .github/agents/catalog.yaml docs/context/setup-context-mode-intellij.md`.

## 12. Emenda D (2026-10-08) - testes de regressao: arquivo novo/nao rastreado com referencia a projeto local
- Aprovacao: humano, 2026-10-08, via chat (pedido do usuario: "preciso que tenha testes cobrindo esse cenario depois vamos para o commit"). Status permanece `approved`. Executor: `@python-test-engineer`. Tudo GENERICO (R-038/R-043/R-044): fixtures somente com identificadores sinteticos; NUNCA nomes de projetos reais.
- Escopo: testes pytest de regressao do cenario "arquivo NOVO/nao rastreado (ex.: plano em `docs/implementation-plans/`) com referencia a projeto local passa despercebido".

### Checklist Emenda D (GFM Unificado)
- [x] D1 `tests/governance_audit/test_local_project_isolation.py`: refatorar a funcao de varredura para aceitar `root` e lista de identificadores; testes com repositorio git TEMPORARIO (`tmp_path`, `git init`) e arquivo nao rastreado com identificador sintetico, provando deteccao ANTES de qualquer `git add`; arquivos gitignorados ignorados `{paralelizavel: false, responsavel: "@python-test-engineer"}`
- [x] D2 mesmo arquivo: carregamento de identificadores com `projects.local.yaml` INVALIDO (barras sem escape), fixture sintetica; parser de fallback retorna ids (nao vazio) `{paralelizavel: true, responsavel: "@python-test-engineer"}`
- [x] D3 mesmo arquivo: falsos positivos - palavra comum (>= / < tamanho minimo), boundary (id sintetico vs id + sufixo), lockfile ignorado, mensagem de falha mascarada com `ID-LOCAL` `{paralelizavel: true, responsavel: "@python-test-engineer"}`
- [x] D4 mesmo arquivo: detector de caminho absoluto de workspace e de env vars `*_STORAGE_STATE_PATH`/`_TEST_USER`/`_TEST_PASSWORD` (positivos, negativos com placeholders `<PROJETO>`/exemplo, isencoes) `{paralelizavel: true, responsavel: "@python-test-engineer"}`
- [x] D5 `tests/governance_audit/test_planning_doc_template_governance.py`: todo arquivo em `docs/implementation-plans/` (exceto `README.md`) segue `^\d{8}-[a-z0-9]+(-[a-z0-9]+)*\.md$`, inclui prefixo de workflow derivado dos nomes existentes (sem hardcode fragil) e nenhum nome contem identificador proibido `{paralelizavel: true, responsavel: "@python-test-engineer"}`

### Allowlist adicional (Emenda D)
Incluida no frontmatter `allowed_files`: `tests/governance_audit/_helpers.py` (somente se necessario para helper) e `tests/governance_audit/test_planning_doc_template_governance.py`; `tests/governance_audit/test_local_project_isolation.py` ja constava.

### Criterio de pronto
- `pytest tests/governance_audit` verde.
- Mutation sanity: remover a varredura de nao rastreados faz D1 falhar.
- Nenhum identificador real em fixtures, mensagens ou nomes de arquivo.

### Riscos Emenda D
- `git` ausente no ambiente de teste -> `pytest.skip` explicito apenas nesse caso.
- Refatoracao da varredura quebrar o teste existente -> manter assinatura com defaults.
- Rollback: `git revert` do commit da Emenda D; nenhum codigo de aplicacao tocado.
