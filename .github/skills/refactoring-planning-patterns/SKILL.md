---
name: refactoring-planning-patterns
description: >-
  Diretrizes consolidadas para planejamento e decomposição macro de refatorações
  estruturais: Mikado Method, Strangler Fig, Branch by Abstraction, testes de
  caracterização (Golden Master), métricas de acoplamento e rollback multicamada.
tier: 2
category: process
triggers:
  - "planejamento de refatoração"
  - "refactor planning"
  - "mikado method"
  - "strangler fig"
  - "branch by abstraction"
  - "golden master"
  - "characterization tests"
  - "blast radius refactor"
  - "decomposição de refatoração"
  - "rollback de refatoração"
source_docs:
  - .github/agents/refactor-planner.agent.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Refactoring Planning Patterns

> Base de conhecimento especializada em **planejamento e governança de refatorações estruturais e arquiteturais**. Utilizada pelo `@refactor-planner` para estruturar planos acíclicos atômicos (DAGs) com garantias de zero-downtime, rede de segurança e rollback desacoplado de reversão de commit.

## Quando Usar

- Ao decompor refatorações amplas em código de alto risco, alta complexidade ou múltiplos dependentes.
- Ao planejar a modernização ou extração de módulos legados com ou sem testes automatizados prévios.
- Ao arquitetar migrações estruturais que exigem coexistência temporária entre legado e novo componente.
- Ao mapear rollback e contingência em nível de contrato, feature flag ou schema de banco de dados.

---


## 1.1) Vocabulário de Deep Module (Codebase Design)

> **Origem / Inspiração**: Princípios de arquitetura e design de software de John Ousterhout (*A Philosophy of Software Design*) consolidados em `mattpocock/skills/codebase-design`.
> **Objetivo em Refatoração**: Projetar **módulos profundos** (*deep modules*), onde uma alta densidade de comportamento e complexidade reside atrás de uma interface enxuta e estável, posicionada em uma costura (*seam*) limpa e testável.

### Conceitos Fundamentais

| Termo | Definição | Objetivo em Refatoração | Exemplo Concreto |
|---|---|---|---|
| **Deep Module** | Módulo cuja interface expõe pouca complexidade (poucos métodos/parâmetros), mas cuja implementação interna encapsula alto comportamento e regras de negócio. | Maximizar a alavancagem dos chamadores e isolar mudanças internas sem quebrar consumidores. | Um serviço `OrderProcessor.process(orderId)` que internamente orquestra estoque, pagamento, antifraude e mensageria sem expor 15 métodos intermediários. |
| **Shallow Module** | Módulo cuja interface é quase tão complexa quanto sua implementação interna (pass-through ou wrapper fino sem agregação de valor). | Eliminar ou aprofundar durante o refactoring, fundindo camadas redundantes ou ocultando detalhes internos. | Um `UserService` anêmico que apenas repassa chamadas idênticas para `UserRepository.findById` sem validação, transformação ou política adicional. |
| **Seam (Costura)** | Ponto de junção onde é possível alterar o comportamento do sistema sem editar o código naquele ponto exato (Michael Feathers). | Estabelecer limites desacoplados onde módulos legados e novos possam coexistir ou ser interceptados por testes/mocks. | Injeção de dependência via interface `PaymentGateway` permitindo alternar entre implementação real (Stripe) e fake em memória nos testes. |
| **Adapter Pattern** | Estrutura concreta que preenche um slot em uma costura (*seam*), adaptando uma interface externa ou legado ao contrato exigido pelo módulo. | Permitir que o novo design avance com vocabulário de domínio limpo, isolando peculiaridades de clientes ou sistemas externos. | `LegacyCustomerSoapAdapter` implementando a nova interface `CustomerDomainService` enquanto consome chamadas SOAP de um ERP legado. |
| **Leverage Points** | Pontos de alta alavancagem onde uma pequena alteração ou abstração na interface beneficia N pontos de chamada e M testes. | Concentrar o esforço de refatoração nos componentes que maximizam a redução de complexidade em toda a base de código. | Centralizar a política de validação de tokens em um interceptor/middleware único, removendo parsing manual de 40 endpoints. |
| **Locality** | Propriedade de concentração de contexto, conhecimento, bugs e verificação em um único ponto, evitando dispersão sistêmica. | Garantir que correções ou alterações de regras ocorram em um único local (*fix once, fixed everywhere*), eliminando *shotgun surgery*. | Centralizar regras fiscais de cálculo de tributos em `TaxCalculator` em vez de espalhá-las nas camadas de checkout, fatura e relatório. |
| **Deletion Test** | Teste de validação conceitual: imaginar a exclusão do módulo do sistema para auditar se ele realmente justifica sua existência. | Validar se o módulo é um intermediário dispensável ou se concentra complexidade real que reapareceria nos consumidores caso removido. | Se deletar `OrderValidationHelper` faz a complexidade desaparecer, ele era ruído; se espalha validações em 10 controladores, era legítimo. |

### Diretrizes de Design para Refatoração

1. **Profundidade é propriedade da interface, não do tamanho do código**: Um módulo profundo pode ser internamente composto por partes menores e intercambiáveis (costuras internas), mas sua superfície externa permanece pequena e coesa.
2. **A interface é a superfície de teste**: Testes e chamadores cruzam a mesma costura (*seam*). Se for necessário inspecionar detalhes privados além da interface para testar, o módulo provavelmente está com o formato incorreto.
3. **Uma costura sem variação é custo**: Uma única implementação concreta indica uma costura hipotética; duas ou mais indicam uma costura real necessária. Evitar criar abstrações ou interfaces prematuras quando não há variabilidade real.
4. **Preferir dependências recebidas a criadas**: Receber dependências via construtor ou parâmetro em vez de instanciar internamente (`new ConcreteGateway()`), garantindo testabilidade limpa na costura.
5. **Retornar resultados em vez de produzir efeitos colaterais ocultos**: Favorecer métodos que retornam estruturas imutáveis e resultados explícitos, facilitando testes e reduzindo acoplamento temporal.

---

## 1) Metodologias e Padrões de Refatoração Estrutural

```text
[Identificação de Smells / Hotspots]
                │
                ▼
  [Safety Net: Characterization Tests]
                │
                ▼
  [Mikado Method: Grafo de Dependências]
         ┌──────┴──────┐
         ▼             ▼
   [In-Process]   [Inter-Process]
    Branch by       Strangler
   Abstraction         Fig
         │             │
         └──────┬──────┘
                ▼
   [Cutover & Descomissionamento]
```

### A) Mikado Method (Ellnestam & Brolund)
- **Princípio**: Decomposição por exploração reversa. Define-se o objetivo raiz (*Mikado Goal*) e realiza-se um experimento (*spike*).
- **Regra Cardeal de Rollback**: Se o spike quebrar a compilação ou revelar pré-requisitos ausentes, o código é **imediatamente revertido** (`git reset --hard`).
- O erro nunca é consertado dentro do spike; ele é registrado como nó folha no grafo de pré-requisitos.
- As mudanças reais só são integradas no tronco principal quando as folhas do grafo estiverem resolvidas e com testes verdes.

### B) Branch by Abstraction (Paul Hammant)
- **Escopo**: Refatorações intra-processo no mesmo repositório sem branches de longa duração.
- **Passos Canônicos**:
  1. Criar interface/abstração sobre o código legado alvo.
  2. Redirecionar todos os clientes para a nova interface.
  3. Criar a nova implementação moderna ao lado da legada.
  4. Introduzir **Feature Flag** em runtime para chavear entre implementações.
  5. Validar em produção, alternar tráfego para 100% novo e remover o código legado.

### C) Strangler Fig Application (Martin Fowler)
- **Escopo**: Refatorações arquiteturais cross-serviços ou entre monolito e microsserviços.
- **Mecanismo**: Interceptação perimetral de tráfego via API Gateway / Reverse Proxy.
- Rotas específicas são migradas incrementalmente para o novo serviço enquanto a rota legada permanece ativa para o tráfego restante, até a extinção do subsistema antigo.

---

## 2) Safety Net e Testes de Caracterização (Michael Feathers)

- **Premissa**: Não existe refatoração segura em código sem cobertura confiável.
- **Characterization Tests / Golden Master**:
  - Capturar o comportamento *real observado* da aplicação legada (incluindo bugs tácitos aceitos pelo negócio).
  - Alimentar a rotina com massas variadas de entrada e armazenar os snapshots de saída (Approval Testing).
  - Esse baseline congelado serve como oráculo determinístico para atestar que o comportamento externo não sofreu regressão.
- **Identificação de Seams (Costuras)**:
  - Localizar pontos do código onde o comportamento pode ser interceptado e injetado sem edição invasiva (ex.: construtores, interfaces, factory methods).

---

## 3) Análise Comportamental e Métricas de Acoplamento

### A) Hotspots (Adam Tornhill — CodeScene)
$$\text{Hotspot Score} = \text{Normalized Churn (frequência de commits)} \times \text{Complexidade Ciclomática}$$
- Concentrar esforço de planejamento nos 2% a 4% de arquivos que concentram o maior número de incidentes e retrabalho.

### B) Acoplamento Temporal (Co-change Analysis)
- Detectar arquivos que mudam juntos no histórico do Git sem dependência estática explícita:
$$Jaccard(A, B) = \frac{|\text{Commits}(A \cap B)|}{|\text{Commits}(A \cup B)|}$$
- $Jaccard \ge 0.5$ indica acoplamento oculto grave (*Shotgun Surgery*) que deve ser unificado na refatoração.

### C) Métricas de Estabilidade e Abstração (Robert C. Martin)
- **Instabilidade ($I$)**: $I = C_e / (C_a + C_e)$ (onde $C_a$ é fan-in e $C_e$ é fan-out).
- **Abstração ($A$)**: proporção de tipos abstratos/interfaces.
- **Zone of Pain ($A \to 0, I \to 0$)**: classes muito concretas e com dezenas de dependentes diretos. Exigem criação de interface intermediária antes de qualquer alteração de lógica.

---

## 4) Estrutura do DAG de Tarefas Atômicas

Cada nó do plano de refatoração deve ser estruturado com contratos estritos:

| Campo | Descrição |
|---|---|
| **Task ID & Propósito** | Identificador sequencial único e objetivo único (*Single Concern*) |
| **Executor Especialista** | Agente de stack responsável (`@angular-engineer`, `@spring-boot-engineer`, etc.) |
| **Gate In (Pré-condições)** | Testes de caracterização verdes, workspace limpo, branches alinhadas |
| **Ação Determinística** | Escopo delimitado (máx. 1 a 3 arquivos por passo) |
| **Gate Out (Pós-condições)**| Suíte de testes 100% verde, compilação sem warnings/erros, diff mínimo |
| **Contingência / Rollback** | Mecanismo de reversão local ou em runtime |

---

## 5) Matriz de Rollback Multicamada (Zero-Downtime)

> Esta matriz detalha o rollback específico de refatorações zero-downtime; para a classificação genérica de reversibilidade (T1/T2/T3) aplicável a qualquer plano de decomposição, ver `task-decomposition-patterns/SKILL.md` §7 (fonte canônica, evitar redefinição divergente — R-055).

Evitar dependência exclusiva de `git revert` em produção. Planejar contingência por camada:

| Camada | Padrão Aplicado | Mecanismo de Rollback Rápido |
|---|---|---|
| **Contrato de API** | Evolução aditiva (*Tolerant Reader*) | Gateway chaveia rota de volta ao handler legado |
| **Lógica Interna** | *Branch by Abstraction* | Desativação imediata da Feature Flag em runtime |
| **Persistência / DB** | *Expand & Contract* (Parallel Change) | 1. Reverter leitura para coluna legada<br>2. Desativar dual-write<br>3. Drop de coluna nova apenas após soak time |

---

## Checklist Verificável de Planejamento

- [ ] Código alvo possui safety net (testes unitários confiáveis ou testes de caracterização documentados).
- [ ] Dependências, fan-in/fan-out e blast radius foram avaliados via `@codegraph-engine`.
- [ ] Hotspots históricos e acoplamento temporal (co-change) foram considerados no agrupamento das etapas.
- [ ] Padrão de migração selecionado adequadamente (Mikado, Branch by Abstraction ou Strangler Fig).
- [ ] Tarefas organizadas em DAG com no máximo 1 a 3 arquivos alterados por nó.
- [ ] Cada nó do plano possui Gate In, Gate Out e agente especialista de stack atribuído.
- [ ] Rollback planejado em runtime (flags, tolerância a falhas, expand & contract) sem depender puramente de commit revert.
- [ ] Módulos-alvo avaliados quanto à profundidade (Deep Module vs Shallow Module) e submetidos ao Deletion Test, prevenindo ativamente Pass-Through Methods sem agregação de valor.
- [ ] Seams (costuras) identificadas nos pontos de injeção de teste/desacoplamento antes de iniciar a refatoração.

---

## Anti-padrões

| Anti-padrão | Risco / Sintoma | Correção Recomendada |
|---|---|---|
| "Big Bang" Refactoring | Conflitos insolúveis de merge e quebras em produção | Aplicar Mikado Method e fatiamento em DAG |
| Refatorar sem Safety Net | Quebra silenciosa de regras de negócio tácitas | Escrever Characterization Tests antes de mover código |
| Depender de `git revert` para BD | Perda irrecuperável de dados ou corrupção | Adotar padrão *Expand & Contract* com dual-write |
| Modificar comportamento e estrutura juntos | Impossibilidade de rastrear causa raiz de bugs | Separar estritamente refactoring de nova feature |
| Ignorar Zone of Pain ($A=0, I=0$) | Propagação de quebras em cascata no sistema | Injetar interface (Branch by Abstraction) primeiro |
| Pass-Through Method / Shallow Module residual | Interface tão complexa quanto a implementação; wrapper fino sem agregação de valor detectado pelo Deletion Test | Fundir camadas redundantes (aprofundar o módulo) ou eliminar o intermediário, concentrando comportamento atrás de interface enxuta |

---

## Referências Oficiais

- Fowler, Martin. *Refactoring: Improving the Design of Existing Code*. Addison-Wesley, 2018.
- Feathers, Michael. *Working Effectively with Legacy Code*. Prentice Hall, 2004.
- Ellnestam, Ola; Brolund, Daniel. *The Mikado Method*. Manning Publications, 2014.
- Tornhill, Adam. *Your Code as a Crime Scene*. Pragmatic Bookshelf, 2ª ed., 2024.
- Hammant, Paul. *Branch by Abstraction* (https://paulhammant.com/blog/branch-by-abstraction.html)
- Martin, Robert C. *Clean Architecture: Software Structure and Design*. Prentice Hall, 2017.

