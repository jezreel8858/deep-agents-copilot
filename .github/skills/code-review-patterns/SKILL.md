---
name: code-review-patterns
description: >-
  Diretrizes de mercado para revisão de código automatizada por IA — taxonomia
  de severidade, dimensões de análise, critérios de bloqueio de merge,
  anti-padrões de review (review fatigue, falso-positivo, revisão fora do
  diff), Convergence Contract (rodadas 1-3 anti ping-pong), Noise Budget
  quantificado (teto de 5 nits), Evidence-First/pesquisa obrigatória e
  heurística anti-AI Slop.
tier: 2
category: quality
license: "CC-BY-4.0"
source_attribution: "Tech Leads Club (agent-skills) — conceitos assimilados de 'the-judge', autor Felipe Rodrigues"
imported_from: "https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/(development)/the-judge"
triggers:
  - "revisar código"
  - "code review"
  - "revisão antes do merge"
  - "analisar pull request"
  - "revisar diff"
  - "severidade de achado"
  - "review ping-pong"
  - "rodada de revisão"
  - "noise budget"
  - "código gerado por IA com ruído"
tools: []
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
---

# Code Review Patterns

> Base de conhecimento para agents/prompts que revisam código (diff/PR) antes do merge — nunca corrigem, apenas analisam e reportam.

## Quando Usar

- Antes de revisar um diff/PR e decidir a severidade dos achados.
- Ao definir se um achado deve **bloquear** o merge ou apenas alertar.
- Ao estruturar o relatório de saída de uma revisão de código.
- Ao avaliar se o agent está caindo em anti-padrões de review (ruído, falso-positivo).

## 1) Taxonomia de Severidade (padrão de mercado)

| Nível | Equivalente de mercado | Critério | Bloqueia merge? |
|---|---|---|---|
| 🔴 **Bloqueador** | blocker / critical / P0 | Bug funcional, falha de segurança, quebra de contrato não documentada | ✅ Sim |
| 🟠 **Alta prioridade** | major / P1 | Violação de convenção com impacto real, gap de teste em caminho crítico | ⚠️ Recomendado antes do merge |
| 🟡 **Sugestão** | minor / nitpick / P2-P3 | Estilo, otimização opcional, preferência sem impacto funcional | ❌ Não |
| ✅ **Aprovação** | approved | Trecho bem implementado, digno de nota positiva | — |

## 2) Dimensões de Análise (cobertura mínima)

| Dimensão | O que verificar |
|---|---|
| **Correção funcional** | Lógica, edge cases, condições de corrida, off-by-one |
| **Segurança** | OWASP Top 10 / CWE — injeção, exposição de dados, auth bypass, secrets no diff |
| **Convenções** | Aderência ao adapter de stack do projeto (`.github/instructions/<projeto>.instructions.md`) |
| **Impacto** | Breaking change, dependências afetadas, contratos quebrados |
| **Testes** | Cobertura ausente em caminho crítico, testes quebrados pelo diff |
| **Performance** | N+1, queries sem índice, loops/alocações desnecessárias no hot path |
| **Manutenibilidade** | Complexidade ciclomática alta, duplicação, nomes obscuros |
| **UX/Design System & Navegabilidade** | Nova rota frontend possui entrada correspondente em componente de navegação do projeto (menu/sidenav/tabs — Smell 2.18); componentes de UI novos reaproveitam `shared/`/design system do projeto em vez de HTML/CSS customizado duplicado (Smell 2.19) |
| **Conformidade Documental (Living Docs)** | Mudanças estruturais, rotas, entidades, contratos ou padrões de UI estão refletidos na documentação do projeto (`docs/`, ADRs, schemas, README) de forma auto-sincronizada (R-033) |
---

## 3.1) Taxonomia de Code Smells Clássicos

Inspirada no catálogo clássico de Martin Fowler (*Refactoring*) e no padrão `mattpocock/skills/code-review`, esta taxonomia estabelece o vocabulário compartilhado para achados de manutenibilidade e design em code reviews automatizados por IA.

### 1. Data Clumps
- **Definição**: Grupos de variáveis ou campos que aparecem repetidamente juntos em parâmetros de funções, classes ou retornos.
- **Quando detectar**: O diff adiciona funções com 3+ parâmetros correlatos (ex.: `rua`, `cidade`, `cep`, `numero` ou `startDate`, `endDate`, `timezone`) repetidos em múltiplos métodos.
- **Exemplo de achado em diff**:
```diff
- function createOrder(userId: string, street: string, city: string, zip: string, country: string) {
+ interface ShippingAddress { street: string; city: string; zip: string; country: string; }
+ function createOrder(userId: string, address: ShippingAddress) {
```

### 2. Primitive Obsession
- **Definição**: Uso excessivo de tipos primitivos (`string`, `number`, `boolean`) para modelar conceitos de domínio que possuem invariantes, validações ou comportamentos específicos.
- **Quando detectar**: O diff manipula strings brutas para entidades como `Email`, `CPF`, `Money`, `OrderId` ou `CurrencyCode`, espalhando validações manuais via `regex` ou `if`.
- **Exemplo de achado em diff**:
```diff
- function sendInvoice(recipientEmail: string, amount: number) {
+ function sendInvoice(recipientEmail: EmailAddress, amount: Money) {
```

### 3. Repeated Switches
- **Definição**: Estruturas condicionais (`switch` ou cadeias `if/else if`) sobre o mesmo discriminante (tipo, status, role) repetidas em diferentes módulos da aplicação.
- **Quando detectar**: O diff adiciona mais um `case` em um `switch (user.role)` ou `switch (payment.type)` que já existe em 3 ou mais lugares no código.
- **Exemplo de achado em diff**:
```diff
- switch (notification.type) { case 'SMS': sendSms(); break; case 'EMAIL': sendEmail(); break; }
+ // Preferir Strategy Pattern ou Record de Handlers polimórficos:
+ const handler = notificationHandlers[notification.type];
+ handler.dispatch(notification);
```

### 4. Shotgun Surgery
- **Definição**: Sintoma onde uma única alteração conceitual de negócio exige dezenas de pequenas modificações espalhadas em arquivos, camadas ou repositórios diferentes.
- **Quando detectar**: O PR toca 15+ arquivos com diffs de 1-3 linhas apenas para adicionar um novo status ou campo a uma entidade central.
- **Exemplo de achado em diff**:
```diff
- // Adicionar 'isVIP: boolean' exige alterar 12 arquivos: Model, DTO, Repository, Mapper, Controller...
+ // Centralizar comportamento ou delegar para objeto de valor / extensão modular
```

### 5. Divergent Change
- **Definição**: Uma única classe, módulo ou arquivo que é frequentemente modificado por razões completamente distintas (violação direta do Princípio de Responsabilidade Única - SRP).
- **Quando detectar**: O diff mistura alteração de persistência/SQL, formatação de UI e regra de negócio no mesmo arquivo (ex.: `UserService.ts` alterado tanto para suporte a OAuth quanto para relatório em PDF).
- **Exemplo de achado em diff**:
```diff
- class OrderManager { saveToDb() { ... } generateInvoicePdf() { ... } notifySlack() { ... } }
+ // Separar em OrderRepository, InvoicePdfGenerator e SlackNotifier
```

### 6. Feature Envy
- **Definição**: Um método em uma classe que acessa dados, getters e lógica de outro objeto com mais frequência do que os dados de sua própria classe.
- **Quando detectar**: O diff introduz um método que invoca 4+ getters encadeados de outra classe para realizar um cálculo ou decisão que pertence logicamente à classe dona dos dados.
- **Exemplo de achado em diff**:
```diff
- function calculateDiscount(customer: Customer) {
-   return customer.getOrders().getTotal() * customer.getTier().getFactor();
- }
+ // Mover o cálculo para a própria entidade dona dos dados:
+ const discount = customer.calculateDiscount();
```

### 7. Mysterious Name
- **Definição**: Nomes de variáveis, funções, classes ou módulos enigmáticos, abreviados ou genéricos que ocultam a verdadeira intenção do código.
- **Quando detectar**: O diff introduz identificadores como `d`, `tmp`, `data2`, `res`, `processData()`, `handleStuff()` ou abreviações não-padrão (`usrMgrFn`).
- **Exemplo de achado em diff**:
```diff
- const fn = (d: number, m: boolean) => m ? d * 1.1 : d;
+ const applyTaxAdjustment = (baseAmount: number, isTaxExempt: boolean) =>
+   isTaxExempt ? baseAmount : baseAmount * 1.1;
```

### 8. Duplicated Code
- **Definição**: Estruturas de código, algoritmos ou blocos idênticos ou quase idênticos duplicados em múltiplos pontos, gerando dívida técnica e risco de correções divergentes.
- **Quando detectar**: O diff copia e cola blocos de cálculo de frete, parsing de datas ou tratamento de erros em um novo controller em vez de extrair utilitário ou hook compartilhado.
- **Exemplo de achado em diff**:
```diff
- // No Controller A e no Controller B:
- const token = req.headers.authorization?.split(' ')[1];
- if (!token) throw new UnauthorizedError();
+ // Extrair middleware ou helper compartilhado:
+ const token = extractBearerToken(req);
```

---

## 3) Critérios de Bloqueio de Merge
Bloquear (🔴) **somente** quando:
- Segurança crítica (secret exposto, injeção, bypass de autenticação/autorização).
- Bug funcional com evidência clara (não suposição).
- Breaking change de contrato público sem documentação/versionamento.
- Ausência total de teste em caminho crítico de negócio (pagamento, auth, dado sensível).

Demais achados → alertar (🟠/🟡), nunca bloquear por preferência de estilo isolada.

## 4) Boas Práticas de Prompt/Análise

- **Diff-only**: revisar apenas as linhas alteradas + contexto imediato — nunca o arquivo inteiro (evita ruído e review fatigue).
- **Evidência obrigatória**: todo achado cita `arquivo:linha` — nunca afirmação vaga sem localização.
- **Contexto do PR**: usar descrição/issue vinculada quando disponível antes de classificar severidade (reduz falso-positivo por falta de contexto de negócio).
- **Complementar, não substituir SAST/lint**: rodar/considerar linters e SAST determinísticos (ESLint, SonarQube) primeiro; a revisão por IA cobre o que é semântico e contextual, não o que já é checável por regra estática.

## 5) Anti-Padrões (review fatigue e falso-positivo)

- ❌ Gerar dezenas de comentários "nitpick" sem priorização — sinaliza ruído, não qualidade.
- ❌ Revisar arquivo inteiro quando só uma função mudou.
- ❌ Alertar "possível vulnerabilidade" sem evidência concreta (linha, padrão, CWE referenciável).
- ❌ Ignorar contexto de negócio documentado (issue/PR description) e sugerir mudança já rejeitada anteriormente.
- ❌ Bloquear merge por preferência de estilo sem violação de convenção declarada.
- ❌ Corrigir o código diretamente — revisão é read-only por definição.
- ❌ Aprovar PR de feature frontend com rota nova sem verificar se está integrada à navegação do projeto (menu/sidenav) — feature entregue porém inalcançável (Smell 2.18).
- ❌ Aprovar componente de UI novo sem verificar reaproveitamento de `shared/`/design system já documentado no projeto (Smell 2.19).
- ❌ Aprovar PR com alterações relevantes de arquitetura, rotas, schemas ou regras de negócio sem que a documentação viva (`docs/`, README, ADRs) tenha sido sincronizada (drift documental — R-033).
- ❌ Exceder 3 rodadas de revisão sem declarar convergência/escalar para decisão humana (review ping-pong).
- ❌ Afirmar comportamento de biblioteca/API/framework externo sem citar documentação oficial ou changelog da versão em uso.
- ❌ Ignorar ou aprovar silenciosamente código/comentário inflado por IA (refraseio óbvio, abstração especulativa, try/catch defensivo redundante).
## 6) Formato de Saída Recomendado

- Sumário executivo no topo (contagem por severidade + veredito).
- Achados agrupados por severidade, não por arquivo (facilita priorização).
- Cada achado: `[categoria] descrição → arquivo:linha`.
- Veredito final: `APROVADO | APROVADO COM RESSALVAS | BLOQUEADO`.

## 7) Convergence Contract (Protocolo de Rodadas de Revisão 1-3)

> Assimilado de `the-judge` (Tech Leads Club, CC-BY-4.0) para evitar *review ping-pong* (ciclos infinitos de idas e vindas entre revisor e autor).

| Rodada | Objetivo | Regra |
|---|---|---|
| **1 — Inicial** | Revisão completa do diff | Reporta todos os achados (Bloqueador/Alta/Sugestão) com evidência `arquivo:linha`. |
| **2 — Foco em pendências** | Revisão incremental | Reavalia **apenas** os itens pendentes da Rodada 1; não reabre pontos já aprovados nem introduz nits novos fora do diff incremental. |
| **3 — Convergência final** | Decisão definitiva | Se ainda houver 🔴 Bloqueador, declarar explicitamente que é a última rodada automática e escalar para decisão humana/arbitragem — nunca iniciar uma 4ª rodada sozinho. |

- Todo relatório de revisão declara `Rodada: N/3` no sumário executivo.
- Ultrapassar 3 rodadas sem convergência é anti-padrão (review ping-pong).

## 8) Noise Budget Quantificado (Teto de Nits)

- Máximo de **5 (cinco)** apontamentos cosméticos/nitpick (🟡 Sugestão de estilo sem impacto funcional) exibidos **inline** no corpo do relatório por rodada.
- Excedente ao teto: NÃO descartar — agrupar e reportar como **métrica agregada** no sumário executivo (ex.: "+12 nits adicionais agrupados").
- 🔴 Bloqueador e 🟠 Alta prioridade **nunca** contam para o Noise Budget — o teto aplica-se exclusivamente a 🟡 Sugestão cosmética.
- Finalidade: mitigar review fatigue sem perder rastreabilidade do achado.

## 9) Evidence-First & Pesquisa Obrigatória

- **Verificação em código/repro local obrigatória**: antes de afirmar que uma função falha, quebra contrato ou introduz bug, localizar a evidência real no diff (`arquivo:linha`) — nunca por suposição.
- **Consulta obrigatória a documentação oficial/changelog**: antes de alegar comportamento de biblioteca, API ou framework externo (ex.: "essa versão não suporta X", "método depreciado"), é obrigatório consultar a documentação oficial ou changelog da versão em uso — nunca afirmar por recall de treinamento desatualizado.
- Toda alegação sobre comportamento externo cita a fonte (link de doc oficial/changelog/release notes), equivalente à exigência de `arquivo:linha` para achados internos.
- Hipótese não verificada deve ser rotulada explicitamente como hipótese — nunca classificada como 🔴 Bloqueador.

## 10) Heurística Anti-AI Slop (Código/Comentário Inflado por IA)

| Padrão de AI Slop | Sintoma no diff |
|---|---|
| Comentário que só refraseia o código | Comentário acima da linha repete literalmente o que o código já diz, sem valor informativo adicional |
| Abstração especulativa (YAGNI) | Interface/classe genérica criada para um único caso de uso concreto, sem segundo consumidor real |
| Try/catch defensivo redundante | Bloco try/catch envolvendo chamada síncrona confiável, sem tratamento real do erro — apenas suprimindo exceção |
| Nomenclatura prolixa redundante | Nome de variável/função repete o tipo ou comentário adjacente sem agregar semântica de domínio |

- Classificar como 🟡 Sugestão (salvo quando compromete legibilidade crítica → 🟠 Alta).
- Não bloqueia merge isoladamente; acumula-se no Noise Budget (seção 8) quando for puramente cosmético.

## Checklist

- [ ] Revisão restrita ao diff (não ao arquivo inteiro).
- [ ] Todo achado tem `arquivo:linha` como evidência.
- [ ] Severidade classificada conforme critério de bloqueio (seção 3), não por preferência.
- [ ] Contexto de PR/issue considerado antes de classificar.
- [ ] Nenhuma correção aplicada — apenas relatório.
- [ ] Veredito final declarado (APROVADO/RESSALVAS/BLOQUEADO).
- [ ] Rodada de revisão declarada (`Rodada: N/3`) e convergência respeitada (≤ 3 rodadas, escalar se persistir Bloqueador).
- [ ] Nits cosméticos respeitam o Noise Budget (máx. 5 inline; excedente agrupado como métrica).
- [ ] Alegações sobre comportamento de lib/API externa citam fonte oficial (doc/changelog).
- [ ] Código/comentário inflado por IA (AI Slop) sinalizado quando presente.

## Referências

- Fowler, Martin. *Refactoring: Improving the Design of Existing Code*.
- Matt Pocock / AI Hero: *code-review skill* (https://github.com/mattpocock/skills).
- Google Engineering Practices — Code Review Guide: https://google.github.io/eng-practices/review/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Padrões observados em ferramentas de mercado (CodeRabbit, Qodo/PR-Agent, Sourcery, DeepSource, SonarQube AI CodeFix) — revisão diff-only, severidade blocker/major/minor, complemento a SAST/lint.
- Tech Leads Club — *agent-skills*: `the-judge` (autor Felipe Rodrigues, licença CC-BY-4.0) — https://github.com/tech-leads-club/agent-skills — fonte do Convergence Contract, Noise Budget, Evidence-First e heurística anti-AI Slop.

