---
name: requirements-engineering-patterns
description: >
  Diretrizes consolidadas de Engenharia de Requisitos (ISO/IEC/IEEE 29148, notação
  EARS, INVEST, Gherkin/BDD, FURPS+) para elicitar, estruturar e validar requisitos
  funcionais e não-funcionais a partir de pedidos de negócio ambíguos — antes de
  qualquer análise técnica de impacto ou plano de implementação. Base de
  conhecimento do agent `requirements-analyst`.
triggers:
  - "levantar requisitos"
  - "requisito ambíguo"
  - "elicitação de requisitos"
  - "user story"
  - "critério de aceite"
  - "requisito funcional"
  - "requisito não-funcional"
  - "escrever requisito"
tools: []
---

# Requirements Engineering Patterns

## 1) Qualidade de Requisito Individual (ISO/IEC/IEEE 29148 Clause 5)

Todo requisito deve satisfazer as 9 características abaixo antes de ser aceito como estruturado:

| Característica | Critério de falha comum |
|---|---|
| Necessário | Não rastreável a uma necessidade real do stakeholder |
| Apropriado | Nível de detalhe incompatível com a fase (ex.: detalhe de implementação em requisito de negócio) |
| Inequívoco | Linguagem vaga ("rápido", "fácil", "assim que possível") sem limiar mensurável |
| Completo | Falta condição, exceção ou critério de sucesso |
| Singular | Mistura duas obrigações na mesma frase (viola INCOSE Rule C5 — ver § 5) |
| Factível | Inviável no orçamento/prazo/limite técnico conhecido |
| Verificável | Não há teste objetivo que comprove atendimento |
| Correto | Não reflete o que o stakeholder realmente pediu |
| Conforme | Não segue o template/notação padrão do projeto |

**Qualidade do conjunto** (5 características, ISO 29148): Completo, Consistente (sem contradição entre requisitos), Factível como conjunto, Compreensível, Validável pelos stakeholders reais.

## 2) Notação EARS (Easy Approach to Requirements Syntax)

Usar para requisitos funcionais verificáveis — cada padrão mapeia para um elemento de teste:

| Padrão | Template | Uso |
|---|---|---|
| Ubíquo | `O <sistema> deve <resposta>` | Comportamento sempre ativo |
| Guiado por evento | `Quando <estímulo>, o <sistema> deve <resposta>` | Reação a um gatilho |
| Guiado por estado | `Enquanto <precondição>, o <sistema> deve <resposta>` | Comportamento condicionado a estado |
| Opcional | `Onde <característica>, o <sistema> deve <resposta>` | Feature configurável |
| Indesejado | `Se <condição indesejada>, então o <sistema> deve <resposta>` | Tratamento de erro/exceção |

Nunca combinar dois padrões na mesma frase — viola singularidade (§ 5).

## 3) Funcional vs. Não-Funcional (FURPS+)

| Categoria | Pergunta-chave |
|---|---|
| Functionality | O que o sistema faz? |
| Usability | Quão fácil é usar? |
| Reliability | Com que confiabilidade opera sob falha? |
| Performance | Com que limiar mensurável de tempo/carga? |
| Supportability | Quão fácil é manter/observar/testar? |
| **+** Design/Implementation/Interface/Physical | Restrições técnicas, de integração ou de compliance |

Nunca listar requisito funcional e não-funcional na mesma seção — separar explicitamente (evita ambiguidade de teste).

## 4) User Stories (INVEST) + Critério de Aceite (Gherkin)

**INVEST**: Independent, Negotiable, Valuable, Estimable, Small, Testable. Um requisito que falha em ≥ 2 critérios deve ser dividido.

Critério de aceite em Gherkin (Given/When/Then) — cada critério mapeia a 1 teste automatizável:

```gherkin
Dado <precondição observável>
Quando <ação do usuário/sistema>
Então <resultado verificável e mensurável>
```

## 5) Regra de Singularidade (INCOSE Rule C5)

Um requisito = uma obrigação verificável. Frase como *"o sistema deve autenticar em 500ms usando AES-256"* mistura comportamento + limiar de performance + restrição de design — nenhum teste único produz veredito inequívoco. Dividir em 3 requisitos rastreáveis.

## 6) Anti-padrão: Solution-Jumping

Quando o stakeholder propõe a **solução técnica** direto ("usar Kafka", "criar tabela X") em vez do **problema/necessidade**, aplicar **Five Whys** antes de aceitar a solução como requisito:

1. Perguntar "por que essa solução resolve o problema?" repetidamente (máx. 5 vezes) até isolar a necessidade real.
2. Documentar a necessidade (requisito) separadamente da solução proposta (candidata de design).
3. Handoff da necessidade para `tech-solution-architect` decidir a solução técnica — nunca aceitar a tecnologia como requisito funcional.

Fonte de mercado: sistemas de mediação de arquitetura para LLM assistants demonstraram 100% de detecção de "solution-jumping" aplicando este fluxo antes de comprometer com tecnologia.

## 7) Guardrail Anti-Alucinação (obrigatório)

- Todo requisito documentado **DEVE** citar a frase/trecho original do stakeholder que o originou (rastreabilidade).
- **NUNCA** inventar requisito não mencionado — ambiguidade ou lacuna vira pergunta via `ask_questions`, nunca suposição.
- Pesquisas mostram que LLMs alucinam requisitos ocasionalmente e carecem de conhecimento de domínio especializado — por isso toda saída deste perfil exige validação humana antes de virar input técnico.
- Modelo de responsabilidade: LLM conduz o diálogo de elicitação; validação de completude/consistência é checklist determinístico (§ 1), não "achismo" do modelo.

## 8) Priorização (MoSCoW)

`Must have` (bloqueia entrega) · `Should have` (importante, não bloqueia) · `Could have` (desejável) · `Won't have` (fora do escopo desta rodada, registrar para não reabrir debate).

## 9) Formato de Documento de Saída

Documento estruturado tipo StRS simplificado (Stakeholder Requirements Specification, ISO 29148 Clause 8/9): cabeçalho de contexto, lista de requisitos com ID rastreável `REQ-NNN`, categoria (funcional/não-funcional), notação EARS, critério de aceite Gherkin, prioridade MoSCoW, citação da fonte.

## 10) Anti-padrões Gerais

- Misturar funcional e não-funcional no mesmo item.
- Critério de aceite não testável ("deve responder rápido" sem limiar).
- Aceitar solução técnica do stakeholder sem aplicar Five Whys.
- Requisito sem citação de origem (alucinação).
- Gerar dezenas de requisitos "possíveis" sem validar com o stakeholder real.
- Confundir elicitação de requisito **novo** com extração de regra de negócio de código **existente** (isso é escopo de `business-rules-extractor`).

## Referências

- ISO/IEC/IEEE 29148:2018 — Systems and software engineering — Requirements engineering.
- EARS (Easy Approach to Requirements Syntax) — Rolls-Royce/Intel, consolidado por INCOSE Guide for Writing Requirements.
- INCOSE Guide for Writing Requirements (Rule C5 — singularidade).
- INVEST criteria (Bill Wake, extreme programming).
- Gherkin/BDD (Cucumber).
- FURPS+ (Robert Grady, HP; extensão IBM/Peter Eeles).
- Pesquisa 2024-2025 sobre elicitação de requisitos multi-agente com LLMs (hallucination, domain-knowledge gaps) e mediação anti-solution-jumping.

