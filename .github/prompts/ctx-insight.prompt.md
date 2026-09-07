---
name: ctx-insight
description: Abre o dashboard de analytics do Context Mode com `ctx_insight` para observar uso de ferramentas e sessões.
agent: 'agent'
model: "Gemini 3.8 Flash"
tools:
  - context-mode/ctx_insight
argument-hint: '[port]'
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/context-mode/SKILL.md
---

# `/ctx-insight`

Atalho para abrir o painel Insight e revisar métricas da sua rotina no Context Mode.

> **Propósito**: Inicializar o painel analítico local com métricas de consumo de ferramentas e sessões.
> **Workspace**: `${workspaceFolder}`

---

## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO

- ✅ **APENAS** inicializar e disponibilizar a URL do painel analítico de sessões do Context Mode.
- ✅ **SEMPRE** informar a porta e a URL de acesso local.
- ❌ **NÃO** alterar configurações ou manipular dados da aplicação.
- ❌ **NÃO** iniciar múltiplos servidores em concorrência na mesma porta.

---

## Sintaxe

```
/ctx-insight
```

## Execução obrigatória

### Passo 0 — Diagnóstico rápido antes de abrir (opcional)
Se houver suspeita de problema de conexão, rode `/ctx-doctor` antes de abrir o dashboard.

### Passo 1 — Abrir Dashboard
Execute `ctx_insight` com parâmetros padrão.
2. Informe a URL/porta retornada e se o servidor iniciou corretamente.
3. Se necessário, ofereça nova execução com porta customizada.

## Exemplo de execução

```javascript
ctx_insight({ "port": 4747 })
```

## Resposta esperada

- Porta e URL do dashboard.
- Observação curta de primeiro uso (instalação inicial pode levar ~30s).
- Ação sugerida quando a porta estiver ocupada.

## Regras

- Não usar terminal para abrir o dashboard; use apenas `ctx_insight`.
- Não executar testes/build junto com `/ctx-insight`.
- Em erro, reportar no formato compacto (Causa / Local / Ação).

## Combina Com

- `/ctx-doctor` → diagnostique conectividade antes de abrir o dashboard
- `/ctx-status` → use para revisão rápida sem interface gráfica

