# CHANGELOG — Keep a Changelog 1.1 (Nível 3 — git-governance)

## 1) Estrutura

```markdown
## [Unreleased]

## [X.Y.Z] - AAAA-MM-DD
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

Regras: mais recente primeiro; datas ISO 8601; links de comparação no rodapé; escrito para humanos (não despejar `git log`); versionamento SemVer 2.0.

## 2) Mapeamento Conventional Commits → Seção → SemVer

| Commit | Seção | Bump |
|---|---|---|
| `feat` | Added (ou Changed) | MINOR |
| `fix` | Fixed | PATCH |
| `fix` de vulnerabilidade | Security | PATCH |
| `perf`, `refactor` com efeito visível | Changed | PATCH |
| descontinuação anunciada | Deprecated | MINOR |
| remoção de feature | Removed | MAJOR se quebra contrato |
| `!` / `BREAKING CHANGE` | Changed/Removed + nota de migração | MAJOR |
| `docs`, `test`, `chore`, `style`, `ci`, `build` | omitir (salvo impacto ao usuário) | — |

## 3) Entrada Sugerida (bloco `diff`)

```diff
+ ## [X.Y.Z] - AAAA-MM-DD
+ ### Added
+ - <item voltado ao usuário>
```

Novas mudanças sem release vão em `[Unreleased]`.

## 4) Orçamento de Concisão e Anti-Bloat (Normativo)

- **Limite por bullet**: no máximo `<= 200 caracteres` por linha de bullet (`^- `).
- **Orçamento por release**: recomendação editorial de `6–8 bullets` e teto hard de `<= 12 bullets` por seção `## [X.Y.Z]`.
- **Formato orientado a valor (1 linha)**: `- **<Escopo curto>**: <efeito observável>.` (sem sub-bullets aninhados prolixos).
- **Proibições expressas**:
  - ❌ Listas exaustivas de `>= 4` arquivos, agents, skills ou funções de teste nominalmente enumeradas;
  - ❌ Métricas brutas efêmeras de suíte (ex.: `91/91 passed`, contagens de linhas ou hashes transitórios);
  - ❌ Narrativas de RCA (Root Cause Analysis), stack traces ou detalhes internos de implementação.
- **Exemplo Ruim vs. Bom**:
  - ❌ **Ruim (> 200 chars / RCA / lista exaustiva)**: `- **Correção no runner**: corrigido bug onde cli.py, evaluator.py, seeds.py e runner.py falhavam por causa de regex malformada na linha 42 passando 91/91 testes em test_a.py, test_b.py, test_c.py e test_d.py.`
  - ✅ **Bom (<= 200 chars / orientado a valor)**: `- **Runner de avaliação (`headless-governance-runner`)**: estabilizado o parser de métricas e ampliada a cobertura de regressão da CLI.`

## 5) Política de Contenção de Tamanho e Gatilho de Rotação

- **Faixa operacional saudável**: `650–850 linhas` totais no `CHANGELOG.md`.
- **Limiar de alerta**: `900 linhas` (aciona compactação preventiva na release corrente).
- **Teto hard**: `<= 1.000 linhas` (invariante auditada pela suíte de integridade).
- **Procedimento de compactação automática in-place**: quando o `CHANGELOG.md` ultrapassar `900 linhas`, condensar semanticamente bullets antigos e achatar sub-bullets in-place para `<= 200 chars/bullet` e `<= 12 bullets/release`, **preservando 100% dos cabeçalhos `## [X.Y.Z]`** em ordem SemVer decrescente e todas as versões-âncora históricas.
