# REQ — Sumarização de Código-Fonte Agnóstica a Linguagem via Agent Especialista + Context-Mode Sandbox

> Documento gerado por `requirements-analyst`. Fase: elicitação prospectiva (pedido → requisito). Nenhuma decisão de arquitetura, tecnologia ou lib específica foi tomada aqui — ver seção "Handoff".

## 0) Fonte do Pedido (verbatim)

> "usar uma lib de sumarização [de código-fonte, agnóstica a linguagem] + o context-mode sandbox no nosso projeto com intuito de economizar créditos ou tokens de AI"

**Avaliação de solution-jumping (skill § 6):** o pedido menciona ferramenta técnica ("lib de sumarização", "context-mode sandbox"), mas a necessidade real subjacente é **reduzir bytes/tokens levados ao contexto de chat sem perder fidelidade de comportamento do código**. A escolha da lib específica e o desenho técnico do pipeline **não** são tratados neste documento (fora de escopo deste agent) — ficam para `@analysis-architect`.

> 🔄 **Pivô de solução confirmado pelo usuário (2026-08-31, rodada 2):** a sumarização **não** será realizada por uma lib isolada consumida diretamente pelos agents existentes. Será responsabilidade de um **novo agent especialista dedicado** (nome ainda não definido — ver Lacunas §4), que orquestra o processo. O agent pode usar libs de parsing (ex.: tree-sitter) **internamente como tool**, mas a decisão/orquestração é sempre do agent — nunca "lib sozinha, sem agent". Esse agent segue um modelo **híbrido**: tenta heurística/AST determinística primeiro (sem custo de tokens) e só invoca um modelo LLM barato (ex.: Haiku) como fallback quando a sumarização determinística for insuficiente. Essa decisão **revisa RNF-001** (ver §3).

> ⚠️ **Nota de correção de governança (2026-08-31, rodada 1):** a primeira versão deste documento foi gerada por um subagent autônomo (`run_subagent`) que executou `ask_questions` em contexto isolado — sem acesso ao usuário real — e **presumiu** as respostas P1..P9 abaixo para poder prosseguir (risco de violação R-027). O agent orquestrador identificou o risco, **não aceitou as respostas como válidas** e reexecutou `ask_questions` diretamente com o usuário real para validar cada premissa crítica. Todas as premissas foram **confirmadas integralmente** pelo usuário nesta rodada real. A tabela abaixo foi atualizada para refletir essa validação real, mantendo o rótulo original `ask_questions P1..P9` apenas como referência ao mapeamento de campos (não como prova de intake real — ver coluna "Confirmação").

## 1) Contexto de Coleta (ask_questions)

| Campo | Classe | Valor coletado | Confirmação |
|---|---|---|---|
| Gatilho/fluxo | Obrigatório | Pós-`/init-context` (sugestão, não automática) + sob demanda quando agent identificar necessidade | ✅ Confirmado pelo usuário real (2026-08-31) |
| Granularidade | Obrigatório | MVP = arquivo inteiro; função/método e classe/módulo = fase seguinte | ✅ Confirmado pelo usuário real (2026-08-31) |
| Métrica de economia | Recomendado | Sem meta percentual fixa nesta fase — apenas medir e reportar bytes/tokens antes-vs-depois | ✅ Confirmado pelo usuário real (2026-08-31) |
| Fidelidade aceitável | Obrigatório | MVP = preservar assinatura pública + regras de negócio identificáveis; variação fina por gatilho fica em aberto | ⚠️ Presumido pelo subagent — **não** revalidado nesta rodada (ver Lacunas §4) |
| Execução (local vs. externo) | Obrigatório | 100% local/offline no sandbox do context-mode | ✅ Confirmado pelo usuário real (2026-08-31) |
| Escopo de stacks | Obrigatório | Cobrir todas as stacks do `catalog.yaml` (Java/Spring Boot, Angular/TS, Python, SQL) desde o MVP | ⚠️ Presumido pelo subagent — **não** revalidado nesta rodada |
| Persistência | Obrigatório | Apenas cache do context-mode (`ctx_index`/`ctx_search`); sem TTL nesta fase | ⚠️ Presumido pelo subagent — **não** revalidado nesta rodada |
| Recorte de MVP | Obrigatório | Proposta do analista aceita integralmente pelo usuário nesta rodada | ✅ Confirmado pelo usuário real (2026-08-31) |
| Restrições/riscos | Obrigatório | R-009, R-010, R-038 aceitas como restrições explícitas | ⚠️ Presumido pelo subagent — restrições de governança, não dependem de preferência do usuário |
| Arquivo `.md` criado sem pedido explícito | Governança | Usuário optou por **manter e corrigir** o arquivo com base nas respostas reais | ✅ Confirmado pelo usuário real (2026-08-31) |
| Natureza do executor (agent vs. lib) | Obrigatório | **Novo agent especialista dedicado** (não lib isolada); modelo híbrido — heurística/AST primeiro, LLM barato como fallback | ✅ Confirmado pelo usuário real (2026-08-31, rodada 2) |
| Uso de libs pelo agent | Obrigatório | Agent pode usar libs de parsing (ex.: tree-sitter) **internamente como tool**; orquestração/decisão sempre do agent | ✅ Confirmado pelo usuário real (2026-08-31, rodada 2) |

**Pronto para prosseguir:** PARCIAL — 7 premissas críticas confirmadas com o usuário real; 3 permanecem como hipótese do subagent (fidelidade por gatilho, escopo multi-stack, persistência/TTL) e devem ser revalidadas antes de fechar RF-004/RF-005/RNF-003 como Must definitivo.

| Resposta confirmada (real) | Estratégia adotada |
|---|---|
| Gatilho = pós-`/init-context` + sob demanda | RF-001/RF-002 cobrem os dois modos, ambos não-bloqueantes (sugestão, não execução automática) |
| MVP = arquivo inteiro | RF-003 fecha granularidade fina como Should/fase 2, não Must |
| Métrica sem meta fixa | RF-006/RF-007 medem e reportam sem bloquear por ausência de meta |
| Execução 100% local | RNF-001 é guardrail Must, elimina candidatos de solução baseados em LLM externo (decisão técnica futura restrita por este NFR) |
| Nenhuma resposta sobre latência-limiar | Registrado em Lacunas — não vira requisito suposto |
| Arquivo mantido e corrigido | Esta revisão (2026-08-31) substitui a rastreabilidade fictícia da versão anterior |
| Executor = novo agent especialista, não lib | RF-008 (novo) formaliza o agent dedicado; RF-001/RF-002 passam a invocar esse agent, não uma lib inline |
| Agent híbrido (heurística/AST → LLM fallback) | RNF-001 revisado (não é mais "zero LLM absoluto") — ver §3 |
| Lib como tool interna do agent, nunca substituta | RF-008 e RNF-007 (novo) formalizam que libs de parsing são ferramentas do agent, não executores autônomos |
| Gatilho RF-001 corrigido para `/add-project-context` | `@analysis-architect` encontrou contradição factual: `/init-context` não indexa código de projeto. Confirmado pelo usuário real (2026-08-31, rodada 3). Implementado em `add-project-context.prompt.md` (FASE 3.5) |
| Threshold RF-002 = >300 linhas OU >20KB | Confirmado pelo usuário real (2026-08-31, rodada 3). Implementado em `context-mode/SKILL.md` §3 |
| Regra central RF-002 documentada em `context-mode/SKILL.md` | Confirmado pelo usuário real (2026-08-31, rodada 3) — Tier 1, lido por todos os 25 agents |

> ⚠️ **Nota de correção de governança (rodada 3, 2026-08-31):** o `analysis-architect` também rodou `ask_questions` em contexto isolado e apresentou "5/5 perguntas respondidas" sem acesso ao usuário real — mesmo padrão de risco das rodadas 1 e 2. As 3 decisões técnicas centrais (gatilho corrigido, threshold, local de documentação) foram revalidadas e confirmadas pelo usuário real antes de qualquer implementação.

## 2) Requisitos Funcionais (RF)

### RF-001 — Sugestão automática ao final do registro de projeto — **CORRIGIDO (rodada 3, 2026-08-31)**
> ⚠️ Substitui a versão original ("após `/init-context`"), que continha premissa factualmente incorreta: `/init-context` roda 1x por sessão e nunca lê/indexa código-fonte de projeto (6 passos, sem scanner de projeto). Quem faz scanner + registro de projeto é `/add-project-context` (FASE 1-3). Achado técnico de `@analysis-architect`, confirmado pelo usuário real.

**[EARS-Guiado por evento]** Quando o registro de um novo projeto via `/add-project-context` (FASE 3) for concluído com sucesso, o sistema deve sugerir explicitamente ao usuário o início do processo de sumarização de código-fonte para todos os arquivos desse projeto, invocando o **agent especialista de sumarização (RF-008 — `code-summarizer`)** — nunca uma lib chamada diretamente — e aguardando confirmação antes de executar. Se já existir sumarização prévia registrada (`ctx_search`), exibir aviso compacto de 1 linha em vez de repetir o prompt completo (controle de ruído).
**Fonte:** *"apos o /init-context deve ser sugerido o processo de sumarizacao para todo o projeto adicionado ao contexto"* (resposta P1, gatilho corrigido) + achado técnico `@analysis-architect` + confirmação do usuário real (rodada 3, 2026-08-31)
**Prioridade:** Must
**Implementado em:** `.github/prompts/add-project-context.prompt.md` (FASE 3.5)

```gherkin
Dado que um projeto foi registrado com sucesso via /add-project-context (fim da FASE 3)
Quando não houver sumarização prévia registrada para esse projeto (ctx_search vazio)
Então o sistema deve exibir uma sugestão explícita de sumarização via ask_questions
E aguardar confirmação do usuário antes de invocar o agent especialista de sumarização

Dado que já existe sumarização prévia registrada para o projeto
Quando o registro do projeto for concluído novamente ou revisitado
Então o sistema deve exibir apenas um aviso compacto de 1 linha, sem repetir o prompt completo
```

### RF-002 — Sumarização sob demanda por identificação do agent solicitante
**[EARS-Guiado por evento]** Quando um agent (qualquer agent do catálogo) identificar que um arquivo-fonte excede **300 linhas OU 20KB** (o que disparar primeiro) e seja necessário ao contexto da tarefa, esse agent deve delegar a sumarização ao **agent especialista de sumarização (RF-008 — `code-summarizer`)** via `run_subagent` — nunca chamar uma lib de sumarização diretamente — antes de anexar o resultado ao contexto da sessão.
**Fonte:** *"a sumarizacao pode ser solicitado quando o agent identificar a necessidade"* (resposta P1) + pivô de solução (rodada 2) + threshold confirmado pelo usuário real (rodada 3, 2026-08-31)
**Prioridade:** Must
**Implementado em:** `.github/skills/context-mode/SKILL.md` §3 (Regras de substituição — Tier 1, lido por todos os 25 agents)

```gherkin
Dado que um agent precisa de contexto de um arquivo de código-fonte para responder a uma tarefa
Quando o arquivo exceder 300 linhas OU 20KB
Então o agent solicitante deve delegar ao agent especialista de sumarização via run_subagent, antes de incluir o conteúdo no contexto do chat

Dado um arquivo-fonte com 300 linhas ou menos E menos de 20KB
Quando o agent solicitante precisar de seu conteúdo
Então o agent pode ler o arquivo diretamente, sem delegar ao code-summarizer (evita overhead desnecessário — RNF-002)
```

### RF-003 — Granularidade de arquivo inteiro (MVP)
**[EARS-Ubíquo]** O sistema deve sumarizar código-fonte na granularidade de arquivo inteiro para qualquer arquivo indexado.
**Fonte:** resposta P2 (múltiplas granularidades pedidas) + confirmação de MVP (recorte a "arquivo inteiro")
**Prioridade:** Must (arquivo inteiro) — granularidade função/método e classe/módulo: **Should** (fase seguinte, fora do MVP)

```gherkin
Dado um arquivo-fonte de qualquer linguagem indexado pelo context-mode
Quando o processo de sumarização for executado para esse arquivo
Então o sistema deve produzir 1 sumário correspondente ao arquivo inteiro
E armazená-lo no cache do context-mode
```

### RF-004 — Preservação de fidelidade mínima
**[EARS-Ubíquo]** O sistema deve preservar, no sumário gerado, a assinatura pública (interfaces, métodos/funções expostas) e as regras de negócio identificáveis no código-fonte original.
**Fonte:** resposta P4 + recorte de MVP confirmado ("preservar assinatura pública + regras de negócio identificáveis")
**Prioridade:** Must

```gherkin
Dado um arquivo-fonte contendo função pública com regra de negócio explícita (validação, cálculo, condição de decisão)
Quando o arquivo for sumarizado
Então o sumário resultante deve mencionar a assinatura pública e a regra de negócio identificada, sem omissão
```

### RF-005 — Cobertura multi-stack desde o MVP
**[EARS-Ubíquo]** O sistema deve sumarizar código-fonte das stacks registradas em `docs/ai-context/catalog.yaml` (Java/Spring Boot, Angular/TypeScript, Python, SQL) de forma agnóstica a linguagem, desde a primeira entrega.
**Fonte:** resposta P6 ("Cobrir todas as stacks do catalog.yaml desde o MVP")
**Prioridade:** Must

```gherkin
Dado um arquivo-fonte pertencente a uma das stacks registradas em catalog.yaml
Quando o processo de sumarização for acionado
Então o sistema deve produzir um sumário válido sem depender de tratamento exclusivo por linguagem além do parsing básico necessário
```

### RF-006 — Medição de bytes/tokens antes-vs-depois
**[EARS-Ubíquo]** O sistema deve medir e reportar o tamanho (em bytes e/ou tokens estimados) do conteúdo original versus o conteúdo sumarizado, a cada execução de sumarização.
**Fonte:** proposta de MVP confirmada ("medir e reportar bytes/tokens antes-vs-depois por execução, sem meta percentual fixa")
**Prioridade:** Must

```gherkin
Dado que um arquivo foi sumarizado com sucesso
Quando o resultado for retornado
Então o sistema deve reportar o tamanho original e o tamanho sumarizado, permitindo cálculo do delta
```

### RF-007 — Ausência de meta numérica não bloqueia execução
**[EARS-Indesejado]** Se não houver meta numérica de economia de tokens definida, então o sistema não deve bloquear a sumarização por ausência dessa meta — o reporte de RF-006 permanece apenas informativo.
**Fonte:** resposta P3 ("Ainda não definido — requisito fica em aberto")
**Prioridade:** Must

### RF-008 — Agent especialista dedicado de sumarização (não lib isolada)
**[EARS-Ubíquo]** O sistema deve executar todo o processo de sumarização de código-fonte por meio de um **novo agent especialista dedicado** (nome a definir — ver Lacunas §4), registrado no catálogo de agents do repositório, e não por chamada direta a uma lib de sumarização por outros agents. Esse agent especialista deve:
- operar em modelo **híbrido**: tentar sumarização determinística (heurística/AST/parser) primeiro, sem custo de tokens;
- só invocar um modelo LLM leve/barato como **fallback** quando a sumarização determinística for insuficiente para atender RF-004 (fidelidade mínima);
- poder usar libs de parsing (ex.: tree-sitter, ASTs específicos por linguagem) **internamente como tool**, nunca expor a lib diretamente para os agents solicitantes (RF-001/RF-002) — a interface pública é sempre o agent, via `run_subagent`.

**Fonte:** pivô de solução confirmado pelo usuário real (2026-08-31, rodada 2) — respostas "natureza-agent" (híbrido) e "escopo-lib" (lib como tool interna)
**Prioridade:** Must

```gherkin
Dado que um agent solicitante (RF-001 ou RF-002) precisa de um sumário de código-fonte
Quando a solicitação for delegada ao agent especialista de sumarização via run_subagent
Então o agent especialista deve tentar a via determinística (heurística/AST/parser) primeiro
E somente invocar um modelo LLM leve como fallback se a via determinística não atender à fidelidade mínima exigida (RF-004)
E em nenhum momento uma lib de parsing deve ser chamada diretamente por RF-001/RF-002 sem passar pelo agent especialista
```

## 3) Requisitos Não-Funcionais (RNF — FURPS+)

### RNF-001 — Execução prioritariamente local/offline, com fallback LLM controlado [Design/Implementation] — **REVISADO (rodada 2, 2026-08-31)**
> ⚠️ Substitui a versão original ("100% local/offline, sem chamada a LLM externo"), que foi confirmada na rodada 1 mas ficou **incompatível** com a decisão de usar um agent especialista (LLM-backed por natureza, como os demais agents do catálogo). Ver nota de pivô em §0.

O agent especialista de sumarização (RF-008) deve tentar primeiro a via determinística (heurística/AST/parser), sem qualquer custo de tokens. Somente quando essa via for insuficiente para atender à fidelidade mínima (RF-004), o agent pode invocar um modelo LLM **leve/barato** (ex.: Haiku), dentro do mesmo provedor/ecossistema já contratado (Claude/Copilot) — nunca um serviço de LLM de terceiro externo e não relacionado ao provedor em uso.
**Fonte:** resposta "natureza-agent" — opção "Híbrido: agent orquestra, mas delega para LLM (barato) apenas quando necessário" (2026-08-31, rodada 2)
**Prioridade:** Must

```gherkin
Dado o agent especialista de sumarização em execução para um arquivo-fonte
Quando a via determinística (heurística/AST/parser) for suficiente para atender à fidelidade mínima
Então nenhuma chamada a modelo LLM deve ocorrer

Dado que a via determinística não atendeu à fidelidade mínima exigida
Quando o agent especialista invocar um modelo LLM como fallback
Então esse modelo deve ser leve/barato e pertencer ao mesmo provedor/ecossistema já contratado
E o custo dessa chamada deve ser medido conforme RNF-002
```

### RNF-002 — Custo da sumarização não pode superar a economia [Supportability]
O custo total (tokens/créditos) de gerar o sumário não deve exceder a economia projetada de tokens no fluxo consumidor que o utiliza.
**Fonte:** *"custo aceitável da própria sumarização (não pode custar mais tokens do que economiza)"* (pedido original, ponto 5 da lista de esclarecimentos)
**Prioridade:** Must

```gherkin
Dado um sumário gerado para um fluxo consumidor específico
Quando o custo total de geração do sumário for maior que a economia projetada de tokens desse fluxo
Então o sistema deve sinalizar essa condição e não considerar o sumário benéfico
```

### RNF-003 — Idempotência e cache [Reliability/Supportability]
Solicitações repetidas de sumarização para conteúdo-fonte inalterado devem reaproveitar o resultado já cacheado, sem reprocessar.
**Fonte:** *"idempotência/cache de resultado sumarizado"* (pedido original) + resposta P7 (persistência apenas no cache do context-mode)
**Prioridade:** Should

```gherkin
Dado um arquivo já sumarizado e sem alteração desde a última execução
Quando uma nova solicitação de sumarização for feita para o mesmo arquivo
Então o sistema deve retornar o resultado cacheado sem reexecutar a sumarização
```

### RNF-004 — Versionamento de cache por hash [Supportability] — FORA DO MVP
TTL/invalidação de cache por hash do arquivo-fonte não é exigido nesta fase.
**Fonte:** proposta de MVP confirmada ("sem TTL nesta fase")
**Prioridade:** Won't (nesta fase — registrado para não reabrir debate)

### RNF-005 — Compliance de governança [Design/Implementation+]
O processo de sumarização deve respeitar:
- **R-009**: a sugestão pós-`/init-context` (RF-001) nunca executa nem persiste sem confirmação explícita do usuário.
- **R-010**: o sumário nunca deve expor credencial, token ou segredo presente no código-fonte original.
- **R-038**: qualquer artefato de governança gerado por este requisito (agent/skill/instruction) deve permanecer genérico, desacoplado de projeto/tecnologia específica.

**Fonte:** resposta P9 (aceitar como restrições explícitas) + `CLAUDE.md` R-009/R-010/R-038
**Prioridade:** Must

```gherkin
Dado um arquivo-fonte contendo uma credencial ou segredo hardcoded
Quando o arquivo for sumarizado
Então o sumário resultante não deve reproduzir o valor do segredo
```

### RNF-006 — Latência por execução [Performance] — NÃO IDENTIFICADO
Limiar de latência aceitável por sumarização não foi coletado nesta rodada de intake. **Declarado explicitamente como não identificado** — não suposto.

### RNF-007 — Libs de parsing como tool interna do agent, nunca como executor autônomo [Design/Implementation] — NOVO (rodada 2)
Qualquer lib de parsing/sumarização (ex.: tree-sitter, AST parsers específicos por linguagem) utilizada pelo agent especialista (RF-008) deve ser tratada como **ferramenta interna** do agent, nunca como componente chamado diretamente por outros agents (RF-001/RF-002) sem passar pela orquestração do agent especialista.
**Fonte:** resposta "escopo-lib" — opção "Sim, o agent pode usar libs internamente como tool, desde que a orquestração/decisão seja do agent" (2026-08-31, rodada 2)
**Prioridade:** Must

```gherkin
Dado que o agent especialista de sumarização utiliza uma lib de parsing internamente
Quando um agent solicitante (RF-001/RF-002) precisar de um sumário
Então esse agent solicitante deve invocar o agent especialista via run_subagent
E nunca deve chamar a lib de parsing diretamente
```

## 4) Lacunas / Ambiguidades Pendentes

- **Meta numérica de economia de tokens (RF-006/RF-007):** stakeholder optou por deixar em aberto; requer nova rodada de `ask_questions` quando houver dado real de baseline para propor meta.
- **Latência aceitável por execução (RNF-006):** não coletado — pendente de pergunta futura antes de qualquer NFR de performance ser fechado.
- **Fidelidade diferenciada por gatilho (RF-004):** resposta indicou "depende do gatilho (P1)" — apenas o piso mínimo de MVP foi fechado; regras de fidelidade específicas por RF-001 vs. RF-002 ainda não foram detalhadas.
- **Granularidade fina (função/método, classe/módulo):** fora do MVP (Should) — sem critério de aceite Gherkin definido; requer nova rodada de intake na fase 2.
- **TTL/invalidação de cache por hash (RNF-004):** fora do MVP — sem critério definido.
- ~~**Nome/identidade do agent especialista (RF-008)**~~ — **RESOLVIDO (rodada 3):** implementado como `code-summarizer` em `.github/agents/code-summarizer.agent.md`, registrado em `catalog.yaml`/`README.md`/`routing-graph.yaml`/`casos-roteamento.yaml`. Nome de trabalho aceito por uso; TODO-a no corpo do agent mantém aberto para rename futuro se necessário.
- ~~**Critério objetivo de fallback determinístico → LLM dentro do `code-summarizer` (TODO-b do agent)**~~ — **RESOLVIDO (2026-08-31):** `@deep-search` pesquisou libs open-source (tree-sitter/web-tree-sitter, node-sql-parser, typescript-estree, java-parser) e `@analysis-architect` validou/fechou a decisão no contexto real do sandbox `ctx_execute`. Threshold fechado: fallback dispara quando <100% assinatura pública OU <80% blocos de decisão (definição por stack) OU erro de parsing/stack não suportada — mesmo par de números já usado em "Critérios Objetivos e Mensuráveis", sem faixa intermediária. Libs fechadas por stack: `web-tree-sitter` (Java/TS), `ast` nativo (Python), `node-sql-parser` (SQL). Ver `code-summarizer.agent.md` § "Libs de Parsing por Stack (Modo 1)".
- **Modelo LLM barato específico para o fallback:** RNF-001 menciona "leve/barato (ex.: Haiku)" como exemplo, mas não há confirmação formal de qual modelo usar — decisão técnica, não de requisito.

## 5) Rastreabilidade Resumida

| ID | Fonte |
|---|---|
| RF-001 | Resposta P1 (freeform) + pivô rodada 2 + correção de gatilho rodada 3 (confirmado pelo usuário real) |
| RF-002 | Resposta P1 (freeform) + pivô rodada 2 + threshold >300 linhas/20KB confirmado rodada 3 (usuário real) |
| RF-003 | Resposta P2 + confirmação MVP |
| RF-004 | Resposta P4 + confirmação MVP |
| RF-005 | Resposta P6 |
| RF-006 | Confirmação MVP |
| RF-007 | Resposta P3 |
| RF-008 | Resposta "natureza-agent" + "escopo-lib" (rodada 2, 2026-08-31) — implementado em `code-summarizer.agent.md` |
| RNF-001 | Resposta "natureza-agent" (rodada 2) — **revisa** resposta P5 da rodada 1 |
| RNF-002 | Pedido original (ponto 5) |
| RNF-003 | Pedido original + resposta P7 |
| RNF-004 | Confirmação MVP |
| RNF-005 | Resposta P9 + CLAUDE.md |
| RNF-006 | Não identificado (lacuna) |
| RNF-007 | Resposta "escopo-lib" (rodada 2, 2026-08-31) |

---

**Veredito de completude:** INCOMPLETO — MVP fechado e **implementado** para RF-001 (corrigido), RF-002 (threshold definido), RF-003, RF-006, RF-007, RF-008 (agent criado), RNF-001 (revisado), RNF-002, RNF-007 (todos **confirmados pelo usuário real**, rodadas 1, 2 e 3 — 2026-08-31). RF-004, RF-005, RNF-003, RNF-005 permanecem como **hipótese do subagent, ainda não revalidada com o usuário**. 5 lacunas (§4) seguem pendentes — nome do agent resolvido nesta rodada.

**Artefatos já criados/atualizados (rodada 3):**
- `.github/agents/code-summarizer.agent.md` (agent RF-008)
- `.github/agents/catalog.yaml` + `.github/agents/README.md` (registro do agent)
- `docs/ai-context/routing-graph.yaml` (nó + 2 arestas — R-040)
- `.github/agents/agent-router.agent.md` (Decision Tree + Quando Delegar — R-040)
- `docs/ai-context/evals/casos-roteamento.yaml` (canon-015 — R-040)
- `.github/prompts/add-project-context.prompt.md` (FASE 3.5 — hook RF-001 real)
- `.github/skills/context-mode/SKILL.md` (regra central RF-002 + exceção de guardrail para resumos)

**Handoff sugerido:**
- `@test-strategy` — planejar cobertura de teste para os critérios de aceite Gherkin (RF-001..RF-008, RNF-001..RNF-003, RNF-005, RNF-007).
- `requirements-analyst` (nova rodada) — revalidar com o usuário real: fidelidade por gatilho (RF-004), escopo multi-stack (RF-005), persistência/TTL (RNF-003), meta numérica (lacuna), latência (lacuna), granularidade fina (lacuna).

**Próximo passo mínimo:** threshold de fallback (TODO-b) e libs de parsing por stack fechados (2026-08-31); próxima ação recomendada é implementar o Modo 1 do `code-summarizer` usando as libs fechadas, rodando smoke test contra os 4 golden fixtures antes do PR, ou `@test-strategy` para cobertura Gherkin.

