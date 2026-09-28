---
id: ADR-0011
title: "MCP Server Java framework-agnóstico com MCP Java SDK + LangChain4j Agentic"
status: Aceito
date: 2026-09-28
decision-makers:
  - tech-solution-architect
  - docs-engineer
consulted:
  - code-knowledge-graph
  - deep-search
informed:
  - adr-sentinel
  - pr-gatekeeper
type: explanation
diataxis: explanation
---

# ADR-0011: MCP Server Java framework-agnóstico com MCP Java SDK + LangChain4j Agentic

> **Status**: Aceito  
> **Data de Referência**: 2026-09-28  
> **Área / Módulo**: `tools/mcp-agentic-server`  
> **Workflow**: `WF3_TECH_ANALYSIS` (concluído e aprovado por humano) $\rightarrow$ `WF4_BLUEPRINT_SPEC`  
> **Origem**: Handoff de `tech-solution-architect` para persistência de Architectural Decision Record (ADR)

---

## 1. Contexto e Declaração do Problema

O ecossistema `deep-agents-copilot` carece de suporte nativo para orquestração agêntica avançada e execução de ferramentas corporativas no padrão Model Context Protocol (MCP) em linguagem Java.

### 1.1 Cenário Atual do Repositório
1. **Ausência de Código Java**: A análise estática do repositório confirma a inexistência prévia de módulos ou código-fonte Java. O servidor em `tools/mcp-agentic-server` constitui uma implementação estritamente *greenfield*, com raio de impacto (*blast radius*) nulo sobre as funcionalidades existentes.
2. **Topologia de Servidores MCP Existentes**: O projeto já possui servidores MCP integrados via `.vscode/mcp.json` (`codegraph` e `context-mode`). O novo módulo Java deverá ser acoplado seguindo o mesmo padrão declarativo de tooling.
3. **Stack de Telemetria e Observabilidade Existente**: Conforme estabelecido em `docs/architecture/BLUEPRINT_AGENT_OBSERVABILITY.md`, o padrão de telemetria corporativa do projeto baseia-se em:
   - Proxy STDIO transparente em Node (`tools/mcp-otel-proxy`) interceptando chamadas e gerando spans no padrão OpenTelemetry GenAI (`gen_ai.*`).
   - OpenTelemetry Collector Contrib (`tools/otel-langfuse`) operando como proxy local (:4317/:4318) para exportação segura a instâncias do **Langfuse Cloud**.
   - **Phoenix NÃO adotado como backend central**: Não há pacote Java estável para instrumentação automática OpenInference (`openinference-instrumentation-*`), mantendo o Langfuse como destino primário e canônico de telemetria dos agentes.

---

## 2. Opções Avaliadas

Três alternativas arquiteturais foram avaliadas durante a fase técnica (`WF3_TECH_ANALYSIS`):

| Critério | (1) Quarkus MCP Server 2.x + quarkus-langchain4j | (2) Spring AI 1.x starter-mcp-server-webflux | (3) MCP Java SDK puro + LangChain4j AgenticServices (Escolhida) |
|---|---|---|---|
| **Acoplamento a Framework** | Alto (inversão de controle Quarkus, CDI, build-time augmentation) | Alto (ecossistema Spring Boot, Spring WebFlux, reativo) | Mínimo / Nulo (bibliotecas independentes, Java puro / standard) |
| **Pegada de Memória / Runtime** | Baixa com GraalVM Native Image; média em JVM standard | Média/Alta (dependências reativas e infraestrutura Spring) | Baixa a Média (dependências mínimas necessárias) |
| **Aderência ao Padrão de Ferramental** | Exige configuração de plugin Maven/Gradle específico e wrapper | Exige inicialização de ApplicationContext e convenções Spring | Inicializável diretamente via STDIO com comando `java -jar` padrão |
| **Complexidade de Depuração / Tracing** | Média (interceptores de bytecode e CDI) | Média (cadeias reativas WebFlux) | Baixa (fluxo síncrono/assíncrono explícito e listener direto) |
| **Risco de Obsolescência** | Dependência do ciclo de releases da extensão da Red Hat | Dependência da evolução do starter Spring AI | Controle total do ciclo de vida das chamadas do protocolo |

### Detalhamento das Opções:

1. **Opção 1: Quarkus MCP Server 2.x + quarkus-langchain4j, native-image**:
   - *Prós*: Suporte a compilação nativa (GraalVM), inicialização sub-segundo e baixo consumo de heap.
   - *Contras*: Forte acoplamento a extensões do ecossistema Quarkus; restrições de reflexão para reflection-heavy LLM tooling; complexidade desnecessária para um servidor satélite de ferramentas de desenvolvedor.
2. **Opção 2: Spring AI 1.x starter-mcp-server-webflux (protocol=STREAMABLE)**:
   - *Prós*: Abstrações prontas de transporte Streamable HTTP sobre WebFlux e convenções declarativas de tools.
   - *Contras*: Exige trazer o stack reativo Spring WebFlux e Spring Boot; elevado overhead de inicialização; atrito com o transporte local via STDIO através de wrapper proxy.
3. **Opção 3: MCP Java SDK puro + LangChain4j AgenticServices (CHOSEN)**:
   - *Prós*: Abordagem *framework-agnostic* e desacoplada; arquitetura centrada no SDK oficial (`io.modelcontextprotocol.sdk:mcp`); orquestração agêntica limpa via `dev.langchain4j:langchain4j-agentic`; integração direta com STDIO para proxying OTel local.
   - *Contras*: Requer mais código de infraestrutura inicial (*boilerplate*) para transporte HTTP Jakarta Servlet em comparação aos starters dos frameworks opinados.

---

## 3. Decisão Arquitetural

Adotar a **Opção 3: MCP Java SDK puro + LangChain4j Agentic**, formalizando a implementação com as seguintes especificações:

### 3.1 Módulo e Integração
- **Localização**: Novo módulo isolado `tools/mcp-agentic-server/` (projeto Maven/Gradle autocontido, sem contaminação do escopo raiz).
- **Registro de Ferramenta**: Mapeado diretamente em `.vscode/mcp.json` como subprocesso executável local.
- **Isolamento**: Raio de impacto nulo sobre os demais componentes do ecossistema (*zero blast radius*).

### 3.2 Camada de Transporte e Protocolo
- **Transporte Primário**: **STDIO local**, encadeado através do `tools/mcp-otel-proxy` já existente no repositório.
- **Transporte Secundário Opcional**: **Streamable HTTP** (via Jakarta Servlet padrão, nativo do core do SDK) para suporte a execuções remotas caso venha a ser requerido em ambiente distribuído.
- **Exclusão Explícita**: Protocolo legado SSE (*Server-Sent Events*) está expressamente excluído.
- **Fixação do Protocolo**: O protocolo MCP fica **fixado na revisão `2025-11-25`**, por ser a versão com conformidade comprovada no SDK Java 2.0.1. A especificação mais recente `2026-07-28` foi corroborada apenas de forma indireta e não está confirmada como suportada pelo SDK Java disponível.

### 3.3 Versões de Dependências (Referência Maven Central: 2026-09-28)
- `io.modelcontextprotocol.sdk:mcp`: **2.0.1** (GA)
- `dev.langchain4j:langchain4j-core`: **1.20.1** (GA)
- `dev.langchain4j:langchain4j-mcp`: **1.20.1-beta30** (não-GA, risco explícito)
- `dev.langchain4j:langchain4j-agentic`: **1.20.1-beta30** (não-GA, risco explícito)

> ⚠️ **Itens Marcados como 'A Confirmar'**:
> - As versões exatas dos BOMs OpenTelemetry (`io.opentelemetry:opentelemetry-bom` e `io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom`) deverão ser confirmadas na montagem do build descriptor (`pom.xml` / `build.gradle`).
> - As versões exatas de protocolo enumeradas no enum/constantes da classe `McpSchema` do SDK Java 2.0.1 deverão ser validadas durante a compilação inicial.

### 3.4 Observabilidade e Telemetria
- **Convenções Semânticas**: OpenTelemetry GenAI (`gen_ai.*`), com captura de spans de modelo e execução de ferramentas agênticas.
- **Mecanismo de Interceptação**: LangChain4j `ChatModelListener` (API experimental), instrumentando o ciclo de vida de prompts e completions.
- **Exportação Primária**: Spans OTLP exportados diretamente para o OTel Collector local (`tools/otel-langfuse`), que os repassa para o **Langfuse Cloud**.
- **Phoenix como Backend Opcional**: Como inexiste pacote oficial `openinference-instrumentation-*` para ecossistema Java, o Arize Phoenix **NÃO** é adotado como backend central. O Phoenix permanece exclusivamente como alternativa local opcional (via OTLP HTTP na porta `:6006/v1/traces` ou gRPC na porta `:4317`), aproveitando sua capacidade nativa de auto-conversão de atributos `gen_ai.*` para o formato OpenInference introduzida na versão 15.10.0.

---

## 4. Consequências e Gestão de Riscos

### 4.1 Consequências Positivas
- **Independência Tecnológica**: Arquitetura livre de amarras com frameworks proprietários de servidores ou convenções rígidas de injeção de dependência.
- **Convergência de Observabilidade**: Reutilização transparente do ecossistema de telemetria (`tools/mcp-otel-proxy` + OTel Collector + Langfuse Cloud) sem necessidade de infraestrutura adicional.
- **Estabilidade Operacional**: Operação local via STDIO garante compatibilidade universal com ferramentas de desenvolvimento e clientes MCP.

### 4.2 Riscos e Estratégias de Mitigação

| Risco Identificado | Severidade | Estratégia de Mitigação |
|---|---|---|
| **Módulos LangChain4j em versão beta** (`1.20.1-beta30`) | Alta | Fixação estrita de versões no descritor de dependências; encapsulamento de todas as chamadas agênticas atrás de interfaces internas proprietárias do servidor. |
| **Maior volume de boilerplate de transporte** | Baixa | Utilização dos utilitários nativos de servlet do SDK MCP Java; isolamento das rotinas de transporte em pacote dedicado (`transport`). |
| **API experimental de observabilidade** (`ChatModelListener`) | Média | Criação de adapter de telemetria isolado; em caso de deprecação, substituição localizada sem impacto na camada de domínio das tools. |
| **Evolução do protocolo MCP para 2026-07-28** (remoção de `Mcp-Session-Id`) | Média | Monitoramento das releases do MCP Java SDK; manutenção do servidor em design estritamente *stateless* para permitir transição transparente. |

### 4.3 Procedimento de Rollback
Em caso de inviabilidade técnica, instabilidade dos módulos beta ou necessidade de descontinuação:
1. Remover o diretório isolado `tools/mcp-agentic-server/`.
2. Remover a entrada correspondente em `.vscode/mcp.json`.
3. Nenhuma outra parte do repositório será afetada devido ao isolamento arquitetural *greenfield*.

---

## 5. Rastreabilidade e Fontes de Verificação

1. **Maven Central Repository**: Validação de metadados de dependências realizada em 2026-09-28:
   - `io.modelcontextprotocol.sdk:mcp:2.0.1`
   - `dev.langchain4j:langchain4j-core:1.20.1`
   - `dev.langchain4j:langchain4j-mcp:1.20.1-beta30`
   - `dev.langchain4j:langchain4j-agentic:1.20.1-beta30`
2. **Model Context Protocol Specification**: Revisão `2025-11-25` e release notes do SDK Java oficial (`github.com/modelcontextprotocol/java-sdk`).
3. **Governança de Observabilidade do Repositório**: Alinhamento com `docs/architecture/BLUEPRINT_AGENT_OBSERVABILITY.md` e stack `tools/mcp-otel-proxy`.
4. **Arize Phoenix Semantic Conventions**: Suporte nativo a OTLP `gen_ai.*` desde a versão 15.10.0 (`arize.com/docs/phoenix`).
