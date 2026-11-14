# Code Tracing — Busca, Stack Trace e Rastreio de API (Detalhes)

> Referência detalhada (lazy) extraída de `code-tracing/SKILL.md` (R-066).

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

