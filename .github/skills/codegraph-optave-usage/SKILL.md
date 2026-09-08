---
name: codegraph-optave-usage
description: >
  Uso da lib externa @optave/codegraph (CLI local, zero API keys) como motor único
  de construção e consulta de grafo de conhecimento de código — build, query,
  blast radius, ciclos, dead code e CI gate. Substitui scripts legados de build de grafo.
tier: 2
category: tooling
triggers:
  - "grafo de codigo"
  - "code knowledge graph"
  - "codegraph"
  - "blast radius"
  - "dependencia circular"
  - "impacto de mudanca"
  - "dead code"
  - "call graph"
source_docs:
  - "../../../CLAUDE.md"
  - "../../../.github/copilot-instructions.md"
---

# codegraph-optave-usage — Motor de grafo de conhecimento de código

Skill genérica para operar `@optave/codegraph` (repo `optave/ops-codegraph-tool`, Apache-2.0) como **motor único** de construção/consulta de grafo de código, via CLI local — sem LLM, sem API key, sem chamada de rede.

## 1) Objetivo

- Construir e manter um grafo de código local (`.codegraph/graph.db`, SQLite) para 34 linguagens.
- Responder perguntas de impacto, dependência, dead code, ciclo e complexidade sem depender de scripts legados ad-hoc.
- Servir de base para `check` em CI (exit code 0/1) e para agents/skills consumidores do grafo.

## 1.1) Governança de Acesso: Operador Exclusivo (@code-knowledge-graph — R-045 / RNF-004)

- **Operador único**: os comandos desta skill (`codegraph build`, `codegraph query`, `codegraph fn-impact`, etc.) são de competência e execução **EXCLUSIVAS** do agent `@code-knowledge-graph`.
- **Proibição universal**: NENHUM outro agent (specialists híbridos como `angular-engineer`, `spring-boot-engineer`, `spring-reactive-engineer`, analistas como `tech-solution-architect`, ou routers) está autorizado a executar o CLI `codegraph` diretamente via terminal (`run_in_terminal`) ou acessar `.codegraph/graph.db`.
- **Canal de consumo**: qualquer agent que necessite de mapeamento estrutural de dependências, arquitetura, chamadas ou blast radius DEVE invocar compulsoriamente `@code-knowledge-graph` via `run_subagent(agentName: 'code-knowledge-graph', ...)`.

## 2) Instalação e verificação

| Passo | Comando |
|---|---|
| Instalação global (CLI) | `npm install -g @optave/codegraph` |
| Instalação local (uso como lib embarcável) | `npm install @optave/codegraph` |
| Verificar instalação | `codegraph --version` |
| Selecionar engine do parser | `--engine native\|wasm\|auto` (fallback automático WASM se native indisponível) |

## 3) Fluxo básico

1. `codegraph build .` — build inicial (incremental por padrão), grava em `.codegraph/graph.db`.
2. `codegraph watch [dir]` — (opcional) atualização incremental contínua durante desenvolvimento.
3. Comandos de consulta (tabela §4) sobre o grafo já construído.
4. `codegraph check --staged` — gate de CI antes de merge.

Rebuild completo: apagar `.codegraph/` e repetir `build`. Uso normal é incremental (não precisa rebuild manual a cada mudança se `watch` estiver ativo).

## 4) Comandos CLI mais usados

| Comando | Uso |
|---|---|
| `codegraph build --engine wasm\|native\|auto` | Construir/reconstruir grafo |
| `codegraph map` | Visão geral de módulos |
| `codegraph stats` | Saúde do grafo |
| `codegraph query <name> -T` | Cadeia de chamadas (exclui testes por padrão) |
| `codegraph path <from> <to> -T` | Caminho mais curto entre dois símbolos |
| `codegraph deps <file>` | Dependências de um arquivo |
| `codegraph exports <file> -T` | Consumidores de um export |
| `codegraph fn-impact <name> -T` | Blast radius de uma função |
| `codegraph diff-impact --staged -T` | Impacto de mudanças staged (git diff) |
| `codegraph cycles` | Detecção de dependência circular |
| `codegraph dataflow <name> -T` | Fluxo de dados interprocedural |
| `codegraph cfg <name> -T --format mermaid\|dot` | Control flow graph |
| `codegraph ast [pattern] -k call\|new\|string\|regex\|throw\|await` | Consulta de nós AST |
| `codegraph complexity -T` | Métricas de complexidade |
| `codegraph roles --role dead -T` | Dead code (símbolos não referenciados/exportados) |
| `codegraph roles --dynamic` | Arestas de call dinâmico (eval, computed-key) |
| `codegraph communities` | Community detection (clustering) |
| `codegraph co-change` | Análise de co-mudança via histórico git |
| `codegraph audit <target> -T` | Relatório composto (explain + impact + health) |
| `codegraph triage -T` | Fila de prioridade |
| `codegraph check --staged` | **CI gate** (exit 0/1) — complexity, blast radius, cycles, boundary violations |
| `codegraph batch t1 t2 -T --json` | Query em lote |
| `codegraph search "<query>"` | Busca semântica/híbrida local |
| `codegraph branch-compare` | Diff estrutural entre 2 git refs (símbolos + impacto transitivo) |
| `codegraph plot` | **Visualização HTML interativa nativa** (ver §4.1) |
| `codegraph export -f dot\|mermaid\|json\|graphml\|graphson\|neo4j` | Exportar grafo para ferramenta externa |

Flags universais: `-T`/`--no-tests` (exclui `.test.`/`.spec.`/`__test__` na maioria dos comandos de query); `--limit`/`--offset` e `--ndjson` para paginação/streaming em resultados grandes.

**Architecture boundaries**: regras de dependência definíveis pelo usuário entre módulos + preset "onion architecture". Violações aparecem em `manifesto` e bloqueiam `codegraph check` (CI gate) — não é uma classificação de força de acoplamento, é enforcement binário de regra.

### 4.1) Visualização nativa (`codegraph plot`) — validado em execução real

`@optave/codegraph` **tem visualização gráfica interativa nativa** — motor interno é [`vis-network`](https://visjs.github.io/vis-network/) (Canvas + físicas), gerando um HTML standalone (sem servidor, sem CDN externo).

```
codegraph plot --cluster community --color-by role --size-by fan-in -o graph-view.html
```

| Opção | Valores | Efeito |
|---|---|---|
| `--functions` | flag | Grafo em nível de função (mais granular que arquivo) |
| `--cluster` | `none\|community\|directory` | Agrupamento visual (community = Leiden clustering) |
| `--color-by` | `kind\|role\|community\|complexity` | Cor por categoria |
| `--size-by` | `uniform\|fan-in\|fan-out\|complexity` | Tamanho do nó por métrica |
| `--overlay` | `complexity,risk` | Realce visual de hotspots |
| `--seed <strategy>` | `all\|top-fanin\|entry` | Estratégia de amostragem inicial (padrão: `top-fanin`) |
| `--seed-count <n>` | número | Quantos nós-semente iniciam a visualização (padrão: 30) |
| `--min-confidence <score>` | 0-1 | Filtra arestas de baixa confiança (padrão: 0.5) |

**Por que não satura o navegador em grafos grandes**: por padrão NÃO renderiza todos os nós — usa `--seed top-fanin --seed-count 30` e expande por clustering, mantendo a contagem de nós renderizados na faixa confortável do `vis-network` (< ~1.000 nós; acima disso a renderização degrada — validado com pesquisa de mercado 2026). Validado em execução real (174 arquivos, 4.794 símbolos totais no grafo): HTML gerado com **148 nós renderizados**, interativo, ~100 KB.

**Quando usar `export` em vez de `plot`**: se precisar de uma ferramenta externa mais robusta para grafos muito maiores (10k+ nós) — `codegraph export -f graphml` (Gephi), `-f neo4j` (Neo4j Bloom) ou `-f json` (Sigma.js/Cosmograph customizado). Para o uso comum deste agent, `codegraph plot` é suficiente e é a opção recomendada por padrão (zero setup, zero dependência externa).

## 5) Configurações Avançadas (`.codegraphrc.json`)

O arquivo `.codegraphrc.json` (ou `.codegraph/config.json`) na raiz do projeto permite personalizar o comportamento de parsing, regras e fronteiras arquiteturais:

### 5.0) Chaves de Filtro de Arquivos (`exclude`, `ignoreDirs`, `ignoreAdditionalDirs`, `extensions`)

| Chave | Tipo | Efeito |
|---|---|---|
| `exclude` | `string[]` (glob) | Padrões de arquivo/caminho excluídos do parsing (ex.: `**/*.spec.ts`, `dist/**`, `*.class`) |
| `ignoreDirs` | `string[]` | Substitui a lista padrão de diretórios ignorados pelo motor |
| `ignoreAdditionalDirs` | `string[]` | Diretórios adicionais ignorados **em complemento** à lista padrão (não substitui) |
| `extensions` | `string[]` | Restringe parsing às extensões informadas; se omitido, usa o conjunto padrão das 34 linguagens |

**Templates prontos por stack** (`docs/agent-context/templates/codegraph/`): `angular.codegraphrc.json` (Angular + Capacitor), `spring-boot.codegraphrc.json`, `spring-reactive.codegraphrc.json` (herda base Spring Boot + geradores openapi/reactor) e `ejb-legacy.codegraphrc.json`. Ver detalhes em [`docs/agent-context/codegraph-guia-uso.md`](../../../docs/agent-context/codegraph-guia-uso.md) §7.

### 5.1) Fronteiras Arquiteturais (`manifesto.boundaries`)
Define camadas e regras de dependência entre módulos:

```json
{
  "manifesto": {
    "boundaries": {
      "preset": "hexagonal",
      "modules": {
        "domain": "src/domain/**",
        "application": "src/application/**",
        "adapters": "src/adapters/**",
        "infrastructure": "src/infrastructure/**"
      },
      "rules": [
        { "from": "domain", "onlyTo": [] },
        { "from": "application", "notTo": ["infrastructure"] }
      ]
    }
  }
}
```
- **Presets**: `hexagonal`, `layered`, `clean`, `onion`.
- **Comandos**: `codegraph check --staged --boundaries` (valida violações no CI) e `codegraph communities --drift -T` (inspeciona desvio arquitetural).

### 5.2) Mapeamento de Monorepos & Módulos Cruzados (`aliases`)
Permite conectar módulos locais ou pacotes irmãos diretamente na árvore AST:

```json
{
  "aliases": {
    "@core/": "./src/app/core/",
    "@shared/": "./src/app/shared/",
    "@contracts/": "../shared-contracts/src/"
  }
}
```

### 5.3) Gerenciamento Multi-Repositório (`registry` e `mcp`)
Para projetos com múltiplos repositórios ou microserviços:
- `codegraph registry add <caminho>`: adiciona repositório ao catálogo central.
- `codegraph registry list`: lista repositórios registrados.
- `codegraph mcp --multi-repo`: expõe todos os repositórios registrados no servidor MCP.

## 6) Uso via CLI (preferencial) vs. MCP (least-tools)

- **Preferencial neste ecossistema**: CLI via `run_in_terminal` — mais controlável, auditável e alinhado a R-024 (Least-Tools).
- A lib expõe também um **MCP server com 34 tools**. Se for necessário habilitá-lo em algum ambiente, **nunca habilitar as 34 de uma vez**. Habilitar apenas o subconjunto mínimo equivalente a: `build`, `query`, `fn-impact`/`diff-impact`, `cycles`, `dataflow`/`cfg`, `check`.
- Agents/skills consumidores do grafo devem preferir sempre a via CLI, reservando MCP para cenários onde o orquestrador já exige esse protocolo.

## 7) Gaps conhecidos / Fora de escopo

⚠️ **Aviso explícito — decisão consciente de migração total (não híbrida).** `@optave/codegraph` **não cobre** os itens abaixo e não há plano de substituição por outro meio nesta migração:

| Gap | Detalhe |
|---|---|
| Mensageria RabbitMQ | Sem nós `queue` nem arestas producer/consumer |
| Cross-repo SOAP/JAX-WS | Sem suporte a `@WebService`/`targetNamespace` |
| Classificação de coupling própria | "Architecture boundaries" é enforcement de regra, **não** taxonomia tight/loose/eventual/circular |
| Risco por sensibilidade de dado | Sem classificação PII/financeiro |
| Resolução cross-repo REST | Sem correlação nativa Angular `apiUrl` ↔ Spring `@RequestMapping` |

> **Correção (2026-09-03)**: "Visualização HTML interativa" foi documentado incorretamente como gap em versão anterior desta skill. `@optave/codegraph` **tem** visualização nativa via `codegraph plot` (vis-network) — ver §4.1. Gap real remanescente aqui é apenas ausência de uma visualização em nível arquitetural tipo Cytoscape.js customizado (cores por `coupling`/realce de ciclo específicas do motor anterior) — não uma ausência total de visualização.

Qualquer agent/skill que consuma o grafo produzido por `@optave/codegraph` deve estar ciente destes gaps ao reportar cobertura de análise.

## 8) Checklist

- [ ] `codegraph --version` confirmado antes de qualquer build.
- [ ] Verificar existência de `.codegraphrc.json` no projeto; se ausente, provisionar o template compatível com a stack (`docs/agent-context/templates/codegraph/`) antes do build, para honrar `exclude`/`ignoreAdditionalDirs`/`boundaries`/`aliases`.
- [ ] `codegraph build .` executado (ou `watch` ativo) antes de qualquer query.
- [ ] `-T`/`--no-tests` aplicado em queries de impacto/blast radius, salvo necessidade explícita de incluir testes.
- [ ] CI usa `codegraph check --staged` como gate, não como sugestão.
- [ ] Se MCP for usado, subconjunto mínimo de tools habilitado (nunca as 34).
- [ ] Gaps da §7 mencionados ao consumidor final quando a análise tocar mensageria, SOAP, coupling ou risco de dado.

## 9) Referências

- Repositório oficial: `github.com/optave/ops-codegraph-tool`
- Pacote npm: `@optave/codegraph`
- Consumidor principal previsto: `.github/agents/code-knowledge-graph.agent.md` — motor oficial de grafo de conhecimento de código no repositório.

