---
name: health
description: >-
  Verifica saúde completa da infraestrutura de governança. Valida catalog.yaml,
  .index.json, binding context, agents acessíveis e sincronização entre arquivos.
  Vai além do /ctx-doctor (que cobre apenas Context Mode MCP).
agent: 'agent'
router_bypass: utility
model: "Gemini 3.8 Flash"
tools: ['read_file', 'list_dir', 'file_search', 'context-mode/ctx_execute', 'context-mode/ctx_batch', 'context-mode/ctx_search']
argument-hint: '[--quick | categoria]'
source_docs:
  - '.github/instructions/README.md'
  - '.github/projects.local.yaml.example'
  - '.github/skills/terminal-governance/SKILL.md'
  - 'CLAUDE.md'
  - '.github/copilot-instructions.md'
  - '.github/skills/context-mode/SKILL.md'
---

# `/health`

Diagnóstico completo da infraestrutura de governança.

> **Propósito**: Executar diagnóstico abrangente da governança: arquivos, catálogos, binding, sincronização e integridade estrutural.
> **Workspace**: `${workspaceFolder}`
>
> **DIFERENÇA vs `/ctx-doctor`**: `/ctx-doctor` verifica apenas o MCP Context Mode. `/health` verifica toda a estrutura de governança: arquivos, sincronização, YAML, binding.

---

## 🎯 Invocação e Variáveis Nativas

Invocação via comando slash `/health` (argumento: `[--quick | categoria]`), com suporte às variáveis nativas do VS Code Copilot:
- `${file}`: Arquivo ativo atualmente aberto e em foco no editor.
- `${selection}`: Trecho de código ou texto selecionado no editor no momento da chamada.
- `${workspaceFolder}`: Diretório raiz do workspace ativo na sessão.

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ❌ **NÃO** invocar `@agent-router` nem delegar via `run_subagent` — este prompt utilitário possui `router_bypass: utility` (exceção canônica a R-037/R-063) e DEVE ser executado diretamente pelo Orquestrador Raiz.
- ✅ O uso de `context-mode` (`ctx_batch`, `ctx_execute`, `ctx_search`) é **100% OBRIGATÓRIO** quando disponível; ferramentas nativas são **fallback exclusivo** de indisponibilidade (`R-056`).
- ✅ **APENAS** inspecionar e relatar o status de saúde da governança em 7 categorias.
- ✅ **SEMPRE** sinalizar divergências entre arquivos e catálogos estruturados.
- ❌ **NÃO** alterar arquivos ou configurações sem aprovação humana prévia.
- ❌ **NÃO** ignorar falhas de binding ou catálogos ausentes.

---

---

---

## 📋 Fluxo de Execução Passo a Passo

1. **Coleta de Contexto**: Avaliar os insumos fornecidos (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos do comando `/health`).
2. **Execução Governada**: Seguir rigorosamente as etapas operacionais detalhadas nas seções abaixo respeitando os limites de escopo e precedência do `context-mode` (`R-056`/`R-059`).
3. **Validação e Apresentação**: Verificar o checklist de conformidade antes de apresentar a saída consolidada.

---

## 🎯 Uso

```bash
/health   → diagnóstico completo
```

Se o usuário enviar flags (ex.: `--quick`), informe que o comando atual executa o diagnóstico completo.

---

## 📋 Verificações em 7 Categorias

### CAT-1: Binding Context

```
[Binding Context]
├─ .github/instructions/README.md     → ✅/❌ (existe + YAML válido?)
├─ .github/instructions/README.md       → ✅/❌ (existe?)
├─ .github/projects.local.yaml.example → ✅/❌ (template do overlay local existe?)
└─ Projetos registrados (fonte: projects.local.yaml, gitignored) → <N> projetos
```

**Se faltarem**: alertar + sugerir `binding-initializer`.

### CAT-2: Agents

```
[Agents]
├─ .github/agents/catalog.yaml     → ✅/❌ (YAML válido?)
├─ total_agents declarado          → <N> (coincide com arquivos .agent.md?)
├─ .agent.md files                 → <N> arquivos encontrados
└─ Desincronização                 → <lista de discrepâncias se houver>
```

### CAT-3: Skills

```
[Skills]
├─ .github/skills/.index.json      → ✅/❌ (JSON válido?)
├─ total_skills declarado          → <N> (coincide com pastas?)
├─ Pastas com SKILL.md             → <N> encontradas
└─ Skills sem entrada no índice    → <lista ou "nenhuma">
```

### CAT-4: Prompts

```
[Prompts]
├─ .github/prompts/README.md       → ✅/❌ (atualizado?)
├─ Prompts registrados no README   → <lista>
├─ Arquivos .prompt.md existentes  → <lista>
└─ Prompts órfãos (arquivo sem entrada no README) → <lista ou "nenhum">
```

### CAT-5: Conformidade R-038 (Genericidade)

```
[Genericidade R-038]
├─ QUICK-START.md sem nomes específicos → ✅/❌
├─ instructions/README.md sem lista de projetos específicos → ✅/❌
└─ copilot-instructions.md genérico → ✅/❌
```

### CAT-6: Conformidade ctx-first (Economia de Créditos)

```
[ctx-first]
├─ Prompts críticos usam ctx_search(sort:"timeline") → ✅/⚠️/❌
├─ Coleta principal via ctx_batch(commands, queries) → ✅/⚠️/❌
├─ Follow-up em queries em lote (evita chamadas unitárias) → ✅/⚠️/❌
├─ Uso de source quando múltiplas fontes são citadas → ✅/⚠️/❌
├─ Bloqueio de payload grande em ctx_index(content) → ✅/⚠️/❌
└─ Anti-dump (sem saída bruta extensa inline) → ✅/⚠️/❌
```

### CAT-7: Environment Fingerprint

> Complementa o PASSO 2 do `/init-context` (`.github/prompts/init-context.prompt.md`) — `/health` apenas
> **audita** se o fingerprint existe e está fresco; nunca redetecta nem escreve em `projects.local.yaml`
> (isso é responsabilidade exclusiva do `/init-context`).

```
[Environment Fingerprint]
├─ .github/projects.local.yaml existe? → ✅/❌
├─ Chave `environment:` presente e não-vazia?  → ✅/❌
├─ `environment.detected_at` presente?         → ✅/❌
├─ Idade de `detected_at` (agora - detected_at) → <N> dias
├─ Expirado? (idade > 7 dias, mesmo TTL do PASSO 2 do init-context) → ✅ fresco/⚠️ expirado
├─ `python.available` / `nodejs.available` / `java.available` → ✅/❌ cada
└─ Status → ✅/⚠️/❌
```

**Se `projects.local.yaml` não existir ou `environment:` estiver ausente/vazio:**
```
⚠️ Environment Fingerprint nunca foi coletado nesta máquina.
   → Execute /init-context (PASSO 2 detecta e registra automaticamente).
```

**Se `detected_at` existir mas estiver expirado (> 7 dias):**
```
⚠️ Environment Fingerprint expirado (última detecção: <N> dias atrás).
   → Execute /init-context para redetectar (PASSO 2 reexecuta automaticamente
     quando o cache expira — não requer nenhuma flag especial).
```

**Se fresco (≤ 7 dias) e completo:** apenas reportar ✅, sem ação sugerida.

---

## 📊 Saída Final

```
╔═══════════════════════════════════════════════════════════╗
║              🏥 GOVERNANCE HEALTH CHECK                   ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║ [CAT-1] Binding Context    → ✅/⚠️/❌                    ║
║ [CAT-2] Agents             → ✅/⚠️/❌  (<N> de <total>)  ║
║ [CAT-3] Skills             → ✅/⚠️/❌  (<N> de <total>)  ║
║ [CAT-4] Prompts            → ✅/⚠️/❌                    ║
║ [CAT-5] R-038 Conformidade → ✅/⚠️/❌                    ║
║ [CAT-6] ctx-first          → ✅/⚠️/❌                    ║
║ [CAT-7] Environment        → ✅/⚠️/❌  (fingerprint <N>d)║
║                                                           ║
║ Status Geral: ✅ SAUDÁVEL | ⚠️ AVISOS | ❌ AÇÃO NECESSÁRIA║
╚═══════════════════════════════════════════════════════════╝

⚠️ Itens que requerem atenção:
  - <lista de problemas detectados ou "Nenhum">

🎯 Próximo passo mínimo:
  - <ação sugerida se houver problema>
```

---

## 🔗 Comparativo: `/health` vs `/ctx-doctor`

| Aspecto | `/health` | `/ctx-doctor` |
|---------|-----------|---------------|
| Binding context | ✅ | ❌ |
| Agents sync | ✅ | ❌ |
| Skills sync | ✅ | ❌ |
| R-038 conformidade | ✅ | ❌ |
| Conformidade ctx-first | ✅ | ❌ |
| Environment fingerprint (idade/completude) | ✅ (auditoria, read-only) | ❌ |
| MCP conectividade | ❌ | ✅ |
| Context Mode stats | ❌ | ✅ |

**Uso recomendado**: `/health` no início do dia (governance check) + `/ctx-doctor` antes de tarefa crítica (MCP check).

---

*v1.0 — health prompt — 2026-06-12*

*v1.1 — 2026-09-01*
CAT-7 (Environment Fingerprint) adicionada: audita se `projects.local.yaml` possui a chave
`environment:` populada e se `detected_at` está dentro do TTL de 7 dias usado pelo PASSO 2 de
`/init-context`. Puramente read-only — nunca redetecta nem escreve no overlay local (isso é
escopo exclusivo do `/init-context`); apenas orienta a reexecutar `/init-context` quando ausente
ou expirado. `source_docs` ganhou `.github/projects.local.yaml.example` (schema de
referência do fingerprint).

---

## ✅ Checklist Antes de Apresentar

- [ ] Escopo e limites de Não-Escopo (`R-056` / `R-059` / `R-060`) integralmente respeitados.
- [ ] Entradas e contexto (`${file}`, `${selection}`, `${workspaceFolder}` ou argumentos) validados.
- [ ] Todas as etapas operacionais do fluxo concluídas sem desvios ou inferências não autorizadas.
- [ ] Saída formatada com evidências rastreáveis e pronta para revisão do usuário.

---

## 📊 Formato de Saída

Apresente o resultado consolidado da execução de `/health` conforme a estrutura operacional definida neste prompt:
- **Comando Executado**: `/health`
- **Escopo Processado**: `${file}` / `${workspaceFolder}`
- **Status e Evidências**: Resumo objetivo das verificações/ações realizadas e próximo passo recomendado.

## ⚙️ Protocolo de Execução Obrigatório

<execution_protocol>

**Protocolo Plan-Then-Batch (R-059):**
1. **ENUMERAR**: Antes de qualquer ação de modificação ou inspeção, liste internamente todos os arquivos e comandos necessários para a demanda completa (não apenas o próximo passo aparente).
2. **CONSOLIDAR (Limiar >= 2)**: Se a tarefa envolver 2 (dois) ou mais arquivos ou comandos, é TERMINANTEMENTE PROIBIDO disparar chamadas unitárias de `ctx_execute` por alvo no chat. Use compulsoriamente `ctx_batch(commands, queries)` OU script iterativo consolidado em `ctx_execute`. No `ctx_execute`, use obrigatoriamente `language: "javascript"` (`fs`/`path` nativos do Node.js) para I/O, inspeção e mutação de arquivos (proibido `language: "python"` ou `python -c` para I/O, evitando bloqueio do `python.exe` pelo Windows Defender/AMSI); em `ctx_batch`, use apenas comandos shell leves com escopo restrito (proibido `python -c` inline ou varreduras recursivas irrestritas). Em caso de timeout (`ETIMEDOUT`/`timed out`/`taskkill`), aplica-se **Circuit Breaker Fail-Fast**: tolerância zero para repetir a mesma chamada/runtime — máximo de **1 retry** exigindo troca obrigatória de estratégia (migrar para `language: "javascript"` puro com `fs` ou reduzir o lote); no 2º timeout, aborte novos spawns e reporte em formato Compact Error Reporting (R-020).
3. **Comandos curtos não suspendem a regra**: Prompts curtos ("prosseguir", "continue", "pode seguir") NÃO isentam o agente do limiar >= 2 nem do context-mode em lote — a regra vincula-se ao escopo da tarefa, nunca ao tamanho do prompt.
4. **Teto Rígido de Tool Turns (≤ 5) e Circuit Breaker (R-060)**: O agente opera sob orçamento estrito de no máximo 5 turnos de ferramentas por ciclo de execução. Turno 1: Batch Gather / Warm Start silencioso; Turno 2: Processamento aprofundado ou execução em lote consolidada; Turno 3: Validação consolidada / Quality Gate. Se atingir o 4º turno sem conclusão, aciona compulsoriamente o Circuit Breaker: consolida as evidências em ctx_index / memória de sessão e emite o parecer final conclusivo ou aciona clarificação via ask_questions (R-027: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais sem espantalhos, `description` obrigatório com `[Consequência prática + Trade-off/quando escolher]` e 1ª opção `(Recomendado)` para melhor prática técnica), vedando loops investigativos de dívida de tokens O(N²).
5. **Warm Start Compulsório & Batch Querying (R-060)**: Ferramentas locais que dependem de índices ou bases pré-computadas devem verificar e inicializar a base silenciosamente no primeiro comando (build-if-missing). É proibido disparar consultas granulares individuais para múltiplos nós — agrupe todas as pesquisas via chamadas em lote (batch_query, ctx_batch, script iterativo) com destilação semântica e truncamento na borda (Edge Truncation).
6. **Validação Agrupada com `get_errors` (R-051)**: Aplique todas as mutações em processo único no sandbox (all-or-nothing verificado) e execute `get_errors` agrupado uma única vez ao final com a lista completa de arquivos alterados (quando aplicável).

</execution_protocol>
