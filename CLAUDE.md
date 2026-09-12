# CLAUDE.md — governanca-ai-reutilizavel

## 1) Objetivo

Este arquivo é a fonte de verdade operacional para o uso de IA em qualquer repositório que adote esta base de governança.

- Escopo desta base: estabelecer governança genérica, desacoplada de domínio e tecnologia.
- Regra de ouro: evitar duplicação de regra entre arquivos de instrução.

## 2) Hierarquia de Instruções

Em caso de conflito, siga esta ordem:

1. System
2. Developer
3. User
4. Arquivos locais deste repositório (`CLAUDE.md`, `.github/*`)

## 3) Regras Normativas (R-001..R-051)

- **R-001 (Escopo)**: altere apenas o que foi solicitado.
- **R-002 (Mudança mínima)**: prefira alterações pequenas, reversíveis e rastreáveis.
- **R-003 (Sem duplicação)**: regra global fica em `CLAUDE.md`; `.github/*` referencia, não copia.
- **R-004 (Rastreabilidade)**: sempre citar caminhos exatos dos arquivos tocados.
- **R-005 (Não inventar catálogo)**: não listar agent/skill inexistente.
- **R-006 (Pré-condições — Roteador)**: vide [`agent-router.agent.md`](.github/agents/agent-router.agent.md) § *Matriz de Decisão: Quando Pedir Contexto*. Regra específica do roteador; não é norma global.
- **R-007 (Decisões explícitas)**: registrar decisões relevantes em bullets curtos.
- **R-008 (Execução preferencial via context-mode — Think in Code)**: para leitura, escrita, análise, busca e remoção de arquivos, use **100% o `context-mode` MCP** (`ctx_execute`, `ctx_execute_file`, `ctx_batch_execute`, `ctx_index`, `ctx_search`). O processamento de dados e mutações de filesystem devem ocorrer no sandbox em código, imprimindo apenas o resultado derivado limpo. `read_file` e `replace_string_in_file` são restritos a edições cirúrgicas pontuais do editor. `run_in_terminal` é **FALLBACK de última instância** restrito exclusivamente a comandos de ciclo de vida (`git`, `npm install`, `mvn`, `pytest`) — comandos de inspeção/varredura de arquivos no shell (`find`, `grep`, `cat`, `dir`, scripts inline `node -e`) são estritamente proibidos. Se o Context Mode falhar, PARE e informe o problema.
- **R-009 (Sem arquivos autônomos)**: nunca crie arquivos de qualquer formato sem solicitação explícita. Se julgar necessário, SOLICITE aprovação ANTES.
- **R-010 (Segurança)**: nunca expor credenciais, tokens ou dados sensíveis.
- **R-011 (Sem overengineering)**: implementar o necessário para a fase atual.
- **R-012 (Clarificação progressiva)**: antes de implementar, avalie se a solicitação tem escopo suficiente. Se ambígua, use `ask_questions` com sugestões pré-preenchidas — nunca pergunte em aberto. Máximo 3 perguntas por ciclo. Não aplique em solicitações simples com intenção clara.
- **R-013 (PT-BR operacional)**: documentação de governança e respostas operacionais em PT-BR.
- **R-014 (Um objetivo por arquivo)**: cada documento deve ter responsabilidade clara.
- **R-015 (Atualização atômica de catálogo)**: alterou governança, atualize os READMEs de catálogo na mesma entrega.
- **R-016 (Evidência objetiva)**: resultados com evidência (`arquivo`, `simbolo`, `comando`) e próximo passo mínimo.
- **R-017 (PT-BR com acentuação correta)**: em arquivos `.md` redigidos em português, use ortografia e acentuação corretas. Evite transliteração ASCII quando o termo exigir acento.
- **R-018 (Planejamento paralelo)**: ao estruturar planos, identifique etapas independentes. Marque com `[P]` paralelo ou `[S]` sequencial. Etapas sem dependência DEVEM ser agrupadas para execução simultânea.
- **R-019 (Busca web proativa com ctx-cache)**: antes de propor solução para cenários de incerteza técnica, siga o fluxo: `ctx_search` no cache primeiro → Tavily se insuficiente → indexar resultado via `ctx_index`. Para docs externos, prefira `ctx_fetch_and_index` (cache 24h nativo). Não use para perguntas sobre o próprio codebase.
- **R-020 (Falha compacta)**: ao reportar erros, use formato 3 linhas — Causa / Local / Ação sugerida. Proibido stack trace completo sem pedido. Máximo 5 erros; resto: `(+N erros similares)`.
- **R-021 (Model Routing Signal)**: avalie o tipo da tarefa antes de agir. Emita sinal visual **antes** de codar quando a tarefa exigir modelo 1× ou superior. MCP tools amplificam modelos menores — use-os antes de escalar. Nunca use modelo pesado para tarefa que modelo leve resolve.
- **R-022 (Auto-recuperação do Context Mode)**: quando `ctx_*` falhar com `Not connected`, realize **1 tentativa automática** de recuperação. Após restart, execute 1 health check (`ctx_doctor`) e retome. Se não voltar, PARE e solicite ação manual. Proibido repetir tentativas automáticas.
- **R-023 (MCP Trust Allowlist)**: conecte apenas servidores MCP confiáveis/aprovados; nunca use MCP de origem não verificada.
- **R-024 (MCP Least-Tools)**: mantenha ativas somente as ferramentas MCP necessárias à tarefa corrente.
- **R-025 (MCP Prompt Budget)**: se houver degradação por excesso de tools MCP, reduza a superfície de ferramentas antes de prosseguir.
- **R-026 (Sem código inline em agents/skills/prompts)**: arquivos `.github/agents/*.md`, `.github/skills/*/SKILL.md` e `.github/prompts/*.md` NÃO devem conter blocos de código com implementações > 8 linhas. Código real vai em `snippets/`, `templates/` ou `commands/`, referenciado por caminho ou `source_docs:`.
- **R-027 (Clarificação Obrigatória via ask_questions)**: frente a qualquer ambiguidade, use EXCLUSIVAMENTE `ask_questions` antes de agir. Proibido inferir ou deduzir intenção. A última opção sempre deve ser campo aberto. Sem exceções, ressalvado R-041 (loop controlado do agent `prompt-structuring`, limitado a 5 iterações).
- **R-028 (Estrutura de Resposta — Code Assist Standard)**: ao iniciar qualquer implementação, exiba resumo em 5 seções: **(1)** Resumo da Abordagem; **(2)** Visão Geral dos Componentes; **(3)** Implementação; **(4)** Passos Cruciais; **(5)** Notas Técnicas de Impacto. Para outros perfis de agent (router, analista, operacional), consulte o modelo de 2 camadas (universal + template por perfil) em `.github/skills/agent-contracts/SKILL.md` § 8.
- **R-029 (Postura Senior Engineer)**: **(a)** prefira bullets e tabelas a parágrafos; **(b)** código limpo sem explicações inline; **(c)** elimine introduções genéricas de IA — responda como colega sênior, preciso e focado.
- **R-030 (Checkpoint obrigatório por fase/plano)**: durante `/implement`, ao concluir cada fase (`- [x]`) e ao concluir o plano, execute `/ctx-checkpoint` imediatamente, registrando `lastStep`, `nextStep` e `source` do checkpoint na resposta.
- **R-031 (Plano Auto-Implementável — Zero-Interrupção)**: todo plano aprovado (explícito ou por contexto claro) DEVE ser executado integralmente sem interrupção nem contra-medida do agent. **Pré-voo obrigatório** antes de iniciar: **(a)** Escopo completo — todos os artefatos mapeados e dependências resolvidas; **(b)** Contingências por fase — cada passo com `[fallback: <ação alternativa se falhar>]` inline; **(c)** Critério de falha tolerável — distinguir o que é contornável (warnings, arquivo ausente, tool lenta) do que é bloqueante real; **(d)** Bloqueantes absolutos — único motivo de parada permitido: violação de R-003 (commit autônomo), exposição de credencial (R-010), ou estado de dados irrecuperável detectado. **Formato de contingência por passo:** `[S] Passo X — descrição [fallback: alternativa]`. Ao final, **relatório de execução** (o que foi feito, o que usou fallback, próximo passo) substitui checkpoints intermediários. Proibido pedir confirmação mid-plan.
- **R-032 (Nomeação de documentação)**: todo novo arquivo de documentação `.md` criado deve usar `kebab-case` no nome.
- **R-033 (Não gerar documentação automaticamente)**: nunca gere documentos `.md` se não for solicitado ou sem a aprovação por `ask_questions`.
- **R-034 (Health Check de Binding Context)**: ao iniciar trabalho em novo repositório com esta base, Copilot DEVE verificar se existem `.github/instructions/README.md` e `.github/projects.local.yaml.example`. Se faltarem: ⚠️ **ALERTAR E DISPARAR AGENT `binding-initializer`** com sequência de `ask_questions` para gerar arquivos customizados. Sem exceções — binding é pré-requisito para descoberta de adapters.
- **R-035 (Terminal sem paginação interativa — Zero Pager Bloqueante)**: NUNCA executar comandos git ou de sistema que abram pager interativo (`less`, `more`, `man`, `git diff` puro, `git log` puro, `git show` puro, `git branch`/`tag` longos) que exijam `q` para sair e travem a sessão indefinidamente em "Processing...". TODO comando git no terminal que produza saída DEVE compulsoriamente incluir flag não-interativa: **SEMPRE usar `git --no-pager <comando>`** (ex.: `git --no-pager diff ...`, `git --no-pager log ...`, `git --no-pager show ...`) OU prefixar inline com `GIT_PAGER=cat git <comando>` OU pipear com `| cat`. O uso de `git diff` puro ou `git log` puro sem `--no-pager` é **TERMINANTEMENTE PROIBIDO E BLOQUEANTE**. Em repositórios de workspace, configurar `git config core.pager cat` como salvaguarda incondicional no nível do Git.
- **R-036 (Identificador Normativo Reservado / Rastreabilidade Histórica)**: número normativo reservado e preservado para assegurar integridade referencial cruzada e rastreabilidade entre versões do catálogo de governança.
- **R-037 (Ponto de Entrada Obrigatório — Agent Router First)**: **SEM EXCEÇÕES**, toda solicitação deve começar com `@agent-router`. Controller routing é o ponto de entrada único para: **(a)** classificação de intenção; **(b)** decisão de rota; **(c)** prevenção de implementação direta sem triagem. O roteador delega para downstream (bug-triage, test-strategy, refactor-planner, docs-engineer, deep-search, tech-solution-architect) conforme necessidade. Bypass de @agent-router é violação de governança. Proibido implementar sem passar por triagem. **Salvaguarda Anti-Duplicação de Subagente**: Quando o `@agent-router` emitir o bloco de decisão (`Delegado: @<agent>`), o Orquestrador Raiz despacha o agent delegado UMA ÚNICA VEZ. Se por qualquer anomalia a resposta do subagente já contiver o resultado de execução concluída do downstream (`Resultado do @<agent>:`), o Orquestrador NUNCA deve re-invocar o mesmo agent.
- **R-038 (Genericidade Obrigatória em Governança)**: Toda documentação de governança criada em `.github/` (agents, skills, prompts, copilot-instructions) **DEVE ser genérica**, desacoplada de: **(a)** projetos específicos; **(b)** tecnologias exclusivas; **(c)** convenções de domínio particulares. Convencionalidades, adapters e exemplos concretos **PERTENCEM EXCLUSIVAMENTE A** `.github/instructions/*.instructions.md` (adapters) ou `.github/instructions/` (contexto de binding). Se uma regra de governança referencia projeto, domínio ou tech específica, é violação de R-038. Teste: substituir nome de projeto/tecnologia por `[PROJETO]` ou `[TECH]` — se deixar de fazer sentido, está muito específica para governança global.
- **R-039 (Diagramas em Markdown com Mermaid)**: Todo diagrama incorporado em arquivo `.md` **DEVE usar Mermaid** (sintaxe nativa de blocos code com linguagem `mermaid`). Razões: **(a)** versionabilidade — diagramas vivem no Git, não em binários; **(b)** portabilidade — renderização nativa em GitHub, GitLab, Notion e ferramentas de IA; **(c)** manutenibilidade — patches e reviews sem ferramentas específicas. Proibido: imagens PNG/SVG geradas externamente, Visio, Lucidchart embarcados. Se precisar de estilo avançado, use plugins Mermaid ou refatore para simplificar.
- **R-040 (Grafo de Roteamento como Fonte de Verdade)**: O roteamento de agents **DEVE ser declarado como dado estruturado** (ex.: `.github/agents/routing-graph.yaml` com nós, arestas, thresholds e política de cascata). A Decision Tree em prosa de qualquer agent-router é **documentação derivada** — não fonte única. Toda nova rota ou agente adicionado ao ecossistema exige: **(a)** entrada no grafo estruturado; **(b)** atualização da Decision Tree (derivada); **(c)** novo caso de teste em `.github/agents/evals/casos-roteamento.yaml` (equivalente ao R-015 para evals). Threshold de confiança para cada rota deve ser declarado explicitamente no grafo e reportado no output do router.
- **R-041 (Exceção de Loop Controlado — Agent `prompt-structuring` & Fast-Path Determinístico)**: por exceção formal a R-011 (sem overengineering), R-012 (clarificação progressiva, máx. 3 perguntas/ciclo) e R-027 (proibição de loop em `ask_questions`), o agent `prompt-structuring` é o **ÚNICO** agent do catálogo autorizado a operar em loop de auto-refinamento de prompt. Regras do loop: **(a)** limite rígido `loop_count <= 5` — ao atingir 5 iterações sem completude, o loop é interrompido compulsoriamente e o fluxo prossegue com o melhor prompt disponível, sinalizando a limitação; **(b)** cada iteração avalia o prompt contra o checklist estrutural `<task>/<context>/<constraints>/<output_format>`; se incompleto, faz **no máximo 1 pergunta objetiva por iteração** via `ask_questions` (nunca aberta); **(c)** encerramento antecipado é obrigatório assim que o prompt atingir completude — não force as 5 iterações; **(d)** o agent SEMPRE retorna para `@agent-router` ao final (sucesso ou limite atingido) — nunca roteia diretamente para downstream. **Fast-Path Determinístico**: para eliminar perda de evidências, latência desnecessária e desvios indevidos na cadeia de resolução, solicitações com intenção operacional evidente — **(1) Bug / Defeito / Layout / Runtime Error** (para `@bug-triage`); **(2) Refatoração Estrutural com alvo definido** (para `@refactor-planner`); **(3) Análise Técnica / Grafo / Auditoria direta** (para o especialista analítico correspondente) — **DEVEM acionar o Fast-Path bypass**, ingressando diretamente na primeira etapa do respectivo workflow operacional (R-050) sem passar por `@prompt-structuring`. O `@prompt-structuring` é reservado e obrigatório para solicitações de novas features abertas ou de alto nível, pedidos ambíguos ou quando o `@agent-router` identificar falta de especificações fundamentais.
- **R-042 (Re-triagem Obrigatória por Turno — Anti Sticky-Session)**: R-037 ("toda solicitação começa em `@agent-router`") aplica-se a **cada novo turno do usuário**, não apenas ao primeiro. Todo agent downstream ativo opera em `task_mode` e deve checar deriva de intenção a cada nova mensagem contra seu **Não-Escopo** declarado. **Critério objetivo de deriva** (qualquer um): **(a)** mudança de verbo de ação (elicitar→implementar, revisar→codar, analisar→corrigir, planejar→executar) **quando o agent ativo não cobre implementação** (ex.: `tech-solution-architect`, `bug-triage`, `requirements-analyst`, `test-strategy`, `deep-search`); **(b)** menção a stack/artefato fora da matriz de competência do agent ativo (ex.: pedir código Angular enquanto `@spring-boot-router` está ativo); **(c)** pedido explícito de execução/código quando o agent é estritamente read-only/advisory. **Nota (v2.1.0 dos specialists)**: `angular-router`, `spring-boot-router` e `spring-reactive-router` (e os especialistas em suas respectivas pastas) têm perfil híbrido (Advisory + Implementação) — pedir para "implementar" dentro do próprio domínio deles **não é deriva**; deriva só ocorre se o pedido sair do domínio de stack do specialist. **Ação obrigatória ao detectar deriva**: handoff imediato de retorno para `@agent-router` (payload do schema `handoff-governance` § 2.1, com `motivo: "deriva_de_intencao"`) — **nunca prosseguir silenciosamente fora do escopo**. Todo `.agent.md` deve declarar seção **"Retorno ao Router"** com o gatilho específico de deriva (atualização atômica conforme R-015). O `agent-router` declara `Agente Ativo: <nome>` em toda resposta para tornar a re-triagem auditável. Arestas de retorno universais (`de: <qualquer downstream> → para: agent-router`, condição `intent_drift_detected`) são declaradas em `.github/agents/routing-graph.yaml` (R-040). **Exceção de ação in-scope**: mudança de verbo de ação NÃO constitui deriva de intenção se a ação solicitada já constar expressamente na seção "Quando Delegar" do agent atualmente ativo (ex.: `tech-solution-architect` já delega pesquisa externa a `deep-search` — logo pedir pesquisa web com `tech-solution-architect` ativo é sub-tarefa in-scope, não deriva). Nesse caso, o router devolve o controle ao agent ativo (sem re-triagem completa). **Protocolo de Retorno Lateral / Call Stack (`call_type: "subroutine"`)**: quando um agent invoca outro como sub-rotina com `origem_contexto.call_type: "subroutine"` e `origem_contexto.return_to_parent: true`, o agent receptor (ex.: `@deep-search`) opera como sub-rotina delimitada e DEVE, ao concluir sua análise ou síntese, invocar `run_subagent(agentName: parent_agent, ...)` devolvendo os dados diretamente ao agent solicitante, em vez de finalizar no chat ou devolver ao `@agent-router` por falsa deriva. **Pré-requisito estrutural (tooling baseline)**: o handoff de retorno só é efetivo se **executado** via tool `run_subagent` (`agentName: "agent-router"`) — descrever o handoff apenas em texto/markdown não cumpre R-042. Por isso, `run_subagent` é **obrigatório e bloqueante** no frontmatter `tools:` de TODO agent do catálogo, incluindo os templates-base (`templates/research-agent.md`, `templates/operational-agent.md`); `agent-factory` valida essa regra em toda criação/revisão (baseline detalhado em `agent-contracts/SKILL.md` § 9). **Visibilidade de fluxo (banner obrigatório)**: para que R-042 seja auditável turno a turno (não apenas no turno em que `@agent-router` responde), **TODO agent — não apenas o `agent-router` — declara `Agente Ativo: <name>` como a primeira linha de toda resposta**, mesmo quando o agent apenas continua respondendo em `task_mode` sem handoff neste turno; quando a resposta é resultado de handoff/re-triagem recebido, uma segunda linha declara a transição (`Handoff: <origem> → <destino> (motivo: ...)`), equivalente ao `HandoffOutputItem` do OpenAI Agents SDK e ao campo `active_agent` streamado pelo LangGraph (padrão de mercado consolidado — detalhes em `agent-contracts/SKILL.md` § 0). Em seguida, o agent declara `Skills Carregadas: <skill-1>, <skill-2>, ...` (nomes curtos das skills efetivamente consultadas/pre-fetched nesta resposta, conforme `source_docs:`/`skills:` do próprio frontmatter — ou `nenhuma (apenas regras globais)` quando aplicável), dando visibilidade explícita da base de conhecimento ativa a cada turno. **Rastreabilidade Estruturada Auxiliar (opcional / context-mode MCP)**: quando houver necessidade de persistir o rastro de delegações além da janela de contexto ou entre sessões, o agent delegante PODE, na mesma resposta (convenção single-turn), indexar o `handoff_payload` (schema `handoff-governance` v1.1, campo opcional `roteamento_grafo`) via `ctx_index(source: "handoff-telemetry", content: ...)`. Esta camada é estritamente AUXILIAR e assíncrona — a leitura via `ctx_search` NÃO deve ser executada como pré-requisito bloqueante antes da triagem de cada novo turno do `@agent-router`, preservando a baixa latência do fluxo. O banner `Agente Ativo:`/`Handoff:` permanece a fonte PRIMÁRIA e obrigatória de visibilidade — nunca é substituído ou deprecado por este mecanismo.
- **R-043 (Local Overlay Pattern — Desacoplamento Total de Projetos e Adapters Locais)**: bindings de projeto (`projetos:`) e adapters gerados automaticamente por `adapter-generator` são dados **LOCAIS/PRIVADOS de cada desenvolvedor** e **NUNCA** podem ser escritos no repositório de governança compartilhado/commitado. **Localização obrigatória**: `.github/projects.local.yaml` (overlay de projetos) e `.github/instructions/local/` (adapters por-projeto) — ambos declarados em `.gitignore`, nunca tocados por `git add`/commit de rotina. O repositório mantém adapters genéricos em `.github/instructions/*.instructions.md` (com applyTo nativo) e documentados em `.github/instructions/README.md`. **Template rastreado**: `.github/projects.local.yaml.example` (sem dados reais) é commitado como schema de referência; cada desenvolvedor copia para `projects.local.yaml` (análogo a `.env`/`.env.example`). **Regra de leitura (merge em memória)**: todo agent/prompt que precisa da lista de projetos DEVE ler `projects.local.yaml` (se existir) e mesclar em memória — nunca escrever entrada de projeto de volta no arquivo compartilhado. **Regra de escrita**: `/add-project-context` e `adapter-generator` escrevem exclusivamente em `projects.local.yaml` e `.github/instructions/local/`; `/del-project-context` remove exclusivamente dali. **Defesa em profundidade**: hook `git` em `.githooks/pre-commit` bloqueia commit que introduza `projetos:` não-vazio em catálogos compartilhados ou qualquer arquivo staged sob `.github/instructions/local/` — protege contra `git add -f` acidental. Motivo: evitar que um `git commit`/`push` de rotina suba nomes/caminhos de projetos privados para o repositório de governança compartilhado.
- **R-044 (Anonimização Obrigatória de Evidência de Análise Real)**: agents que **analisam repositórios reais do usuário** (ex.: `code-knowledge-graph`, `business-rules-extractor`, `context-builder`, `project-scanner`) frequentemente produzem "evidência real" (números de validação, nomes de classe/método/namespace, caminhos de arquivo, nomes de repositório) como prova de funcionamento. Essa evidência é **útil e bem-vinda na resposta ao usuário no chat** (efêmera, não persistida), mas **PROIBIDA de ser escrita em qualquer arquivo commitável de governança compartilhada** (`.github/**` exceto `local/`, `CLAUDE.md`, qualquer `README.md`/changelog do catálogo) — isso é uma extensão direta de R-038 para o caso específico de **evidência derivada de análise**, não apenas exemplos escritos manualmente. **Antes de persistir qualquer changelog/seção de validação/exemplo derivado de análise real**, o agent DEVE genericizar: **(a)** nomes de repositório/projeto → `[PROJETO-A]`, `[PROJETO-B]`, ...; **(b)** nomes de classe/método/variável reais → `ServicoExemploX`, `operacaoExemploX`, ...; **(c)** pacotes/namespaces/domínios reais (ex.: `com.empresa.produto.*`, `https://api.empresa.com/...`) → `com.exemplo.pacote.*`, `http://contrato.exemplo.com/...`; **(d)** caminhos absolutos de sistema de arquivos (`C:\Users\...`, `D:\workspace\...`, `/home/usuario/...`) → `<workspace>\[PROJETO-X]` ou removidos; **(e)** nome de empresa/ecossistema real → `exemplo`/`[ECOSSISTEMA]`. **Métricas numéricas agregadas** (contagem de nós, arestas, órfãos, cobertura %) **podem ser mantidas reais** — não identificam projeto. **Teste objetivo**: um terceiro lendo o arquivo commitado NÃO deve conseguir inferir qual projeto/empresa foi analisado. Violação de R-044 é tratada com a mesma severidade de R-038 (bloqueante antes de commit). Incidente de origem documentado em `code-knowledge-graph.agent.md` (changelog v3.2.0).
- **R-045 (Exclusividade do Motor de Grafo — @code-knowledge-graph, RNF-004)**: O CLI `@optave/codegraph` e os artefatos de grafo (`.codegraph/graph.db`) são ferramentas de competência e execução **EXCLUSIVAS** do agent `@code-knowledge-graph`. NENHUM outro agent (specialists híbridos, analistas, revisores, router) está autorizado a executar comandos `codegraph *` diretamente no terminal ou realizar varreduras manuais exploratórias de diretórios (`list_dir`, `read_dir`) para mapear arquitetura, dependências ou chamadas. Toda extração de grafo, fluxo de chamadas, blast radius ou ciclos deve ser solicitada compulsoriamente via `run_subagent` para `@code-knowledge-graph`. Agents especialistas operam em modo Advisory de forma estritamente analítica e read-only — `run_in_terminal` é restrito ao modo Implementação (testing-first e linter).
- **R-046 (Single-Turn Batching Obrigatório — Economia de Tokens e Créditos)**: Toda alteração de código ou arquivos que envolva múltiplos arquivos, ou múltiplas substituições, DEVE aplicar o protocolo da skill `efficient-batch-code-modification`: **(a)** Dry-Run prévio em memória (mapear todos os alvos antes de invocar tools de escrita) com decisão obrigatória de ferramenta por limiar: se 1-4 arquivos com edição pontual → editor tools (`replace_string_in_file`, `insert_edit_into_file`) em *Single-Turn Batching*; se 5+ arquivos OU padrão repetitivo em múltiplos arquivos (rename, atualização de campos, injeção em massa) → OBRIGATÓRIO usar `ctx_execute`/`ctx_execute_file`/`ctx_batch_execute` com script em processo único no sandbox (zero tool calls de editor e zero re-envio de contexto); **(b)** *Single-Turn Batching* — quando no limiar de editor (<5 arquivos), emitir todas as tool calls de edição agrupadas na mesma rodada de resposta (*parallel tool calls*), sendo expressamente proibida a execução sequencial (editar 1 arquivo → aguardar retorno → editar outro); **(c)** Proibição de releitura pós-edição imediata com o único intuito de verificar se a alteração foi aplicada; **(d)** Validação de erro agrupada — `get_errors` DEVE ser invocado exatamente uma única vez ao final com o array completo `filePaths: [...]`, nunca arquivo por arquivo; **(e)** Diffs cirúrgicos mínimos com 2 a 3 linhas de contexto para unicidade.
- **R-047 (Fluxo Contínuo Sem Becos Sem Saída)**: Nenhum agent do catálogo pode encerrar uma resposta apenas com texto descritivo sugerindo um "próximo passo". Ao final de toda resposta, o agent DEVE obrigatoriamente: **(a)** acionar `run_subagent` (handoff a outro agent) OU **(b)** acionar `ask_questions` (decisão/aprovação humana pendente) — salvo quando a resposta for 100% conclusiva, sem qualquer pendência de execução ou decisão. **Exceção de Routers / Triadores (Delegação Plana vs Aninhamento)**: O `@agent-router` (e supervisores hierárquicos de domínio quando roteando) encerra seu turno emitindo o bloco padronizado de decisão de roteamento (`Agente Ativo: ... | Delegado: @<agent> | Pipeline de Execução do Workflow`), o qual NÃO é considerado beco sem saída. É **TERMINANTEMENTE PROIBIDO ao `@agent-router` invocar subagente executor (`run_subagent`) para rodar tarefas downstream de workflow canônico por dentro do router** (aninhamento `root -> agent-router -> executor`). A invocação de `run_subagent` pelo `@agent-router` é restrita exclusivamente a `@prompt-structuring` (R-041) para refinamento pré-roteamento ou `@binding-initializer` (R-034). Toda execução de downstream deve ser despachada pelo Orquestrador Raiz (Copilot Chat) em nível plano (Flat Delegation), evitando consumo duplicado de contexto e re-execução em cascata (Smell 2.20).
- **R-048 (Proibição de Leitura Integral de Arquivos Grandes — Leitura Cirúrgica Obrigatória)**: Arquivos com mais de 100 linhas NÃO DEVEM ser lidos integralmente via `read_file` quando a intenção for inspeção pontual, debug localizado ou edição de bloco específico. O agent DEVE compulsoriamente: **(1)** localizar o trecho alvo via `grep_search` (com número de linha), **(2)** usar `read_file` informando `offset` e `limit` restritos à janela de trabalho (teto recomendado de 80 linhas úteis + margem de 10), ou **(3)** delegar o processamento analítico a `ctx_execute_file` (Context Mode) sem trafegar o conteúdo bruto na memória conversacional. Nota de escopo: as tools `read_file`/`grep_search` já suportam nativamente paginação e busca filtrada — R-048 é uma regra comportamental de disciplina de uso, não uma especificação de novas ferramentas MCP. Toda modificação subsequente mantém a premissa de diff cirúrgico com 2 a 3 linhas de contexto (R-046).
- **R-049 (Vinculação Compulsória de Governança de Terminal em Tooling)**: Todo agent (`*.agent.md`), prompt (`*.prompt.md`) ou entrada de catálogo (`catalog.yaml` e sub-catálogos locais `<stack>-catalog.yaml`) que declare a ferramenta `run_in_terminal` em `tools:` DEVE compulsoriamente referenciar `.github/skills/terminal-governance/SKILL.md` em `source_docs:` (ou na lista `skills:` dos sub-catálogos locais de stack). É terminantemente proibido conceder privilégio de execução no terminal sem vincular o respectivo contrato de governança que veda pager/interatividade (R-035), proíbe scripts inline exploratórios e exige context-mode MCP (R-008).
- **R-050 (Workflows Operacionais Determinísticos — Pipelines de Estado Finito)**: Toda solicitação de desenvolvimento de software deve ser vinculada e executada rigorosamente sob um dos **5 Workflows Canônicos**. Cada workflow constitui uma máquina de estados finita predefinida, onde a ordem dos estados, papéis dos agents e artefatos de transição são determinísticos:
  1. **`WORKFLOW-BUG-FIX` (Bug / Layout / Runtime Exception / Regressão)**:
     `Fast-Path -> [1. Triagem & Causa Raiz: @bug-triage (com @debugger em sub-rotina se multi-camada)] -> [2. Teste de Regressão TDD: specialist-unit-test/component-test] -> [3. Correção Cirúrgica: specialist-bug-fixer] -> [4. Validação Green Test & Linter: runtime-verifier] -> [5. Quality Gate: @code-review / @pr-gatekeeper]`.
  2. **`WORKFLOW-REFACTORING` (Refatoração Estrutural / Desacoplamento / Modernização)**:
     `Fast-Path (se alvo definido) -> [1. Regras Vigentes: @business-rules-extractor] -> [2. Grafo & Blast Radius: @code-knowledge-graph (R-045)] -> [3. Plano Macro & Safety Net: @refactor-planner + @test-strategy] -> [4. Execução Incremental em Lote (R-046): specialist router/developer] -> [5. Validação de Regras: @business-rules-extractor + @code-review]`.
  3. **`WORKFLOW-TECHNICAL-ANALYSIS` (Análise Técnica / Grafo / Segurança / Performance / Arquitetura)**:
     `Fast-Path -> [1. Especialista Analítico Específico: @code-knowledge-graph | @ddd-bounded-context-mapper | @adr-sentinel | @security-reviewer | @performance-agent | @compliance-guardrails | @tech-solution-architect] -> [2. Coleta Determinística Read-Only] -> [3. Síntese Técnica & Próximos Passos (R-047)]`.
  4. **`WORKFLOW-FEATURE-DEVELOPMENT` (Nova Feature / Evolução Funcional / Fullstack)**:
     `[1. Prompt Structuring (R-041 se ambíguo)] -> [2. Elicitação de Requisitos: @requirements-analyst | @feature-planner] -> [3. Technical Blueprint: @tech-solution-architect] -> [4. Matriz de Riscos & Testes: @test-strategy] -> [5. Implementação Domain-Driven TDD: domain routers & specialists] -> [6. Quality Gate & PR: @code-review -> @pr-gatekeeper]`.
  5. **`WORKFLOW-GOVERNANCE-MAINTENANCE` (Auditoria & Manutenção do Ecossistema)**:
     `[1. Auditoria Read-Only: @agent-auditor | @repo-hygiene-auditor] -> [2. Checkpoint Humano: ask_questions] -> [3. Execução Governada em Lote: @governance-maintainer | @governance-factory]`.
  Agents participantes de um workflow NÃO podem pular estados, gerar becos sem saída descritivos (R-047) ou desviar arbitrariamente da cadeia sem evento explícito de deriva de intenção (R-042).
  - **Fast-Chaining (R-050.1)**: Quando o usuário aprovar uma proposta diagnóstica de workflow anterior (ex.: 'implemente a melhoria 1'), o router aciona Fast-Path herdando arquivos e diagnósticos via `carry_over_state`, sem desvio para @prompt-structuring.
  - **Circuit Breaker & Rollback State (R-050.2)**: Teto de 3 tentativas de autocorreção em testes ou falha de validação de regras em refatoração aciona compulsoriamente o estado de reversão (4b/5b), limpando o workspace e escalando para aprovação humana (ask_questions).
  - **Multi-Project Tracking (R-050.3)**: Solicitações sobre repositórios conectados (projects.local.yaml) transportam compulsoriamente `projeto_alvo` (id, root_path, adapter_ref) no workflow_tracking.
  - **Visibilidade Obrigatória no Chat (Anti-Cegueira)**: Logo após a decisão do workflow pelo `@agent-router`, e a cada transição de etapa por qualquer agent downstream, a resposta DEVE exibir o bloco visual `### 🗺️ Pipeline de Execução do Workflow (<total> etapas)` com os estados ordenados e marcadores de status: `[✅]` Concluído, `[▶]` Em Andamento (Atual), `[⏳]` Pendente, mapeando explicitamente os agentes responsáveis até a conclusão.
- **R-051 (Proteção Anti-Corrupção em Edição de Arquivo Único Grande/Estruturado)**: Antes de editar QUALQUER arquivo — mesmo um único arquivo, fora do escopo de R-046 (que trata de lote multi-arquivo) — se o arquivo-alvo tiver mais de 200 linhas, OU extensão `.yaml`/`.yml`/`.json` (sintaxe sensível a indentação), OU for consumido diretamente por testes automatizados/CI, o agent DEVE seguir o Padrão de Edição Segura Verificada definido em `efficient-batch-code-modification/SKILL.md` § 5 (ler o arquivo inteiro → contar ocorrências exatas do texto-âncora em memória → abortar se != 1 → escrever somente se seguro → reler do disco para confirmar) em vez de `insert_edit_into_file`, cujo uso nesses arquivos é **ANTI-PADRÃO BLOQUEANTE**. O agent NUNCA deve confiar cegamente na mensagem de sucesso/falha retornada pela tool de edição em arquivos consumidos por CI/testes — deve reler/validar o estado real do arquivo antes de prosseguir (foram observados tanto falsos-positivos de corrupção silenciosa quanto falsos-negativos de falha reportada). Incidente de origem documentado em `efficient-batch-code-modification/SKILL.md` § 5.1 e `governance-audit-patterns/SKILL.md` Smell 2.16 (2026-09: `insert_edit_into_file` corrompeu `workflows.md` e `routing-graph.yaml` três vezes durante uma auditoria de workflows).

## 3.1) Regra de Autoria de Agents

- Toda criação ou revisão de agent customizado deve usar o `governance-factory`.
- Ao criar novo agent, atualizar `README.md` e `catalog.yaml` na mesma entrega.

## 4) Fluxo Operacional Base

**SEM EXCEÇÃO: Todo fluxo deve começar com `@agent-router`, e todo turno subsequente é re-triado (R-042)**

```
Solicitação do Usuário (turno N)
           ↓
    @agent-router ←── OBRIGATÓRIO (Health Check R-034)
           ↓
    Existe agent ativo de turno anterior? (R-042)
           ├─ Não (1º turno) ────────────────────────────────────────────────────────┐
           └─ Sim -> checar deriva de intenção                                       │
                (verbo de ação | stack fora de                                       │
                 competência | pedido de execução                                    │
                 em agent read-only)                                                 │
                ├─ Sem deriva -> devolve ao agent ativo (sem re-rotear)              │
                └─ Deriva detectada (handoff motivo: "deriva_de_intencao") ──────────┤
                                                                                     ↓
                         [CLASSIFICAÇÃO DE WORKFLOW & FAST-PATH (R-041/R-050)]
                                ├────────────────────────────────────────┐
                                │ FAST-PATH DETERMINÍSTICO               │ CASO AMBÍGUO / FEATURE ABERTA
                                ↓                                        ↓
             Ingresso Direto no Workflow Canônico:              @prompt-structuring (R-041)
             - WORKFLOW-BUG-FIX (→ @bug-triage)                 (refina prompt em loop máx. 5x)
             - WORKFLOW-REFACTORING (→ @refactor-planner)                ↓
             - WORKFLOW-TECHNICAL-ANALYSIS (→ Especialista)      @agent-router (retorno obrigatório)
             - WORKFLOW-GOVERNANCE (→ @agent-auditor)                    ↓
                                ├────────────────────────────────────────┘
                                ↓
                 [EXECUÇÃO SEQUENCIAL ESTRITA (R-050)]
                 - WORKFLOW-BUG-FIX: triage → red-test → bug-fixer → green-test → gate
                 - WORKFLOW-REFACTORING: rules → graph/blast radius → plan → batch-exec → validation
                 - WORKFLOW-TECHNICAL-ANALYSIS: scope → deterministic analysis → report
                 - WORKFLOW-FEATURE-DEVELOPMENT: requirements → blueprint → test-strategy → TDD → gate
                 - WORKFLOW-GOVERNANCE-MAINTENANCE: audit → approval → batch execution
                                ↓
                 Turno seguinte muda de fase/escopo? (R-042)
                        ├─ Sim -> agent ativo retorna a @agent-router (handoff de deriva)
                        └─ Não -> agent ativo continua no workflow em task_mode
                                ↓
                            [RESULTADO]
```

**Fases de Execução:**

1. **Triagem & Seleção de Workflow** (agent-router): classificar intenção, acionar Fast-Path ou Prompt Structuring e declarar `Agente Ativo` e `Workflow` (R-050)
2. **Execução de Workflow** (agents especialistas): seguir os estados do pipeline determinístico em `task_mode`
3. **Re-triagem por turno** (R-042): a cada nova mensagem, o agent ativo checa deriva de intenção contra seu Não-Escopo antes de responder; ao detectar deriva, devolve controle ao `@agent-router` via handoff (nunca prossegue fora do escopo)
4. **Validação & Não-Regressão** (self-check / tests): executar verificação de qualidade e suites de teste (R-046)
5. **Resumo & Handoff Contínuo** (R-028, R-047): reportar resultado, evidências e acionar próximo agente ou aprovação humana

## 5) Estrutura de Governança

- `.github/copilot-instructions.md` -> regras operacionais e roteamento rápido.
- `.github/agents/README.md` -> catálogo de agents e uso.
- `.github/skills/README.md` -> catálogo de skills e padrão.
- `.github/instructions/README.md` -> catálogo de instructions e convenções de domínio.
- `.github/hooks/context-mode.json` -> hooks de continuidade para context-mode.
- `.githooks/pre-commit` -> hook Git de defesa em profundidade para R-043/R-044 (bloqueia commit que vaze `projetos:` em catálogos compartilhados, arquivo em `.github/instructions/local/`, ou caminho de sistema de arquivos local absoluto em arquivo de governança); setup: `git config core.hooksPath .githooks`.
- `.github/prompts/README.md` -> comandos operacionais do workflow.
  - **Novo (v1.1)**: 
    - `/add-project-context` — Auto-carregar contexto com Intent + RRF (**com implementation guide para Copilot**)
    - `/del-project-context` — Remover contexto de projeto com confirmação
  - **Novo (v1.2)**:
    - Health Check (R-034): Se faltarem catálogos compartilhados + `binding.md`, disparar `binding-initializer` automaticamente
  - **Novo (v1.3 — R-043)**:
    - Local Overlay Pattern: projetos/adapters locais vivem em `projects.local.yaml` + `.github/instructions/local/` (gitignored) — nunca em catálogos compartilhados/`.github/instructions/` (compartilhados)
- `docs/repo-map.md` -> mapa estrutural do repositório para navegação determinística de arquivos (zero buscas cegas).
- `.ignore` e `.rgignore` -> whitelist de `.github/` para indexação por ripgrep (file_search e grep_search sem 0 matches).
- `.github/agents/catalog.yaml` -> catálogo estruturado de agents (metadados e modelos — NUNCA confundir com `.github/instructions/catalog.yaml` de binding).
- `.github/instructions/catalog.yaml` -> manifest de binding de adapters e stacks.
- `.github/skills/.index.json` -> índice estruturado de skills.

## 6) Catálogo Atual (estado verificado)

### Agents (36 catalogados / 79 arquivos totais com especialistas)
- `agent-router` v2.0.0 — entry point obrigatório; confidence score + nível de routing declarados no output; routing-graph.yaml como fonte estrutural (R-040)
- `prompt-structuring` — ⚠️ passo mandatório pós-`agent-router` (R-041); loop de refinamento de prompt limitado a 5 iterações; sempre retorna ao `agent-router`
- **Planejamento & Análise**: `requirements-analyst`, `deep-search`, `feature-planner`
- **Arquitetura & Design**: `tech-solution-architect`, `code-knowledge-graph`, `business-rules-extractor`, `refactor-planner`, `ddd-bounded-context-mapper`, `adr-sentinel`
- **Implementação (Domain Routers & Specialists)**:
  - `angular-router` — orquestra os 8 especialistas em `.github/agents/frontend/angular/`
  - `spring-boot-router` — orquestra os 7 especialistas em `.github/agents/backend/spring-boot/`
  - `spring-reactive-router` — orquestra os 7 especialistas em `.github/agents/backend/spring-reactive/`
  - `ejb-router` — orquestra os 7 especialistas em `.github/agents/backend/ejb/`
  - `python-router` — orquestra os 7 especialistas em `.github/agents/backend/python/`
  - `database-router` — orquestra os 6 especialistas em `.github/agents/backend/database/`
  - `database-specialist` — migrações de schema e integridade referencial
- **Qualidade & Validação**: `bug-triage`, `debugger`, `test-strategy`, `code-review`, `code-style-enforcer`, `security-reviewer`, `performance-agent`, `devops-engineer`, `runtime-verifier`, `repo-hygiene-auditor`
- **Documentação**: `docs-engineer` (modos `author`/`curate`), `context-builder`
- **Governança & Orquestração**: `governance-factory` (unifica criação/revisão de agents, skills, prompts e stacks), `governance-maintainer`, `agent-auditor`, `binding-initializer`, `adapter-generator`, `agentic-memory-manager`, `compliance-guardrails`, `pr-gatekeeper`

### Artefatos Estruturais de Orquestração
- `.github/agents/routing-graph.yaml` — grafo de roteamento (R-040): 37 nós de agents + 5 nós de workflows, arestas com condições, política de cascata
- `.github/agents/evals/casos-roteamento.yaml` — suíte de evals de regressão de roteamento (81 casos)

## 7) Política de Mudança

- Atualize este arquivo quando regras globais mudarem.
- Evite mover detalhe técnico de stack para regras globais se for específico de um app.
- Se a mudança afetar catálogo, sincronize:
  - `.github/agents/README.md`
  - `.github/skills/README.md`
  - `.github/instructions/README.md`
  - `.github/agents/catalog.yaml`
  - `.github/skills/.index.json`

## 8) Definition of Done (governança)

- [ ] Regras globais estão apenas em `CLAUDE.md`.
- [ ] O catálogo de adapters e binding está atualizado em `.github/instructions/README.md`.
- [ ] `.github/copilot-instructions.md` referencia estes arquivos sem duplicação excessiva.
- [ ] Catálogos em `.github/agents/README.md` e `.github/skills/README.md` refletem o estado real.
- [ ] Artefatos `.github/hooks/context-mode.json` e `.github/prompts/README.md` estão presentes e coerentes.
- [ ] Linguagem clara, direta e rastreável.
- [ ] Documentação em PT-BR com acentuação correta quando aplicável.

### Checklist de Genericidade (R-038)

**ANTES de submeter arquivo novo em `.github/` (agents, skills, prompts, copilot-instructions):**

- [ ] Substitua mentalmente todos os nomes de projeto por `[PROJETO]` — o texto faz sentido?
- [ ] Substitua todas as tecnologias/frameworks por `[TECH]` — o texto ainda é válido?
- [ ] Nenhuma referência a: domínio de negócio, linguagem de programação específica, framework exclusivo
- [ ] Se há customização de tech/domínio, está em `.github/instructions/*.instructions.md` (adapter)?
- [ ] Se há lista de exemplos concretos, apontam para `.github/instructions/README.md` e nunca duplicam?

**Teste rápido**: Seu documento continua útil para um projeto completamente diferente (ex: Go backend, React frontend)?
- ✅ Sim? → Pode ir para `.github/` (global)
- ❌ Não? → Deve ir para `.github/instructions/<adapter>.instructions.md` (adapter)

### Checklist de Anonimização de Evidência Real (R-044)

**ANTES de persistir qualquer changelog, seção de validação ou exemplo derivado de análise de repositório real** (aplica-se sobretudo a agents analíticos: `code-knowledge-graph`, `business-rules-extractor`, `context-builder`, `project-scanner`):

- [ ] Nomes de repositório/projeto genericizados (`[PROJETO-A]`, `[PROJETO-B]`, ...)?
- [ ] Nomes de classe/método/variável reais trocados por equivalentes de exemplo (`ServicoExemploX`, `operacaoExemploX`)?
- [ ] Pacotes/namespaces/domínios reais (`com.empresa.*`, URLs reais) trocados por `com.exemplo.*`/`http://contrato.exemplo.com/...`?
- [ ] Caminhos absolutos de sistema de arquivos (`C:\Users\...`, `D:\workspace\...`, `/home/...`) removidos ou trocados por placeholder (`<workspace>\[PROJETO-X]`)?
- [ ] Nome de empresa/ecossistema real removido ou genericizado?
- [ ] Métricas numéricas agregadas (contagens, %) — **podem permanecer reais**, não identificam projeto.

**Teste rápido**: um terceiro lendo o arquivo commitado consegue inferir qual projeto/empresa foi analisado?
- ✅ Não consegue? → Pode commitar.
- ❌ Consegue? → Genericize antes de commitar (bloqueante, mesma severidade de R-038).

### Descoberta progressiva de convenções

- Comece por `CLAUDE.md`, `.github/instructions/README.md` e `.github/copilot-instructions.md`.
- Em seguida, use o índice de adapters em `.github/instructions/README.md` para carregar apenas as instruções específicas de cada projeto/stack.
- Depois, se ainda houver dúvida, valide diretamente no código do projeto-alvo e nos documentos do adapter correspondente.
