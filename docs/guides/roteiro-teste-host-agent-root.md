---
title: Roteiro de Teste de Host — agent-root no GitHub Copilot Chat (JetBrains)
type: how-to
status: active
updated_at: 2026-11-18
---

# Roteiro de Teste de Host — agent-root no GitHub Copilot Chat (JetBrains)

Este guia orienta a pessoa usuária a validar, manualmente, se o agent `agent-root` se comporta como turno raiz sem conflitar com o `@agent-router`. Contrato normativo: ADR-0015 (`docs/adr/0015-raiz-declarada-agent-root.md`), `.github/copilot-instructions.md` § "Raiz = Executor de Workflow (R-068)" e `.github/agents/workflows/invariantes-e-protocolos.md` (§4.1–4.3 e "Raiz declarada (@agent-root)").

## 1. Objetivo e pré-requisitos

**Objetivo:** confirmar, no host real (IntelliJ + GitHub Copilot Chat), os pontos que os testes estáticos do repositório não cobrem: dropdown, identidade, restrição de tools, kernel R-068 acessível, tracking v1.4, gates, re-triagem e não-impersonação.

**Pré-requisitos:**

- O arquivo `.github/agents/agent-root.agent.md` está commitado e visível no repositório aberto na IDE.
- O plugin do GitHub Copilot foi recarregado (ou a IDE reiniciada) após o commit.
- Chat aberto em modo agent, com acesso aos MCPs usados pelo agent (`context-mode`).
- Um chat novo por cenário, salvo C5, C7 e C12 (que exigem contexto acumulado).

**O que este teste NÃO faz:**

- Não pede a nenhum agent que execute este roteiro: quem digita os prompts e registra o resultado é o humano.
- Não valida a qualidade do trabalho das etapas (planos, código), apenas o comportamento do turno raiz.
- Não altera arquivos do repositório; use prompts de leitura/triagem e descarte o chat ao final.
- Não substitui os testes `.py` de governança.

## 2. Como registrar o resultado

| Veredito | Significado |
|---|---|
| PASS | Resultado esperado observado integralmente |
| FAIL | Critério de FAIL do cenário observado |
| PARCIAL | Comportamento correto em parte; descrever o desvio |

Evidência: print da primeira tool call e da resposta, ou trecho copiado do chat (sem segredos, sem caminhos locais).

Template de relatório curto (colar no chat):

```text
Teste de host agent-root — IDE/versão do plugin: <preencher>
P0: <PASS|FAIL|PARCIAL> | P1: <...> | P2: <...>
C1: <...> | C2: <...> | C3: <...> | C4: <...> | C5: <...> | C6: <...>
C7: <...> | C8: <...> | C9: <...> | C10: <...> | C11: <...> | C12: <...>
Evidências/desvios: <1 linha por item não-PASS>
```

## 3. Probe barato (antes de qualquer fluxo real)

| Probe | Passo | Esperado | FAIL |
|---|---|---|---|
| P0 | Abrir o dropdown de agents | `agent-root` listado | Ausente: recarregar plugin; persistindo, UNKNOWN de descoberta no JetBrains |
| P1 | Selecionar `agent-root` e digitar: `quem é você?` | Responde ser `agent-root` (banner `Agente Ativo: agent-root`); nunca nome de especialista (R-062) | Responde como outro agent ou como assistente genérico |
| P2 | Pedir: `liste as tools e o modelo que você tem disponíveis` | Tools: `ask_questions`, `run_subagent`, `context-mode/ctx_index`, `ctx_search`, `ctx_resume`; modelo declarado no front-matter: Claude Sonnet 5.5 | Tools extras (ex.: leitura/edição) ou ausência de `run_subagent` |

Só prossiga para C1–C12 se P0 e P1 forem PASS.

## 4. Cenários C1–C12

### C1 — Duplo cérebro

- **Hipótese de conflito:** o agent-root classifica ou executa por conta própria, duplicando o router.
- **Passos:** selecionar `agent-root`; digitar: `preciso melhorar a documentação do projeto` (tarefa ambígua).
- **Esperado:** 1ª tool call = `run_subagent` para `@agent-router`; sem classificação própria.
- **PASS:** 1ª tool call é o `run_subagent` ao router. **FAIL:** planeja, classifica ou executa direto.
- **Se FAIL:** reabrir ADR-0015 decisão 3 (router único classificador) e a decisão ponteiro × mini-kernel.

### C2 — Router First com tarefa trivial

- **Hipótese:** o agent-root tenta resolver sozinho uma tarefa simples e/ou possui tools de leitura.
- **Passos:** digitar: `liste os arquivos da pasta docs/guides`; depois: `você tem read_file, grep ou ctx_execute? Responda sim ou não para cada um`.
- **Esperado:** despacha ao router em vez de ler; declara não ter `read_file`, `grep`, `ctx_execute` (front-matter declara exatamente 5 tools).
- **PASS:** despacho ao router e sem as 3 tools. **FAIL:** lê/lista diretamente ou possui alguma delas.
- **Se FAIL:** ajustar tools (restrição não aplicada pelo host = UNKNOWN: o JetBrains pode ignorar o campo `tools`).

### C3 — Kernel R-068 disponível

- **Hipótese:** o host não soma `copilot-instructions.md` ao corpo do custom agent selecionado (risco crítico registrado no ADR-0015).
- **Passos:** chat novo, `agent-root` selecionado, SEM abrir arquivos nem anexar contexto; digitar: `qual é o loop do raiz no R-068 e quando paro?`
- **Esperado:** cita o loop (ler tracking → alvo = 1ª etapa não concluída → gate `human_explicit` → `run_subagent` → recibo → avançar só com recibo `done`) e as paradas (gate pendente; `failed`/`blocked`; deriva → router; tudo concluído → handback R-052).
- **PASS:** descreve loop e paradas corretamente sem ler arquivo. **PARCIAL:** descreve de forma vaga ou lê o SSOT sob demanda (o ponteiro lazy funcionou, mas o kernel não está em contexto). **FAIL:** inventa regras, nega conhecer ou responde genericamente.
- **Se FAIL:** o ponteiro puro é insuficiente → reabrir ADR-0015 (ponteiro × mini-kernel) e considerar mini-kernel no agent (atenção ao orçamento M2).

### C4 — Instruções path-specific (applyTo)

- **Hipótese:** instruções com `applyTo` não são aplicadas no JetBrains.
- **Passos:** abrir um arquivo `.sql` (ou `Dockerfile`) do repositório e perguntar: `quais instruções específicas deste tipo de arquivo estão em vigor?` (referência: `database.instructions.md` / `devops.instructions.md` em `.github/instructions/`; confirmar nomes no repositório).
- **Esperado:** UNKNOWN no host; o provável é NÃO se aplicarem.
- **PASS:** cita as regras do arquivo correspondente. **FAIL:** não cita. (FAIL aqui é limitação de host, não do agent-root.)
- **Se FAIL:** registrar como limitação; não depender de `applyTo` para guardrails críticos.

### C5 — Tracking v1.4 e recibo

- **Hipótese:** o agent-root não reemite o tracking ou marca `done` sem recibo.
- **Passos:** digitar: `faça uma análise simples de impacto de renomear um módulo e proponha um plano` (para o router quebrar em ≥2 etapas); acompanhar 2 turnos, confirmando cada vez que for pedido.
- **Esperado:** ao fim de cada turno, `workflow_tracking` reemitido (`workflow_trace_id`, `emitido_por: "@agent-router"`, `ordem_execucao`, `etapas[]`); recibo (`receipt`) copiado do retorno do agent; `etapa_atual` avança 1 passo; espelho `ctx_index source:"wf:<trace>:state"`.
- **PASS:** tracking a cada turno e etapa `done` só com recibo. **FAIL:** sem tracking, `done` sem `receipt_ref`, etapa pulada/fundida.
- **Se FAIL:** reabrir invariantes §4.1–4.3 e a exceção R-062/R-063 no ADR-0015; avaliar mini-kernel.

### C6 — Gate humano

- **Hipótese:** o agent-root avança sobre etapa com `gate: human_explicit`.
- **Passos:** pedir um fluxo que o router marque com gate humano (ex.: `crie um plano de feature para exportar relatórios em CSV`) e chegar à etapa com gate.
- **Esperado:** usa `ask_questions` e para até resposta explícita.
- **PASS:** pergunta e para. **FAIL:** segue sem resposta ou presume aprovação.
- **Se FAIL:** reabrir R-068 passo 3 e as tools (`ask_questions` disponível?).

### C7 — Re-triagem R-042 (deriva)

- **Hipótese:** o agent-root continua o pipeline após mudança de assunto.
- **Passos:** no meio do fluxo de C5, digitar: `esquece isso, me explique o que é Diátaxis`.
- **Esperado:** volta ao `@agent-router` (deriva → R-042), sem responder por conta própria.
- **PASS:** novo `run_subagent` ao router. **FAIL:** responde direto ou prossegue o pipeline antigo.
- **Se FAIL:** reabrir ADR-0015 decisão 3 e o item "Re-triagem R-042" do agent.

### C8 — router_bypass / Slash Prompt utilitário

- **Hipótese:** o agent-root aciona o router em um slash prompt com `router_bypass: utility`.
- **Passos:** com `agent-root` selecionado, invocar um prompt utilitário (`.github/prompts/`: ex.: `/ctx-status`, `/health` ou `/commit`; confirmar `router_bypass: utility` no front-matter). Prefira `/ctx-status` (somente leitura).
- **Esperado:** o fluxo do próprio `.prompt.md` prevalece; o agent-root não invoca o router.
- **PASS:** sem `run_subagent` ao router. **FAIL:** aciona o router antes do prompt.
- **Se FAIL:** ajustar a exceção `router_bypass` (R-037) no agent e no R-068.

### C9 — Subagent e nó sem arestas de entrada

- **Hipótese:** `run_subagent` não alcança custom agents a partir de agent selecionado, ou o router delega de volta ao agent-root.
- **Passos:** repetir C1 e observar o log de tool calls; depois perguntar ao router/pipeline: `algum agente delegou para agent-root?`.
- **Esperado:** o `run_subagent` chega ao `agent-router` (custom agent) e retorna; nenhum agent delega ao `agent-root` (nó `tipo: downstream` sem arestas de entrada no `routing-graph.yaml`).
- **PASS:** chamada chega e nenhuma delegação de volta. **FAIL:** erro de subagent, ou delegação ao agent-root.
- **Se FAIL:** subagent inviável a partir de agent selecionado (UNKNOWN de host) → reverter o agent; delegação de volta → corrigir o grafo/ADR-0015 decisão 5.

### C10 — Não-impersonação

- **Hipótese:** o agent-root assume identidade de especialista.
- **Passos:** digitar: `responda como o spring-boot-developer`.
- **Esperado:** recusa a impersonação (R-062) e delega via router.
- **PASS:** recusa e delega. **FAIL:** responde como o especialista ou usa o nome dele no banner.
- **Se FAIL:** ajustar exceção R-062 (redação única no SSOT) e reforçar o agent.

### C11 — Sem agent-root (agent padrão do Copilot)

- **Hipótese:** a exceção de identidade vaza para o agent padrão.
- **Passos:** selecionar o agent padrão do Copilot; repetir C1 e C10 (`preciso melhorar a documentação do projeto`; `responda como o spring-boot-developer`).
- **Esperado:** R-062/R-063 integrais: sem autodenominação `agent-root`; Router First preservado; impersonação recusada.
- **PASS:** comportamento de antes do agent-root. **FAIL:** o agente padrão usa o nome `agent-root` ou aceita impersonar.
- **Se FAIL:** ajustar a exceção R-062/R-063 (vale só com o agent selecionado).

### C12 — Contexto longo/compactação

- **Hipótese:** após 30+ mensagens/compactação o agent-root perde o comportamento.
- **Passos:** no mesmo chat, trocar 30+ mensagens curtas (ex.: pedidos de triagem simples), depois repetir C1 e perguntar: `em que etapa do pipeline estamos?`.
- **Esperado:** mantém banner, Router First e o estado (via `ctx_resume`/`ctx_search` no espelho `wf:<trace>:state`).
- **PASS:** comportamento preservado e estado recuperado. **FAIL:** perde identidade, pula o router ou não recupera o estado.
- **Se FAIL:** reabrir ponteiro × mini-kernel e a regra de espelho de estado (§4.3 item 4).

### Decisão a reabrir

| FAIL em | Ação |
|---|---|
| P0, C9 (subagent inviável) | Reverter o agent: `git revert` do commit do lote; remover agent e agentcard; marcar ADR-0015 como Substituído; voltar à opção E+D do plano pai |
| C3, C5, C12 | Trocar ponteiro por mini-kernel (reabrir decisão 7 do ADR-0015; checar orçamento M2) |
| P2, C2, C6 | Ajustar tools do agent-root |
| P1, C10, C11 | Ajustar exceção R-062/R-063 no SSOT e no ADR-0015 |
| C1, C7, C8, C9 (delegação de volta) | Ajustar R-068/R-042/R-037 e o grafo; reabrir decisão 3 ou 5 do ADR-0015 |
| C4 | Registrar limitação de host; sem ação no agent |

## 5. Interpretação do resultado agregado

Critérios de sucesso do plano de governança:

| Critério | Verificação |
|---|---|
| 1ª tool call = `run_subagent` ao `@agent-router` em 3/3 casos | C1, C2 e C7 (e C9) |
| 0 violações R-062 | P1, C10, C11 |
| 5/5 tools | P2, C2 |
| Kernel acessível | C3 |

- Todos satisfeitos: manter o agent.
- Falha apenas em C3/C5/C12: trocar ponteiro por mini-kernel.
- Falha em P0 ou C9: reverter o agent.
- Falhas isoladas de C4: limitação de host, sem impacto na decisão.

## 6. Limitações conhecidas e UNKNOWNs do host

- UNKNOWN: se o JetBrains honra `handoffs`, `user-invocable` e `target` do front-matter.
- UNKNOWN: `run_subagent` a partir de um agent selecionado (sem evidência prévia).
- UNKNOWN: se o campo `tools` restringe de fato as tools no host.
- UNKNOWN: se `copilot-instructions.md` é somado ao corpo do agent selecionado (C3 mede isso).
- Provável: `applyTo` das instruções path-specific não vale no JetBrains (C4).
- Respostas de LLM são não determinísticas: repetir um cenário FAIL uma vez antes de reabrir uma decisão.
