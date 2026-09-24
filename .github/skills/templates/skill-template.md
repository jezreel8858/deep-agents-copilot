---
name: <nome-kebab-case>
description: >-
  Fornece diretrizes e padrões canônicos para <objetivo central em 3ª pessoa>. Use quando precisar de <cenário de uso com gatilho>. Não use para <cenário fora de escopo>.
tier: 2
category: process
triggers:
  - "<expressão gatilho 1 em PT-BR>"
  - "<expressão gatilho 2 em PT-BR>"
# SSOT e Progressive Disclosure (Anthropic Agent Skills Open Standard):
# Skills expõem metadados (Nível 1) no frontmatter para descoberta e o blueprint operacional (Nível 2) no corpo.
# É TERMINANTEMENTE PROIBIDO criar seções de herança, catálogo ou pré-carregamento no corpo markdown.
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# <Nome Humano da Skill>

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description`, `tier`, `category` e `triggers` para descoberta e roteamento rápido.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` contendo regras essenciais, processo canônico, exemplos contrastantes e checklist (~1.500 a 2.000 palavras).
> - **Nível 3 (Recursos Suplementares)**: Pastas opcionais `references/` (documentações extensas), `scripts/` (utilitários de automação) e `snippets/` (exemplos de código longos > 8 linhas, conforme R-026), carregadas sob demanda.

Esta skill formaliza as práticas recomendadas e diretrizes operacionais para `<resolver o problema X>`, evitando divergências de implementação, retrabalho e quebras de conformidade arquitetural no repositório.

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao projetar, implementar ou revisar rotinas relacionadas a `<domínio-alvo>`.
- Quando houver necessidade de padronização em `<processo/tecnologia>`.
- Como base de conhecimento para agentes operacionais ou deliberativos.

### ❌ Quando NÃO Usar
- Para tarefas que envolvam `<outro-domínio>` — delegar para `<skill-alternativa>`.
- Quando a demanda for puramente exploratória sem necessidade deste padrão.
- Em tarefas pontuais que já possuam automação determinística dedicada.

---

## 2) Diretrizes Operacionais e Processo Canônico

Siga o fluxo estruturado abaixo para aplicação das diretrizes:

### Etapa 1: Diagnóstico e Validação de Pré-requisitos
1. Inspecione o estado atual do componente ou fluxo a ser trabalhado.
2. Identifique se as precondições mínimas estão satisfeitas antes de iniciar intervenções.

### Etapa 2: Aplicação do Padrão Canônico
1. Aplique a estrutura padronizada conforme as convenções do projeto.
2. Mantenha blocos de código inline curtos (≤ 8 linhas, conforme R-026). Códigos mais extensos devem residir em `snippets/` ou `templates/`.

### Etapa 3: Verificação de Conformidade
1. Confronte a implementação contra o checklist da Seção 4.
2. Assegure que nenhum anti-padrão foi introduzido durante o processo.

---

## 3) Padrões Canônicos com Exemplos Contrastantes

### Padrão 1: <Nome do Padrão Principal>

#### ❌ Anti-padrão (Incorreto)
```typescript
// ❌ Código acoplado, sem validação ou violando convenções
function handleData(raw: any) {
  return raw.map((item: any) => item.value * 2);
}
```
*Problema*: Uso de `any`, ausência de tratamento defensivo e ausência de tipagem explícita.

#### ✅ Padrão Canônico (Correto)
```typescript
// ✅ Tipagem estrita, imutabilidade e validação de limites
interface DataItem { readonly value: number; }
function processItems(items: readonly DataItem[]): number[] {
  return items.map(item => item.value * 2);
}
```
*Benefício*: Segurança de tipos em tempo de compilação, legibilidade e conformidade com R-026.

---

## 4) Checklist de Auto-Verificação

Utilize este checklist para auditar artefatos produzidos com base nesta skill:

- [ ] Critério de conformidade 1 validado.
- [ ] Critério de conformidade 2 verificado com evidências.
- [ ] Nenhum bloco de código inline no artefato ultrapassa 8 linhas (R-026).
- [ ] Anti-padrões identificados foram mitigados.
- [ ] Documentação e referências cruzadas atualizadas.

---

## 5) Consumidores Mapeados e Integrações

| Consumidor | Papel na Relação | Momento de Uso |
|---|---|---|
| `@agent-router` | Descoberta e roteamento | Triagem inicial de solicitações compatíveis |
| `@<especialista-alvo>` | Executor / Implementador | Aplicação direta das regras operacionais |
| `governance-factory` | Auditoria e evolução | Validação estrutural e integridade do catálogo |

---

## 6) Referências e Documentação Conexa

- `CLAUDE.md` — Regras normativas do repositório.
- `.github/copilot-instructions.md` — Diretrizes de autonomia e contexto do workspace.
- Documentação externa oficial: <Link ou referência da tecnologia alvo>.

