---
name: prototype-patterns
description: >-
  Padrão formalizado de prototipagem descartável para responder perguntas de design, validar modelos de estado e testar viabilidade de UI/API antes de implementar em produção. Use para spikes rápidos, prova de conceito (POC) e alinhamento HITL. Não use para código destinado diretamente a produção sem refatoração formal.
tier: 2
category: process
triggers:
  - "protótipo"
  - "prototipagem"
  - "spike"
  - "proof of concept"
  - "POC"
  - "descartável"
  - "HITL rápido"
source_docs:
  - .github/skills/prompt-engineering-patterns/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Prototype Patterns

> Base de conhecimento especializada em **prototipagem rápida e descartável** (*throwaway prototypes*). Fornece diretrizes e heurísticas para criar código focado exclusivamente em responder a uma incerteza técnica ou pergunta de design com o menor esforço e tempo possíveis.

---

## 0) Problema Resolvido & Princípios Fundamentais

Modelos mentais ou especificações em texto frequentemente escondem inconsistências sutis de regras de negócio, atritos de UX ou gargalos de fluxo de estado. Tentar resolver essas incertezas construindo diretamente a solução final em produção gera desperdício de esforço de engenharia, polimento prematuro e retrabalho massivo.

Um protótipo é **código descartável criado estritamente para responder a uma pergunta de design**. Uma vez respondida a pergunta, o código é descartado ou arquivado em branch efêmera, e apenas as decisões validadas e modelos formais são incorporados na base principal.

### Princípios Universais

1. **Descartável por Design**: O protótipo é concebido para ser jogado fora. Localize o código próximo ao contexto de uso, mas nomeie-o explicitamente como protótipo (ex.: `__prototype__`, `scratch-poc`).
2. **Trivial de Executar**: Zero fricção de setup. Um protótipo de lógica/estado roda com duplo clique em um único arquivo HTML; um protótipo de UI inicia com um comando trivial no task runner do projeto (`pnpm dev:proto`, `python -m http.server`).
3. **Sem Persistência por Padrão**: O estado vive na memória volátil. Não acoplar bancos de dados reais a menos que o próprio schema/persistência seja a pergunta central a ser respondida.
4. **Sem Polimento Prematuro**: Sem testes unitários completos, sem tratamento sofisticado de erros, sem abstrações antecipadas. O foco é obter feedback e clareza.
5. **Superfície Explícita de Estado**: Toda ação do usuário ou mutação deve expor visualmente o estado resultante completo para facilitar inspeção humana imediata.
6. **Captura como Fonte Primária**: Ao concluir, registrar a decisão no issue tracker ou commit de documentação, congelando o aprendizado antes de descartar o código.

---

## 1) Quando Usar vs Quando Não Usar

### Quando Usar
- Para responder perguntas críticas de viabilidade técnica: *"Este modelo de máquina de estados cobre todos os corner cases?"*
- Para validar contratos de API e ergonomia de integração antes de congelar schemas.
- Para explorar variações radicais de UI/UX com stakeholders ou usuários finais (Human-in-the-Loop - HITL).
- Para realizar *spikes* investigativos de bibliotecas terceiras desconhecidas.

### Quando Não Usar
- Para implementar features cujo design e contrato já estão consolidados e compreendidos.
- Quando a intenção for fazer um "MVP" que irá direto para produção sem reescrita sob os padrões de governança.
- Para correções de bugs em código existente (usar fluxo canônico de TDD/refactoring).

---

## 2) Ciclo de Vida da Prototipagem

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌───────────────────────────┐
│ 1. Setup     │ ---> │ 2. Build     │ ---> │ 3. Test &    │ ---> │ 4. Decisão:               │
│    Mínimo    │      │    Rápido    │      │    Feedback  │      │    Discard vs Formalize   │
└──────────────┘      └──────────────┘      └──────────────┘      └───────────────────────────┘
```

1. **Setup Mínimo**:
   - Definir com precisão a **pergunta única** que o protótipo deve responder (ex.: *"Como lidar com conflitos de concorrência na transição de status do pedido?"*).
   - Escolher o ramo adequado: **Lógica/Estado** (arquivo único interativo) ou **UI** (sandbox com variações).
2. **Build Focado**:
   - Implementar apenas o caminho crítico que responde à questão.
   - Usar mocks in-memory e dados estáticos representativos.
3. **Test & Feedback (HITL)**:
   - Apresentar o protótipo executável ao desenvolvedor, time ou usuário.
   - Testar cenários extremos e validar a fluidez do modelo.
4. **Decisão Discard vs Formalize**:
   - **Descarte**: O código do protótipo é removido da árvore principal (ou arquivado em branch de scratch).
   - **Formalização**: As decisões de arquitetura, contratos de tipos e tabelas de transição validadas são transferidas para a documentação técnica ou tarefas de implementação formal.

---

## 3) Artefatos Esperados

Dependendo do tipo de pergunta, o protótipo deve gerar um dos seguintes artefatos padronizados:

### A) Single-File HTML (Para Lógica e Máquinas de Estado)
- Um único arquivo autossuficiente (`prototype-logic.html`) com HTML, CSS e JavaScript inline.
- Contém controles interativos (botões para disparar eventos) e visualizadores de estado em tempo real (`<pre id="state">`).
- Permite que qualquer pessoa abra o arquivo no navegador local sem instalar dependências.

### B) UI Sandbox / Variações Chaveáveis (Para Experiência do Usuário)
- Uma rota efêmera ou componente sandbox na aplicação existente.
- Permite alternar instantaneamente entre variações conceituais distintas via parâmetro de URL (ex.: `?variant=inline`, `?variant=modal`) ou barra de controle inferior.

### C) Script CLI Executável
- Um script simples (`proto.py`, `proto.ts` via bun/tsx) demonstrando a interação e performance de uma API externa ou biblioteca.

### D) Documento de Achados (README do Spike)
- Síntese curta (máximo 1 página) contendo:
  - Pergunta original.
  - Veredito / Resposta encontrada.
  - Riscos ou limitações descobertas.
  - Decisão formal de adoção ou rejeição.

---

## 4) Critério de Transição para Implementação Formal

A passagem do protótipo para o código de produção DEVE obedecer às seguintes regras:

1. **Nunca promover o protótipo diretamente para produção**: O código do protótipo carece intencionalmente de testes, tratamento de erros e segurança.
2. **Extração de Decisões**: Apenas esquemas de tipos, tabelas de transição de estado ou snippets cruciais de algoritmo são reaproveitados.
3. **Registro como Fonte Primária**: Se o protótipo gerou código de referência útil, commitar em branch de descarte (ex.: `spike/order-state-poc`) e apontar o link no ticket de implementação.
4. **Execução via Ciclo Canônico**: A implementação formal deve ser executada pelo fluxo padrão de engenharia (TDD, testes de integração, auditoria SonarQube, conformidade de governança).

---

## 5) Anti-Padrões

| Anti-Padrão | Descrição | Como Evitar |
|---|---|---|
| **Protótipo que Vira Produção** | O protótipo "funciona", então é mergeado diretamente na branch principal sem testes nem governança. | Tratar protótipos como estritamente efêmeros; comitar em branch isolada ou deletar após validar. |
| **Spike sem Pergunta Definida** | Iniciar um protótipo aberto sem escopo claro (*"vamos ver como fica"*), gerando dias de esforço sem conclusão. | Exigir a definição prévia de uma pergunta objetiva e binária antes de iniciar a primeira linha de código. |
| **Superpolimento Prematuro** | Gastar horas configurando linters, pipelines de CI, testes unitários ou estilização refinada para código descartável. | Manter deliberadamente código cru; se demorar mais de algumas horas para rodar, o escopo está inflado. |
| **Acoplamento a Infraestrutura Real** | Conectar o protótipo a bancos de dados de homologação, mensageria real ou serviços externos pesados. | Usar fakes em memória, mocks estáticos e arquivos locais temporários. |

---

## 6) Checklist Verificável de Prototipagem

- [ ] A pergunta de design ou viabilidade está explicitamente enunciada.
- [ ] O artefato é autossuficiente e executável com zero ou mínimo esforço de setup.
- [ ] Nenhum banco de dados ou serviço externo complexo foi introduzido sem real necessidade.
- [ ] O estado interno está visível durante a execução interativa.
- [ ] As conclusões e aprendizados foram documentados no ticket/plano de trabalho.
- [ ] O código do protótipo foi isolado em branch descartável ou deletado antes da implementação final.

---

## 7) Referências

- Pocock, Matt. *Prototype Skill Pattern*. `mattpocock/skills/tree/main/skills/engineering/prototype`
- Hunt, Andrew & Thomas, David. *The Pragmatic Programmer* (Capítulo: Tracer Bullets & Prototypes).
- Feathers, Michael. *Working Effectively with Legacy Code*.
