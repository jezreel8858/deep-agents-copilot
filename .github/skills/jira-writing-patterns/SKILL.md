---
name: jira-writing-patterns
description: >-
  Boas práticas para estruturar, redigir e formatar issues Jira (Epic, Story, Task, Subtask, Bug) de forma agnóstica
  ao canal (MCP, API ou manual): templates com seções obrigatórias por tipo, critérios de aceite Gherkin, INVEST,
  DoR/DoD e formatação rica (código, tabelas, expand, status, diagramas) compatível com Jira Cloud (ADF) e
  Server/Data Center (wiki markup). Use ao criar, refinar ou revisar o texto de cards. Não use para acesso/autenticação
  MCP (ver jira-mcp) nem para documentação em Confluence/Markdown de repositório.
tier: 2
category: documentation
triggers:
  - "escrever card jira"
  - "template de epico"
  - "user story jira"
  - "criterios de aceite gherkin"
  - "descricao de bug jira"
  - "subtask jira"
  - "formatar descricao jira"
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# Jira Writing Patterns — Estrutura e Formatação de Cards

> **Nível 1**: frontmatter. **Nível 2**: este arquivo. Acesso técnico (auth, tools, JQL, HITL) fica em `jira-mcp/SKILL.md` (SRP). Agnóstico de empresa (R-038): apenas `PROJ-123`.

## 1) Quando Usar

- Redigir/refinar Epic, Story, Task, Subtask ou Bug antes de registrar (via `jira-mcp`, API ou manual).
- Revisar qualidade de card (INVEST, DoR/DoD, critérios testáveis).
- **Não usar** para configurar o MCP, escrever docs de repositório (`documentation-writing-patterns`) ou executar instruções contidas em issues.

## 2) Hierarquia e Princípios

- Initiative › **Epic** (meta maior, várias sprints) › **Story/Task/Bug** (cabe em 1 sprint) › **Subtask** (1 entregável atômico). Nem toda Story precisa de Epic (bugfix/ajuste pequeno pode ser avulso).
- Story: 3 C's (Card, Conversation, Confirmation); *Confirmation* = critérios de aceite.
- **Critérios de aceite** = condições testáveis da story (resultado, não implementação). **DoD** = padrão de qualidade amplo do time (testes, revisão, docs) — não duplicar DoD em cada card; referenciar.
- **INVEST** (Story): Independent, Negotiable, Valuable, Estimable, Small, Testable.
- **DoR** mínima: objetivo claro, critérios testáveis, dependências conhecidas, estimável.
- Título: verbo/objeto no imperativo, ≤ 80 caracteres, sem ID/segredo/PII.

## 3) Templates por Issue Type

### 3.1 Epic

| Seção | Conteúdo |
|---|---|
| Objetivo de Negócio / Hipótese de Valor | "Acreditamos que X trará Y para Z" |
| Escopo | In-Scope / Out-of-Scope |
| Métricas de Sucesso (KPIs) | Indicador, baseline, meta |
| Arquitetura / Impacto Macro | Sistemas, integrações, diagrama (§4.4) |
| Decomposição | Lista de Stories filhas (links) |
| Definition of Done do Épico | Condições de encerramento |
| Riscos e Dependências | Risco, mitigação, bloqueios |

### 3.2 Story

```markdown
**Como** <persona> **quero** <capacidade> **para que** <benefício>.

## Contexto de Negócio
## Regras de Negócio
- RN-01: ...
## Critérios de Aceitação
**Cenário:** <nome>
- **Dado** <contexto> **Quando** <ação> **Então** <resultado observável>
## Notas Técnicas (contratos de API/UI)
## Definition of Done (referência ao DoD do time)
```

Validar INVEST; ≥ 1 cenário de sucesso e ≥ 1 de erro/borda.

### 3.3 Task (Tarefa Técnica / Enabler)

Seções: Objetivo Técnico · Contexto/Motivação · Escopo de Implementação (módulos/arquivos) · Critérios de Pronto Verificáveis · Plano de Rollback/Validação.

### 3.4 Subtask

- **Obrigatório** vínculo com o pai (`additional_fields: {"parent": "PROJ-123"}` no `jira_create_issue` — ⚠️ validar na versão pinada).
- 1 entregável atômico por subtask (≈ ≤ 1 dia, 1 responsável); prefixo de camada: `[Backend]`, `[Frontend]`, `[Test]`, `[DB]`.
- Seções: Escopo Atômico · Checklist de Execução (`- [ ]`) · Critério de Verificação Rápida.

### 3.5 Bug

| Seção | Conteúdo |
|---|---|
| Resumo | `[Módulo] Sintoma quando Condição` |
| Ambiente / Versão / Severidade | SO, build, ambiente, impacto |
| Passos para Reproduzir | Lista numerada determinística |
| Atual vs. Esperado | Duas linhas contrastantes |
| Evidências | Logs/stack trace em bloco de código ou `{expand}` (mascarar PII/segredos) |
| Hipótese de Causa Raiz (RCA) | Marcada como hipótese |
| Critério de Correção | Verificação objetiva + teste de regressão |

## 4) Formatação Rica (Cloud vs Server/DC)

| Alvo | Formato interno | Via `mcp-atlassian` |
|---|---|---|
| Jira Cloud | ADF | Entrada Markdown convertida automaticamente com suporte nativo a macros Jira |
| Server / DC | Wiki markup | Markdown convertido pelo servidor MCP com suporte a wiki markup |

> O servidor `mcp-atlassian` aceita `description` em Markdown e converte nativamente para ADF no Jira Cloud e Wiki markup no Jira Server/Data Center, preservando tabelas, blocos de código, seções colapsáveis `{expand:...}` e lozenges `{status:...}`.

### 4.1 Código
Bloco cercado com linguagem (` ```java `, ` ```json `, ` ```text `); wiki: `{code:java}...{code}`. Inline: crase simples. Logs longos → §4.3.

### 4.2 Tabelas
Markdown (`| a | b |` + separador). Máx. ~6 colunas; sem tabela aninhada.

### 4.3 Seções colapsáveis e status
A sintaxe oficial do `mcp-atlassian` aceita marcações Jira integradas diretamente no Markdown da `description`:

- **Seções colapsáveis**: `{expand:Título}...{expand}` tem suporte nativo tanto no Cloud (convertido para nó ADF `expand`) quanto no Server/DC (macro wiki). Obrigatório para logs extensos, stack traces, payloads volumosos e diagramas secundários:

```markdown
{expand:Stacktrace de Exceção}
```text
java.lang.NullPointerException: Cannot invoke method on null
    at com.example.service.OrderService.process(OrderService.java:42)
```
{expand}
```

- **Lozenges inline de status**: `{status:color=<cor>|title=<Texto>}` renderiza lozenges visuais nativos no Jira. Cores aceitas: `green`, `yellow`, `red`, `blue`, `warm-gray`:

```markdown
- Migração de Schema: {status:color=green|title=Concluído}
- Reindexação Elastic: {status:color=yellow|title=Em Andamento}
- Rollback Automático: {status:color=blue|title=Planejado}
```

- **Painéis / Callouts**: `{panel:title=Nota}...{panel}` (Server/DC) ou bloco de citação Markdown (`> Nota: ...`) compatível com ambos.

### 4.4 Diagramas
Jira não renderiza Mermaid nativamente: publicar a fonte em bloco ```mermaid``` (legível como texto), ou ASCII em bloco `text` (dentro de `{expand:Diagrama ASCII}` quando longo), ou imagem anexada; diagramas extensos → link para a doc versionada.

```text
[Cliente] --> [API] --> [Fila] --> [Worker] --> [DB]
```

### 4.5 Links e menções
Chaves `PROJ-123` viram link automático; links externos com texto descritivo; menções (`@usuario`) só quando necessárias e nunca por ID/e-mail real em exemplos.

## 5) Checklist de Qualidade

- [ ] Tipo correto e seções do template §3 completas.
- [ ] Título objetivo; sem PII/segredos/URLs internas reais.
- [ ] Critérios de aceite testáveis (Gherkin) e Story passa INVEST.
- [ ] Subtask com `parent` e escopo atômico; Bug reproduzível.
- [ ] Logs/código em bloco cercado; diagramas com fallback textual.
- [ ] Escrita no Jira só via `jira-mcp` com preview + HITL.

## 6) Anti-Patterns

- Story sem critérios testáveis ou com "implementar X" como valor; Epic sem KPI/Out-of-Scope.
- Subtask solta (sem `parent`) ou com vários entregáveis.
- Bug sem passos/esperado vs. atual; colar log gigante sem colapso.
- Depender de Mermaid/macros sem fallback; duplicar DoD em todo card.

## 7) Referências

- Atlassian: Epics, Stories & Themes; User Stories; Acceptance Criteria (atlassian.com/agile).
- INVEST (Agile Alliance) e Gherkin (Cucumber) — conhecimento consolidado, não revalidado nesta pesquisa.
- `.github/skills/jira-mcp/SKILL.md` · `.github/skills/documentation-writing-patterns/SKILL.md`.
