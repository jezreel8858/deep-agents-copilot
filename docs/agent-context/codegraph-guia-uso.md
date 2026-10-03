# @optave/codegraph — Guia Básico de Uso

> Guia operacional para uso da biblioteca e CLI [`@optave/codegraph`](https://github.com/optave/ops-codegraph-tool).
> Motor de grafo de conhecimento de código-fonte determinístico (Tree-sitter/Rust nativo), 100% local e com zero chaves de API/LLM.

---

## 1) 🎯 Por que usamos

O `@optave/codegraph` substitui varreduras lentas e repetitivas de arquivos por um grafo persistente de dependências estruturais:

- **Parsing determinístico via AST**: cobre 34 linguagens de programação via Tree-sitter nativo (Rust/napi-rs com fallback WASM).
- **Zero chamadas de rede ou LLM**: todo o cálculo é local, sem envio de código para servidores externos.
- **Análise profunda**: rastreia chamadas (`calls`), imports, herança, fluxo de dados interprocedural (`dataflow`) e grafos de fluxo de controle (`cfg`).
- **Detecção de qualidade**: identifica dependências circulares (`cycles`), dead-code, hotspots de acoplamento e métricas de complexidade cognitiva/ciclomática.
- **Visualização web integrada**: gera visualizador HTML interativo standalone via `vis-network` (`codegraph plot`).

---

## 2) ⚙️ Instalação e Verificação

### Instalação Global (CLI)

```bash
npm install -g @optave/codegraph
```

### Verificação

```bash
codegraph --version
```

Deve retornar a versão instalada (ex.: `3.17.0` ou superior).

---

## 3) 🚀 Fluxo de Trabalho Básico

### Passo 1: Construir o grafo no projeto (Repositório Único)

Execute na raiz do projeto que deseja indexar:

```bash
codegraph build .
```

Ou aponte para um diretório específico:

```bash
codegraph build /caminho/do/projeto
```

O comando analisa o código e gera o banco SQLite local em `.codegraph/graph.db`. O build é incremental por padrão.

> 💡 **Dica de `.gitignore`**: adicione `.codegraph/` e `codegraph-view.html` ao `.gitignore` do projeto para não versionar o banco local.

### Passo 1.1: Construção e Gerenciamento Multi-Repositórios (Multi-Repo)

Se você trabalha com múltiplos repositórios ou microserviços e deseja que o grafo e o MCP reconheçam todos eles:

#### 1. Build individual de cada repositório

```bash
codegraph build /caminho/repo-frontend
codegraph build /caminho/repo-backend
```

#### 2. Registrar os projetos no Registry do Codegraph

O comando `registry` gerencia o catálogo central de projetos indexados:

```bash
# Adicionar repositórios ao registro
codegraph registry add /caminho/repo-frontend
codegraph registry add /caminho/repo-backend

# Listar todos os repositórios registrados
codegraph registry list

# Remover um repositório do registro (se necessário)
codegraph registry remove <nome-do-repo>

# Limpar entradas antigas ou diretórios inexistentes
codegraph registry prune
```

#### 3. Expor múltiplos repositórios no MCP Server

Para que o assistente de IA acesse todos os repositórios simultaneamente via MCP:

```bash
# Acesso a todos os repositórios registrados
codegraph mcp --multi-repo

# Ou restringir para um conjunto específico de repositórios
codegraph mcp --multi-repo --repos "repo-frontend,repo-backend"
```

### Passo 2: Acompanhar alterações em tempo real (Opcional)

Durante o desenvolvimento ativo:

```bash
codegraph watch .
```

Atualiza o grafo incrementalmente a cada arquivo salvo.

---

## 4) 🔍 Comandos Essenciais

### A) Análise de Impacto e Dependências

| Objetivo | Comando | Descrição |
|---|---|---|
| **Impacto de função** | `codegraph fn-impact <nomeFuncao> -T` | Mostra quais funções quebram se esta for alterada |
| **Impacto de arquivo** | `codegraph impact <caminhoArquivo> -T` | Rastreia dependentes transitivos do arquivo |
| **Impacto de git staged** | `codegraph diff-impact --staged -T` | Avalia o blast radius das mudanças staged antes do commit |
| **Cadeia de chamadas** | `codegraph query <nomeSimbolo> -T` | Mostra chamadores e chamados (callers/callees) |
| **Caminho mais curto** | `codegraph path <origem> <destino> -T` | Encontra a cadeia de invocação entre dois símbolos |
| **Consumidores de export** | `codegraph exports <caminhoArquivo> -T` | Mostra quem consome cada símbolo exportado |

> 📌 **Flag `-T` / `--no-tests`**: exclui arquivos de teste (`.spec.ts`, `.test.ts`, etc.) para evitar distorção nas métricas de blast radius de produção.

### B) Saúde e Qualidade do Código

| Objetivo | Comando | Descrição |
|---|---|---|
| **Resumo geral** | `codegraph stats` | Visão geral de nós, arestas, hotspots de acoplamento e qualidade |
| **Mapa de módulos** | `codegraph map` | Top módulos e arquivos mais conectados do sistema |
| **Dependência circular** | `codegraph cycles` | Detecta ciclos de dependência em nível de arquivo e função |
| **Código morto** | `codegraph roles --role dead -T` | Lista símbolos não referenciados e não exportados |
| **Complexidade** | `codegraph complexity -T` | Métricas cognitivas, ciclomáticas e índice de manutenibilidade (MI) |
| **Fila de auditoria** | `codegraph triage -T` | Fila priorizada por risco composto (conectividade + complexidade + churn) |

### C) Fluxo de Dados e Controle

| Objetivo | Comando | Descrição |
|---|---|---|
| **Dataflow** | `codegraph dataflow <nomeFuncao> -T` | Mapeia parâmetros, mutações e consumidores do retorno |
| **Control Flow Graph** | `codegraph cfg <nomeFuncao> -T --format mermaid` | Gera o diagrama de fluxo de controle em formato Mermaid |
| **Consulta AST** | `codegraph ast "<padrao>" -k call` | Busca nós AST por tipo (`call`, `new`, `throw`, `await`, `regex`) |

---

## 5) 🌐 Visualização Web do Grafo

O `@optave/codegraph` possui um gerador de visualização HTML standalone integrado via [`vis-network`](https://visjs.github.io/vis-network/):

### Gerar visualizador interativo

```bash
codegraph plot --output codegraph-view.html --cluster community --color-by role --size-by fan-in --no-open
```

### Opções de Customização do Plot

- `--cluster community`: agrupa nós por módulos/comunidades detectadas (Leiden clustering).
- `--color-by role`: colore nós pelo papel arquitetural (`entry`, `core`, `utility`, `dead`, `leaf`).
- `--size-by fan-in`: dimensiona nós proporcionalmente à quantidade de dependentes.
- `--functions`: gera visualização em nível de função em vez de nível de arquivo.
- `--seed top-fanin --seed-count 30`: estratégia de amostragem padrão que evita sobrecarregar o navegador com dezenas de milhares de nós simultâneos.

Abra o arquivo `codegraph-view.html` diretamente em qualquer navegador web para explorar, filtrar e buscar nós interativamente.

---

## 6) 🔌 Configuração do Servidor MCP nas IDEs (IntelliJ IDEA & VS Code)

O `@optave/codegraph` expõe um servidor **MCP (Model Context Protocol)** via `stdio` que permite que assistentes de IA (GitHub Copilot, Claude Code, Cursor, JetBrains AI Assistant) consultem o grafo diretamente como ferramentas estruturadas.

### A) VS Code & GitHub Copilot

No VS Code, configure o MCP no arquivo de configurações da extensão ou em `.vscode/mcp.json` (nível de workspace):

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph",
      "args": ["mcp"]
    }
  }
}
```

> 💡 **No Windows com `npx` (alternativa sem PATH global):**
> ```json
> {
>   "mcpServers": {
>     "codegraph": {
>       "command": "cmd.exe",
>       "args": ["/c", "npx -y @optave/codegraph mcp"]
>     }
>   }
> }
> ```

---

### B) IntelliJ IDEA (JetBrains)

No IntelliJ IDEA / JetBrains Copilot, a configuração do MCP é feita via arquivo de configuração do GitHub Copilot ou nas preferências da IDE:

#### 1. Localização do arquivo de configuração

- **Windows**: `%LOCALAPPDATA%\github-copilot\intellij\mcp.json`  
  *(Exemplo: `C:\Users\{username}\AppData\Local\github-copilot\intellij\mcp.json`)*
- **Linux / macOS**: `~/.config/github-copilot/intellij/mcp.json`

#### 2. Configuração no `mcp.json` (IntelliJ IDEA)

```json
{
  "servers": {
    "codegraph": {
      "type": "stdio",
      "command": "cmd.exe",
      "args": [
        "/c",
        "codegraph mcp"
      ],
      "env": {}
    }
  }
}
```

> 📌 **Dica para multi-projeto no IntelliJ / VS Code**: se você registrou múltiplos repositórios via `codegraph registry add`, habilite o acesso global no `args`:
```json
{
  "args": [
    "/c",
    "codegraph mcp --multi-repo"
  ]
}
```
> Ou para apontar para um banco explícito:
```json
{
  "args": [
    "/c",
    "codegraph mcp -d /caminho/do/projeto/.codegraph/graph.db"
  ]
}
```

---

### C) As 34 Ferramentas Expostas pelo MCP

Quando o servidor é iniciado, ele disponibiliza as seguintes ferramentas para o modelo de IA:

| Grupo | Ferramentas MCP |
|---|---|
| **Chamadas & Contexto** | `query`, `path`, `fn_impact`, `context`, `symbol_children`, `where`, `execution_flow`, `sequence` |
| **Dependências & Arquivos** | `file_deps`, `file_exports`, `impact_analysis`, `brief`, `structure`, `module_map` |
| **Qualidade & Métricas** | `find_cycles`, `complexity`, `communities`, `node_roles`, `triage`, `audit` |
| **Fluxo de Dados & AST** | `dataflow`, `cfg`, `ast_query`, `implementations`, `interfaces` |
| **Git & Diff** | `diff_impact`, `branch_compare`, `co_changes`, `check` |
| **Busca & Exportação** | `semantic_search`, `list_functions`, `export_graph`, `batch_query`, `code_owners` |

---

## 7) 🛠️ Configurações Avançadas (`.codegraphrc.json`)

Você pode criar um arquivo `.codegraphrc.json` (ou `.codegraph/config.json`) na raiz do projeto para definir regras arquiteturais, aliases de resolução, filtros de arquivos e limites de qualidade personalizados.

### A0) Chaves de Filtro de Arquivos Suportadas

| Chave | Tipo | Efeito |
|---|---|---|
| `exclude` | `string[]` (glob) | Padrões de arquivo/caminho a excluir do parsing (ex.: `**/*.spec.ts`, `dist/**`) |
| `ignoreDirs` | `string[]` | Diretórios ignorados integralmente na varredura (substitui a lista padrão do motor quando definida) |
| `ignoreAdditionalDirs` | `string[]` | Diretórios adicionais ignorados **em complemento** à lista padrão do motor (não substitui, apenas soma) |
| `extensions` | `string[]` | Restringe o parsing às extensões informadas (ex.: `[".ts", ".java"]`); se omitido, o motor usa o conjunto padrão das 34 linguagens suportadas |

> 💡 Use `exclude` para padrões glob pontuais (arquivos gerados, specs, stubs) e `ignoreAdditionalDirs` para diretórios inteiros que não fazem parte da lista padrão do motor (ex.: `android/`, `ios/`, `target/`, `ear/`) — evita reescrever toda a lista padrão via `ignoreDirs`.

### A1) Templates Prontos por Stack

Templates de `.codegraphrc.json` prontos para uso ficam em [`docs/agent-context/templates/codegraph/`](templates/codegraph/):

| Stack | Template | Cobre |
|---|---|---|
| Angular (+ Capacitor) | [`angular.codegraphrc.json`](templates/codegraph/angular.codegraphrc.json) | `dist`, `.angular`, `coverage`, `android`, `ios`, specs/stories, `.d.ts`, `polyfills.ts`, templates/estilos, `codegraph-view.html`, `*.iml` |
| Spring Boot | [`spring-boot.codegraphrc.json`](templates/codegraph/spring-boot.codegraphrc.json) | `target`/`build`, `.gradle`/`.mvn`, wrappers (`mvnw`/`gradlew`), fontes geradas, artefatos compilados (`*.jar`/`*.war`/`*.class`), `*.iml`, `.factorypath` |
| Spring Reactive | [`spring-reactive.codegraphrc.json`](templates/codegraph/spring-reactive.codegraphrc.json) | Herda base do Spring Boot + `**/generated/openapi/**`, `**/generated/reactor-*` |
| EJB Legado | [`ejb-legacy.codegraphrc.json`](templates/codegraph/ejb-legacy.codegraphrc.json) | Stubs/Ties/Skels gerados (`_Stub`/`_Tie`/`_Skel`), `ear`/`exploded`, libs `WEB-INF`/`META-INF`, artefatos `*.ear`/`*.war`/`*.class`/`*.jar`, `*.iml` |

Para aplicar: copie o template correspondente para a raiz do projeto-alvo como `.codegraphrc.json`, ajustando `exclude`/`ignoreAdditionalDirs` conforme peculiaridades locais antes do `codegraph build`.

### B) Regras de Fronteiras Arquiteturais (`boundaries`)

O motor de manifesto permite definir camadas e regras estritas de comunicação entre módulos, identificando desvios arquiteturais automaticamente:

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
        {
          "from": "domain",
          "onlyTo": []
        },
        {
          "from": "application",
          "notTo": ["infrastructure"]
        }
      ]
    }
  }
}
```

- **Presets disponíveis**: `hexagonal`, `layered`, `clean`, `onion`.
- **Validação**: `codegraph check --staged --boundaries` (bloqueia o commit em caso de import proibido).
- **Inspeção de Drift**: `codegraph communities --drift -T` (destaca visualmente onde a arquitetura real desviou das fronteiras configuradas).

---

### C) Mapeamento de Módulos e Monorepos (`aliases`)

Para monorepos ou projetos que utilizam caminhos customizados de import (TypeScript `paths` ou pacotes locais), configure aliases para que a AST resolva as referências cruzadas:

```json
{
  "aliases": {
    "@core/": "./src/app/core/",
    "@shared/": "./src/app/shared/",
    "@contracts/": "../shared-contracts/src/"
  }
}
```

O `codegraph` conecta os nós dessas pastas automaticamente no grafo único.

---

### D) Integração e Exportação Cross-Sistema (Neo4j & GraphML)

Para visualizar integrações entre múltiplos sistemas em um banco de grafos unificado (Enterprise Graph):

1. **Exportar os repositórios em formato compatível**:
   ```bash
   codegraph export -f neo4j -o ./export-frontend
   codegraph export -f neo4j -o ./export-backend
   ```
   *(Formatos suportados: `neo4j`, `graphml`, `dot`, `mermaid`, `json`, `graphson`)*

2. **Visualizar em ferramentas corporativas**:
   - **Neo4j Bloom / Neo4j Browser**: carregue os CSVs e crie relações de rede entre nós do frontend e controllers do backend (`(Client)-[:HTTP_CALL]->(Endpoint)`).
   - **Gephi**: para análise visual de densidade de grafos gigantes (100k+ nós).

---

## 8) 🛡️ Gate de CI / Automação

Para validar a integridade estrutural em pipelines de CI antes do merge:

```bash
codegraph check --staged --rules
```

Opções de validação no CI:
- `--cycles`: falha se houver ciclos de dependência.
- `--blast-radius <n>`: falha se o blast radius exceder o limite numérico permitido.
- `--boundaries`: falha se houver violação de fronteiras configuradas.
- `--signatures`: falha se houver alteração de assinatura em declarações públicas exportadas.

---

## 9) ⚠️ Gaps Conhecidos

Como decisão consciente de uso de ferramenta focada em AST estático:

1. **Mensageria assíncrona**: não modela tópicos de filas como RabbitMQ/Kafka producer/consumer.
2. **Contratos cross-repo SOAP/JAX-WS**: não correlaciona stubs SOAP distribuídos entre múltiplos repositórios.
3. **Rastreamento de dados sensíveis**: não classifica nativamente campos PII ou financeiros.

---

## 10) 🔗 Referências

- **Repositório oficial**: [`github.com/optave/ops-codegraph-tool`](https://github.com/optave/ops-codegraph-tool)
- **Pacote npm**: [`@optave/codegraph`](https://www.npmjs.com/package/@optave/codegraph)
- **Skill de governança**: [`.github/skills/codegraph-optave-usage/SKILL.md`](../../.github/skills/codegraph-optave-usage/SKILL.md)
- **Agent integrador**: [`.github/agents/codegraph-engine.agent.md`](../../.github/agents/codegraph-engine.agent.md)

