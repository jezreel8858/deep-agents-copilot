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
