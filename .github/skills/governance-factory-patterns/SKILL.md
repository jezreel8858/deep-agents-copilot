---
name: governance-factory-patterns
description: >
  Fluxo canônico "Factory Pattern" para agents que criam/revisam artefatos de
  governança (agent, skill, prompt, stack) — Decision Tree comum, checklist de
  qualidade estrutural e template de saída com validações ✅/❌ parametrizável
  por tipo de artefato ou subsistema de domínio.
tier: 1
category: governance
triggers:
  - "criar agent"
  - "criar skill"
  - "criar prompt"
  - "criar stack"
  - "nova stack"
  - "ecossistema de agentes"
  - "factory pattern"
  - "atualizar catálogo"
  - "checklist de criação"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/agents/governance-factory.agent.md
tools: []
---

# Governance Factory Patterns

## 0) Problema Resolvido

Esta skill formaliza o fluxo compartilhado pelos 4 tipos de artefatos e subsistemas de governança criados/revisados por `governance-factory` (**agent**, **skill**, **prompt** e **stack** — ecossistema de domínio completo). Os 3 primeiros unificam a governança atômica (que antes eram `agent-factory`, `skill-factory`, `prompt-factory`), enquanto o tipo `stack` padroniza a criação de novos subsistemas tecnológicos hierárquicos isolados (como Angular, Spring Boot e Spring Reactive), evitando a proliferação desordenada de nós no catálogo central. Sem esta skill, cada `type` reimplementaria o mesmo fluxo com variações e risco de drift (R-015, R-040, R-042).

## 1) Decision Tree Canônica (Factory Pattern)

```text
Solicitação de criar/revisar/auditar artefato de governança
    ↓
Tipo de artefato? → agent | skill | prompt | stack
    ↓
Já existe artefato/ecossistema equivalente? (busca por nome + escopo semântico)
    ├─ Sim → propor REVISÃO do existente (nunca duplicar)
    └─ Não → prosseguir para CRIAÇÃO
    ↓
[Se CRIAÇÃO — OBRIGATÓRIO] Delegar ao @deep-search via run_subagent:
    Pesquisar na web (quando disponível via Tavily) e internamente sobre
    as melhores diretrizes, tooling de testes e skills para o artefato/stack
    ↓
[Após retorno do @deep-search] Consumir síntese e incorporar diretrizes/skills ao escopo
    ↓
Coletar campos obrigatórios via ask_questions (ver `structured-intake-patterns`
para o padrão de intake, se aplicável)
    ↓
Gerar arquivo(s) seguindo template canônico do tipo de artefato ou topologia da stack:
    ├─ agent  → .github/agents/<name>.agent.md
    ├─ skill  → .github/skills/<nome>/SKILL.md
    ├─ prompt → .github/prompts/<verbo>-<objeto>.prompt.md
    └─ stack  → .github/agents/<camada>/<stack>/ (<stack>-catalog.yaml + <stack>-router + especialistas)
    ↓
Se artefato = agent | prompt | router de stack → Selecionar e validar `model:` (§9 desta skill —
  classificar perfil, escrever candidato, rodar get_errors, confirmar antes de prosseguir)
    ↓
Autocrítica grounded, 1 round (§3.1 — gate obrigatório antes de finalizar)
    ↓
Executar Checklist de Qualidade Estrutural (§3 desta skill)
    ↓
Atualizar catálogo(s) + README na MESMA entrega (R-015 — atomicidade obrigatória):
    ├─ agent  → catalog.yaml + README.md
    ├─ skill  → .index.json + README.md
    ├─ prompt → README.md de prompts
    └─ stack  → catalog.yaml (apenas router) + routing-graph.yaml + agent-router.agent.md + README.md
    ↓
Reportar no Formato de Saída (§4 desta skill)
```

## 2) Campos Obrigatórios por Tipo de Artefato

| Campo | agent | skill | prompt | stack |
|---|---|---|---|---|
| Nome (kebab-case) | ✅ | ✅ | ✅ | ✅ |
| Descrição objetiva (frontmatter) — ≤ 500 caracteres, ver §10 | ✅ | ✅ | ✅ | ✅ (no sub-catálogo e no router) |
| Tier/Categoria | — | ✅ | — | — |
| Model | ✅ | — | ✅ (se aplicável) | ✅ (no router e nos especialistas) |
| Tools (com `run_subagent` obrigatório — R-042) | ✅ | opcional | opcional | ✅ (em todos os agents) |
| Triggers (PT-BR) | — | ✅ | — | — |
| Source_docs | recomendado | ✅ | recomendado | ✅ |
| Registro em índice/catálogo | `catalog.yaml` + `README.md` | `.index.json` + `README.md` | `README.md` de prompts | `catalog.yaml` + `routing-graph.yaml` + `agent-router.agent.md` + `README.md` |

## 3) Checklist Genérico de Qualidade Estrutural

- [ ] Nome em `kebab-case`, sem espaços/maiúsculas.
- [ ] Campo obrigatório do tipo de artefato presente (ver tabela §2).
- [ ] Não duplica artefato existente (busca prévia por nome E por escopo semântico).
- [ ] Se CRIAÇÃO: pesquisa prévia de melhores diretrizes e skills delegada ao `@deep-search` (web/local) e síntese incorporada ao design do artefato/ecossistema.
- [ ] Catálogo/índice atualizado **na mesma entrega** (R-015 — nunca "depois").
- [ ] README correspondente atualizado **na mesma entrega**.
- [ ] Se `agent`: `run_subagent` presente no frontmatter `tools:` (bloqueante — R-042); seção "Retorno ao Router" declarada; banner "Agente Ativo" presente no Formato de Saída.
- [ ] Se `skill`: `tier`, `category`, `triggers` em PT-BR presentes; `source_docs` aponta para arquivos reais (não inventados).
- [ ] Se `prompt`: nomenclatura `.prompt.md`, frontmatter mínimo (`description`, `model` quando aplicável), separação de responsabilidade clara com `.instructions.md` (não duplicar regra já coberta por adapter).
- [ ] Se `stack`: diretório isolado criado em `.github/agents/<camada>/<stack>/` contendo `<stack>-catalog.yaml`, `<stack>-router.agent.md` e pacote canônico de especialistas (.agent.md) — ver §11.
- [ ] Se `stack`: `<stack>-router.agent.md` implementa R-042, banner de visibilidade de fluxo, e consulta ao `@test-strategy` (Fluxo 2 TDD).
- [ ] Se `stack`: sincronização atômica em 4 arquivos globais (`catalog.yaml` [apenas o router], `routing-graph.yaml`, `agent-router.agent.md`, `README.md`).
- [ ] Se `agent`/`prompt`/`stack`: `model:` é string única (nunca array), Title Case oficial (nunca kebab-case), e validado via `get_errors` sem `Unknown model` (§9).
- [ ] `description` do frontmatter ≤ 500 caracteres (alvo ≤ 400), 1 parágrafo, sem RF-ID/RNF-ID/changelog embutido (§10).

### 3.1) Gate de Autocrítica Semântica (grounded, 1 round — obrigatório)

> Fecha o gap que a checklist estrutural acima **não cobre**: coerência de *conteúdo*, não de *forma*. Baseado no padrão single-shot de [`reflection-self-critique-patterns/SKILL.md`](../reflection-self-critique-patterns/SKILL.md) §2 — aplicado aqui porque os 3 factory agents **geram artefato revisável** (diferente de um Retriever decidindo parar/continuar uma chamada externa, que é anti-padrão de uso desta mesma skill).

Antes de finalizar o conteúdo (antes do Checklist §3), responder objetivamente, com evidência (não opinião):

1. **Toda referência cruzada a outra skill/agent no conteúdo gerado é uma dependência FUNCIONAL real, ou apenas um rótulo semântico?** (ex.: registrar um agent como "consumidor" de uma skill exige que o mecanismo do agent dependa daquela skill — não basta o tema "parecer" relacionado).
2. **O escopo declarado da skill/agent sendo referenciado bate com o uso real proposto?** Reler a `description`/§0 do artefato referenciado e confirmar, não assumir pelo nome.
3. **Esta mudança introduz acoplamento novo entre 2 artefatos que antes eram independentes?** Se sim, esse acoplamento é necessário ou é conveniência de redação?

Se qualquer resposta indicar inconsistência: corrigir o conteúdo (remover referência indevida, ajustar redação) **antes** de prosseguir para o Checklist §3 — máximo 1 round de correção automática (alinhado a R-011/regra "Sem Loops"); se ainda inconsistente após 1 round, reportar como bloqueante (R-020) e aguardar orientação.

## 4) Formato de Saída — Bloco de Validações ✅/❌ (parametrizável)

```markdown
Arquivo criado/alterado: `.github/<tipo>/<nome>.<extensao>` (ou pasta `.github/agents/<camada>/<stack>/`)

Validações:
- Nome kebab-case: ✅/❌
- Campo obrigatório do tipo presente: ✅/❌
- Não duplica artefato existente: ✅/❌
- [se criação] Pesquisa prévia via @deep-search executada e incorporada: ✅/❌
- Catálogo/índice atualizado atomicamente (R-015): ✅/❌
- README atualizado atomicamente: ✅/❌
- [se agent] run_subagent presente (R-042): ✅/❌
- [se agent] Seção "Retorno ao Router" presente: ✅/❌
- [se skill] tier/category/triggers presentes: ✅/❌
- [se agent/prompt/stack] model: string única, Title Case oficial, validado via get_errors (§9): ✅/❌
- [se stack] Sub-catálogo local e supervisor configurados (§11): ✅/❌
- [se stack] Quádrupla sincronização global executada (catalog + routing-graph + agent-router + README): ✅/❌
- description do frontmatter ≤ 500 caracteres, sem changelog/RF-ID embutido (§10): ✅/❌

Arquivos atualizados:
- <lista de catálogo/README/índice tocados>

Resumo: <1-2 linhas do que foi criado/revisado e por quê>
```

## 5) Regra de Ouro: Atualização Atômica (R-015)

Nenhuma criação/revisão de artefato de governança é considerada completa sem a atualização do catálogo/índice correspondente **na mesma entrega**. Isso é comum aos 4 tipos de artefato e não deve ser tratado como etapa opcional/posterior — um artefato criado sem registro no catálogo é invisível para o `agent-router` e para descoberta progressiva (`@agent list`, `@skill list`). Para novas stacks (`type: stack`), a atomicidade é quádrupla: catálogo central (apenas router), grafo de roteamento, agent-router e README.

## 6) Anti-padrões

- ❌ Criar novo agent, prompt, skill ou stack sem delegar previamente a pesquisa de melhores diretrizes e skills ao `@deep-search` (web quando disponível / repositório).
- ❌ Descartar ou ignorar os achados retornados pelo `@deep-search` ao gerar o artefato ou ecossistema.
- ❌ Criar artefato e "esquecer" de atualizar catálogo/README na mesma entrega (viola R-015).
- ❌ Criar especialistas de uma nova stack espalhados na raiz `.github/agents/` em vez de isolados em pasta dedicada com sub-catálogo (causa explosão de nós no catálogo central).
- ❌ Duplicar artefato existente por não ter buscado por escopo semântico (só buscar por nome exato é insuficiente).
- ❌ Agent criado sem `run_subagent` no frontmatter (estruturalmente incapaz de cumprir R-042).
- ❌ Skill criada sem `triggers` em PT-BR ou com `source_docs` apontando para arquivo inexistente.
- ❌ Reinventar o fluxo de Decision Tree em vez de referenciar esta skill — risco de drift entre os 4 `type` (agent/skill/prompt/stack) do `governance-factory`.
- ❌ Registrar referência cruzada a outra skill/agent (ex.: "consumidor de X") sem confirmar dependência funcional real — pular o gate §3.1 e validar só a estrutura (achado real: `deep-search` registrado como consumidor de `reflection-self-critique-patterns` sem uso funcional).
- ❌ Definir `model:` como array ou como slug kebab-case sem rodar `get_errors` (§9) — achado real: 15+ agents/prompts com `Unknown model` por usar `["a","b"]` ou `claude-haiku-4.5` em vez do display name oficial.
- ❌ `description` do frontmatter virar resumo de changelog/RF-ID (§10) — achado real: `code-knowledge-graph` v2.1.0 com description de +1300 caracteres misturando função do agent com histórico de correções.

## 7) Consumidores Mapeados

- `governance-factory` — único consumidor; mantém especificidade por `type` (templates `research-agent.md`/`operational-agent.md` para `type: agent`, template `SKILL.md` para `type: skill`, template/naming `.prompt.md` para `type: prompt`, e topologia hierárquica §11 para `type: stack`), referencia esta skill para o fluxo genérico e checklist comum a todos os tipos.
- **Futuro:** qualquer novo tipo de artefato de governança (ex.: `instructions-factory`, se vier a existir) herda o padrão sem reinventar o fluxo.

## 8) Referências

- `CLAUDE.md` — R-015 (atualização atômica de catálogo).
- `.github/copilot-instructions.md` — R-042 (tooling mínimo, `run_subagent` bloqueante).
- `.github/skills/agent-contracts/SKILL.md` §8-9 — baseline de formato de saída e tooling mínimo por perfil.
- `.github/skills/reflection-self-critique-patterns/SKILL.md` — padrão de autocrítica grounded 1-round usado no gate §3.1.
- `.github/skills/governance-audit-patterns/SKILL.md` — taxonomia de smells usada como referência de coerência semântica no gate §3.1 (auditoria pós-hoc equivalente feita por `agent-auditor`).
- GitHub Docs — [Supported AI models in GitHub Copilot](https://docs.github.com/copilot/reference/ai-models/supported-models) — fonte oficial de nomenclatura de modelo, usada em §9.

## 9) Seleção e Validação de Modelo (`model:` — obrigatório para `agent`/`prompt`)

> Aplica-se quando `governance-factory` cria `type: agent` ou `type: prompt` (skills não têm campo `model:` — ver tabela §2). Fecha 2 gaps reais encontrados em auditoria (2026-09-01): (a) 15+ artefatos usavam array `["a","b"]` — campo não suporta lista, sempre falha; (b) slugs kebab-case (`claude-haiku-4.5`) não são reconhecidos pelo validador do IDE — o nome correto é o **display name oficial** (Title Case).

### 9.1) Classificação de Perfil (escolha do tier — antes de qualquer validação técnica)

| Pergunta (aplicar em ordem — primeira que bater decide) | Tier | Custo (R-021) |
|---|---|---|
| Só lê, roteia, ou preenche template a partir de fatos já extraídos, sem julgamento aberto? (scanner, template-fill, roteamento, checklist, validação) | **Gemini 3.8 Flash** | 0×/0.33× |
| Implementa, refatora, planeja com risco, ou sintetiza análise técnica não-trivial? (specialists, planners, reviewers, extractors) | **Gemini 3.8 Flash** | 1× |
| Decide arquitetura crítica, causa-raiz complexa cross-sistema, ou ação de alta irreversibilidade? (raro — só escalar se as 2 acima não bastarem) | **Claude Opus 5** | 3× |

**Regra de ouro (redução de créditos):** nunca escalar tier acima do mínimo necessário — um agent operacional em Sonnet/Opus é desperdício de crédito sem ganho de qualidade (ver exemplos reais no catálogo: `adapter-generator`, `agent-router`, `binding-initializer` = Haiku; `analysis-architect`, `code-review`, `angular` = Sonnet).

### 9.2) Validação de Disponibilidade Real (obrigatória — antes de finalizar o artefato)

O valor de `model:` deve ser a **string exata do display name oficial** (Title Case) da [tabela oficial](https://docs.github.com/copilot/reference/ai-models/supported-models) — nunca kebab-case, nunca slug de API.

**Protocolo (nesta ordem, sem pular etapa):**
1. Escrever o candidato (Title Case oficial, ex.: `"Gemini 3.8 Flash"`) no frontmatter do arquivo já criado/editado.
2. Chamar `get_errors` no arquivo.
3. Se aparecer `Unknown model: '<valor>'` → modelo não reconhecido **neste ambiente real** (VS Code ou JetBrains) — não prosseguir com esse valor; tentar o próximo candidato do mesmo tier (ex.: se `"Gemini 3.8 Flash"` falhar, considerar `"Claude Sonnet 4.6"` como fallback temporário) e repetir o passo 2.
4. Se `get_errors` não reportar erro de modelo → validado, prosseguir para o restante do checklist (§3).
5. Se 2 candidatos do mesmo tier falharem e não houver certeza de qual string funciona, perguntar ao usuário via `ask_questions`: *"Qual modelo aparece disponível no seletor do Copilot Chat (VS Code) ou do plugin Copilot/AI Assistant (JetBrains) para o tier <Haiku|Sonnet|Opus>?"* com opções pré-preenchidas da tabela oficial + campo aberto — nunca adivinhar variações às cegas indefinidamente.

### 9.3) VS Code vs JetBrains — Sem Paridade Garantida

A tabela oficial declara disponibilidade por superfície (colunas "Visual Studio Code" vs "JetBrains IDEs" vs "Copilot CLI" etc.) — nem todo modelo tem paridade entre as duas. `get_errors` reflete o **ambiente real da sessão atual** e é sempre a fonte de verdade — a tabela estática pode estar desatualizada ou o modelo pode estar indisponível pelo plano/tier de Copilot do usuário (Free vs Pro vs Business/Enterprise), mesmo que a tabela o liste.

### 9.4) Nunca Fazer (Anti-padrões de §9)

- ❌ Usar array `["a","b"]` no campo `model:` — não suportado; sempre string única.
- ❌ Usar slug kebab-case (`claude-haiku-4.5`, `gpt-5.3-codex`) — usar o display name oficial (Title Case).
- ❌ Finalizar o artefato sem rodar `get_errors` para confirmar que o modelo é reconhecido neste ambiente.
- ❌ Escalar para tier mais caro (Sonnet/Opus) quando Haiku atende ao perfil real da tarefa (§9.1) — desperdício de créditos.
- ❌ Perguntar ao usuário (§9.2 passo 5) antes de tentar a validação automática via `get_errors` — pergunta é último recurso, não primeiro passo.

## 10) Tamanho e Conteúdo da `description` (Frontmatter — obrigatório para `agent`, `skill`, `prompt`)

> Fecha gap real (2026-09-01): `code-knowledge-graph.agent.md` acumulou uma `description` de +1300 caracteres em bloco YAML multi-linha (`description: >`), misturando o que o agent faz com changelog de correções ("RF-021 consolidação de motor", "bug corrigido nesta rodada", validação 9/9, histórico de versões). Isso é *anti-padrão* — `description` é metadado de **descoberta** (usado por `@agent search`, `catalog.yaml`, roteamento), não documentação de mudança.

### 10.1) Regra de Ouro (Tamanho)

- **Alvo: ≤ 400 caracteres. Teto rígido: 500 caracteres.** Sempre 1 parágrafo contínuo — sem quebra de linha decorativa nem lista.
- **2-3 frases, no máximo.** Se precisar de uma 4ª frase para explicar o agent, o conteúdo pertence ao corpo (`## Objetivo`), não ao frontmatter.
- Medir com contagem de caracteres do valor de `description` (sem contar a chave `description:`) antes de finalizar — não estimar de cabeça.

### 10.2) O Que Entra (conteúdo permitido)

1. **O quê** o artefato faz (1 frase, verbo de ação).
2. **Quando/para quem** é o ponto de entrada certo (1 frase — diferenciador vs. artefato vizinho, se houver confusão possível).
3. Opcionalmente, 1 restrição crítica de escopo (ex.: "read-only", "nunca implementa código").

### 10.3) O Que NÃO Entra (mover para o corpo do artefato)

| Proibido na `description` | Onde vai de verdade |
|---|---|
| Lista de IDs de requisito (RF-00X, RNF-00X) | `## Objetivo` ou seção dedicada do corpo |
| Changelog / "corrigido nesta rodada" / histórico de versão | `version:` no frontmatter (já existe para isso) + corpo |
| Resultado de validação/gate ("9/9 ✅", "validado em produção") | Seção de critérios objetivos do corpo |
| Detalhe de motor/algoritmo interno (ex.: nome de lib, subprocess) | Seção técnica do corpo (ex.: "Estrutura Interna") |
| Justificativa extensa de decisão de design | Corpo, com link para REQ/ADR se existir |
| Exemplos de uso, tabelas, listas com bullets | Corpo |

### 10.4) Exemplo Real (antes/depois — `code-knowledge-graph`)

**❌ Antes (anti-padrão, ~1300 caracteres, 6+ frases, changelog embutido):** descrição misturava função do agent com RF-001..RF-022, RNF-008..RNF-013, "já removidos", "validado em 4 rodadas reais", regras de motor primário/fallback em detalhe.

**✅ Depois (~350 caracteres, 3 frases):**
```yaml
description: >-
  Constrói e consulta o grafo de conhecimento de código-fonte (imports, chamadas,
  blast radius, acoplamento, ciclos), cross-projeto e puramente determinístico —
  nunca invoca LLM. Motor único: pattern-matching via regex (TypeScript + Java),
  100% Node.js built-ins. FASE obrigatória de `/add-project-context`; grafo
  sempre indexado via ctx_index.
```

### 10.5) Checklist de Conformidade

- [ ] `description` ≤ 500 caracteres (alvo ≤ 400) — contado, não estimado.
- [ ] No máximo 3 frases, 1 parágrafo, sem lista/tabela embutida.
- [ ] Nenhum ID de requisito (RF-/RNF-), changelog ou "corrigido nesta rodada" no valor.
- [ ] Detalhe técnico/algoritmo movido para o corpo (`## Objetivo` ou seção dedicada).
- [ ] Se o artefato tem `version:`, ele é o lugar do histórico — não a `description`.

### 10.6) Anti-padrões

- ❌ `description` como resumo executivo do REQ inteiro (achado real: `code-knowledge-graph` v2.1.0).
- ❌ Usar `description: >` (multi-linha) como desculpa para escrever um parágrafo de changelog — o formato YAML permitir múltiplas linhas não significa que o conteúdo deva crescer sem limite.
- ❌ Copiar a `description` de uma versão anterior e ir "só adicionando mais uma frase" a cada rodada de correção sem nunca revisar o tamanho total.
- ❌ Repetir no frontmatter o mesmo texto já detalhado em `## Objetivo` — se ambos existem, a `description` deve ser o resumo curto, `## Objetivo` o detalhado.

## 11) Topologia e Padrão Canônico para Novas Stacks (type: stack)

A criação de um novo ecossistema de stack (ex.: EJB, React, Python FastAPI) segue a topologia hierárquica consolidada em Angular, Spring Boot e Spring Reactive, estruturada em 5 passos atômicos:

### 11.1) Estrutura de Diretórios e Isolamento
- Caminho: `.github/agents/<camada>/<stack>/`
- `<camada>`: `frontend` ou `backend`
- Mantém o catálogo raiz despoluído e confina os especialistas ao seu respectivo domínio.

### 11.2) Sub-catálogo Local (`<stack>-catalog.yaml`)
- Define metadados do domínio (`domain: "<camada>-<stack>"`), papel do supervisor (`router: id: "<stack>-router"`) e dicionário dos especialistas (`agents:`).
- Cada especialista declara: `id`, `model`, `role` (advisory, implementer, fixer, performance, tester), `domain`, `description` (≤ 400 caracteres), `keywords`, `tools` (com `run_subagent`) e `skills`.

### 11.3) Supervisor de Domínio (`<stack>-router.agent.md`)
- Nome: `<stack>-router`
- Função: Supervisor hierárquico — recebe tarefas do `agent-router` central e despacha para os especialistas locais.
- Regras herdadas: aponta para `../../../../CLAUDE.md` e `./<stack>-catalog.yaml`.
- Banner obrigatório: `Agente Ativo: <stack>-router`.
- Anti-sticky session: regra R-042 com retorno ao `@agent-router` em deriva de intenção.
- Fluxo 2 TDD: consulta prévia ao `@test-strategy` para requisitos de teste complexos antes de acionar test-writers locais.

### 11.4) Pacote Canônico de Especialistas
- **Backend (ex.: EJB)**:
  - `<stack>-arch-advisor` (Read-Only: arquitetura, migrações, dependências)
  - `<stack>-feature-developer` (TDD: componentes, services, transações)
  - `<stack>-bug-fixer` (Fixer: runtime errors, memory leaks, diff mínimo)
  - `<stack>-perf-tuner` (Performance: pool, queries, concorrência, GC)
  - `<stack>-unit-test-writer` (Testes unitários isolados com mocks)
  - `<stack>-integration-test-writer` (Testes integrados com banco/container real)
  - `<stack>-test-fixer` (Diagnóstico e correção de falhas em suítes de teste)
- **Frontend (ex.: React)**:
  - `<stack>-arch-advisor`, `<stack>-feature-developer`, `<stack>-bug-fixer`, `<stack>-ui-stylist`, `<stack>-unit-test-writer`, `<stack>-component-test-writer`, `<stack>-test-fixer`, `<stack>-e2e-writer`.

### 11.5) Quádrupla Sincronização Global Obrigatória (R-015)
Ao criar a stack, o `governance-factory` DEVE atualizar atomicamente:
1. **`.github/agents/catalog.yaml`**: adiciona o nó do `<stack>-router` (apenas o router, não os especialistas locais).
2. **`.github/agents/routing-graph.yaml`**: adiciona o nó `domain_router` e as arestas bidirecionais de/para `agent-router`.
3. **`.github/agents/agent-router.agent.md`**: adiciona o router na tabela de conhecimento, no branch da Decision Tree e na lista de delegação.
4. **`.github/agents/README.md`**: adiciona o router na tabela de catálogo e no mapeamento de rotas rápidas.


