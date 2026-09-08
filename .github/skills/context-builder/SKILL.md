---
name: context-builder
description: >
  Orienta a preparação de contexto técnico multi-projeto em `docs/context/`, usando
  `docs/ai-context/catalog.yaml` como referência de escopo. Use quando a tarefa for
  condensar evidências dispersas em um prompt enxuto, rastreável e pronto para outro
  agent executar.
tier: 2
category: process
triggers:
  - "preparar contexto"
  - "consolidar contexto"
  - "montar contexto"
  - "recorte de código"
  - "docs/context"
  - "nomecurto timestamp"
  - "catalog"
  - "prompt de entrada"
source_docs:
  - "CLAUDE.md"
  - "docs/ai-context/catalog.yaml"
  - ".github/copilot-instructions.md"
  - ".github/agents/context-builder.agent.md"
  - ".github/skills/context-mode/SKILL.md"
tools:
  - "context-mode"
---

# context-builder — Boas práticas para preparação de contexto

Esta skill orienta a preparação de contexto técnico de alta densidade para outro agent executar com o mínimo de ruído e o máximo de rastreabilidade.

## 1. Objetivo

Transformar material bruto em um documento único, enxuto e útil para execução posterior, preservando o vínculo entre projeto, evidência e decisão.

## 2. Escopo multi-projeto

- Use `docs/ai-context/catalog.yaml` para identificar um ou mais projetos-alvo antes de consolidar o contexto.
- Quando houver vários projetos, explicite o papel de cada um no documento final.
- Preserve a relação entre projeto, arquivo, símbolo, contrato e decisão.

## 3. Recorte e limpeza

| Regra | Orientação |
|---|---|
| Densidade | Remova ruído, duplicação, logs e conversa paralela. |
| Recorte mínimo | Mantenha apenas assinaturas, contratos e trechos isolados realmente necessários. |
| Rastreabilidade | Cada evidência deve apontar para arquivo, símbolo ou projeto. |
| Consolidação | Agrupe por problema/decisão, não por origem da informação. |

## 4. Referenciação inteligente

- Referencie arquivos com `@file` ou `#file` quando o modelo de destino suportar.
- Nomeie os projetos com a mesma convenção usada em `docs/ai-context/catalog.yaml`.
- Destaque dependências cross-projeto sempre que influenciem a próxima execução.

## 5. Saída final

- Diretório obrigatório: `docs/context/`
- Nome obrigatório: `nomecurto-timestamp.md`
- Nome curto, sem acentos, sem espaços e com hífen
- Documento final em Markdown, com alta densidade e baixa redundância
- Instrução principal por último, no bloco final do contexto

## 6. Template de saída executável

```markdown
# [titulo-curto]

## Escopo
- Projetos-alvo: [projeto-a], [projeto-b]
- Objetivo: [1 linha]

## Evidências confirmadas
- `caminho/arquivo.ext`: [símbolo] → [achado]
- `caminho/arquivo.ext`: [símbolo] → [achado]

## Decisões e riscos
- Decisão: [o que foi decidido]
- Risco [Alto|Médio|Baixo]: [descrição]

## Pendências
- [ ] [ação pendente 1]
- [ ] [ação pendente 2]

## Próximo passo mínimo
- Executar [agent/comando] para [resultado esperado]
```

## 7. Checklist antes de consolidar

- [ ] Objetivo explícito.
- [ ] Projetos-alvo mapeados.
- [ ] Evidências selecionadas.
- [ ] Ruído removido.
- [ ] Recorte mínimo aplicado.
- [ ] Nome final definido.
- [ ] Saída pronta para `docs/context/`.

## 8. Anti-padrões

- Criar contexto sem citar projeto(s) do ecossistema.
- Inserir trechos grandes sem necessidade.
- Omitir a relação entre projeto, arquivo e decisão.
- Usar nomes longos, genéricos ou com acentuação.
- Salvar a saída final fora de `docs/context/`.
- Entregar texto prolixo, repetitivo ou sem rastreabilidade.

## 9. Combina com

- `@context-builder` para preparar o contexto final.
- `@deep-search` quando a solicitação ainda estiver ambígua ou precisar de pesquisa técnica interna/externa.
- `@tech-solution-architect` quando houver necessidade de análise técnica, impacto ou dependências.
- `@governance-factory` quando a tarefa envolver criação ou revisão de agents.

## 10. Referências

- Context Engineering (Sourcegraph, 2026): https://sourcegraph.com/blog/context-engineering
- Context management patterns (2026): https://zylos.ai/research/2026-01-19-llm-context-management
