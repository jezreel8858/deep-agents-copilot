# Formatos de Commit (Nível 3 — git-governance)

> Referência carregada sob demanda por `/commit` e `@pr-gatekeeper`. Índice: `../SKILL.md`.

## 1) Regras Gerais

- Título: `<tipo>(<escopo>): <resumo>` — imperativo PT-BR, sem ponto final, ≤ 72 colunas.
- Corpo com wrap ≤ 72 colunas; explica o **porquê**, não só o quê.
- Escopo: substantivo kebab-case (módulo/domínio/camada). Ex.: `auth`, `deps`, `governance`.
- Breaking change: `!` no título **ou** trailer `BREAKING CHANGE:` — nunca ambos.

## 2) Tipos Válidos

| Tipo | Quando usar | SemVer |
|---|---|---|
| `feat` | Nova funcionalidade | MINOR |
| `fix` | Correção de bug | PATCH |
| `refactor` | Reestruturação sem mudar comportamento | — |
| `test` | Testes (add/corrige/remove) | — |
| `docs` | Somente documentação | — |
| `chore` | Manutenção sem impacto funcional | — |
| `perf` | Otimização mensurável | PATCH |
| `build` | Build/dependências (`pom.xml`, `package.json`, `Dockerfile`) | — |
| `ci` | Pipelines (`.github/workflows`) | — |
| `style` | Formatação pura | — |
| `revert` | Reversão de commit | — |
| `wip` | Progresso parcial (nunca mergear em branch principal) | — |

### Classificação de Exclusões

| Situação | Tipo |
|---|---|
| Classe/componente substituído (decomposição) | `refactor` |
| Código morto/órfão sem chamadores | `chore` |
| Teste obsoleto/duplicado | `test` |
| Configuração obsoleta | `chore` |
| Remoção de feature com quebra de contrato | `feat` + `BREAKING CHANGE` |

## 3) Atomicidade (Teste do "e")

Se a descrição exigir conectar intenções distintas com "e"/"também", o commit é não-atômico. Dividir quando houver:

- Backend e frontend em projetos separados (uma mensagem por projeto).
- Schema/migration vs. regra de negócio vs. UI.
- Refatoração prévia vs. feature que a consome.
- Hotfix urgente vs. feature em andamento.

Ação: sugerir split via `git add -p` (execução sempre manual — R-031).

## 4) Formato A — Simples (1 a 5 arquivos)

```text
<tipo>(<escopo>): <resumo curto no imperativo>

- Narrativa sucinta do que foi feito e da motivação.

Arquivos adicionados:
- caminho/Arquivo.ts — responsabilidade.

Arquivos modificados:
- caminho/Arquivo.ts — o que mudou.

Arquivos removidos:
- caminho/Arquivo.ts — motivo e substituto.

Como validar:
- <comando executável>
```

Omitir listas vazias.

## 5) Formato B — Complexo (6+ arquivos ou múltiplas frentes)

```text
<tipo>(<escopo>): <resumo consolidado>

- Narrativa consolidada: o que o conjunto entrega e por quê.
- Referência a plano/ADR quando aplicável.

─── Novos arquivos ──────────────────────────────────────
  [Grupo Funcional A]
  - caminho/Arquivo.ts — responsabilidade

─── Arquivos modificados ────────────────────────────────
  [Grupo Funcional B]
  - caminho/Arquivo.ts — o que mudou e por quê

─── Arquivos removidos ──────────────────────────────────
  [Grupo Funcional C — motivo]
  - caminho/Arquivo.ts — motivo e substituto

─── Breaking changes ────────────────────────────────────
  (omitir se não houver)

Como validar:
- <comando da suíte/módulo>
```

## 6) "Como validar"

Obrigatório para `feat`, `fix`, `refactor`, `test`, `perf`. Para docs/chore puros: `N/A — alteração sem impacto em testes.`

| Stack | Comando |
|---|---|
| Java/Maven | `mvn -Dtest=ClasseTest test` |
| Python | `pytest tests/modulo -v` |
| Angular | `npm test` / `ng test --watch=false` |

## 7) Arquivos Removidos

Nunca listar remoção sem **motivo** e **substituto** (quando houver).

## 8) Trailers

Somente com dados reais:

```text
BREAKING CHANGE: <descrição>
Closes #123
Refs #456
Co-authored-by: Nome <email@exemplo.com>
```

## 9) Aplicação Manual

Entregar o comando via heredoc para preservar quebras de linha: `git commit -F - << 'EOF' ... EOF`. Agentes nunca o executam (R-031).
