# Portal de Documentação — Deep Agents Copilot

> **Bem-vindo à Central Unificada de Documentação do Ecossistema Multi-Agente.**  
> Esta documentação é estruturada seguindo o framework internacional **[Diátaxis](https://diataxis.fr/)**, dividindo o conhecimento técnico em quatro quadrantes orientados às necessidades do leitor: **Tutoriais** (aprendizado prático), **Guias Práticos** (como resolver tarefas), **Referência Técnica** (especificações e schemas) e **Conceitos & Arquitetura** (entendimento profundo).

---

## 🗺️ Mapa da Documentação (Matriz Diátaxis)

```
                          PRÁTICA (Ação)
                                ▲
                                │
          1. 🎓 TUTORIAIS       │       2. 🛠️ GUIAS PRÁTICOS (HOW-TO)
     Passo a passo para novos   │    Soluções para objetivos específicos
      desenvolvedores e IAs     │     e procedimentos operacionais
                                │
APRENDIZADO ────────────────────┼──────────────────── TRABALHO
(Iniciação)                     │                    (Execução)
                                │
        4. 💡 CONCEITOS         │       3. 📖 REFERÊNCIA TÉCNICA
   Arquitetura, arc42, NIST     │    Catálogos, Schemas JSON,
   AI RMF, decisões e porquês   │    regras normativas (R-xxx)
                                │
                                ▼
                         TEORIA (Cognição)
```

---

## 1. 🎓 Tutoriais (Learning-Oriented)
*Documentos guiados voltados ao aprendizado prático passo a passo para desenvolvedores humanos e agentes autônomos que estão começando no repositório.*

- [**Guia de Primeiros Passos & Setup**](context/setup-context-mode-intellij.md): Configuração do ambiente integrado com JetBrains IntelliJ IDEA / PyCharm e ativação do `context-mode` MCP.
- [**Guia Operacional do Motor de Grafo**](agent-context/codegraph-guia-uso.md): Tutorial prático de inicialização e consulta ao `@optave/codegraph` para análise estrutural de código sem IA.
- [**Instruções Globais de Git Commit**](ai-copilot/global-git-commit-instructions.md): Tutorial sobre o formato padronizado Conventional Commits adotado pelos agentes.

---

## 2. 🛠️ Guias Práticos / How-To (Goal-Oriented)
*Procedimentos operacionais focados em objetivos concretos e problemas específicos do dia a dia de engenharia.*

- **Como Rodar Workflows Canônicos**:
  - [Workflows Operacionais Determinísticos](../.github/agents/workflows.md): Especificação dos 8 workflows (Bug-Fix, Refactoring, Technical Analysis, Feature, Governance, CVE, Framework Migration com 6 etapas e Release Readiness).
- **Como Adicionar Contexto de Novo Projeto**:
  - [Project Context Builder](../.github/skills/project-context-builder/SKILL.md): Como executar `/add-project-context` para gerar adapters em `local/` sem vazar dados para o repositório público (R-043/R-044).
- **Como Operar em Modo Context Mode**:
  - [Context Mode MCP Guide](agent-context/context-mode.md): Boas práticas de execução no sandbox, Think-in-Code e prevenção de saturação da janela de contexto (R-056).
- **Como Auditar e Corrigir Smells de Agentes**:
  - [Catálogo de Smells de Governança](../.github/skills/governance-audit-patterns/SKILL.md): Como identificar e sanar os 24 smells canônicos de governança.

---

## 3. 📖 Referência Técnica (Information-Oriented)
*Especificações formais, catálogos estruturados, schemas de validação e regras normativas para consulta rápida e auditoria automatizada.*

- **Regras Normativas de Governança (Ground Truth)**:
  - [CLAUDE.md](../CLAUDE.md): Fonte de verdade operacional global (Regras R-001 a R-056).
  - [Instruções Copilot](../.github/copilot-instructions.md): Diretrizes operacionais e fast-paths do GitHub Copilot.
- **Catálogos Estruturados de Agentes e Skills**:
  - [Catálogo Central de Agents](../.github/agents/catalog.yaml): Metadados, modelos, ferramentas e restrições dos 36 agentes.
  - [Grafo de Roteamento Estrutural](../.github/agents/routing-graph.yaml): Grafo declarativo de nós, arestas e regras de transição (R-040).
  - [Índice Geral de Skills](../.github/skills/.index.json): Mapeamento de 58 skills por tier e categoria.
  - [Catálogo de Prompts Workflow](../.github/prompts/README.md): Prompts padronizados de orquestração.
- **Schemas Canônicos de Validação (JSON Schema)**:
  - [`agentcard.schema.json`](schemas/agentcard.schema.json): Schema de especificação de identidade e capacidades de agentes (A2A Protocol / IETF Draft).
  - [`migration-ir.schema.json`](schemas/migration-ir.schema.json): Schema canônico da Representação Intermediária (Semantic IR) para migrações agnósticas de framework.
  - [`workflow-incident.schema.json`](schemas/workflow-incident.schema.json): Schema de persistência estruturada de incidentes operacionais de workflows.
- **Requisitos de Sistema (EARS / INVEST)**:
  - [`REQ-migration-engine.md`](requirements/REQ-migration-engine.md): Requisitos do motor agnóstico de migração (REQ-001 a REQ-009).
  - [`REQ-workflow-incident-persistence.md`](requirements/REQ-workflow-incident-persistence.md): Requisitos de auditoria e persistência de incidentes.
- **Histórico e Versionamento**:
  - [CHANGELOG.md](../CHANGELOG.md): Histórico completo de versões SemVer e entregas do ecossistema.

---

## 4. 💡 Conceitos & Arquitetura (Understanding-Oriented)
*Explicações conceituais, decisões de design arquitetural, enquadramento em padrões internacionais e o racional por trás das regras.*

- [**Guia Canônico de Arquitetura e Governança (arc42)**](architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md): Documento mestre em 12 seções arc42 cobrindo metas, restrições, contexto, building blocks, runtime view e conceitos transversais.
- [**Guia de Boas Práticas de Documentação em Governança de IA**](architecture/AI_GOVERNANCE_DOCUMENTATION_GUIDE.md): Alinhamento com NIST AI RMF, ISO/IEC 42001, OWASP Agentic AI, Diátaxis e living documentation.
- **Planos e Decisões de Arquitetura (ADR / Blueprints)**:
  - [Plano do Motor Agnóstico de Migração](plan/plano-motor-migracao-agnostica.md): Blueprint técnico do motor IR-based com paridade funcional e redundância pós-migração.
  - [Taxonomia de Perfis de Agentes](plan/agent-profiles-taxonomy.md): Categorização de agentes segundo benchmarks de mercado (Anthropic, OpenAI, LangGraph).
  - [Persistência de Incidentes de Workflows](plan/plano-persistencia-incidentes-workflows.md): Arquitetura de observabilidade e telemetria de falhas em tempo de execução.

---

## 📋 Diretrizes para Contribuição e Manutenção de Docs

Ao adicionar ou editar documentação neste repositório:
1. **Classificação Diátaxis Obrigatória**: Antes de escrever, defina o quadrante do documento (Tutorial, How-to, Referência ou Conceito).
2. **Genericidade Absoluta (R-038)**: Nunca vincule nomes de projetos privados, classes de negócio ou dados proprietários em documentos compartilhados.
3. **Headings Hierárquicos**: Mantenha sequência estrita de títulos (`#` → `##` → `###`) para garantir chunking limpo por ferramentas de IA e RAG.
4. **Living Documentation (R-033)**: Toda alteração arquitetural, de regra ou de workflow exige atualização sincronizada dos documentos correlatos na mesma entrega.

