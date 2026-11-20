---
name: health
description: >-
  Verifica saúde completa da infraestrutura de governança. Valida catalog.yaml,
  .index.json, binding context, agents acessíveis e sincronização entre arquivos.
  Vai além do /ctx-doctor (que cobre apenas Context Mode MCP).
agent: 'agent'
router_bypass: utility
model: "Gemini 4 Hydrogen"
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
├─ Skills sem entrada no índice    → <lista ou "nenhuma">
└─ Eval A/B Utilidade P5 (`python tests/evals/skill_ab_eval.py`) → ✅ PASS / ❌ FAIL (delta médio / redundâncias)
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
**Enumerar & Consolidar (`>= 2` alvos):** Liste todos os arquivos/comandos antes de agir (mesmo em prompts curtos). Para `>= 2` alvos, use `ctx_batch` ou script único em `ctx_execute` (`language: "javascript"` com `fs`/`path` nativos para I/O; proibido `python`/`python -c` para I/O por bloqueio AMSI/Defender e varreduras irrestritas). Em timeout (`ETIMEDOUT`/`taskkill`), máx. **1 retry** trocando de estratégia; no 2º, aborte e reporte via Compact Error Reporting (`R-020`).
**Orçamento de Turnos & Warm Start (R-060):** Teto de **5 tool turns** por ciclo (1: Batch Gather / Warm Start silencioso; 2: Execução em lote; 3: Validação). Ao atingir o Turno 4 sem conclusão, acione o Circuit Breaker, salve evidências no `ctx_index` e finalize ou use `ask_questions` (`R-027`: 1–4 perguntas, `header` ≤ 25 chars, `allowFreeformInput: true`, 2–4 opções reais, `description` com `[Consequência prática + Trade-off]` e 1ª opção `(Recomendado)`).
**Recibo Estruturado de Etapa (R-068):** Encerre entregas de pipeline com bloco YAML `receipt` + `step_delta` conforme `.github/skills/agent-contracts/references/receipt-step-delta-schema.yaml` (`mode: readonly_analysis` para Score 0; máx. 10 itens inline; excedente em `ctx_index` `wf:<trace>:delta:step-<n>`).
**Pós-Mutação & Conformidade de Plano (R-051 / R-064):** Execute mutações em lote atômico, rode `get_errors` agrupado uma única vez ao final e preencha `step_delta.plan_conformance` (`within_allowed_files`, `out_of_scope_files`) contra `allowed_files` do `plan_ref` ativo.

</execution_protocol>
