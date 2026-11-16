# CHANGELOG — Deep Agents Copilot (Estrutura de Governança Genérica e Reutilizável)

Todas as mudanças significativas nesta base de governança são documentadas aqui.

Formato: [Semantic Versioning](https://semver.org/) | [Conventional Commits](https://www.conventionalcommits.org/)

## [2.60.0] — 2026-11-16
### Added
- **R-055 Q0 (RCA Upstream)**: planos de governança corretivos exigem Origem Upstream, Análise de Escape e Neutralização na Fonte; evolutivos isentos com `N/A` justificado.
- Teste `tests/governance_audit/test_upstream_rca_gate.py` validando Q0 em template, rubrica, `@plan-critic` e planejadores.
### Changed
- `plan-template-governance.md`, rubrica pré-HITL (`T2-RCA`), `@plan-critic`, `@agent-auditor`, `@governance-factory` e `planner-preflight-checklist.md` (C2).
- Redação de R-055 em `CLAUDE.md`, `copilot-instructions.md`, `workflows.md` e `invariantes-e-protocolos.md`.

## [2.59.0] — 2026-11-16

### Changed
- **Governança de Concisão do `CHANGELOG.md` (`git-governance` §4/§5)**: instituído orçamento normativo (`<= 200 chars/bullet`, `<= 12 bullets/release`, teto `<= 1.000 linhas`) em 8 artefatos.
- **Compactação Semântica In-Place do `CHANGELOG.md`**: saneamento integral de sub-bullets prolixos e listas exaustivas, preservando 100% dos cabeçalhos SemVer e âncoras históricas.

## [2.58.0] — 2026-11-15

### Changed
- **Roteadores**: metadados do bloco `## Formato de Saída` passam a usar lista Markdown (`- Campo:`) com `Agente Ativo:` isolado na 1ª linha, evitando colapso de quebras de linha (CommonMark).
- **Decision Tree do `@agent-router` / `routing-graph.yaml`**: Fast-Paths explícitos para `WORKFLOW-FRAMEWORK-MIGRATION`, `WORKFLOW-PROMPT-SYNTHESIS` e `WORKFLOW-TECHNICAL-ANALYSIS`.
- **Agents, templates e `agent-contracts/SKILL.md`**: ajustes de contrato e `.a2a/agentcards/` sincronizados.
- **`headless-governance-runner` (synth)**: `cli.py`, `evaluator.py` e `seeds.py` evoluídos para diagnóstico de workflows e extração B2.
### Added
- Testes em `tests/governance_audit/test_router_agents.py` (formato de saída dos roteadores) e `test_synth_workflows_b2_extraction.py`.

## [2.57.0] — 2026-11-14

### Added
- **Agente `@plan-critic` e Quality Gate Revisor Cético Universal Pré-HITL**: Criação do subagent consultivo read-only `.github/agents/plan-critic.agent.md`.
### Changed
- **Governança, Skills, Agents, Prompts, Docs, Hooks e Runtime**: Upgrade `context-mode` v1 -> v2.1.10.
- **Templates de Planos, Catálogos A2A e Paridade de Suítes de Auditoria**: Inclusão dos campos de gate pré-HITL nos 8 templates canônicos de planos, sincronização de `catalog.yaml`.
### Fixed
- **Pipelines GitHub Actions ( e ), Lockfile , Empacotamento PEP 639 e Paridade de Testes**: Upgrade de Node.js para no job de , inclusão do gatilho e instalação prévia do pacote local no job .

## [2.56.0] — 2026-10-06

### Adicionado (Política Anti-Timeout, Runtime Preferencial JavaScript e Circuit Breaker Fail-Fast no Context-Mode)
- **Runtime Obrigatório `language: "javascript"` no `ctx_execute`**: instituída a obrigatoriedade do runtime JavaScript nativo no `ctx_execute` para leitura, inspeção.
- **Higiene de Comandos em `ctx_batch_execute`**: exigência de comandos shell leves, atômicos e com escopo de diretório restrito, vedando `python -c` inline em lote e varreduras recursivas.
- **Circuit Breaker Fail-Fast de Timeout**: tolerância zero para repetição da mesma chamada/runtime após timeout.
### Adicionado / Modificado — GOVERNANCE-PROTOCOL-REFACTOR: Composição Dinâmica por Capabilities e Formatação H2 CommonMark do Execution Protocol (Opção C + Opção 3)
- **Refatoração Estrutural do Protocolo de Execução**: Decomposição modular do fragmento canônico em cláusulas atômicas em `tools/agent_protocol_sync/_execution-protocol-fragment.md`.
- **Padronização Visual e Tipográfica (Opção 3 — Cabeçalho H2 + Tag XML)**: Adicionado cabeçalho CommonMark `## ⚙️ Protocolo de Execução Obrigatório` imediatamente antes da tag `<execution_protocol>`.
- **Auditoria de Governança e Testes Automatizados**: Adicionado teste `test_execution_protocol_option3_h2_header_and_commonmark_formatting` e `test_dynamic_composition_by_capabilities` em.

## [2.55.0] — 2026-10-06

### Adicionado / Modificado — WORKFLOW-GOVERNANCE-MAINTENANCE: Consolidação Global de Agents das 8 Stacks (Fases 1 a 5)
- **Consolidação Global do Ecossistema de Stacks**: Implementação universal do **Padrão Triádico 3+1** em todas as 8 stacks tecnológicas:.
- **Sincronização Atômica Global (R-015 / R-040)**: Atualização estrutural de `catalog.yaml`, sub-catálogos `<stack>-catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md`, `workflows.md`.
- **Quality Gates Globais e Suítes Determinísticas de Governança**: Criadas e validadas 8 suítes dedicadas de conformidade por stack: `test_spring_boot_consolidation.py`.

## [2.54.0] — 2026-10-05

### Modificado — Consolidação de Skills e Decomposição de Outliers
- **Decomposição da Skill Outlier `test-implementation-angular-vitest`**: Refatorado o arquivo da skill para focar exclusivamente nas particularidades do Angular 20/21+ com Vitest.
- **Cross-References Canônicas de Skills**: Estabelecidas referências cruzadas bidirecionais entre a skill central `test-implementation-frontend` e seus runners específicos.
- **Atualização de Catálogos e Metadados A2A**: Sincronizados `.github/skills/.index.json`, `.github/skills/README.md`, catálogos de agentes e arquivos `.a2a/agentcards/*.agentcard.json`.
### Adicionado — Gates Automatizados de Auditoria de Governança
- **Gate de Tamanho e Cross-References de Skills**: Adicionada a suíte `tests/governance_audit/test_stack_skills_cross_reference_and_size_outlier.py` para impedir crescimento desmedido de skills.
- **Suítes de Conformidade e Viabilidade**: Adicionados testes em `test_plan_conformance_skill_boundaries.py` e `test_skill_import_viability_gate.py`.

## [2.53.0] — 2026-10-04

### Adicionado — Integração do MCP Playwright (`microsoft/playwright-mcp`) e Skill Canônica para Agentes Frontend
- **Nova Skill Canônica `playwright-mcp` (Tier 1)**: Criada a skill `.github/skills/playwright-mcp/SKILL.md` fornecendo diretrizes de automação de navegador real orientada a Accessibility Tree.
- **Integração de Tooling MCP em Agentes Frontend**: Habilitada a ferramenta MCP `playwright` no frontmatter de 10 agentes especializados de frontend (Angular e React): Angular.
- **Configuração de MCP no Host IDE (`.config/idea_mcp.json`)**: Adicionado o servidor MCP `@playwright/mcp` via `npx -y @playwright/mcp@latest` com configuração padronizada para suporte a automação.
- **Sincronização de Contratos e Metadados A2A**: Atualizados os 10 arquivos `.a2a/agentcards/*.agentcard.json` correspondentes com as novas capacidades de ferramentas de automação visual/E2E.

## [2.52.4] — 2026-10-03

### Modificado — Poda de Capacidade de Ferramentas de Context-Mode em Agentes Gather-Only (R-055 / R-056 / R-059)
- **Classificação Canônica de Capacidade**: Formalizada a separação objetiva entre perfis **"Gather-only"** vs **"Gather+Process"** sob o critério de corte aprovado de três condições: (a) agregação.
- **Remoção de `ctx_execute` e `ctx_execute_file` em 26 Agentes**: Poda cirúrgica realizada em lote no frontmatter `tools:` de 26 agentes puramente analíticos/consultivos.
- **Prevenção de Bypass de Hook em Subagents**: A poda estática fecha a lacuna de runtime em que subagents gerados via `run_subagent` não eram interceptados pelo hook `preToolUse` do IDE.
- **Novo Teste Determinístico (R-055 Q3)**: Criado `tests/governance_audit/test_ctx_execute_capability_profile.py` garantindo não-regressão e conformidade estática contínua dos 26 agentes.
- **Atualização de Templates e Smells (R-055 Q2)**: Incorporada a pergunta de corte de capacidade no Checklist Estrutural de `governance-factory-patterns/SKILL.md` (§3) e catalogado o **Smell 2.32**.
- **Documentação de Governança (R-064)**: Criados os planos versionados `docs/plans/20261003-governance-maintenance-ctx-execute-profile-classification.md` e.

## [2.52.3] — 2026-10-03

### Corrigido — Hook `PreToolUse` do Circuit Breaker Mecânico Nunca Executava (Templating de `$` pelo Host JetBrains)
- **Gap identificado**: o Circuit Breaker mecânico do `ctx-sequence-guard` nunca produzia efeito observável.
- **Causa raiz confirmada via `idea.log`**: o host JetBrains Copilot aplica *template expansion* na string do campo `"powershell"` do hook.
- **Correção aplicada**: `.github/hooks/context-mode.json`.
- **Documentação atualizada**: `.github/hooks/README.md`, `docs/context/setup-context-mode-intellij.md` (§5.4 novo), `.github/skills/context-mode/SKILL.md` § 4.1.1 condensado para regra genérica.

## [2.52.2] — 2026-10-03

### Corrigido — Gap Irmão: Nenhum dos 22 Prompts Possuía `<execution_protocol>`
- **Gap identificado**: confirmado via `ctx_execute` que **100% dos 22 `*.prompt.md` declaram `source_docs_lazy:`** (migrados em [2.52.0]), mas **nenhum** possuía o bloco `<execution_protocol>`.
- **Correção aplicada**: `tools/agent_protocol_sync/sync_execution_protocol.py` estendido com `get_prompt_files()` + `sync_prompts()`.
- **Conflito de nomenclatura resolvido**: `test_prompt_synthesis_output_format_governance.py::test_no_residual_xml_prompt_synthesis` tratava `<execution_protocol>` como tag XML residual proibida.
- **Template canônico atualizado**: `prompts/templates/prompt-template.md` já nasce com o bloco `<execution_protocol>` (consistência total de F6 — todo novo artefato já nasce em conformidade).
- **2 novos testes determinísticos**: `test_all_prompts_contain_execution_protocol_block`.
- **Validação de regressão**: 540/541 testes passando (toda a suíte, exceto a falha pré-existente e não-relacionada já conhecida).

## [2.52.1] — 2026-10-03

### Corrigido — Gap de Discovery de `source_docs_lazy:` (Nenhuma Instrução Operacional no Corpo do Agent)
- **Gap identificado**: a migração R-066/[2.52.0] moveu `CLAUDE.md`/`.github/copilot-instructions.md`/`workflows.md` para `source_docs_lazy:` em 188 artefatos.
- **Correção aplicada**: adicionado o item 8 ao bloco canônico `<execution_protocol>` em `tools/agent_protocol_sync/_execution-protocol-fragment.md` (fonte única).
- **2 novos testes determinísticos** em `test_r066_progressive_disclosure_budget.py`: `test_execution_protocol_fragment_instructs_source_docs_lazy_semantics` e.
- **Lacuna residual reconhecida**: routers e `code-knowledge-graph` (CUSTOM) não recebem este bloco; aceitável, pois routers operam sob R-054 (Zero Discovery) e não leem `source_docs_lazy` na prática.
- **Validação de regressão**: 539/540 testes passando (toda a suíte, exceto a falha pré-existente e não-relacionada já conhecida).

## [2.52.0] — 2026-10-03

### Adicionado — R-066 Progressive Disclosure Compulsória de `source_docs:` (Anti Context Bloat Inicial)
- **Nova regra normativa R-066**: diferencia `source_docs:` (full-load, <500 linhas) de `source_docs_lazy:`. Enforcement declarado explicitamente como **textual/CI-estático**, não mecânico-runtime.
- **Novo Smell 2.31** em `.github/skills/governance-audit-patterns/SKILL.md` § 2 ("Progressive Disclosure Violation / Full-Load Forçado de Documento Lazy").
- **Nova ferramenta determinística** `tools/agent_source_docs_sync/sync_lazy_source_docs.py`: migra cirurgicamente `CLAUDE.md`/`.github/copilot-instructions.md`/`.github/agents/workflows.md` de.
### Pendente (fora de escopo desta rodada)
- Resolução da duplicação `prerequisite_docs:`/`source_docs:` em `.github/agents/catalog.yaml` (campo manualmente mantido, sem gerador automático confirmado — `tools/agent_protocol_sync` não o gera).

## [2.51.5] — 2026-10-04

- **Unwrap de Shell Wrapper e Segurança no Encadeamento (`permission_policy.py`)**: **Causa raiz (RC1)**: Comandos de terminal despachados pelo Copilot SDK envolvidos em wrappers interativos eram.
- **Detecção Fail-Fast de Porta Ocupada (`dev_watch.py`)**: Implementada função `_porta_ocupada(host, port)` utilizando `socket.create_connection` para abortar a inicialização imediatamente com.
- **Sistema de Logging Aditivo em Arquivo Rotativo (`logging_config.py`)**: Adicionado novo módulo com suporte a `RotatingFileHandler` gravando logs estruturados em formato texto legível em.
- **Testes e Cobertura**: Adicionados 24+ novos testes unitários (`test_permission_policy.py`, `test_dev_watch_port_check.py`, `test_logging_config.py`).
- **Ressalva do Quality Gate (Backlog)**: Identificada oportunidade de hardening futuro para operadores de redirecionamento de shell (`>`, `>>`, `<`) fora do escopo estrito deste bugfix.
- **Planos**: `docs/plans/20261004-bugfix-shell-permission-persistente-logging-arquivo.md`

## [2.51.4] — 2026-10-02

### Corrigido — MCP servers (context-mode/tavily/codegraph) e tools de IDE nunca registrados no Copilot SDK Headless Runner
- **Causa raiz (complementar à `[2.51.3]`)**: agentes servidos via Copilot SDK Headless Runner no `deep-agents-gateway` (`deploy/local-chat-gateway`) não tinham acesso a `ask_questions`.
- **Catálogo e Configuração MCP**: novo módulo `mcp_servers_catalog.py` com lista fechada dos 3 servidores MCP homologados, variáveis de ambiente isoladas via `_env_minimo()` e credenciais lidas.
- **Mapeamento de aliases e allowlist de shell nativo**: `_ALIAS_TOOLS_SDK_HEADLESS` expandido com o mapeamento completo IDE→SDK nativo.
- **Hardening de Segurança em `permission_policy.py` (4 camadas, Quality Gate com 3 iterações do loop R-050.4 + 1 correção pontual aprovada pelo usuário)**:.
- **Testes**: ~32 novos testes unitários distribuídos em `test_agent_catalog.py`, `test_mcp_servers_catalog.py` (novo), `test_config.py`, `test_sdk_session.py` e `test_permission_policy.py`.
- **Planos aprovados**: `docs/plans/20261002-bugfix-mcp-tools-headless-sdk.md` e `docs/implementation-plans/20261002-bugfix-mcp-tools-headless-sdk.md`.

## [2.51.3] — 2026-10-02

### Corrigido — Causa raiz real do bloqueio de `run_in_terminal`/git: `PermissionRequestShell` nunca reconhecida pelo SDK
- **Investigação via `ctx_execute` (sandbox)**: introspecção real do pacote `github-copilot-sdk` instalado no `.venv` do gateway (`copilot.session_events`) revelou que comandos de.
- **Regressão adicional encontrada e corrigida durante a investigação**: uma edição anterior havia reintroduzido acidentalmente uma chamada `await _bridge_edicao_arquivo(...)` dentro da versão.
- **Correção definitiva**: `PermissionRequestShell` agora é reconhecida nativamente em `_identificador_e_seguro_nativo` via nova função `_comando_shell_e_seguro()`.
- **Testes**: 1 nova classe `TestPermissionRequestShell` em `test_sdk_session.py` + placeholder de `PermissionRequestShell` registrado na fixture compartilhada.
- **Validação**: `black`/`isort`/`flake8` 100% limpos nos arquivos alterados (avisos remanescentes de `flake8` confirmados pré-existentes via comparação linha a linha do diff).

## [2.51.2] — 2026-10-02

### Corrigido — `POST /v1/ask-user/{id}/respond` (e irmãos `elicitation`/`file-edit`) 404 silencioso em modo dev
- **Sintoma real reportado em sessão de desenvolvimento**: logo após a correção de permissão acima, o usuário reportou um NOVO sintoma ao responder um diálogo de pergunta na UI.
- **Causa raiz**: `deploy/local-chat-gateway/dev_watch.py` sobe o uvicorn com `--reload` e `reload_dirs=["src"]`.
- **Correção**: os 3 componentes agora checam o status HTTP da resposta e, quando a entrega falha em uma ação que o usuário esperava ver refletida no agente.
- **Não-escopo desta correção**: a perda do `asyncio.Future` em si após um reload é uma limitação arquitetural inerente ao estado em memória + `--reload` em dev.
- **Validação**: `tsc --noEmit` e `eslint` 100% limpos nos 3 arquivos alterados.

## [2.51.1] — 2026-10-02

### Corrigido — Negação de `run_in_terminal`/comandos de shell mesmo em `GATEWAY_PERMISSION_MODE=apply`
- **Sintoma real reportado em sessão de desenvolvimento**: o agent `pr-gatekeeper` reportou no chat "Não tenho permissão para executar comandos git nesta sessão" mesmo com.
- **Causa raiz**: `GATEWAY_PERMISSION_MODE` só era consultado para tools nativas `PermissionRequestWrite`.
- **Correção**: centralizada em `local_chat_gateway/permission_policy.py` a função `comando_terminal_e_seguro()`.
- **Benefício sistêmico**: a correção é aplicada nos 2 handlers de permissão do gateway, beneficiando **todos** os agents do catálogo que dependam de `run_in_terminal` para operações read-only (não.

## [2.51.0] — 2026-10-02

### Alterado — Consolidação de Nomenclatura (Deep Agents Chat / Deep Agents Gateway)
- **Nome de exibição consolidado**: o frontend em `apps/web` (Next.js 16 + CopilotKit v2) agora se identifica como **"Deep Agents Chat"** e o backend em `deploy/local-chat-gateway` (FastAPI) como.
### Removido — Consolidação Exclusiva no Lobe Chat
- **Consolidação Exclusiva no Lobe Chat**: eliminação de serviços e profiles visuais alternativos de `deploy/local-chat-gateway/docker-compose.yml`.
### Adicionado — Local Chat Gateway MVP (FastAPI OpenAI-Compatible com Governança em Código)
- **Pacote `local_chat_gateway` (`deploy/local-chat-gateway/`)**: esqueleto MVP de gateway local opt-in expondo contratos OpenAI-compatible para consumo por Lobe Chat.
### Corrigido — 2 Bugs Reais de Build Descobertos em Teste Manual do Usuário
- **`pull access denied for local-chat-gateway`**: `docker compose up` (sem `--build`) tentava fazer `pull` da imagem `local-chat-gateway:local` como se fosse de um registry.
### Adicionado — Fase 3 (Integração Real com o SDK do Copilot)
- **Módulo `sdk_session.py`**: wrapper de import tardio (lazy) do pacote opcional `copilot` (extra `[sdk]`), leitura de token (`read_sdk_token`) e `stream_chat()` (async generator) conectando a uma.
### Corrigido — Fase 3 — 4 Bugs Descobertos em Teste Real com Token do Usuário
- **Extra `[sdk]` não instalado no Dockerfile**: o `pip install` do estágio `builder` só instalava `local-chat-gateway` (sem o extra), então o pacote `copilot` nunca existia na imagem.
### Corrigido — Fase 3 — 2 Bugs Adicionais Descobertos em 2º Teste Real via Lobe Chat
- **Agente reportava "não tenho acesso ao diretório `/app`"/"nenhum repositório ca**: `stream_chat()` não repassava `working_directory` ao `create_session()` do SDK real.
### Adicionado — Fase 4 (Governança Runtime, Multi-Turno, Checkpoints & SQLite)
- **Causa Raiz do 401 Unauthenticated no Langfuse Cloud — Poluição de Variáveis de**: Diagnosticado que o `.env` do gateway já continha o token Base64 correto de `LANGFUSE_OTLP_AUTH`.

## [2.49.0] — 2026-09-28

### Adicionado — Salvaguardas de Mercado 2025/2026, Model Tiering e Blindagem por Testes
- **R-064 Gate & Model Tiering em Domain Routers**: adicionada etapa obrigatória `implementation_plan_authoring` para `<stack>-arch-advisor` antes de codemod em `WORKFLOW-FRAMEWORK-MIGRATION`.
- **Fronteiras de Autoria de Testes & Paridade Test-Last**: barreira explícita proibindo autoria de testes por `*-feature-developer` em todas as 6 stacks com handoff obrigatório para test-writers.
- **Salvaguardas Operacionais 2025/2026**: `*-bug-fixer` (6 stacks): verificação obrigatória de blast radius antes do diff cirúrgico.
- **Consolidação do Domínio Spring Reactive**: remoção do agente fora de padrão `spring-reactive-resilience-tuner`, absorvendo escopo em `spring-reactive-perf-tuner` e restaurando a topologia.

## [2.48.0] — 2026-09-28

### Adicionado / Resolvido — Fechamento das Pendências Não-Bloqueantes da Fase PoC (Runner Headless)
- **Wiring completo dos reporters (`cli.py::main()`)**: o canal `--report checks,pr-comment` agora efetivamente publica o resultado da auditoria via Checks API (`reporters/checks.py`) e comentário.
- **Novos argumentos do CLI**: `--repo` (default `$GITHUB_REPOSITORY`), `--sha` (default `$GITHUB_SHA`), `--pr-number` — necessários para os reporters identificarem onde publicar.
- **Escopo de execução restrito por custo/credits (`governance-agent-audit.yml`)**: o workflow agora dispara **exclusivamente** em Pull Requests de `develop` para `main`.
- **Feature-flag de ativação sem editar o workflow**: variável de repositório `vars.GOVERNANCE_AGENT_AUDIT_ENABLED` controla se o job roda; Default (variável ausente) é **desativado**.

## [2.47.0] — 2026-09-28

### Resolvido — Q-01 Validado Empiricamente em CI Real + Correções de Integração do Runner Headless
- **Gate PoC → Piloto (subtask 26/27) APROVADO**: primeira execução real e autenticada do `governance-agent-audit.yml` contra o Copilot SDK verdadeiro em GitHub Actions (PR #55, run #6).
- **Correção de path de resolução do grafo (`cli.py`)**: `_GRAFO_PADRAO` usava `Path(__file__).parents[3]` (resolvia para `tools/`); corrigido para `parents[4]` (raiz do repositório).
- **Integração real com o Copilot SDK implementada (`sdk_adapter.py`)**: substituída a implementação-placeholder por uma ponte síncrona real (`_ClienteSDKReal`) sobre a API assíncrona confirmada via.
- **Dependência real do SDK declarada**: extra `sdk` do `pyproject.toml` (antes vazio) agora fixa `github-copilot-sdk>=1.0.0`.

## [2.46.0] — 2026-09-28

### Adicionado — Runner Headless Copilot SDK e Roteamento Determinístico em Código
- **Motor Determinístico de Roteamento (`governance_runner.routing`)**: Implementação em código puro Python da máquina de estados finita e guard clauses das regras normativas R-037 (agent-router.
- **Runner Headless para CI/CD (`governance_runner.runner`)**: Protocol abstrato `CopilotSDKClient` desacoplado da dependência direta de runtime, com Permission Handler restrito a operações.
- **Suíte Canônica de Testes de Roteamento**: 161 testes unitários e de integração.
- **Pipeline de Auditoria Automatizada em CI**: Workflow `.github/workflows/governance-agent-audit.yml` disparado em PRs que tocam `.github/{agents,skills,prompts}/**`.

## [2.45.0] — 2026-09-27

### Adicionado / Modificado — Roteamento Híbrido de Modelo e Política Zero-Noise de Testes
- **Roteamento Híbrido de Modelo (18 Agents Promovidos)**: Promoção dos executores centrais de desenvolvimento e reparo nas stacks Angular, Spring Boot, Spring Reactive, EJB.
- **Nova Regra Normativa R-021.2 (Retry-Rate Model Escalation)**: Formalizada em `.github/copilot-instructions.md` (§3) a exigência de escalonamento pontual para modelo superior (🧠) quando o mesmo.
- **Reforço Textual da Zero-Noise Test Policy**: Padronização literal da menção a `Zero-Noise Test Policy` em todos os 30 agents executores e nos templates canônicos.
- **Quality Gate Determinístico de Roteamento de Modelo**: Novo teste de auditoria estática em `tests/governance_audit/test_hybrid_model_routing_and_zero_noise_governance.py` garantindo que desvios.

## [2.44.0] — 2026-09-27

### Adicionado / Modificado — Persistência de Estado de Sessão e Recuperação de Crash (Terminal Hang)
- **Watchdog de Comando Bloqueante**: nova seção normativa exigindo wrapper `timeout -k <graça> <limite> <cmd>` (Linux/WSL/Git Bash) ou `Start-Job`+`Wait-Job -Timeout`+`Stop-Job` (PowerShell) para.
- **Checkpoint Automático Pré-Risco**: formalização de checkpoint via `ctx_index` obrigatório antes de qualquer comando classificado como risco.
- **Fallback de Retomada Sem Checkpoint (`ctx-resume.prompt.md`)**: novo protocolo de reconstrução best-effort via `git --no-pager status`/`git --no-pager diff --stat` + inspeção de arquivos.
- **Nota de Reúso Sistêmico (R-055)**: a correção em `terminal-governance/SKILL.md` é referenciada (não duplicada) pelos ~61 agents que declaram `run_in_terminal` em seu frontmatter.

## [2.43.0] — 2026-09-27

### Modificado / Manutenção de Governança
- **Migração Global XML → Markdown e Redesenho do `WORKFLOW-PROMPT-SYNTHESIS`**: Substituição global do formato de tags XML pelo template Markdown estruturado em todo o catálogo.

## [2.42.0] — 2026-09-27

### Adicionado
- **R-064**: Norma que estabelece a obrigatoriedade de versionamento e aprovação humana prévia de dois planos em workflows de código: Plano de Planejamento (`docs/plans/`) e Plano de Implementação.
- **Mapa do Repositório Canônico (`docs/repo-map.md`)**: Atualização e consolidação da infraestrutura determinística de arquivos (Zero Blind Searches).

## [2.41.2] — 2026-09-26

### Adicionado
- **Auditoria de Contradição de Tools e Paridade de Modelos (Smell 2.7 & R-015)**: Teste determinístico `test_smell_2_7_no_internal_tool_contradiction_in_body` para garantir que nenhum agente negue.
- **Hermeticidade de Testes de Observabilidade**: Fixture `isolate_env` em `tests/otel_langfuse/conftest.py` para isolamento e hermeticidade contra variáveis OTLP/Langfuse nos testes unitários.
### Modificado
- **Alinhamento de Modelos Recomendados (Claude Sonnet 5.5)**: Atualização do modelo para `Claude Sonnet 5.5` em `test-strategy.agent.md`, `repo-hygiene-auditor.agent.md`.
- **Resolução de Contradição de Tools (Smell 2.7)**: Ajuste de redação em `refactor-planner.agent.md` e `test-strategy.agent.md` esclarecendo operação analítica/read-only sem negação contraditória.

## [2.41.1] — 2026-09-26

### Adicionado
- **Auditoria de Linhas Duplicadas (Smell 2.1)**: Teste determinístico `test_smell_2_1_no_verbatim_consecutive_duplicate_lines` em `tests/governance_audit/test_governance_smells.py` para prevenir.
### Modificado
- **Higiene e Deduplicação de Prompts de Governança**: Remoção em lote de linha duplicada de diretriz do `context-mode` (Single-Turn MCP / Smell 2.26) em 33 agentes e no prompt.

## [2.41.0] — 2026-09-26

### Adicionado (Telemetria Zero-Footprint, SDK Langfuse, MCP Proxy & Framework de Evals)
- **Topologia de Telemetria OTel Proxy para Langfuse Cloud**: Arquitetura de observabilidade leve (~45MB RAM, zero banco local) despachando para Langfuse Cloud via HTTPS OTLP com Basic Auth.
- **SDK Python de Observabilidade e Sanitização**: Cliente OTel/Langfuse assíncrono com ciclo de vida de traces, spans, validação Pydantic e retry exponencial com backoff.
### Modificado
- **Sanitização e Segurança de Variáveis de Ambiente**: Sanitização de `tools/otel-langfuse/.env.example` com placeholders genéricos e token Base64 demonstrativo.
### Removido
- `tools/otel-langfuse/docker-compose.yml`: Remoção do stack monolítico pesado local (PostgreSQL, ClickHouse, MinIO, Redis) em favor do Langfuse Cloud SaaS.

## [2.40.0] — 2026-09-24

### Adicionado (Incorporação de Patterns do mattpocock/skills — Fases 1, 2 e 3)
- **Fase 1 — Novas Skills Autônomas**: `interactive-wizard-patterns` (Tier 2): Padrões para criação de scripts interativos e wizards passo a passo para operações que exigem intervenção humana.
- **Fase 2 — Reforços em Skills Core Existentes**: `code-review-patterns` (§ 3.1): Taxonomia de Code Smells Clássicos.
- **Fase 3 — Reforços Finais em Skills & Integrações Transversais**: `test-coverage-governance` (§ 1 e 1.1): Diretrizes de uso e Regra de Seams Pré-Acordados.

## [2.39.0] — 2026-09-24

### Adicionado (Governança de Batching Context-Mode, Fan-Out Signal & Quality Review Loop)
- **Context-Mode Circuit Breaker & Few-Shot**: Seção 4.1: Circuit Breaker de Tool-Chaining Sequencial para barrar loops degradantes de MCP tools.
- **R-021.1**: Formalização no SSOT `CLAUDE.md` e na tabela de sinais de `.github/copilot-instructions.md` recomendando escalonamento pontual para modelo 1× ou superior em tarefas com ≥ 10.
- **Sincronização de Templates Canônicos**: Atualização dos templates `agent-template.md` e `operational-agent.md` com parâmetro `cwd` explícito em `ctx_batch_execute`.
- **Loop de Revisão de Qualidade**: Formalização do padrão Evaluator-Optimizer com teto rígido de 3 iterações para achados não-bloqueantes nos 6 workflows operacionais.

## [2.38.0] — 2026-09-24

### Adicionado (Governança Anti Root-Agent-Impersonation & Anti Silent Bypass: R-062 e R-063)
- **R-062 e Smell 2.29**: Proibição terminante do modelo raiz ler, resumir ou parafrasear arquivos `.agent.md` para usurpar o papel de subagentes especializados sem dispatch real via `run_subagent`.
- **R-063 e Smell 2.30**: Proibição terminante do modelo raiz executar ferramentas genéricas nativas (terminal, read_file, grep, edit) sem triagem prévia obrigatória via `@agent-router`.

## [2.37.0] — 2026-09-24

### Adicionado (Wiring Sistêmico de Harness/Prompt/Context Engineering & Anti-Silo Fix)
- **Fechamento de Gaps de Wiring**: **Wiring 1**: formalizada dependência operacional em `source_docs:` para agentes chave de orquestração, auditoria e arquitetura.
- **Quality Gate Determinístico**: Novo teste restrito `test_wiring_of_new_skills_in_consumer_agents()` em `tests/governance_audit/test_harness_engineering_governance.py` validando deterministamente.
- **Governança & Portão de Reúso Sistêmico (R-055 / Q1)**: Registrada recomendação para futura auditoria sistêmica global automatizada `.index.json` × `source_docs:` em todo o catálogo de agentes.

## [2.36.0] — 2026-09-23

### Adicionado (Harness Engineering Patterns & Sincronização Normativa R-061)
- **Pesquisa de Mercado 2026**: consolidação de práticas de Harness Engineering a partir de referências públicas de mercado: Diagnóstico sistemático de causa-raiz: segregação entre falhas de.
- **Governança & Cascata Normativa (R-015 / R-046 / R-055 / R-061)**: `CLAUDE.md`: formalização da regra normativa **R-061** (Diagnóstico de Harness-vs-Modelo e Poda Anti-Bloat de Instrução).
- **Correção Pós-Cascata**: a primeira aplicação da cascata pelo `governance-maintainer` converteu inadvertidamente a chave `skills` de `.github/skills/.index.json` de **array** para **objeto/dict**.

## [2.35.0] — 2026-09-23

### Adicionado (Harness Engineering — Sensores, Padrão Gerador–Avaliador Cético & Garbage Collection Contínuo)
- **Pesquisa de base**: síntese das descobertas de mercado 2026 sobre Engenharia de Harness aplicadas ao ecossistema `deep-agents-copilot`.
- **[PROPOSTA-1] Positive Prompt Injection em Sensores Computacionais**: Novo helper `tests/governance_audit/_helpers.py` (`remediation(message, fix_hint=...)`) formatando mensagens de `assert` com.
- **[PROPOSTA-2] Padrão Gerador–Avaliador Cético**: Nova seção `§ 1.4` em `.github/agents/workflows.md` formalizando o padrão.
- **[PROPOSTA-3] Continuous Garbage Collection & Drift Detection**: Nova skill `.github/skills/continuous-garbage-collection-patterns/SKILL.md` cobrindo 5 categorias de drift e o protocolo de.

## [2.34.1] — 2026-09-23

### Refatorado & Otimizado
- **Desduplicação e Redução de Instruction Bloat em `.github/copilot-instructions.md`**: **Consolidação de SSOT e Remoção de Redundâncias**: Redução das seções de Think-in-Code (R-008) (R-060).

## [2.34.0] — 2026-09-23

### Padronizado & Refatorado
- **Padronização Universal do Cabeçalho H1 em 100% dos Agentes e Templates**: **Eliminação de Inconsistência Estrutural e Duplicação de Nomes**: Unificação do H1 de todos os 86 arquivos de agents e.

## [2.33.4] — 2026-09-23

### Corrigido (Unificacao MUTATING/READONLY em execution_protocol)
- **Gap identificado**: a fonte canonica introduzida em [2.33.3] mantinha 2 blocos quase identicos (MUTATING/READONLY), diferindo apenas em 3 palavras cosmeticas no item 3 - a redacao READONLY ja.
- **Correcao**: unificado em um unico bloco canonico `STANDARD` em `tools/agent_protocol_sync/_execution-protocol-fragment.md`. Papel `CUSTOM` (`code-knowledge-graph`) mantido como excecao pinada.
- **Sincronizacao Aplicada**: `protocol_roles.json` convertido; `sync_execution_protocol.py --apply` corrigiu automaticamente os 50 agents que ainda tinham a redacao antiga.
- **Estado Final**: 0 drift confirmado via `--check` nos 77 agents; suite de testes atualizada.

## [2.33.3] — 2026-09-23

### Adicionado (Fonte Unica para execution_protocol — Fim da Duplicacao Manual de R-059/R-060)
- **Diagnostico**: o bloco `<execution_protocol>` estava duplicado manualmente em 77 dos 86 agents, com guardrail de teste fraco (R-060).
- **Solucao**: replicado o padrao ja usado por `tools/agentcard_exporter` para o execution_protocol: Nova fonte canonica `tools/agent_protocol_sync/_execution-protocol-fragment.md` com 2 blocos.
- **Guardrail Fortalecido**: novo teste `test_execution_protocol_sync_tool_reports_zero_drift` substitui a checagem fraca de substring por comparacao byte-a-byte via o proprio script de sync.
- **Estado Validado**: 0 drift detectado nos 77 agents na execucao inicial do script (textos ja estavam consistentes; ferramenta agora formaliza e protege essa consistencia).

## [2.33.2] — 2026-09-23

### Alterado (Consolidacao de Model Routing por Perfil de Agent)
- **Correcao de Drift de Deteccao (Transparencia)**: Auditoria inicial reportou 21 agents "sem modelo declarado" devido a regex sensivel a quebra de linha CRLF que falhou ao ler o frontmatter de.
- **Upgrade Gemini 3.8 Flash -> Claude Sonnet 5.5 (13 agents)**: Aplicado a agents cujo perfil exige julgamento de alto risco ou raciocinio multi-arquivo profundo.
- **Sincronizacao Multi-Fonte**: Atualizados em lote via `ctx_execute` (all-or-nothing): 13 arquivos `.agent.md`, 3 entradas em `.github/agents/catalog.yaml`.
- **Estado Final do Ecossistema**: 30 agents em `Claude Sonnet 5.5` (antes: 17) / 56 agents em `Gemini 3.8 Flash` (antes: 69) - 100% sem drift entre `catalog.yaml` e `.agent.md`.

## [2.33.1] — 2026-09-23

### Corrigido (Auto-Auditoria Pos-Implementacao de R-060)
- **Propagacao Sistemica de R-060 para 100% dos Agentes Executores**: **Gap Identificado**: A regra R-060 havia sido formalizada apenas em CLAUDE.md, copilot-instructions.md.
- **Correcao de Corrupcao de Caracteres de Controle em Arquivos de Governanca**: **Causa Raiz**: Sequencias de escape Python (\a, \b, \f) presentes em palavras como ask_questions, build-if-missing.
- **Quality Gate**: 165/165 testes deterministicos aprovados (tests/governance_audit/ + tests/routing_gate/), incluindo os 2 novos testes de guardrail (propagacao R-060 e anti-corrupcao).

## [2.33.0] — 2026-09-24

### Adicionado & Formalizado
- **Teto Rígido de Tool Turns, Warm Start Compulsório e Consolidação de Queries em**: **Mitigação da Dívida de Tokens Quadrática O(N^2)**: Introduzida a regra normativa **R-060** para eliminar.
- **Atualização Sistêmica de Artefatos**: CLAUDE.md: Adição de R-060 e atualização do índice normativo para R-001..R-060.

## [2.32.0] — 2026-09-24

### Adicionado & Formalizado
- **Universalização do Protocolo Plan-Then-Batch em 100% dos Agentes Não-Routers**: **Extensão Holística do Escopo**: Ampliação do protocolo para todos os 27 agentes analíticos, advisory.
- **Blindagem do Router contra Discovery de Modelos em Tempo de Execução**: **Eliminação de Runtime Discovery**: Formalizada a proibição inegociável de o `@agent-router` e domain routers chamarem.
- **Sincronização Atômica de Catálogos (R-015 / R-040)**: Atualização com paridade estrita em `.github/agents/catalog.yaml` e nos 7 sub-catálogos hierárquicos de domínio.
- **Quality Gates Determinísticos no Pytest (`tests/governance_audit/`)**: Atualização e expansão de `test_context_mode_precedence_governance.py` com novas asserções cobrindo 100% dos 78 agentes.

## [2.31.0] — 2026-09-24

### Adicionado & Formalizado
- **Instituição da Regra R-059, Regra do Limiar >= 2 e Protocolo Plan-Then-Batch**: **Diagnóstico e Causa-Raiz**: Identificado que agents executores mantinham chamadas unitárias sequenciais de.

## [2.30.0] — 2026-09-23

### Adicionado & Formalizado
- **Instituição da Regra R-058 e Invariante 20: Blueprint Técnico e Decomposição O**: **Diagnóstico e Causa Raiz**: Identificado que o `@agent-router`, ao despachar novas funcionalidades de stack.
- **Instituição do 9º Workflow Canônico: `WORKFLOW-PROMPT-SYNTHESIS` e Comando Ope**: **Propósito**: Conduzir o refinamento estrutural de solicitações, mineração determinística de contexto no.

## [2.29.0] — 2026-09-21

### Adicionado & Endurecido
- **Extensão Universal da Precedência Mandatória de Context-Mode e `ctx_batch_exec**: **Diagnóstico e Eliminação de Gaps**: Identificado que 13 agentes não-roteadores e múltiplos prompts não.

## [2.28.0] — 2026-09-21

### Adicionado & Endurecido
- **Single-Turn MCP Batching Compulsório e Erradicação de MCP Tool Chaining Sequen**: **Diagnóstico e Causa Raiz**: Identificado que agentes operacionais e de preparação (como `pr-gatekeeper` e.

## [2.27.0] — 2026-09-21

### Modificado & Endurecido
- **Blindagem Completa de Renderização de Blocos de Código e Formatação de PR no `**: **Eliminação da Corrupção por Fences Aninhados**: Identificada e corrigida a causa raiz da quebra de.

## [2.26.0] — 2026-09-21

### Modificado & Endurecido
- **Blindagem Completa e Sistêmica de Precedência de Context-Mode em Todos os Agen**: **Varredura Universal e Blindagem em Lote**: Aplicada a blindagem em 100% dos 49 agentes executores/mutadores do.

## [2.25.0] — 2026-09-20

### Modificado & Endurecido
- **Endurecimento da Precedência Mandatória de Context Mode**: **Uso 100% Obrigatório do Context-Mode**: O uso de `context-mode` passa a ser **100% OBRIGATÓRIO** tanto para LEITURAS quanto para.

## [2.24.0] — 2026-09-20

### Adicionado
- **Proibição Estrita de Terceirização de Edição Manual ao Usuário por Agentes Ana**: Formalização da regra normativa **R-057** em `CLAUDE.md` e `.github/copilot-instructions.md`.

## [2.23.0] — 2026-09-19

### Adicionado
- **Consolidação Determinística dos Workflows de Resolução de Bugs e Refatoração Estrutural (`WORKFLOW-BUG-FIX` e `WORKFLOW-REFACTORING`)**: **`WORKFLOW-BUG-FIX`**:.

## [2.22.0] — 2026-09-19

### Removido & Descomissionado
- **Descomissionamento Definitivo e Higienização do `agentic-memory-manager`**: Remoção física do arquivo `.github/agents/agentic-memory-manager.agent.md`.

## [2.21.0] — 2026-09-19

### Adicionado
- **Consolidação de Segurança de Aplicação e Gestão Holística de Vulnerabilidades**: Criação do **Guia Canônico de Segurança de Aplicação e Vulnerabilidades**.

## [2.20.0] — 2026-09-19

### Adicionado
- **Consolidação Documental sob Framework Diátaxis & Padrões Globais de Governança**: Criação do **Portal Central de Documentação** em `docs/README.md`, organizando 100% dos artefatos técnicos do.

## [2.19.0] — 2026-09-19

### Adicionado
- **Blindagem Determinística do Workflow de Migração e Camada de Redundância Pós-M**: Elevação do `WORKFLOW-FRAMEWORK-MIGRATION` em `workflows.md` de 5 para **6 etapas canônicas**.

## [2.18.0] — 2026-09-19

### Adicionado
- **Precedência Mandatória de Context Mode em Modificação de Arquivos**: Instituição da regra normativa R-056 em `CLAUDE.md` e `copilot-instructions.md`.

## [2.17.0] — 2026-09-19

### Adicionado
- **Metodologia Test-Last e Isenção de Testes Unitários para UI na Stack Frontend**: Instituição da abordagem **Test-Last com Verification Gate Obrigatório** (Implementation-First) para agentes.

## [2.16.0] — 2026-09-19

### Adicionado
- **Portão de Reúso e Generalização Sistêmica em Governança (R-055 / Anti-Silo Fix)**: Instituição da regra normativa R-055 em `CLAUDE.md`, `copilot-instructions.md` e `workflows.md`.
### Aprimorado
- **Integração do Gate nos Agentes de Governança**: `@agent-auditor`: inclusão de avaliação compulsória de reúso sistêmico (Q1/Q2/Q3) na `Decision Tree`.

## [2.15.0] — 2026-09-19

### Adicionado
- **Prevenção Compulsória de R-054 no `@governance-factory` (v1.3.0)**: Adição da seção normativa *Baseline R-054.
### Aprimorado
- **Auditoria Dinâmica de Smells e R-054 no `@agent-auditor` (v1.2.0)**: Substituição da contagem estática ("14/13 categorias de smell") por referência dinâmica a.
- **Saneamento Documental em `@governance-factory`**: Remoção de bloco de texto corrompido/órfão remanescente no final do arquivo.

## [2.14.0] — 2026-09-19

### Adicionado
- **Governança Estrita de Routers**: Instituição da regra mandatória de **Zero Pre-Routing Discovery**: proibição absoluta de tool calls de leitura exploratória de código.
### Aprimorado
- **Saneamento Universal de Ferramentas em Routers**: Restrição estrita de ferramentas no `agent-router` central, nos 7 supervisores de domínio e no template canônico `router-agent.md` ao baseline.
- **Blindagem Total da Delegação Plana (Flat Delegation / Smell 2.20)**: Proibição expressa de invocar especialistas ou executores downstream via `run_subagent` por dentro de qualquer roteador.

## [2.13.0] — 2026-09-19

### Aprimorado
- **Padronização Canônica de Formato de Saída**: Inserção do banner universal de visibilidade `Agente Ativo: <slug>` e `[Se aplicável] Handoff: <origem> → <destino>` nos blocos de código Markdown de.
- **Evolução de Autonomia Delimitada & Gate Pattern no `@prompt-structuring`**: Implementação do modelo de 3 Tiers para mitigar anti-padrões de mercado em sistemas multi-agentes: Tier 1.

## [2.12.0] — 2026-09-17

### Adicionado
- **Blindagem Determinística contra "Cleverness Trap" & State-Locking Universal**: Implementação compulsória do protocolo de **State-Locking** (`[CURRENT_STATE_LOCK: ...]`) e **Halting Conditions**.
### Aprimorado
- **Endurecimento dos Agentes Planejadores / Deliberativos (Grupo 1)**: `@tech-solution-architect`, `@refactor-planner`, `@feature-planner`, `@requirements-analyst` e `@test-strategy`: saneamento de.
- **Endurecimento dos Supervisores Hierárquicos / Domain Routers (Grupo 2)**: `@angular-router`, `@spring-boot-router`, `@spring-reactive-router`, `@ejb-router`, `@database-router`.
- **Endurecimento dos Executores Táticos (Grupo 3)**: 17 agentes executores: trava de execução em TDD estrito.

## [2.11.0] — 2026-09-16

### Adicionado
- **Matriz De-Para Bidirecional & Prevenção Canônica de Gaps em `WORKFLOW-FRAMEWOR**: Instituição da **Matriz De-Para de Migração & Rastreabilidade de Gaps** como Single Source of Truth obrigatória.
- **Decomposição Estrutural Exaustiva em 5 Dimensões Críticas (Estado 1)**: Eliminação de avaliações superficiais ou limitadas ao "happy path": decomposição sistemática e obrigatória em (1) Borda.
- **Protocolo Brownfield In-Flight**: Mecanismo específico e obrigatório para migrações já iniciadas, parciais ou inacabadas no repositório de destino.
- **Faseamento Orientado a Risco e Impacto Ancorado na Matriz De-Para (Estado 2)**: Fases autônomas entregáveis (B1..BN) onde cada fase possui uma lista explícita de IDs De-Para sob sua.

## [2.10.0] — 2026-09-15

### Adicionado
- **Regra R-052 e Erradicação do Anti-Padrão Sticky Agent**: Nova regra normativa `R-052` em `CLAUDE.md` e `.github/copilot-instructions.md`.
- **Catalogação do Smell 2.22 em `governance-audit-patterns`**: `Smell 2.22 — Sticky Agent e Falha de Reset de Workflow (R-042 / R-052)`: catalogado com severidade Bloqueador.
### Aprimorado
- **Ajuste Fino na Regra R-042**: Esclarecida a cláusula de perfil híbrido dos specialists, restringindo a continuidade sem handoff estritamente a refinamentos imediatos de uma mesma tarefa em.

## [2.9.0] — 2026-09-15

### Adicionado
- **Nova Skill Agnóstica `frontend-visual-feedback-loop`**: Padrão canônico de mercado (2025–2026) para execução do Visual Feedback Loop (VFL) desacoplado de framework.
- **Formalização do Smell 2.21 em `governance-audit-patterns`**: `Smell 2.21.
### Aprimorado
- **Evolução da Regra R-033 e Erradicação do Drift Documental por Autorreflexão**: Reformulação formal de R-033 no `CLAUDE.md` e `copilot-instructions.md`: distinção entre a proibição estrita de.
- **Tratamento Especializado de Bugs de Layout no `WORKFLOW-BUG-FIX`**: Formalização do Cenário C no Estado 2 com o ciclo VFL, capturas multi-viewport (375px/768px/1440px) e asserções estritas de.

## [2.8.10] — 2026-09-14

### Refatorado & Saneado
- **Limpeza Profunda de Seções Não-Homologadas e Citações em Frontmatter/Templates**: Extirpação completa das seções legadas e redundantes no corpo Markdown em 9 arquivos de roteadores e templates.
- **Fortalecimento do Gate de Homologação de Seções (Smell 2.9)**: `tests/governance_audit/test_template_sections.py`: O teste de homologação foi expandido para cobrir **100% dos agentes**.

## [2.8.9] — 2026-09-14

### Adicionado & Aprimorado
- **Guia Canônico de Arquitetura e Governança (arc42 / Diátaxis / IEEE 42010)**: Criado o documento canônico `docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md` estruturado conforme as 12.

## [2.8.8] — 2026-09-14

### Adicionado & Aprimorado
- **Context Engineering & Artifact Offloading em Handoffs (Anthropic 2026 Trends)**: Atualizada a skill `.github/skills/handoff-governance/SKILL.md` com a formalização dos 4 pilares do Context.
- **Multi-Agent Circuit Breakers com Budget de Falhas e Rollback Atômico**: Implementado em `.github/skills/handoff-governance/SKILL.md` o Circuit Breaker de Falhas com Retry Budget estrito.
- **Segurança de Ferramentas MCP e Sandboxing (NSA CSI MCP Security 2026 / CSA v1)**: Adicionada a seção 4.9 em `.github/skills/agent-safety-guardrails/SKILL.md` estabelecendo:.
- **Padronização e Exportação A2A AgentCard**: Criado o schema canônico aberto `docs/schemas/agentcard.schema.json` para interoperabilidade e especificação declarativa de agentes.

## [2.8.7] — 2026-09-14

### Adicionado & Aprimorado
- **Alinhamento com OWASP Top 10 for Agentic Applications 2026 (ASI01..ASI10:2026)**: Atualizada a skill `.github/skills/agent-safety-guardrails/SKILL.md` com a taxonomia formal oficial da OWASP.
- **Nova Skill de Governança: `git-worktree-governance`**: Criada a skill `.github/skills/git-worktree-governance/SKILL.md` (Tier 2, categoria governance) padronizando o ciclo de vida de 5 etapas.
- **Evals Lab — Validação E2E e Simulação dos 8 Workflows Canônicos (R-050)**: `tests/operational_flow/workflow_eval_simulator.py`: Implementado o método `simulate_state_bag_transitions()` para.

## [2.8.6] — 2026-09-14

### Refatorado & Consolidado
- **Consolidação Global de SSOT no Frontmatter e Extirpação de Redundâncias**: Unificação de 100% das dependências normativas, contextuais e skills no frontmatter YAML `source_docs:`.
- **Refinamento e Blindagem dos Templates Canônicos (`.github/templates/`)**: `agent-template.md`, `operational-agent.md`, `research-agent.md`: Adicionada diretriz normativa de SSOT de documentação.
- **Quality Gate de Governança — Gate de Homologação de Seções (Tier 1)**: `tests/governance_audit/test_template_sections.py`: Implementados 4 novos testes determinísticos para barrar.

## [2.8.5] — 2026-09-14

### Aprimorado
- **Evolução do Agent `bug-triage` (v1.1.0 — Blast Radius Proativo & Challenge Gate de Regras)**: `.github/agents/bug-triage.agent.md`:.
- **Codificação de Diretrizes Anti-Band-Aid e Timing Reativo**: `code-tracing/SKILL.md`: Adicionados 4 novos anti-padrões essenciais de diagnóstico: máscara visual.

## [2.8.4] — 2026-09-13

### Corrigido & Sincronizado
- **Saneamento de Referências a Agentes Descomissionados nos READMEs e Catálogo**: `README.md`: Atualizada a seção de especialistas de stack para a topologia vigente de supervisores de domínio.
- **Fortalecimento da Suíte de Testes e Governança Estática (Smell 2.1)**: `tests/operational_flow/test_operational_workflows.py`: Atualizado o conjunto `LEGACY_DEPRECATED_AGENTS` para incluir.

## [2.8.3] — 2026-09-12

### Adicionado & Aperfeiçoado
- **Persistência Local e Nuvem de Incidentes de Workflows (`tools/incident_recorder`)**: **Especificação de Requisitos (`docs/requirements/REQ-workflow-incident-persistence.md`)**:.

## [2.8.2] — 2026-09-12

### Adicionado & Aperfeiçoado
- **Motor Agnóstico de Migração de Tecnologias Legadas (Agnostic Legacy Migration Engine)**: **Especificação de Requisitos (`docs/requirements/REQ-migration-engine.md`)**:.

## [2.8.1] — 2026-09-12

### Adicionado & Aperfeiçoado
- **Geração Integrada de Título e Descrição de Pull Request (`@pr-gatekeeper` e `/commit`)**: **`pr-gatekeeper.agent.md` (v1.1.0 → v1.2.0)**:.

## [2.8.0] — 2026-09-11

### Adicionado
- **Consolidação de Workflows com Padrões de Mercado**: **Expansão de 5 para 8 Workflows Canônicos e de Ciclo de Vida**: Pesquisa de mercado e benchmarking com padrões corporativos identificou e.

## [2.7.0] — 2026-09-11

### Refatorado & Simplificado
- **Coesão em `.github/` — Simplificação Arquitetural e Desacoplamento Definitivo**: **Extinção de `docs/ai-context/catalog.yaml` e `docs/ai-context/binding.md`**: Eliminação de manifestos.

## [2.6.2] — 2026-09-11

### Adicionado
- **Prompt `/init-context` — Verificação de Deriva de Stack e Instruções Locais**: Adicionado novo PASSO 7 para detectar discrepâncias entre os manifestos reais dos projetos locais externos e os.

## [2.6.1] — 2026-09-11

### Refatorado
- **Desacoplamento de Cardinalidade Normativa (Herança Aberta de Governança)**: Substituição da referência rígida ao contador fechado (`R-001..R-051`) pela herança aberta desacoplada em 45.
- **Redefinição do Smell 2.15**: Inversão de sentido do Smell 2.15 de "range desatualizado" para "Acoplamento Rígido de Range Normativo (Hardcoded Range Coupling)".

## [2.6.0] — 2026-09-10

### Adicionado
- **Suíte de Testes de Conformidade de Templates (Disjunção 1-de-N)**: `tests/governance_audit/test_template_sections.py`: Implementação estática da regra de conformidade polimórfica (Smells 2.9.
- **Suíte de Testes de Trajetórias de Workflows Canônicos (R-050) & Simulador MAS**: `tests/operational_flow/casos-workflows.yaml`: Catálogo declarativo com 8 cenários de ponta a ponta (E2E).
- **Documentação Arquitetural de Testes MAS (`tests/README.md`)**: Documentação completa da Pirâmide de Testes de Sistemas Multi-Agentes (MAS), detalhamento arquivo por arquivo.
### Alterado
- **Configuração do Pytest (`pytest.ini`)**: Inclusão da diretiva `pythonpath = .` garantindo resolução determinística da raiz do projeto independente da forma de invocação do runner.

## [2.5.0] — 2026-09-10

### Adicionado
- **Mapa do Repositório Canônico (`docs/ai-context/repo-map.md`)**: Fonte de verdade de navegação determinística de arquivos (princípio Zero Blind Searches), contendo guia de localização direta.
- **Whitelist de Busca e Indexação para ripgrep (`.ignore` e `.rgignore`)**: Arquivos de configuração na raiz liberando a varredura de `!.github/` e `!.github/**` pelas ferramentas de busca.
### Alterado
- **Desambiguação Canônica dos Catálogos (`catalog.yaml`)**: Formalizada a distinção unívoca entre o Catálogo de Agents e o Catálogo de Binding.

## [2.4.0] — 2026-09-10

### Adicionado
- **Novos Smells de Governança (20 Smells Canônicos)**.
- **Reforço de Definition of Done em Frontend**: `angular-implementation-patterns/SKILL.md` ganha passo 0 (Reuse-First) e passo 7 (Navegabilidade) no Workflow.
### Autocrítica de Processo (Achado de Execução)
- Identificado e documentado que a fidelidade de handoff da Etapa 5 (`tdd_domain_implementation`) de `WORKFLOW-FEATURE-DEVELOPMENT` depende de invocação **real** de `run_subagent` para o specialist.

## [2.3.0] — 2026-09-10

### Adicionado
- **Regra Normativa R-051**: Formalizada em `CLAUDE.md` e `efficient-batch-code-modification/SKILL.md` (§ 5).
- **Snippet Canônico de Edição Segura**: Materializado em `.github/skills/efficient-batch-code-modification/snippets/safe-single-file-edit-pattern.js` como template reutilizável para context-mode.
### Evoluído
- **Auditoria e Refinamento Profundo dos 5 Workflows Canônicos**: **Resolução de Papéis Genéricos (`specialist-<papel>`)**: Formalizada convenção em `workflows.md` § 1.3 mapeando papéis agnósticos.
- **Sincronização de Ranges Normativos**: Atualizados 100% dos 44 agents com seção de regras herdadas e todos os prompts e catálogos para a numeração consolidada `R-001..R-051`.

## [2.2.0] — 2026-09-10

### Adicionado
- **Regra Normativa R-050**: Formalizada em `CLAUDE.md` a obrigatoriedade de vincular e executar toda solicitação técnica através de um dos 5 Workflows Canônicos:.
- **Especificação Canônica dos 5 Workflows (`.github/agents/workflows.md`)**: Novo artefato canônico com diagramas Mermaid em `flowchart TD`, matrizes de entrada/saída.
### Evoluído
- **Regra Normativa R-041 (Fast-Path Determinístico)**: Ajustada em `CLAUDE.md`, `copilot-instructions.md`, `routing-graph.yaml` e `agent-router.agent.md` para permitir que solicitações com.
- **Agent Router (`@agent-router` v2.0.0)**: Inserido Passo 0.4 (Classificação de Fast-Path) antes do Passo 0.5 e inclusão de `Workflow:` e `Etapa do Workflow:` no Formato de Saída.

## [2.1.0] — 2026-09-06

### Adicionado
- **Regra Normativa R-046**: Formalizada em `CLAUDE.md` a obrigatoriedade da skill operacional `efficient-batch-code-modification` em toda tarefa que envolva escrita.
- **Injeção Compulsória em `prompt-structuring` (R-046)**: Adicionado mecanismo no refinamento de prompt para injetar nativamente a constraint de dry-run prévio em memória.
### Evoluído
- **Agents Executores de Código Alinhados a R-046**: Inclusão explícita de `efficient-batch-code-modification` em `source_docs`, `skills:` e diretrizes operacionais de 26 agents.
### Consolidado
- **Consolidação Biparadigma de Modelos nos Agents e Prompts**: **Paradigma do Prompt Procedural**: Definido `"Gemini 3.8 Flash"` como escolha padrão em toda a base.

## [2.0.0] — 2026-09-06

### Adicionado
- **Arquitetura Hierárquica de Routers de Domínio**: Decomposição de agentes monolíticos em ecossistemas de domínio com sub-catálogos locais e isolamento em pastas: **Frontend Angular**: Supervisor.
- **Suporte a `type: stack` no `@governance-factory`**: Nova capacidade de geração de ecossistemas tecnológicos completos estruturados em pastas de domínio com sub-catálogo.
### Removido
- Descomissionamento dos agentes monolíticos substituídos pela nova topologia hierárquica: `angular-engineer.agent.md`, `spring-boot-engineer.agent.md`, `spring-reactive-engineer.agent.md` e.

## [1.9.0] — 2026-09-04

### Adicionado
- **`tools/context-insight-visualizer/`**: Suíte analítica completa e dashboard standalone para métricas locais do Context Mode MCP.

## [1.8.0] — 2026-08-30

### Adicionado
- **`agent-contracts/SKILL.md` § 0 — Banner Universal de Identidade**: nova regra de ouro; toda resposta de TODO agent (não apenas `agent-router`) abre com `Agente Ativo: <name>`.
- **`agent-router.agent.md`**: novo campo `Transição` no Formato de Saída, explicitando "Nova triagem (1º turno)" | "`<origem>` → `<atual>` (motivo: deriva_de_intencao)" | "Sem mudança".
### Corrigido
- **Gap de visibilidade em R-042**: antes desta correção, apenas o `agent-router` declarava "Agente Ativo".
### Alterado
- **`agent-factory.agent.md`**: Padrões Obrigatórios (item 10), Checklist e Formato de Saída passam a validar a presença do banner em todo agent criado/revisado.

## [1.7.0] — 2026-08-30

### Corrigido
- **Gap estrutural de tooling para R-042**: `run_subagent` era ausente no frontmatter `tools:` de 3 agents.
- **Causa raiz nos templates**: `templates/research-agent.md` e `templates/operational-agent.md` — todo agent novo criado por `agent-factory` herdava o gap. Ambos corrigidos.
### Adicionado
- **`agent-contracts/SKILL.md` § 9 — Ferramentas Mínimas por Agent (Tooling Baseline)**: tabela de tools mínimas obrigatórias por perfil; regra de ouro.
### Alterado
- **`CLAUDE.md` (R-042)**, **`copilot-instructions.md`** e **`agents/README.md`** § 8.

## [1.6.0] — 2026-08-30

### Alterado
- **Especialistas `angular`, `spring-boot`, `spring-reactive` migrados de perfil "**: além de análise/recomendação, agora também implementam feature nova e correção de bug dentro do próprio domínio.
### Adicionado
- **3 novas skills de implementação** (Tier 2, pesquisa de mercado 2026 via Tavily): `angular-implementation-patterns` — fronteira Signals/RxJS, testing-first, checklist de PR.
### Corrigido
- **SYNC (R-015)**: `.github/skills/.index.json` — corrigido gap pré-existente onde as 3 skills de análise nunca haviam sido registradas; total_skills 39 → 45 (3 análise + 3 implementação novas).
### Adicionado
- **R-042**: R-037 passa a se aplicar explicitamente a **cada novo turno**, não só ao primeiro.
### Corrigido
- Gap de catálogo: `angular`, `spring-boot` e `spring-reactive` já existiam em `catalog.yaml`/`README.md` mas nunca haviam sido registrados como nós roteáveis em `routing-graph.yaml` nem na Decision.
### Pesquisa de mercado (base da decisão)
- OpenAI Agents SDK — padrão `handoff()` + `transfer_back_to_*` (retorno explícito de controle).

## [1.3.0] — 2026-08-29

### Adicionado
- **Agent `requirements-analyst`**: perfil de elicitação prospectiva para transformar pedido de negócio ambíguo em requisitos funcionais/não-funcionais estruturados e testáveis.
- **Skill `requirements-engineering-patterns`** (Tier 2): base de conhecimento consolidada via pesquisa de mercado.
### Corrigido
- **SYNC de catálogos (R-015/R-040)**: atualização atômica de `agents/catalog.yaml` (23 → 24 agents), `skills/.index.json` (38 → 39 skills).
### Conformidade
- Mantida separação de responsabilidades sem duplicação (R-003): `requirements-analyst` opera em requisito **novo/prospectivo**.

## [1.2.0] — 2026-06-12

### Adicionado
- **Prompt `/commit`**: Gera mensagem Conventional Commits (PT-BR) sem executar git autonomamente.
- **Prompt `/review`**: Revisão de código por qualidade, convenções e impacto com relatório por severidade.
### Corrigido
- **SYNC**: `.index.json` com `total_agents: 10` (corrigido para 15) e 2 skills sem entrada (`project-scanner`, `project-context-builder`)
### Conformidade R-038
- Todos os arquivos de governança agora seguem o padrão de genericidade obrigatória (R-038)

## [1.1.0] — 2026-06-11

### Adicionado
- **Prompt `/init-context` v1.1**: PASSO 2 informativo (não bloqueante), PASSO 3 condicional por sessão, PASSO 4 lista projetos por nome.
- **Simplificação `binding-initializer`**: 5 perguntas → 1 pergunta (só nome do ecossistema)
### Corrigido
- `add-project-context`: reduzido de 4 para 3 perguntas (Q2 tipo removida — inferida pelo scanner)
- `QUICK-START.md`: exemplos atualizados com caminhos corretos de projeto.

## [1.0.0] — 2026-06-10

### Adicionado
- Estrutura inicial de governança (`CLAUDE.md`, `copilot-instructions.md`)
- 14 agents: `agent-router`, `bug-triage`, `test-strategy`, `test-implementation`, `refactor-planner`, `impact-architect`, `docs-curator`, `research-router`, `analysis-architect`, `agent-factory`.
- 17 skills: `context-mode`, `context-builder`, `context-compact`, `sonarqube-governance`, `tavily`, `mermaid-diagrams`, `agent-contracts`, `handoff-governance`, `confidence-fallback-policy`.
- Prompts de workflow: `/research`, `/plan`, `/implement`, `/validate` (renomeados de PT→EN em 2026-08-29)
