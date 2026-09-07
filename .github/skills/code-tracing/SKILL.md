---
name: code-tracing
description: >
  Estratégias consolidadas para rastrear código de um sintoma até a causa raiz —
  cobrindo grep vs busca semântica, parsing de stack trace, navegação de call graph,
  rastreio de API/método e coleta mínima de evidências. Agnóstico de linguagem e
  framework. Use em qualquer contexto de investigação de bug, análise de impacto
  ou compreensão de código desconhecido.
tier: 1
category: tooling
triggers:
  - "rastrear código"
  - "encontrar onde está implementado"
  - "stack trace"
  - "call graph"
  - "quem chama esse método"
  - "onde essa API é usada"
  - "rastrear falha"
  - "origem do erro"
  - "investigar bug"
  - "encontrar classe responsável"
  - "tracing"
  - "grep no código"
  - "busca semântica"
  - "dependência de método"
tools:
  - "grep_search"
  - "file_search"
  - "read_file"
  - "run_in_terminal"
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
---

# Code Tracing

Estratégias consolidadas para navegar um codebase a partir de um sintoma — localizando a classe, método, API ou serviço responsável pela falha — com o menor consumo de contexto possível.

> **Aplica-se a**: `bug-triage`, `test-engineer`, `tech-solution-architect`, `refactor-planner` e qualquer agent ou prompt que precise localizar código a partir de um comportamento observado.

---

## 1) Pipeline de Investigação: Do Sintoma à Causa Raiz

```
Sintoma (mensagem de erro / comportamento / stack trace)
        ↓
[FASE 1] Normalizar — extrair identificadores do sintoma
        ↓
[FASE 2] Localizar — grep exato → busca semântica (fallback)
        ↓
[FASE 3] Traçar — call chain: de onde vem? quem chama?
        ↓
[FASE 4] Confirmar — ler apenas o trecho relevante (não o arquivo todo)
        ↓
[FASE 5] Evidenciar — registrar arquivo:linha, símbolo e padrão encontrado
```

---

## 2) Fase 1: Normalizar o Sintoma

Antes de qualquer busca, extrair os **identificadores concretos** do sintoma:

| Tipo de sintoma | Identificadores a extrair |
|---|---|
| Stack trace | Classe, método, linha, arquivo |
| Mensagem de erro | String literal, código de erro, campo de validação |
| Comportamento de API | Endpoint, método HTTP, payload, código de resposta |
| Falha de teste | Nome do spec, describe, arquivo `.spec.ts` / `.test.java` |
| Exceção de runtime | Tipo da exceção, mensagem, módulo de origem |

**Regra**: extrair ao menos 2 identificadores concretos antes de buscar. Com 0 identificadores, use `ask_questions` para obter mais contexto.

---

## 3) Fase 2: Localizar — Grep vs Busca Semântica

### Decisão: quando usar cada abordagem

```
Identificador é exato (nome de classe, método, string)?
├─ Sim → GREP (mais rápido, sem ambiguidade)
│  └─ Fallback: se 0 resultados → Busca Semântica
└─ Não (comportamento, conceito, intenção)?
   └─ BUSCA SEMÂNTICA (grep_search com termos relacionados)
```

### Grep — padrões efetivos por tipo

```bash
# Classe/interface por nome exato
grep_search "class NomeDaClasse"
grep_search "interface NomeDaInterface"

# Método por assinatura
grep_search "def nome_metodo"         # Python
grep_search "function nomeMetodo"      # JS/TS
grep_search "nomeMetodo("              # Java/C#/TS (invocação)

# Endpoint de API
grep_search "@GetMapping(\"/endpoint\")"   # Spring Boot
grep_search "router.get('/endpoint'"        # Express
grep_search "path: '/endpoint'"             # Angular routes

# String de erro literal
grep_search "\"mensagem de erro exata\""

# Import/dependency
grep_search "import.*NomeDoModulo"
grep_search "from.*nome-pacote"

# Anotação/decorator
grep_search "@NomeAnnotation"
grep_search "@Component\|@Service\|@Injectable"
```

### Busca Semântica — padrões para conceitos

```bash
# Conceito de negócio (não literal)
grep_search "validacao cpf"           # sem quotes — mais tolerante
grep_search "calcular desconto"
grep_search "enviar notificacao"

# Comportamento esperado
grep_search "retry backoff"
grep_search "autenticacao oauth"
grep_search "paginacao cursor"
```

### Estratégia de refinamento progressivo

```
1. Busca ampla → muitos resultados → refinar com grep mais específico
2. Busca específica → 0 resultados → ampliar com termos relacionados
3. Ainda 0 resultados → file_search por nome de arquivo (padrão de nomenclatura)
4. Ainda 0 resultados → ask_questions para obter mais contexto
```

---

## 4) Fase 3: Traçar Call Chain

Após localizar o ponto de origem, traçar **quem chama** e **o que é chamado**.

### Traçar callers (quem invoca este método/classe)

```bash
# Quem usa esta classe
grep_search "NomeDaClasse"     # encontra instanciações e imports

# Quem chama este método
grep_search "nomeDoMetodo("    # padrão de invocação

# Quem importa este módulo
grep_search "import.*NomeDaClasse"
grep_search "from.*arquivo-fonte"

# Quem injeta esta dependência (Spring/Angular)
grep_search "NomeDaClasse service"
grep_search "private.*NomeDaClasse"
```

### Traçar callees (o que este método usa)

```
1. Ler apenas o método específico (não o arquivo todo)
2. Identificar dependências diretas (chamadas de método, serviços injetados)
3. Para cada dependência crítica: repetir Fase 2 recursivamente (máx. 2 níveis)
```

### Limite de profundidade de tracing

| Nível | Ação |
|---|---|
| Nível 0 | Ponto de origem do sintoma |
| Nível 1 | Callers diretos + callees diretos do nível 0 |
| Nível 2 | Callers/callees do nível 1 (apenas se ainda não encontrou causa raiz) |
| Nível 3+ | PARAR — reportar hipótese parcial e pedir confirmação |

---

## 5) Fase 4: Confirmar — Leitura Cirúrgica

**Nunca ler o arquivo inteiro**. Ler apenas o trecho relevante.

### Estratégia de leitura mínima

```
1. grep_search para encontrar a linha exata
2. read_file com offset=<linha-5> e limit=30
   → ler ±15 linhas em torno do ponto de interesse
3. Se contexto insuficiente: expandir limit para 60
4. Nunca ler mais de 100 linhas por chamada de read_file
```

### Quando usar ctx_execute_file vs read_file

| Situação | Ferramenta |
|---|---|
| Ler trecho específico (offset/limit conhecido) | `read_file` com offset + limit |
| Contar ocorrências, parsear estrutura do arquivo | `ctx_execute_file` |
| Arquivo > 500 linhas, procurar padrão | `ctx_execute_file` com grep interno |
| Arquivo pequeno (<100 linhas), ler inteiro | `read_file` sem limit |

---

## 6) Fase 5: Evidenciar

Toda investigação deve produzir evidências no formato:

```markdown
## Evidências de Rastreio

| Tipo | Localização | Detalhe |
|---|---|---|
| Classe origem | `src/modulo/Classe.java:42` | `method processarPagamento()` |
| Caller nível 1 | `src/controller/Controller.java:87` | Invoca `Classe.processarPagamento()` |
| Dependência | `src/repo/Repository.java:15` | Injetada via construtor |
| Endpoint | `src/controller/Controller.java:80` | `@PostMapping("/pagamento")` |
| String de erro | `src/modulo/Classe.java:55` | `throw new BusinessException("saldo insuficiente")` |

Causa raiz hipotética: `Classe.processarPagamento():55` — condição de guarda ausente antes de debitar saldo
Confiança: Alta (evidências em 3 pontos independentes)
```

---

## 7) Stack Trace Parsing

Quando há um stack trace disponível, seguir este protocolo:

### Estrutura de parsing

```
1. Identificar o frame mais próximo do código-fonte do projeto
   → ignorar frames de frameworks (spring, angular, node internals)
   → focar nos frames com pacote/namespace do projeto

2. Extrair: arquivo + linha do frame de projeto mais alto
   → este é o ponto de entrada na investigação

3. Se stack trace é de frontend minificado:
   → buscar source maps (.map) em dist/ ou build/
   → mapear frame ofuscado para linha original

4. Se stack trace inclui trace ID (distributed tracing):
   → usar o trace ID para correlacionar spans
   → identificar serviço de origem da chamada
```

### Padrão de frame por linguagem

| Linguagem | Formato do frame | O que extrair |
|---|---|---|
| Java | `at com.empresa.Classe.metodo(Arquivo.java:42)` | Classe + método + linha |
| Python | `File "src/modulo.py", line 87, in funcao` | Arquivo + linha + função |
| TypeScript/JS | `at ClasseOuFuncao (arquivo.ts:42:10)` | Arquivo + linha |
| C# | `at Namespace.Classe.Metodo() in Arquivo.cs:line 42` | Namespace + linha |

---

## 8) Rastreio de API / Endpoint

Para sintomas originados em chamadas de API:

```bash
# 1. Localizar o handler pelo path
grep_search "'/api/endpoint'"
grep_search "\"/api/endpoint\""
grep_search "@RequestMapping.*endpoint"

# 2. Localizar o service chamado pelo handler
grep_search "NomeDoService"   # dentro do controller encontrado

# 3. Localizar o repositório/client chamado pelo service
grep_search "NomeDoRepository\|NomeDoClient"

# 4. Para APIs externas — localizar a configuração
grep_search "http://\|https://"
grep_search "baseUrl\|apiUrl\|API_URL"
grep_search "HttpClient\|axios\|fetch"
```

---

## 9) Classificação de Confiança da Hipótese

Após o rastreio, classificar a confiança da hipótese de causa raiz:

| Nível | Critério | Ação |
|---|---|---|
| **Alta** (>80%) | ≥3 evidências independentes apontando para o mesmo ponto | Propor plano de correção direto |
| **Média** (50-80%) | 1-2 evidências, padrão parcial ou hipótese plausível | Propor hipótese + pedir confirmação |
| **Baixa** (<50%) | Evidências ambíguas ou contraditórias | `ask_questions` para mais contexto antes de prosseguir |

---

## 10) Anti-padrões de Tracing

- ❌ Ler arquivos inteiros quando grep já localizou a linha.
- ❌ Fazer `grep_search` com termos genéricos demais (`class`, `function`, `error`) — sempre adicionar contexto.
- ❌ Parar no primeiro resultado sem verificar se é realmente o código executado (pode ser teste ou mock).
- ❌ Assumir causa raiz sem evidências em ≥2 pontos do código.
- ❌ Traçar mais de 2 níveis de call chain sem reportar hipótese parcial — risco de loop.
- ❌ Ignorar frames de projeto no stack trace em favor de frames de framework.

---

## 11) Referências

- CodeQL Call Graph: https://codeql.github.com/docs/codeql-language-guides/navigating-the-call-graph
- Semantic Code Search vs Grep: https://particula.tech/blog/semantic-code-search-vs-grep-coding-agents
- LLM-Guided Code Navigation: https://arxiv.org/html/2506.18191v1
- Stack Trace Study (multi-language): https://github.com/tintin10q/stack-trace-study
- Skill `terminal-governance` — para comandos grep no terminal com output truncado

