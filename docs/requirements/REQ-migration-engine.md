# REQ-001: Especificação de Requisitos — Motor Agnóstico de Migração de Tecnologias Legadas

**Status:** Aprovado para Blueprint Técnico  
**Data:** 2026-09-12  
**Autor:** @requirements-analyst  
**Workflow:** WORKFLOW-FEATURE-DEVELOPMENT (Etapa 2 — Elicitação de Requisitos)  
**Fonte Original (Stakeholder):**  
> *"preciso elaborar um novo requisito e plano para o nosso projeto, a ideia é que o nosso projeto deve ter a capacidade de realizar com o maximo de precisao a migracao de tecnologias legadas como exemplo: struts, ejb e etc. nao quero a solucao, seja ela de processo ou wrokflow tenha acoplamento algum com nenhum tecnologia, quero algo que seja capaz de migrar para qualquer framework, agora sendo requisito obrigatorio que em nosso projeto tenha as stacks envolvidas na migracao"*

---

## 1. Visão Geral e Alinhamento Estratégico

O objetivo deste requisito é dotar o ecossistema multi-agent de governança (`deep-agents-copilot`) da capacidade de conduzir migrações de tecnologias legadas (como Apache Struts, Java EJB, entre outras) para qualquer stack ou framework moderno de destino com máxima precisão e conformidade.

### Princípios Inegociáveis (Ground Truth)
1. **Zero Acoplamento Tecnológico no Core:** Nem a máquina de estados, nem os workflows, nem as definições de processo podem conhecer detalhes de sintaxe ou APIs de tecnologias específicas. A lógica de migração opera estritamente sobre contratos e representações semânticas neutras.
2. **Obrigatoriedade das Stacks Envolvidas:** O projeto só autoriza a execução de uma migração se ambas as stacks envolvidas (origem e destino) possuírem representação formal completa no projeto via **Governança de Agentes de Domínio** (`.github/agents/<camada>/<stack>/` com supervisor, sub-catálogo e especialistas).
3. **Máxima Precisão via Dual-Verification:** A validação da migração não se baseia em heurísticas visuais ou "achismo", mas em verificação dupla determinística: **Testes de Caracterização Automatizados (Golden Master)** combinados à **Matriz de Rastreabilidade de Regras de Negócio**.
4. **Recomendação de Mercado para Desacoplamento:** Adoção do padrão canônico de engenharia de software **IR-Based Migration Pipeline** (Semantic Intermediate Representation), utilizado por referências de mercado como OpenRewrite, LLVM e Semgrep, reduzindo a complexidade combinatória de $O(N \times M)$ para $O(N + M)$.

---

## 2. Requisitos Funcionais (EARS)

### REQ-001 [EARS - Ubíquo]: Arquitetura Desacoplada com Core Agnóstico
O motor de migração deve orquestrar todo o ciclo de vida da migração através de uma máquina de estados e fluxo de processo 100% desacoplados de bibliotecas, APIs ou sintaxes de tecnologias específicas.
- **Rastreabilidade:** *"nao quero a solucao, seja ela de processo ou wrokflow tenha acoplamento algum com nenhum tecnologia, quero algo que seja capaz de migrar para qualquer framework"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Orquestração de migração sem dependência de framework no workflow
    Dado que uma solicitação de migração foi iniciada entre uma stack de origem A e uma stack de destino B
    Quando o motor de migração executa a máquina de estados (faseamento, checkpoints e gates)
    Então nenhuma instrução, condição ou comando do workflow core deve conter referências hardcoded às tecnologias A ou B
    E todo processamento específico de tecnologia deve ser delegado exclusivamente aos especialistas de domínio da stack.
  ```

### REQ-002 [EARS - Guiado por Estado]: Validação da Presença Obrigatória de Stacks no Projeto
Enquanto uma migração estiver em fase de pré-voo (pre-flight validation), o motor de migração deve validar que tanto a stack de origem quanto a stack de destino possuem seus ecossistemas de governança formalmente registrados no projeto em `.github/agents/<camada>/<stack>/` contendo supervisor hierárquico (`*-router`), sub-catálogo (`*-catalog.yaml`) e especialistas canônicos.
- **Rastreabilidade:** *"agora sendo requisito obrigatorio que em nosso projeto tenha as stacks envolvidas na migracao"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Bloqueio de migração com stack ausente no catálogo de governança
    Dado que o usuário solicita migrar de uma tecnologia X para uma tecnologia Y
    E a tecnologia X ou Y não possui ecossistema de domínio registrado em .github/agents/
    Quando o motor de migração realiza a validação de pré-voo
    Então a migração deve ser rejeitada com diagnóstico explícito de falta de governança
    E o sistema deve orientar a criação do ecossistema de domínio via @governance-factory (type: stack).

  Cenário: Liberação de migração com ambas as stacks registradas
    Dado que a stack de origem possui ecossistema registrado (ex.: .github/agents/backend/struts/)
    E a stack de destino possui ecossistema registrado (ex.: .github/agents/backend/spring-boot/)
    Quando o motor de migração realiza o pré-voo
    Então o pré-voo de stacks deve ser aprovado com sucesso.
  ```

### REQ-003 [EARS - Guiado por Evento]: Extração Semântica para Representação Intermediária (IR)
Quando acionado para analisar um módulo legado, o especialista da stack de origem deve extrair os contratos, fluxos de controle, regras de negócio e modelos de dados para uma Representação Intermediária Agnóstica (IR — Intermediate Representation) documentada em JSON/YAML neutro.
- **Rastreabilidade:** *"realizar com o maximo de precisao a migracao de tecnologias legadas como exemplo: struts, ejb e etc... capaz de migrar para qualquer framework"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Extração de artefatos legados para modelo neutro
    Dado um módulo legado (ex.: Action Struts ou SessionBean EJB)
    Quando o especialista da stack de origem analisa o código
    Então deve ser gerado um artefato de Representação Intermediária (IR) contendo endpoints, DTOs neutros e fluxo de operações
    E o artefato de IR não deve depender de classes de runtime da tecnologia legada.
  ```

### REQ-004 [EARS - Guiado por Evento]: Emissão de Código Alvo pelos Especialistas da Stack Moderna
Quando a Representação Intermediária (IR) estiver validada, o especialista da stack de destino deve consumir a IR e gerar a implementação idiomática, standalone e moderna conforme as convenções vigentes da stack de destino.
- **Rastreabilidade:** *"capaz de migrar para qualquer framework"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Emissão de código a partir da IR
    Dado uma Representação Intermediária (IR) validada
    Quando o especialista da stack de destino é despachado para geração de código
    Então o código moderno deve ser gerado em lote cirúrgico (R-046) adotando 100% dos padrões canônicos da stack de destino
    E os contratos gerados devem ser idênticos aos especificados na IR.
  ```

### REQ-005 [EARS - Guiado por Evento]: Dual-Verification de Paridade Funcional
Quando o código na stack de destino for gerado, o motor de migração deve submeter a entrega à verificação dupla obrigatória: (1) execução de testes de caracterização Golden Master criados antes da migração; e (2) validação da matriz de rastreabilidade contra as regras de negócio extraídas via `@business-rules-extractor`.
- **Rastreabilidade:** *"realizar com o maximo de precisao a migracao"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Sucesso na verificação dupla de paridade
    Dado que a stack legada possuía suíte Golden Master com entradas e saídas documentadas
    E que a matriz de regras de negócio foi formalmente extraída
    Quando a nova implementação é submetida ao Quality Gate de Paridade
    Então 100% dos testes Golden Master adaptados devem passar verdes
    E 100% das regras da matriz de negócio devem ser comprovadas por asserções de teste.
  ```

### REQ-006 [EARS - Indesejado]: Bloqueio por Desvio de Comportamento (Circuit Breaker)
Se durante a execução da Dual-Verification houver divergência de paridade funcional ou falha de contrato em relação à IR original, então o motor de migração deve interromper o avanço para release, isolar o diff divergente e acionar o ciclo de correção cirúrgica pelo especialista da stack.
- **Rastreabilidade:** *"com o maximo de precisao"*
- **Prioridade:** Must Have (MoSCoW)
- **Critério de Aceite (Gherkin):**
  ```gherkin
  Cenário: Bloqueio de avanço em caso de quebra de paridade
    Dado que a nova stack retornou payload diferente do baseline Golden Master para o mesmo estímulo
    Quando o Quality Gate avalia a suíte de testes
    Então o avanço da migração deve ser bloqueado
    E um relatório detalhado de divergência semântica deve ser emitido para correção pelo test-fixer/feature-developer.
  ```

---

## 3. Requisitos Não-Funcionais (FURPS+)

### RNF-001 [Supportability / Design]: Extensibilidade Combinatória $O(N + M)$
O design da engine deve assegurar que a introdução de uma nova tecnologia legada (origem $N$) ou um novo framework moderno (destino $M$) exija apenas a implementação do respectivo adapter de extração ou emissão de IR, sem nenhuma alteração ou refatoração no núcleo do motor ou na máquina de estados de migração.
- **Prioridade:** Must Have

### RNF-002 [Reliability]: Fidelidade Semântica e Limiar Zero de Regressão Silenciosa
O motor de migração não deve tolerar migrações cegas. Toda migração deve possuir rastreabilidade de entrada/saída comprovável via testes automatizados, com cobertura mínima de 80% das branches de regras de negócio do legado.
- **Prioridade:** Must Have

### RNF-003 [Design / Implementation]: Conformidade com Governança de Domínio
Qualquer stack de tecnologia suportada deve estar em estrita conformidade com os padrões de arquitetura de governança do repositório:
- Estrutura isolada em `.github/agents/<camada>/<stack>/`
- Supervisor hierárquico com R-042 (Anti Sticky-Session) e banner de visibilidade de fluxo
- Sub-catálogo local `<stack>-catalog.yaml` com 7 especialistas canônicos (arch-advisor, feature-developer, bug-fixer, perf-tuner, unit-test-writer, integration-test-writer, test-fixer)
- Sincronização quádrupla atômica global (R-015) em `catalog.yaml`, `routing-graph.yaml`, `agent-router.agent.md` e `README.md`.
- **Prioridade:** Must Have

### RNF-004 [Supportability / Observabilidade]: Rastreabilidade de Transição e Auditoria
O motor de migração deve emitir evidências estruturadas de cada fase:
1. Baseline report do legado (métricas de complexidade e grafo de chamadas via `@code-knowledge-graph`).
2. Artefato de IR intermediário versionado.
3. Matriz de regras de negócio de-para.
4. Relatório comparativo de execução dos testes Golden Master.
- **Prioridade:** Should Have

---

## 4. Matriz de Priorização (MoSCoW)

| ID | Nome do Requisito | Tipo | Prioridade |
|---|---|:---:|:---:|
| **REQ-001** | Arquitetura Desacoplada com Core Agnóstico | Funcional | **Must Have** |
| **REQ-002** | Validação da Presença Obrigatória de Stacks no Projeto | Funcional | **Must Have** |
| **REQ-003** | Extração Semântica para Representação Intermediária (IR) | Funcional | **Must Have** |
| **REQ-004** | Emissão de Código Alvo pelos Especialistas da Stack Moderna | Funcional | **Must Have** |
| **REQ-005** | Dual-Verification de Paridade Funcional | Funcional | **Must Have** |
| **REQ-006** | Bloqueio por Desvio de Comportamento (Circuit Breaker) | Funcional | **Must Have** |
| **RNF-001** | Extensibilidade Combinatória $O(N + M)$ | Não-Funcional | **Must Have** |
| **RNF-002** | Fidelidade Semântica e Limiar Zero de Regressão Silenciosa | Não-Funcional | **Must Have** |
| **RNF-003** | Conformidade com Governança de Domínio | Não-Funcional | **Must Have** |
| **RNF-004** | Rastreabilidade de Transição e Auditoria | Não-Funcional | **Should Have** |

---

## 5. Próximo Passo do Workflow

- **Etapa Concluída:** Etapa 2 — Elicitação de Requisitos (`@requirements-analyst`)
- **Próxima Etapa:** Etapa 3 — Technical Blueprint & Contratos (`@tech-solution-architect`)
  - Ação: Elaborar a arquitetura técnica da Representação Intermediária (IR Schema), contratos de comunicação entre adapters, máquina de estados do Core e plano de fases de implementação.

