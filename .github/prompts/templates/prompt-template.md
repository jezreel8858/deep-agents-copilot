---
name: '<nome-kebab-case>'
description: '<Ação imperativa em 1 linha — ex.: Gera X a partir de Y>'
model: "Gemini 3.8 Flash"
tools: ['read_file']
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# `/<nome-kebab-case>`

> **Propósito**: descreva o que este prompt faz em 1-2 frases diretas.
> **NÃO faz**: liste o que está fora do escopo (opcional, incluir se relevante).

---

## 🎯 Uso

```bash
/<nome>                   → comportamento padrão
/<nome> <argumento>       → comportamento com argumento
```

---

## CRÍTICO (remover esta seção se o prompt não tiver escopo delimitado)

- ❌ NÃO executar ação X sem aprovação explícita
- ❌ NÃO alterar arquivos fora do escopo definido
- ✅ APENAS realizar Y
- ✅ SEMPRE confirmar antes de operações destrutivas

---

## 📋 Fluxo

### Passo 1 — Coletar contexto

Execute para entender o estado atual:

```bash
# Listar o necessário (sem paginação)
git --no-pager status --short
```

### Passo 2 — Processar

Descreva a lógica de processamento em linguagem imperativa, clara e passo a passo.

### Passo 3 — Gerar saída

Descreva o formato de saída esperado.

```
Formato de saída:
<campo>: <valor>
<campo>: <valor>
```

---

## ✅ Checklist Antes de Apresentar

- [ ] Critério verificável 1
- [ ] Critério verificável 2
- [ ] **Confirmado: nenhuma operação destrutiva executada sem confirmação.**

---

## 🚨 Regras de Autonomia

- ❌ **NUNCA** executar operações irreversíveis sem `ask_questions`
- ✅ **APENAS** gerar e exibir resultado para o dev revisar

---

## 🔄 Combina Com

```
/<prompt-anterior> → /<este-prompt> → /<prompt-seguinte>
```

- `/<prompt-anterior>` → descreva a dependência
- `/<prompt-seguinte>` → descreva como este prompt alimenta o próximo

---

> **Notas de manutenção**: descreva limitações conhecidas, edge cases ou dependências
> de ambiente que o usuário deve saber.

*v1.0 — <nome-kebab-case> prompt — YYYY-MM-DD*

