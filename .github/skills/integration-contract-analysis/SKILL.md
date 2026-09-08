---
name: integration-contract-analysis
description: >-
  Análise e validação de contratos de integração (OpenAPI, AsyncAPI, gRPC, GraphQL):
  detecção de breaking changes, classificação BREAKING/COMPATIBLE/DEPRECIAÇÃO e
  mapeamento de consumidores afetados.
tier: 2
category: governance
triggers:
  - "Verificar se uma mudança de API é breaking change"
  - "Comparar versões de contrato OpenAPI ou AsyncAPI"
  - "Identificar consumidores afetados por mudança de endpoint"
  - "Validar compatibilidade retroativa de contrato gRPC ou GraphQL"
  - "Antes de fazer merge de PR que altera contrato público"
  - "Auditar drift entre contrato spec e comportamento real da API"
tools:
  - grep_search
  - file_search
  - read_file
  - context-mode/ctx_batch_execute
  - context-mode/ctx_execute
source_docs:
  - "CLAUDE.md"
  - ".github/copilot-instructions.md"
  - ".github/agents/tech-solution-architect.agent.md"
---

# Skill: Análise de Contrato de Integração

> Detecção de breaking changes, classificação de compatibilidade e rastreamento de consumidores afetados para qualquer formato de contrato de integração.

## Quando Usar

- Mudança em endpoint, campo, tipo ou status code de API REST (OpenAPI 3.x).
- Alteração em evento, canal ou schema de mensageria (AsyncAPI 2.x/3.x).
- Mudança em método, mensagem ou enum de serviço gRPC (Protocol Buffers).
- Alteração em tipo, campo ou resolver de API GraphQL.
- Validação pré-merge de PR que toca contratos públicos.
- Auditoria de drift entre spec declarado e comportamento implementado.

## Taxonomia de Mudanças

| Classificação | Definição | Exemplos |
|---|---|---|
| **BREAKING** | Quebra consumidores existentes sem ação deles | Remover endpoint, tornar campo obrigatório, mudar tipo, alterar status code de sucesso |
| **COMPATIBLE** | Retrocompatível — consumidores existentes não precisam mudar | Adicionar campo opcional, novo endpoint, adicionar enum value |
| **DEPRECIAÇÃO** | Aviso de remoção futura — janela de migração obrigatória | `deprecated: true` em OpenAPI, comentário `@deprecated` em proto |

## Protocolo de Análise (5 Passos)

**1. Localizar specs de contrato**

```
# Localizar OpenAPI/AsyncAPI
grep -r "openapi:" --include="*.yaml" --include="*.yml" -l
grep -r "asyncapi:" --include="*.yaml" --include="*.yml" -l
# Localizar protos
find . -name "*.proto" -not -path "*/node_modules/*"
# Localizar schemas GraphQL
find . -name "*.graphql" -o -name "schema.gql"
```

**2. Identificar mudanças (diff estrutural)**

- Comparar versão anterior vs atual do contrato (git diff ou leitura dos dois arquivos).
- Listar cada mudança individualmente: campo, tipo, cardinalidade, status code.

**3. Classificar cada mudança (BREAKING / COMPATIBLE / DEPRECIAÇÃO)**

- Aplicar taxonomia acima por mudança.
- Mudanças combinadas: classificar pelo impacto maior.

**4. Rastrear consumidores afetados**

```
# Grep por clients que usam o endpoint/método afetado
grep -r "ENDPOINT_PATH" --include="*.ts" --include="*.java" --include="*.py" -l
grep -r "METHOD_NAME" --include="*.proto" --include="*.ts" -l
```

**5. Emitir matriz de impacto**

| Mudança | Tipo | Classificação | Consumidores Afetados | Ação Recomendada |
|---|---|---|---|---|
| `DELETE /resource/{id}` | Remoção de endpoint | BREAKING | `service-a`, `service-b` | Manter versão legada + deprecar |
| `campo_novo: string?` | Adição opcional | COMPATIBLE | — | Nenhuma |
| `status: enum` (novo valor) | Extensão de enum | COMPATIBLE* | Verificar `switch` sem default | Adicionar `default` nos consumers |

> *Adição de enum value é COMPATIBLE em specs, mas pode ser BREAKING em consumers com `switch` sem default.

## Checklist por Formato

### OpenAPI 3.x

- [ ] Endpoints removidos ou com path alterado → BREAKING
- [ ] Parâmetros obrigatórios adicionados → BREAKING
- [ ] Tipos de campo alterados (string→integer) → BREAKING
- [ ] Status codes de sucesso alterados (200→201) → verificar consumers
- [ ] Campos opcionais adicionados → COMPATIBLE
- [ ] Novos endpoints → COMPATIBLE
- [ ] `deprecated: true` declarado com `x-sunset-date` → DEPRECIAÇÃO

### AsyncAPI 2.x/3.x

- [ ] Canal removido ou renomeado → BREAKING
- [ ] Schema de mensagem com campos obrigatórios adicionados → BREAKING
- [ ] Protocolo alterado (mqtt→amqp) → BREAKING
- [ ] Canal novo → COMPATIBLE
- [ ] Campo opcional adicionado no payload → COMPATIBLE

### gRPC (Protocol Buffers)

- [ ] Campo removido (por número de field) → BREAKING
- [ ] Tipo de campo alterado → BREAKING
- [ ] Método RPC removido → BREAKING
- [ ] Campo `reserved` sem documentação de migração → BREAKING
- [ ] Novo campo com número novo → COMPATIBLE
- [ ] Novo RPC → COMPATIBLE

### GraphQL

- [ ] Tipo removido ou renomeado → BREAKING
- [ ] Campo não-nullable adicionado → BREAKING
- [ ] Argumento obrigatório adicionado → BREAKING
- [ ] Campo opcional adicionado → COMPATIBLE
- [ ] Novo tipo → COMPATIBLE
- [ ] `@deprecated` declarado → DEPRECIAÇÃO

## Saída Esperada

```markdown
### Análise de Contrato — <nome-do-serviço> v<anterior> → v<nova>

**Classificação geral:** BREAKING | COMPATIBLE | DEPRECIAÇÃO

| # | Mudança | Localização | Classificação | Consumidores Afetados |
|---|---|---|---|---|
| 1 | ... | ... | BREAKING | service-x |
| 2 | ... | ... | COMPATIBLE | — |

**Ação recomendada:** <versionamento / janela de migração / nenhuma>
**Evidências:** <caminhos dos arquivos de spec e consumers>
```

## Referências

- OpenAPI Breaking Changes: https://www.openapis.org/blog/2021/02/16/migrating-from-openapi-3-0-to-3-1-0
- AsyncAPI Migration Guide: https://www.asyncapi.com/docs/migration/migrating-to-v3
- Protocol Buffers Compatibility: https://protobuf.dev/programming-guides/dos-donts/
- GraphQL Breaking Changes: https://graphql.org/learn/best-practices/#versioning

