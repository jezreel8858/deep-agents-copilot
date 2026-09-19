# Guia Canônico de Boas Práticas de Documentação em Governança de IA

> **Referência Normativa:** [`CLAUDE.md`](../../CLAUDE.md) § R-003, R-033, R-038, R-043, R-044, R-050.  
> **Frameworks de Referência:** Diátaxis, NIST AI RMF 1.0, ISO/IEC 42001, OWASP Agentic AI Top 10 (2026), A2A AgentCard Specification (Linux Foundation/IETF).

---

## 1. Visão Geral e Princípios Fundamentais

Em sistemas multi-agente e ecossistemas de desenvolvimento assistido por IA, a documentação deixa de ser mero repositório passivo de leitura humana e assume o papel de **infraestrutura computacional ativa de controle, contexto e governança**.

### 1.1 A Dualidade de Consumo (Human-in-the-Loop & Agentic RAG)
Toda documentação gerada e mantida neste repositório é projetada para atender simultaneamente a dois públicos distintos com requisitos complementares:
1. **Engenheiros e Auditores Humanos**: Necessitam de clareza conceitual, justificativas arquiteturais (o *porquê* das decisões), runbooks operacionais acionáveis e rastreabilidade estrita de conformidade.
2. **Modelos de Linguagem e Agentes Autônomos (LLMs)**: Consomem documentação via prompts, ferramentas de busca indexada (`context-mode/ctx_search`, BM25/trigram) e extração de contexto. Exigem alta densidade semântica, divisão limpa em seções hierárquicas (*chunking-friendly*), ausência de ambiguidades e dados estruturados em tabelas e esquemas formais.

### 1.2 Princípios Inegociáveis de Documentação
- **Single Source of Truth — SSOT (R-003)**: Cada regra, contrato ou invariante possui um único local de definição canônico. Documentos derivados devem conter links relativos diretos para a fonte original, eliminando a duplicação e o risco de descompasso.
- **Genericidade Obrigatória (R-038)**: Toda a documentação pública e compartilhada em `.github/` e `docs/` deve ser agnóstica a projetos proprietários e tecnologias exclusivas. A validação de conformidade aplica o teste canônico: substituir o projeto por `[PROJETO]` e a tecnologia por `[TECH]` — o documento deve permanecer perfeitamente válido e inteligível.
- **Living Documentation & Autorreflexão (R-033)**: Toda entrega técnica que introduza novas rotas, regras, workflows ou componentes deve atualizar atômica e compulsoriamente os documentos vivos do repositório (`docs/`, `README.md`, catálogos e schemas). É proibido criar documentos órfãos ou especulativos.
- **Isolamento e Anonimização Rigorosa (R-043 / R-044)**: Informações sobre repositórios reais conectados vivem exclusivamente no overlay privado local (`.github/projects.local.yaml` e `.github/instructions/local/`, gitignored). Evidências reais de código inspecionado (nomes de pacotes, rotas internas, credenciais) são obrigatoriamente anonimizadas antes de qualquer persistência em changelogs ou relatórios.

---

## 2. Adoção do Framework Diátaxis para Sistemas Multi-Agente

A documentação do projeto adota a arquitetura de informação **[Diátaxis](https://diataxis.fr/)**, categorizando estritamente cada artefato em exatamente um dos 4 quadrantes conforme a necessidade e a intenção do leitor:

```
                          PRÁTICA (Ação)
                                ▲
                                │
          1. 🎓 TUTORIAIS       │       2. 🛠️ GUIAS PRÁTICOS (HOW-TO)
     Aprendizado orientado      │    Resolução orientada a metas
      a passos práticos         │     e cenários operacionais
                                │
APRENDIZADO ────────────────────┼──────────────────── TRABALHO
(Iniciação)                     │                    (Execução)
                                │
        4. 💡 CONCEITOS         │       3. 📖 REFERÊNCIA TÉCNICA
   Explicação de arquitetura,   │    Contratos estritos, schemas,
   racional, NIST AI e normas   │    catálogos e regras normativas
                                │
                                ▼
                         TEORIA (Cognição)
```

### 2.1 Quadrante 1: Tutoriais (Learning-Oriented)
- **Foco**: Conduzir o leitor (humano ou novo agente) em uma jornada inicial de sucesso reproduzível, construindo competência prática a partir do zero.
- **Estrutura**: Pré-requisitos mínimos → Passos ordenados curtos → Resultado esperado comprovado.
- **Exemplos no Projeto**:
  - `docs/context/setup-context-mode-intellij.md`: Configuração do ambiente integrado com JetBrains IDE e ativação do `context-mode` MCP.
  - `docs/agent-context/codegraph-guia-uso.md`: Inicialização e primeira consulta ao grafo determinístico de código.

### 2.2 Quadrante 2: Guias Práticos / How-To (Goal-Oriented)
- **Foco**: Resolver um problema ou atingir um objetivo específico de engenharia assumindo que o leitor já conhece o básico da plataforma.
- **Estrutura**: Declaração do objetivo → Contexto de ativação → Sequência de execução com tratamento de contingências → Critério de pronto (DoD).
- **Exemplos no Projeto**:
  - `.github/agents/workflows.md`: Guia de condução dos 8 workflows canônicos (Bug-Fix, Refactoring, Feature, Migration, etc.).
  - `.github/skills/project-context-builder/SKILL.md`: Como executar `/add-project-context` para escanear novos repositórios.
  - `.github/skills/efficient-batch-code-modification/SKILL.md`: Como realizar edições em lote único via context-mode.

### 2.3 Quadrante 3: Referência Técnica (Information-Oriented)
- **Foco**: Descrição neutra, precisa e exaustiva da maquinaria técnica. Conteúdo voltado a consulta rápida, validação sintática e testes automatizados.
- **Estrutura**: Tabelas densas, listas de parâmetros, tipagem explícita, exemplos de payloads, JSON Schemas e invariantes.
- **Exemplos no Projeto**:
  - `CLAUDE.md`: Regras normativas R-001 a R-056.
  - `.github/agents/catalog.yaml`: Metadados e catálogo de capacidades dos 36 agentes.
  - `.github/agents/routing-graph.yaml`: Grafo estrutural de transições entre agentes.
  - `docs/schemas/*.schema.json`: Schemas canônicos para Agent Card, Semantic IR e Incidentes.

### 2.4 Quadrante 4: Conceitos & Explicações (Understanding-Oriented)
- **Foco**: Fornecer contexto profundo, explicar o *porquê* das decisões de design, contrastar alternativas rejeitadas e discutir limitações teóricas.
- **Estrutura**: Narrativa conceitual, diagramas de contexto/componentes (Mermaid), trade-offs avaliados e referências de mercado/academia.
- **Exemplos no Projeto**:
  - `docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md`: Especificação mestre arc42 do sistema.
  - `docs/plan/plano-motor-migracao-agnostica.md`: Racional do pipeline desacoplado baseado em Representação Intermediária (IR).
  - `docs/plan/agent-profiles-taxonomy.md`: Fundamentação da taxonomia de papéis de agentes baseada em benchmarks de mercado.

---

## 3. Alinhamento com Padrões Internacionais de Governança de IA

A estrutura documental e operacional do `deep-agents-copilot` mapeia diretamente as principais normas globais de inteligência artificial responsável e engenharia de sistemas agentic:

### 3.1 NIST AI Risk Management Framework (NIST AI RMF 1.0)

| Função NIST AI RMF | Expressão Documental e Prática no Repositório |
|---|---|
| **GOVERN (Governar)** | Políticas canônicas estabelecidas em `CLAUDE.md` (R-001 a R-056), separação estrita de camadas (Global vs Adapters), guardrails inegociáveis de autonomia e convenções de commit/PR (`pr-gatekeeper`). |
| **MAP (Mapear)** | Inventário exaustivo de agentes em `.github/agents/catalog.yaml`, catálogo de skills em `.index.json`, mapeamento determinístico de dependências via `@code-knowledge-graph` e taxonomia formal de perfis. |
| **MEASURE (Medir)** | Suíte determinística de 169+ testes automatizados em pytest (`tests/governance_audit/`), suíte de evals comportamentais (`agent-evals-lab`), métricas de complexidade e auditoria contínua de smells via `@agent-auditor`. |
| **MANAGE (Gerenciar)** | Circuit Breakers de execução (R-050.2), checkpoints humanos obrigatórios (`ask_questions`), sandboxing em subprocessos seguros via `context-mode` (R-056) e camadas redundantes de pós-migração. |

### 3.2 ISO/IEC 42001 (Sistema de Gestão de Inteligência Artificial — AIMS)
- **Ciclo PDCA Documentado**:
  - *Plan*: Elicitação de requisitos (`requirements-analyst`) e Technical Blueprints (`tech-solution-architect`).
  - *Do*: Execução em micro-lotes via context-mode pelos especialistas de domínio sob TDD ou Test-Last.
  - *Check*: Dual-Verification Gates, auditoria de smells, varredura de segurança OWASP (`security-reviewer`).
  - *Act*: Retorno compulsório ao `@agent-router` (R-052), mitigação em lote via `@governance-maintainer` e atualização de templates canônicos (R-055).
- **Rastreabilidade de Configuração e Versionamento**: Toda alteração em agentes, skills ou workflows é versionada via SemVer e registrada detalhadamente no `CHANGELOG.md`.

### 3.3 OWASP Agentic AI Top 10 (2025/2026)
A governança documental audita e prescreve salvaguardas explícitas para os riscos críticos de sistemas de agentes:
- **ASI01 (Goal Hijacking & Prompt Injection)**: Validação estruturada via `@prompt-structuring` (R-041) operando estritamente no Problem Space e isolamento de instruções via frontmatter YAML.
- **ASI02 (Tool Misuse)**: Zoneamento de ferramentas com Least Privilege estrito para routers (R-054) e permissões granulares por papel de agente.
- **ASI03 (Over-Privileged Agents & Tool Sprawl)**: Proibição de ferramentas mutativas ou terminais em agentes analíticos e routers; precedência mandatória de context-mode (R-056).
- **ASI08 (Cascading Failures & Autonomous Drift)**: Circuit breakers com teto máximo de tentativas (3x) e retorno obrigatório para intervenção humana com rollback atômico.

---

## 4. O Padrão Agent Card para Documentação de Agentes (A2A Protocol)

Em consonância com o protocolo aberto **Agent2Agent (A2A)** chancelado pela Linux Foundation e a especificação **IETF AgentCard Draft (2026)**, cada agente do ecossistema deve possuir dupla representação:

1. **Representação Operacional (`.agent.md`)**:
   - Cabeçalho Frontmatter YAML estrito (`name`, `description`, `tier`, `category`, `tools`, `source_docs`).
   - Seções canônicas: *Contexto de Ativação*, *Diretrizes Inegociáveis*, *Quando Delegar*, *Anti-Padrões* e *Formato de Saída*.
2. **Representação em Manifesto Máquina-Máquina (`agentcard.json`)**:
   - Validada contra o schema canônico [`docs/schemas/agentcard.schema.json`](../schemas/agentcard.schema.json).
   - Exportada e auditada pela ferramenta em `tools/agentcard_exporter/`.
   - Declara publicamente: identidade única, versão, interfaces suportadas, lista de ferramentas autorizadas e limites contratuais de invocação.

---

## 5. Diretrizes para Estruturação e Chunking de Arquivos Markdown

Para garantir que a documentação seja indexada e recuperada com máxima fidelidade por sistemas de RAG e agentes baseados em context-mode:

### 5.1 Hierarquia Estrita de Headings
- Nunca pular níveis de títulos: `# H1` → `## H2` → `### H3` → `#### H4`.
- Os divisores de contexto de LLMs e o mecanismo `ctx_index` utilizam os títulos para quebrar chunks semânticos; saltos de nível produzem fragmentação incorreta e perda de contexto.

### 5.2 Densidade de Informação via Tabelas e Listas
- Prefira tabelas comparativas densas a longos parágrafos narrativos.
- Estruture comandos e trechos de código sempre com marcadores de linguagem explícitos:
  ````markdown
  ```bash
  git --no-pager diff --stat
  ```
  ````

### 5.3 Nomenclatura e Localização de Arquivos
- Arquivos de documentação Markdown utilizam obrigatoriamente **`kebab-case.md`** (sem espaços, acentos ou maiúsculas).
- Exceções canônicas de raiz mantidas em caixa alta por padrão de mercado: `README.md`, `CLAUDE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`.

---

## 6. Governança da Documentação Viva (Living Documentation Protocol — R-033)

A documentação deve ser tratada como parte integrante do código-fonte (*Docs as Code*). 

### 6.1 Critério de Pronto Documental (Definition of Done)
Nenhum PR ou entrega técnica é considerado concluído se:
- Introduziu nova regra normativa ou refinamento sem atualizar `CLAUDE.md` e `.github/copilot-instructions.md`.
- Modificou ou adicionou um agente sem atualizar `catalog.yaml`, `routing-graph.yaml` e os evals correspondentes.
- Alterou ou expandiu workflows sem sincronizar `workflows.md` e a suíte de testes correspondente.
- Deixou de registrar o impacto da entrega no `CHANGELOG.md` no padrão SemVer.

### 6.2 Proibição de Documentação Especulativa
- Agentes são terminantemente proibidos de gerar arquivos `.md` soltos ou de rascunho sem pedido explícito do usuário.
- Toda documentação criada deve ter um destino formal catalogado no [Portal de Documentação](../README.md).

