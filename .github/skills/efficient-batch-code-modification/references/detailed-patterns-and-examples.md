# Efficient Batch Code Modification — Exemplos Few-Shot e Tabelas

## 2.4) Exemplos Few-Shot: Anti-Padrão vs Padrão Correto de Batching

Toda inspeção, análise, validação ou modificação envolvendo múltiplos alvos (diffs, arquivos, status, branches) DEVE ser consolidada em **UMA ÚNICA chamada de ferramenta MCP**:

1. **Via A — Múltiplos comandos shell/leituras:** Usar compulsoriamente `ctx_batch` com comandos rotulados e queries unificadas em uma única rodada:
   ```javascript
   ctx_batch({
     commands: [
       { label: "git-diff", command: "git --no-pager diff --stat" },
       { label: "git-log", command: "git --no-pager log -n 3 --oneline" },
       { label: "status", command: "git status -s" }
     ],
     queries: ["arquivos modificados", "mensagens de commit recentes"],
     concurrency: 2
   })
   ```
2. **Via B — Múltiplos arquivos no filesystem:** Usar um único script síncrono em `ctx_execute` que itere por todos os alvos e emita um resumo consolidado:
   ```javascript
   ctx_execute({
     language: "javascript",
     code: `
       const fs = require('fs');
       const targets = ['src/a.ts', 'src/b.ts', 'src/c.ts'];
       const summary = targets.map(f => ({ file: f, lines: fs.readFileSync(f, 'utf8').split('\\n').length }));
       console.log(JSON.stringify(summary, null, 2));
     `
   })
   ```
3. **Proibição Absoluta**: É terminantemente proibido disparar turnos separados no chat chamando `ctx_execute` para cada arquivo/comando individualmente.

#### Regra do Limiar >= 2 (Anti Tool Chaining — Smell 2.26 / R-059)

> **Regra do Limiar >= 2 (inegociável):** SE o escopo da tarefa exigir inspecionar, ler, comparar, editar ou executar 2 (DOIS) OU MAIS arquivos/comandos/alvos, é TERMINANTEMENTE PROIBIDO disparar `ctx_execute` isolado por alvo em chamadas/turnos sucessivos. É OBRIGATÓRIO: (a) `ctx_batch(commands, queries)` com todos os alvos rotulados em uma única chamada, OU (b) um único script iterativo em `ctx_execute` que processe todos os alvos em loop interno e imprima o resumo consolidado de uma só vez. Antes de disparar a primeira chamada de ferramenta, o agente DEVE enumerar mentalmente TODOS os alvos necessários para completar a tarefa (Plan-Then-Batch, ver abaixo) — nunca descobrir o próximo alvo reativamente turno-a-turno.

#### Protocolo Plan-Then-Batch (Anti Miopia Reativa — Smell 2.13 / R-059)

> 1. **ENUMERAR**: antes de qualquer tool call, liste internamente todos os arquivos/comandos que compõem a tarefa completa (não apenas o próximo passo aparente).
> 2. **CONSOLIDAR**: se a lista tiver >= 2 itens, agrupe tudo em uma única payload (`commands[]` em `ctx_batch` ou loop único em `ctx_execute`).
> 3. **DESPACHAR**: dispare apenas 1 chamada de ferramenta de leitura/processamento por fase da tarefa — nunca N chamadas sequenciais para N alvos previsíveis.
> 4. **Comandos curtos não suspendem a regra**: prompts do usuário como "prosseguir", "continue", "pode seguir" NÃO isentam o agente da obrigatoriedade de context-mode nem do limiar >= 2 — a obrigação é da TAREFA em andamento, não do tamanho do prompt do turno atual.
>
> *(SSOT Normativa: `.github/copilot-instructions.md` § 2.1; alinhamento operacional em `.github/skills/context-mode/SKILL.md`)*.
>
> - Ver exemplo few-shot Anti-Padrão vs Padrão Correto de batching em `.github/skills/context-mode/SKILL.md § 4.3`.

---
