---
name: tavily
description: >
  Boas práticas de uso do Tavily MCP para pesquisa externa — documentação técnica,
  versões, changelogs, CVEs e padrões de mercado. Define hierarquia de decisão,
  estratégias de query e integração com context-mode.
tier: 2
category: research
triggers:
  - "pesquisar web"
  - "buscar documentação"
  - "tavily"
  - "pesquisa externa"
  - "verificar versão"
  - "changelog"
  - "cve vulnerabilidade"
  - "best practices externas"
  - "docs atualizadas"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools:
  - "tavily/tavily_search"
  - "tavily/tavily_extract"
  - "tavily/tavily_crawl"
  - "tavily/tavily_map"
  - "tavily/tavily_research"
  - "context-mode/ctx_search"
---

# Tavily — Pesquisa Externa

## 1) Hierarquia de Decisão — Quando Usar

```
Pergunta sobre o próprio codebase?
  └─→ ctx_search / grep_search / read_file  (NUNCA Tavily)

Conteúdo já indexado nesta sessão?
  └─→ ctx_search(source: "label")  (mais rápido, zero custo extra)

Informação potencialmente desatualizada no conhecimento do modelo?
  └─→ Tavily (documentação externa atualizada)

Incerteza técnica sobre: versão, API, vulnerabilidade, changelog?
  └─→ Tavily (R-019 — busca web proativa)
```

---

## 2) Casos de Uso Corretos

| Caso | Tool | Por quê |
|---|---|---|
| Verificar versão estável de dependência | `tavily_search` | Conhecimento do modelo pode estar desatualizado |
| Consultar changelog de framework | `tavily_search` | Releases recentes não estão no modelo |
| Verificar CVE de biblioteca | `tavily_search` | Segurança exige informação atual |
| Consultar docs de API (OpenAI, Jira) | `tavily_fetch_and_index` | Página oficial é fonte de verdade |
| Pesquisar best practices (2025+) | `tavily_search` | Padrões evoluem rapidamente |
| Comparar versões de frameworks | `tavily_search` | Matriz de compatibilidade muda |

---

## 3) Estratégias de Query

### Query eficaz

```
# Inclua: ano, versão específica, contexto técnico
✅ "Angular 21 Vitest official support 2025 ng test builder"
✅ "SonarQube 10 quality gate new code configuration 2025"
✅ "OWASP LLM Top 10 2025 prompt injection agentic applications"
✅ "deepeval 3.0 agent metrics tool correctness 2026"

# Evite: genérico demais (retorna resultados antigos/irrelevantes)
❌ "como testar angular"
❌ "sonarqube"
❌ "segurança de IA"
```

### Parâmetros por cenário

```python
# Pesquisa rápida (notícias, versão recente)
tavily_search(query="...", search_depth="fast", max_results=5)

# Pesquisa profunda (best practices, comparações, docs)
tavily_search(query="...", search_depth="advanced", max_results=8)

# Extração de página específica (docs oficiais, APIs)
tavily_extract(urls=["https://docs.exemplo.com/..."])
```

---

## 4) Integração com context-mode (fluxo obrigatório)

```
NUNCA fazer Tavily → responder diretamente (desperdiça tokens)

SEMPRE:
  1. ctx_search primeiro (cache de sessão)
  2. Se insuficiente → tavily_search
  3. Indexar resultado → ctx_fetch_and_index (TTL 24h)
  4. Responder via ctx_search (economiza tokens)
```

**Exemplo de fluxo correto:**

```python
# 1. Verificar cache primeiro
ctx_search(queries=["Angular Vitest official support 2025"])

# 2. Se vazio → buscar
tavily_search(query="Angular 20 21 official Vitest runner 2025 ng test builder")

# 3. Indexar para reutilização
ctx_fetch_and_index(url="https://timdeschryver.dev/blog/angular-testing-library-with-vitest",
                   source="angular-vitest-2025")

# 4. Consultar indexado
ctx_search(queries=["Angular Vitest configuration angular.json"], source="angular-vitest-2025")
```

---

## 5) Tavily Research (pesquisa aprofundada)

Para tarefas complexas com múltiplos subtópicos:

```python
# Use tavily_research quando:
# - Precisar de análise em profundidade de um tema
# - Múltiplos ângulos de um problema técnico
# - Curadoria de melhores práticas de mercado

tavily_research(
  input="Vitest Angular 20 21 best practices testing signals zoneless 2025 2026",
  model="pro"   # 'mini' para queries simples, 'pro' para broad research
)
```

---

## 6) Anti-padrões

- ❌ Usar Tavily para responder perguntas sobre o próprio codebase
- ❌ Não indexar resultado — próxima vez busca de novo (custo duplo)
- ❌ Query muito genérica → resultados irrelevantes ou antigos
- ❌ Chamar Tavily sem verificar ctx_search antes
- ❌ Usar `tavily_research` para Q&A simples (muito caro — use `tavily_search`)
- ❌ Passar resultado bruto de Tavily direto para o contexto sem sumarizar (usa tokens)
- ❌ Executar pesquisa multi-subtema sequencialmente em vez de decompor e paralelizar (ver § 7)
- ❌ Exceder o budget de 3 chamadas Tavily por pergunta/sub-query sem aplicar o checkpoint de autocrítica (ver § 9)
- ❌ Encadear rodadas de confirmação quando a evidência já coletada já responde com confiança média/alta

---

## 7) Decomposição e Paralelização (Orchestrator-Worker)

Para pesquisa **composta** (2+ subtemas, comparação, "melhores práticas de X e Y"), siga o padrão orchestrator-worker do Anthropic Multi-Agent Research System em vez de buscar tudo sequencialmente em uma única chamada:

```text
1. Decompor o tema em N sub-queries objetivas (1 subtema cada)
2. Delegar cada sub-query via run_subagent (deep-search) em paralelo
3. Coletar resultados brutos de cada subagent (título + URL + ano + snippet)
4. Sintetizar com checklist de citação (nenhuma fonte inventada)
```

**Quando NÃO paralelizar:** pergunta atômica (1 fato, 1 tema) — buscar direto com `tavily_search`, sem overhead de decomposição.

## 8) Checklist de Síntese e Citação

- [ ] Cada afirmação relevante cita fonte (título + URL + ano).
- [ ] Fontes contraditórias foram reconciliadas ou explicitamente apontadas.
- [ ] Nenhuma fonte foi inventada — lacuna declarada quando a busca não retornar dado.
- [ ] Veredito final explícito (não apenas lista de achados soltos).

---

## 9) Budget de Chamadas por Pesquisa (Anti-Overuse)

Problema observado: agents consumidores (ex.: `deep-search`) podem se aprofundar além do necessário, encadeando chamadas Tavily sucessivas "só para garantir" e consumindo cota de forma desproporcional ao ganho de confiança marginal.

**Regra de budget (aplicável a qualquer consumidor desta skill):**

```
Budget: no máximo 3 chamadas Tavily (tavily_search/tavily_extract/tavily_crawl/
        tavily_map/tavily_research, combinadas) por pergunta atômica ou por
        sub-query em pesquisa composta (workers paralelos NÃO somam budget entre si).

Checkpoint (após a 2ª chamada, antes da 3ª):
  "A evidência já coletada responde com confiança média/alta?"
    ├─ Sim -> parar, sintetizar, não fazer 3ª chamada.
    └─ Não -> 1 chamada final; encerrar independentemente do resultado e
              declarar lacuna explícita (nunca insistir além do budget).

Exceder o budget exige justificativa explícita no relatório final
(ex.: fontes conflitantes que exigem desempate) — nunca silenciosa.
```

Este checkpoint é uma aplicação restrita do padrão de autocrítica de 1 round descrito em `reflection-self-critique-patterns/SKILL.md` — usado aqui como **critério de parada** (stop-condition) antes de escalar para nova chamada externa, não como revisão de qualidade de um artefato gerado.

**Por que 3 e não um número maior:** pesquisa profunda (`tavily_research`, `search_depth="advanced"`) já retorna múltiplas fontes por chamada — 3 chamadas cobrem o padrão hierárquico (busca ampla → refinamento → extração/desempate) sem justificar rodadas adicionais de "confirmação".

---

## 10) Referências

- Tavily MCP Docs: https://docs.tavily.com/
- R-019 (Busca web proativa): `CLAUDE.md`
- Integração ctx: `.github/skills/context-mode/SKILL.md`
- Critério de parada (checkpoint de autocrítica): `.github/skills/reflection-self-critique-patterns/SKILL.md`
- Anthropic, "How we built our multi-agent research system" (2026) — https://www.anthropic.com/engineering/multi-agent-research-system — padrão orchestrator-worker (base da § 7).
- Encytics, "The Router-Planner Pattern" (2026) — https://www.encytics.ai/insights/blog/router-planner-pattern-multi-agent-architecture
- arXiv:2506.18096, "Deep Research Agents: A Systematic Examination" (2025) — retrieval planning dinâmico e síntese estruturada.