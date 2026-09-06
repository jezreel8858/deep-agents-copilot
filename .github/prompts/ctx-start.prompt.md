---
name: ctx-start
description: Inicializa e valida a sessão do Context Mode para garantir rastreabilidade e ingestão no dashboard.
model: "Gemini 3.8 Flash"
tools: ['context-mode/ctx_stats', 'context-mode/ctx_doctor', 'context-mode/ctx_execute']
---

# /ctx-start

Garante que o Context Mode está ativo e pronto para uso com baixo custo de contexto.

## Objetivo
Validar conectividade MCP, bootstrap mínimo da sessão e disponibilidade de métricas para execução `ctx-first`.

## Execução

### Passo 1 — Health Check de Conectividade
Execute `ctx_doctor()` e exiba o retorno completo.

### Passo 2 — Validação de Sessão Manual (Sync)
Execute um comando leve para registrar pelo menos uma chamada na sessão:
```javascript
ctx_execute({
  language: "shell",
  code: "echo 'context-mode: sync-validation'"
})
```

### Passo 3 — Verificação de Ingestão e Regras
Execute `ctx_stats()`. 
- **Se `Total calls > 0`**: Sucesso.
- **Se `Total calls = 0`**: rode `ctx_doctor` novamente e siga o comando de correção retornado (se houver). Persistindo zero, reportar falha compacta e aguardar ação do usuário.

## Resposta Esperada
```
✅ Sessão Context Mode Validada
├─ Conectividade: [OK] via ctx_doctor
├─ Ingestão: chamada detectada em ctx_stats
└─ Próximo: /pesquisar ou @agent-router
```

## Troubleshooting (Dashboard Vazio)
Se o dashboard continuar sem sessões:
1. Execute `/ctx-doctor` e aplique o comando sugerido no retorno.
2. Reexecute `/ctx-start` para validar se `ctx_stats` passa a registrar chamadas.

## Regras
- **R-022 (Auto-recuperação)**: Aplique se o Context Mode estiver desconectado.
- Não usar terminal para a verificação de stats; use `ctx_stats`.
- Priorize sempre ferramentas `ctx_*`; não usar fallback fora do fluxo sem aprovação do usuário.
- Em caso de falha persistente de ingestão (stats continuam em zero após trigger), reportar no formato compacto (Causa / Local / Ação).

## Combina Com
- `/ctx-status` → para ver o consumo detalhado após o início
- `/ctx-doctor` → diagnóstico profundo se o início falhar
- `/init-context` → executado após a governança global ser carregada
