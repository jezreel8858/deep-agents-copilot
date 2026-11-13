---
name: del-project-context
description: >-
  Remove contexto estruturado de um projeto do overlay local (projects.local.yaml,
  gitignored — R-043) e do cache Context Mode. Operação destrutiva com validação
  prévia, confirmação e rollback via Git. NUNCA toca .github/agents/catalog.yaml
  (compartilhado/commitado).
agent: 'agent'
router_bypass: slash_workflow
model: "Gemini 3.8 Flash"
tools: ['read_file', 'insert_edit_into_file', 'file_search', 'list_dir', 'ask_questions', 'run_subagent', 'context-mode/ctx_execute', 'context-mode/ctx_batch_execute', 'context-mode/ctx_search']
argument-hint: '<nome-do-projeto>'
source_docs:
  - '.github/projects.local.yaml.example'
  - '.github/instructions/README.md'
  - 'CLAUDE.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/del-project-context`

> **Propósito**: Remover o registro de um projeto no overlay local `projects.local.yaml` e seu adapter em `.github/instructions/local/`.
> **Workspace**: `${workspaceFolder}`
> **Projeto Alvo**: `${input:nomeDoProjeto}`

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/del-project-context` (argumento: `<nome-do-projeto>`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` na triagem inicial — este Slash Prompt possui `router_bypass: slash_workflow` (exceção canônica a R-037/R-063) e seu fluxo já está definido abaixo; o Orquestrador Raiz DEVE executar diretamente as instruções deste `.prompt.md` (ou despachar diretamente para o subagente previsto neste próprio prompt).
- ✅ O uso de `context-mode` (`ctx_batch_execute`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** remover o projeto especificado de `projects.local.yaml` e deletar seu adapter correspondente em `.github/instructions/local/`.
- ✅ **SEMPRE** solicitar confirmação humana explícita antes de executar a exclusão.
- ❌ **NÃO** tocar em `.github/agents/catalog.yaml` (compartilhado/commitado, R-043).
- ❌ **NÃO** excluir código-fonte ou diretórios do projeto real externo.

---

workflow:
  1: "User fornece nome do projeto"
  2: "Agent valida existência em projects.local.yaml (gitignored, R-043)"
  3: "Agent lista artefatos a remover (YAML entry + arquivo .instructions.md em local/)"
  4: "Agent pede confirmação explícita"
  5: "Se confirmado: Atualiza projects.local.yaml + valida YAML + registra em audit.log"

constraints:
  - "Operação destrutiva — exigir confirmação explícita"
  - "Validar YAML imediatamente após alteração"
  - "NÃO remove adapters globais nem código-fonte"
  - "NÃO usa rm ou operações shell destrutivas — Python via project-context-builder"
  - "NUNCA edita .github/agents/catalog.yaml (compartilhado/commitado) — R-043"
  - "Registrar ação em audit.log"
---

# `/del-project-context` — Remoção de Contexto de Projeto

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/del-project-context`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## Visão Geral

Remove um projeto do overlay local (`.github/projects.local.yaml`, gitignored) e do
armazenamento de instruções locais (`.github/instructions/local/`) — **todos os artefatos
são NESTE repositório de governança, porém LOCAIS/gitignored (R-043)**. Reversível via Git
(arquivo local) ou recriação via `/add-project-context`.

> ⚠️  Esta operação modifica APENAS artefatos locais/gitignored deste repositório.
>     O repositório externo do projeto removido NÃO é tocado.
>     `.github/agents/catalog.yaml` (compartilhado/commitado) NUNCA é tocado.

## Uso

```bash
/del-project-context <nome-do-projeto>
```

### Exemplos

```
/del-project-context project-app
```

## O Que é Removido (NESTE repositório, LOCAIS/gitignored)

| Alvo | Ação | Observação |
|------|------|-----------|
| `./.github/projects.local.yaml` | Remove entrada YAML do projeto | Sintaticamente validado; gitignored |
| `./.github/instructions/local/<projeto>.instructions.md` | Deleta arquivo de instruções | Específico do projeto; gitignored |
| Context Mode Cache (FTS5) | Invalida índice + snapshot | TTL reset (24h) |

## O Que NÃO é Removido

- ✗ Repositório Git / código-fonte do projeto externo
- ✗ Qualquer arquivo dentro do projeto externo
- ✗ Adapters genéricos já existentes em `.github/instructions/` (raiz, compartilhados)
- ✗ `.github/agents/catalog.yaml` (compartilhado/commitado) — nunca teve entrada de projeto (R-043)
- ✗ Regras em `CLAUDE.md` (governança global)
- ✗ Documentação em `docs/` (preservada)

## Fluxo

```
/del-project-context meu-projeto-backend

[1] Validar existência em projects.local.yaml (gitignored)  ✓
[2] Listar artefatos a remover                          ✓
[3] Pedir confirmação explícita (sim/não)               → User
[4] Se sim:
    ├─ Atualizar projects.local.yaml (remove entrada YAML)
    ├─ Validar YAML com yamllint                        [fallback: abortar + Git checkout]
    ├─ Deletar .github/instructions/local/<projeto>.instructions.md
    └─ Registrar em audit.log
[5] Relatório: artefatos removidos + próximos passos    ✓
```

## Validação de YAML (Obrigatória)

Após qualquer alteração em `projects.local.yaml`:

**Python (recomendado)**
```bash
python -c "import yaml; yaml.safe_load(open('.github/projects.local.yaml')); print('✅ Válido')" || echo "❌ Erro"
```

**yamllint**
```bash
yamllint .github/projects.local.yaml
```

Erros comuns:

| Erro | Causa | Solução |
|------|-------|---------|
| `mapping values are not allowed here` | Indentação errada | Revise indentação (2 espaços) |
| `could not find expected ':'` | Colon faltando | Verifique sintaxe |
| `unexpected indent` | Tabs/espaços misturados | Use sempre 2 espaços |

## Casos de Uso

| Situação | Ação |
|----------|------|
| Projeto descontinuado | `/del-project-context <nome>` |
| Reorganizar binding | `/del-project-context <antigo>` + `/add-project-context <novo>` |
| Cache corrompido | `/del-project-context` + `/add-project-context` (recupera) |
| Remover adapter customizado | `/del-project-context <nome>` |

## Recuperação

Se remover por engano:

```bash
# Recuperar via Git (só funciona se projects.local.yaml estiver sob controle de versão local
# customizado pelo dev — por padrão é gitignored, então a via normal de recuperação é recriar):
/add-project-context <caminho-absoluto-do-projeto>
```

## Fallbacks

| Cenário | Ação |
|---|---|
| Project não encontrado em projects.local.yaml | Abortar com mensagem clara |
| YAML inválido após remoção | Reverter com Git checkout (se local.yaml estiver versionado) ou recriar manualmente + report |
| Confirmação não fornecida | Aguardar entrada do user |

---

**Status**: Prompt v1.2 (Local Overlay Pattern — R-043)
**Integração**: Agent `project-context-builder`
**Dependência**: `yaml-governance` skill
**Referência**: `/add-project-context` (operação inversa)
**Audit**: Registrado em `.github/hooks/context-mode.json`

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/del-project-context` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/del-project-context`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch_execute(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch_execute`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch_execute, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).
7. **Emissão Obrigatória de Telemetria de Handoff (R-042 / handoff-governance § 2.4)**: a cada chamada real de `run_subagent`, emitir compulsoriamente um evento `telemetry_entry` (tag `[HANDOFF]`) via `ctx_index`, incluindo `session_id` (reaproveitado do `sessionStart` do hook `context-mode`) e `sequence_index` (ordenação determinística dentro da sessão).

</execution_protocol>
