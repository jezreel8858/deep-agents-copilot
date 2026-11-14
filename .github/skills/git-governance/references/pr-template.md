# Template de PR (Nível 3 — git-governance)

> Padrão de mercado 2026. Índice: `../SKILL.md`. Matriz de risco: `risk-matrix.md`.

## 1) Título

Conventional Commits, imperativo PT-BR, ≤ 72 colunas. Ex.: `feat(auth): adiciona autenticação por token JWT`.

## 2) Template (emitir em bloco de 4 backticks `markdown`)

````markdown
## O que foi feito
- <item 1>
- <item 2>

## Tipo de mudança
- [ ] 🐛 Bug fix
- [ ] ✨ Nova feature
- [ ] ♻️ Refactor
- [ ] 📝 Documentação / Governança
- [ ] 🚀 Performance
- [ ] 🔧 Chore / Build / CI

## Matriz de Risco
| Área afetada | Risco | Mitigação |
|---|---|---|
| <área> | baixo/médio/alto | <mitigação> |

## Como validar
1. `pytest tests/modulo -v`
2. <verificação funcional>

## Plano de Rollback
- Estratégia: <revert do PR | feature flag off | redeploy da versão anterior>
- Passos: <comandos/ações>
- Impacto de dados: <migration reversível? sim/não + como>

## Checklist
- [ ] Code review aprovado
- [ ] Guardrail de segredos limpo
- [ ] Testes adicionados/atualizados e passando
- [ ] Documentação viva atualizada
- [ ] CHANGELOG.md atualizado
- [ ] Plano de Rollback preenchido
````

## 3) Regras

- **Plano de Rollback é obrigatório** em todo nível de detalhamento Padrão/Completo; risco Alto exige passos verificáveis.
- Em "Como validar", usar comandos inline (`comando`) para evitar conflito de cercas aninhadas.
- Avisos no topo quando aplicável:
  - `> ⚠️ **Aviso de Divergência**: Destino possui N commit(s) não incorporados à origem — recomenda-se rebase/merge.`
  - `> ℹ️ **Commits locais pendentes de push**: detectados commits ausentes em origin/<origem>.`
- Nível Mínimo: título + lista curta "O que foi feito" (rollback em uma linha).
