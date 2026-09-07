---
name: context-compact
description: >
  Boas práticas para compactar contexto pós-leitura em ambientes multi-projeto.
  Use quando o material bruto já foi lido e precisa virar um resumo executivo,
  enxuto e executável para outro agent.
tier: 2
category: process
triggers:
  - "compactar contexto"
  - "compactação de contexto"
  - "resumir contexto"
  - "limpar ruído"
  - "resumo executável"
  - "contexto enxuto"
  - "pós-leitura"
  - "sintetizar contexto"
tools: ["context-mode"]
source_docs:
  - "../../../CLAUDE.md"
  - "../../../docs/ai-context/catalog.yaml"
  - "../../../.github/copilot-instructions.md"
  - "../../../.github/agents/context-builder.agent.md"
  - "../../../.github/skills/context-builder/SKILL.md"
  - "../../../.github/skills/context-mode/SKILL.md"
---

# context-compact — Compactação de contexto pós-leitura

Esta skill transforma leituras extensas, diffs, logs e notas dispersas em um resumo de alta densidade para execução posterior.

## 1) Objetivo

- Reduzir ruído sem perder evidência.
- Converter material bruto em resumo executável.
- Preservar o vínculo entre projeto, arquivo, símbolo, decisão e risco.

## 2) Quando usar

- Após `read_file`, `grep_search`, `ctx_search`, `git diff` ou análise de logs.
- Quando a próxima etapa for implementação, revisão ou decisão.
- Quando houver excesso de texto, duplicação ou contexto paralelo.

## 3) O que preservar

| Elemento | Preservar | Como registrar |
|---|---|---|
| Escopo | projeto(s) e objetivo | citar `docs/ai-context/catalog.yaml` e os arquivos relevantes |
| Evidência | nomes de arquivos, símbolos, comandos, contratos | apontar a origem exata |
| Decisão | o que foi concluído e por quê | usar bullets curtos |
| Risco | impacto funcional, técnico ou operacional | classificar em Alto, Médio, Baixo |
| Próximo passo | ação mínima para avançar | uma ação por item |

## 4) Regras de compactação

- Remova ruído, repetição, logs e conversa paralela.
- Mantenha apenas o trecho mínimo necessário para a próxima execução.
- Se houver inferência, marque como hipótese e separe de fato confirmado.
- Não reescreva a história completa; entregue apenas o sinal alto.
- Se houver conflito entre fontes, preserve a divergência e cite ambas.
- Prefira tabelas e bullets a parágrafos longos.
- Nunca troque rastreabilidade por concisão.

## 5) Estrutura do resumo executável

1. Escopo e projetos-alvo.
2. Evidências confirmadas.
3. Impactos e riscos.
4. Pendências e bloqueios.
5. Próximo passo mínimo.

## 6) Template de resumo compacto

```markdown
## Escopo
- Projeto(s): [projeto-a], [projeto-b]
- Objetivo: [1 linha]

## Evidências confirmadas
- `path/arquivo.ext` — [achado]
- `path/arquivo.ext` — [achado]

## Impactos e riscos
- Impacto técnico: [descrição]
- Risco [Alto|Médio|Baixo]: [descrição]

## Pendências
- [ ] [pendência 1]
- [ ] [pendência 2]

## Próximo passo mínimo
- [ação objetiva + critério de conclusão]
```

## 7) Fluxo recomendado

1. Ler o material bruto.
2. Separar fatos, hipóteses e dúvidas.
3. Eliminar redundâncias e detalhes não acionáveis.
4. Agrupar por problema ou decisão.
5. Gerar um resumo curto, preciso e pronto para outro agent consumir.

## 8) Anti-padrões

- Copiar trechos inteiros sem necessidade.
- Misturar contexto bruto com saída final.
- Omitir projeto, arquivo ou comando de origem.
- Produzir narrativa longa sem ação futura.
- Apagar incertezas em vez de explicitá-las.
- Compactar demais a ponto de perder o caminho de auditoria.

## 9) Combina com

- `@context-builder` para transformar o resumo compacto em documento final persistido.
- `@context-mode` para recuperar e revisar material já indexado.
- `@tech-solution-architect` quando a compactação servir de base para análise técnica.
- `@deep-search` quando ainda houver ambiguidade de rota ou necessidade de pesquisa.

## 10) Referências

- Context Engineering (Sourcegraph, 2026): https://sourcegraph.com/blog/context-engineering
- Long-context strategies (2026): https://zylos.ai/research/2026-01-19-llm-context-management
