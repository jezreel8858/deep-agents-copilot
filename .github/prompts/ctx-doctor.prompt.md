---
name: ctx-doctor
description: Diagnostica o Context Mode usando `ctx_doctor` para validar instalação, hooks e conectividade.
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_doctor
---

# /ctx-doctor

Atalho para executar diagnóstico rápido do Context Mode antes de troubleshooting mais profundo.

## Sintaxe

```
/ctx-doctor
```

## Execução obrigatória

### Passo 0 — Rodar diagnóstico diretamente
`/ctx-doctor` é o ponto de entrada de diagnóstico. Execute mesmo sem pré-checagem.
Se retornar `Not connected`, aplique R-022 (1 auto-recuperação) e tente novamente uma única vez.

### Passo 1 — Diagnóstico de Conectividade
1. Execute `ctx_doctor` sem argumentos.
2. Exiba o relatório completo exatamente como retornado (`[OK]`, `[WARN]`, `[FAIL]`).
3. Se o retorno incluir comando de correção/repair, execute esse comando e reporte em checklist curto.
4. Se houver falha após correção, recomende próximo passo objetivo e aguarde aprovação.

## Exemplo de execução

```javascript
ctx_doctor()
```

## Resposta esperada

- Saída completa do `ctx_doctor` (sem truncar).
- Checklist do comando executado (quando houver repair).
- Próximo passo mínimo (apenas se ainda houver `WARN`/`FAIL`).

## Regras

- Não usar terminal para diagnóstico; use apenas `ctx_doctor`.
- Não executar testes/build junto com `/ctx-doctor`.
- Em erro, reportar no formato compacto (Causa / Local / Ação).
- Se `ctx_doctor` retornar `Not connected`, disparar auto-recuperação conforme R-022.
- Não ocultar linhas do relatório original sem pedido explícito do usuário.

## Combina Com

- `/ctx-status` → verifica consumo após confirmar que o Context Mode está saudável
- `/ctx-resume` → retoma contexto após confirmar conectividade

