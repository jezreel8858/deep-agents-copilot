---
name: task-decomposition-patterns
description: >
  Padrões consolidados de decomposição de tarefas complexas em subtasks —
  decomposição sequencial/hierárquica/paralela, granularidade ideal (2-3 níveis),
  rastreamento de dependências e validação antes de execução. Base para
  planejamento genérico de features (distinto de refactor-planner, que é
  específico para refatoração de código existente).
tier: 2
category: process
triggers:
  - "decompor tarefa"
  - "quebrar em subtarefas"
  - "task decomposition"
  - "planejar feature"
  - "planejamento de implementação"
  - "granularidade de tarefa"
  - "dependência entre tarefas"
  - "plano de execução"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
tools: []
---

# Task Decomposition Patterns

> Base de conhecimento para agents que decompõem requisitos/features complexas em subtasks executáveis — distinto de `refactor-planner` (específico para refatoração de código existente com foco em risco/rollback).

## Quando Usar

- Ao receber requisito de alto nível que precisa virar plano de execução.
- Ao decidir se uma feature deve ser dividida em múltiplas entregas paralelas ou sequenciais.
- Antes de delegar subtasks para agents especializados (coder, tester, docs writer).

## 1) Estratégias de Decomposição

| Estratégia | Quando Usar | Exemplo |
|---|---|---|
| **Sequencial** | Subtasks com dependência estrita (B precisa de A) | Migration → Service → Controller → Teste |
| **Hierárquica** | Tarefa complexa com múltiplos subníveis | Feature → Épico → Story → Task |
| **Paralela** | Subtasks genuinamente independentes | Frontend + Backend + Docs simultâneos |
| **Híbrida** | Combinação — grupos paralelos com barreira de sincronização | Implementação paralela → Convergência em Review |


> **Tracer Bullets (Vertical Slicing / Matt Pocock):**
> Em vez de decompor horizontalmente em camadas isoladas (construir todo o schema, depois toda a service, depois toda a controller, depois toda a UI — postergando a integração para o final), fatiar verticalmente de ponta a ponta. A primeira subtask implementa e testa um caminho feliz mínimo atravessando todas as camadas (UI → API → Banco) com um teste funcional executável. Valida contratos e arquitetura imediatamente, eliminando o risco de incompatibilidades tardias.

## 2) Granularidade Ideal

> Regra prática de mercado (2026): **2-3 níveis de decomposição** para a maioria das tarefas.

| Complexidade | Profundidade Recomendada |
|---|---|
| Tarefa simples | 1 nível (decomposição única) |
| Tarefa média | 2 níveis |
| Refactor complexo/feature grande | 3 níveis |

**Cuidado**: decomposição rasa demais deixa subtask complexa demais para um agent executar; decomposição profunda demais cria overhead de coordenação que supera o ganho.

## 3) Processo de Decomposição

```
1. Identificar objetivo de alto nível (o que o usuário quer)
2. Quebrar em subtasks atômicas (1 subtask = 1 responsabilidade clara)
3. Mapear dependências entre subtasks (o que bloqueia o quê)
4. Identificar subtasks paralelizáveis (sem dependência mútua)
5. Validar dependências antes de iniciar execução
6. Atribuir subtask a agent especializado por domínio
```

## 4) Validação de Dependências (Antes de Executar)

- [ ] Toda subtask tem entrada e saída claramente definidas.
- [ ] Dependências circulares foram descartadas (A depende de B que depende de A = erro de decomposição).
- [ ] Subtasks paralelas realmente não compartilham estado mutável.
- [ ] Critério de conclusão objetivo por subtask (não apenas "feito").

## 5) Template de Plano de Decomposição

```markdown
## Objetivo
<descrição do requisito de alto nível>

## Subtasks

### [P] Paralelo / [S] Sequencial — Subtask 1: <nome>
- Responsável: <agent/stack>
- Entrada: <o que precisa>
- Saída: <critério de conclusão>
- Depende de: <nenhuma | subtask X>

### [P] Paralelo / [S] Sequencial — Subtask 2: <nome>
- ...

## Convergência
- <ponto onde subtasks paralelas se juntam, se houver>

## Critério de Pronto (Definition of Done)
- <lista objetiva>
```

## 6) Anti-Padrões

- ❌ Decompor além de 3 níveis sem necessidade real (overhead de coordenação).
- ❌ Marcar subtasks como paralelas quando compartilham arquivo/estado mutável.
- ❌ Omitir critério de conclusão objetivo por subtask.
- ❌ Confundir decomposição de feature nova (este skill) com planejamento de refactor de código existente (`refactor-planner`, que tem foco em risco/rollback).
- ❌ Gerar plano sem validar dependências circulares.

## Checklist de Saída

- [ ] Objetivo de alto nível declarado.
- [ ] Subtasks atômicas com entrada/saída claras.
- [ ] Dependências mapeadas e validadas (sem circularidade).
- [ ] Marcação `[P]`/`[S]` por subtask (paralelo/sequencial, conforme R-018).
- [ ] Critério de pronto objetivo por subtask e para o todo.

## Referências

- Padrões Planner-Worker e decomposição hierárquica (AgentOrchestra, 2026).
- Cockburn — níveis "sea/sub-functional" de decomposição de user stories.
- Prática de mercado: granularidade 2-3 níveis como regra geral para custo-benefício de coordenação.

