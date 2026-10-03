# Plano de Planejamento - Correcao de Falso Positivo no Hook Anti-Truncamento (CHANGELOG.md)

> Workflow: WORKFLOW-BUG-FIX | Etapa: 1/5 (Triagem concluida) -> 2/5 (@governance-maintainer)
> Autor da triagem: @bug-triage
> Status: Aprovado para implementacao (Challenge Gate C1/C2/C3 = SIM)

## 1. Sumario Executivo

O hook `.githooks/pre-commit` (bloco "Defesa Anti-Truncamento de Historico", linhas 110-122) bloqueia falsamente commits legitimos que inserem multiplas entradas novas de versao no `CHANGELOG.md` antes de um cabecalho pre-existente. A causa e uma heuristica de deteccao por `grep` sobre o diff textual unificado (linha unica `-## [...]`), que nao distingue remocao liquida de deslocamento posicional causado por insercao de conteudo precedente (artefato do algoritmo de Myers diff sem deteccao de movimentacao).

## 2. Classificacao

| Campo | Valor |
|---|---|
| Severidade | Alta |
| Categoria de falha | logic-error (falso positivo em heuristica textual) |
| Natureza | Comportamento nunca correto (nao e regressao) - introduzido no commit 0b9837e (2026-09-14) e nunca exercitado por este padrao de diff ate agora |
| Classificacao de escopo | Cirurgico (Verde) - 1 arquivo, bloco isolado, sem consumidores externos |
| Esforco estimado | 0.5h - 1h |
| Risco de regressao | Baixo (hook local, rollback trivial via git) |

## 3. Causa Raiz (RCA)

- Arquivo: `.githooks/pre-commit:115`
- Codigo atual:
```bash
deleted_headers=$(git diff --cached -- CHANGELOG.md | grep -E '^-##\s+\[' || true)
```
- Problema: captura qualquer linha removida `## [...]` no diff unificado, mesmo quando a mesma linha reaparece como adicionada (`+## [...]`) em outra posicao do mesmo diff - padrao tipico quando N >= 1 cabecalhos novos sao inseridos antes de um cabecalho ja existente no mesmo commit.
- Evidencia de validacao (multiset HEAD vs. staged):
  - `git show HEAD:CHANGELOG.md` -> topo: `## [2.51.5]`, `## [2.51.4]`, `## [2.51.3]`...
  - `git show :CHANGELOG.md` (staged) -> topo: `## [2.52.4]`, `## [2.52.3]`, `## [2.52.2]`, `## [2.52.1]`, `## [2.52.0]`, `## [2.51.5]` (presente), `## [2.51.4]`...
  - Todos os cabecalhos de HEAD estao presentes no conjunto staged -> falso positivo confirmado.

## 4. Blast Radius

- Arquivo unico a alterar: `.githooks/pre-commit` (linhas 114-122).
- Varredura de padrao similar (R-055 Anti-Silo Fix): executada contra `.githooks/*`, `tools/*.sh`, `.github/workflows/*.yml|*.yaml` com `grep 'diff --cached'` combinado a remocao (`^-`). Resultado: nenhum outro script replica o padrao ingenuo de diff-grep de linha unica para deteccao de remocao. As demais 7 verificacoes do mesmo hook (linhas 22, 23, 32, 39, 54, 58, 102) usam `--name-only` ou checam adicoes (`^+`), padrao estruturalmente diferente e nao afetado por este bug.
- Consumidores: nenhum script ou pipeline de CI consome `.githooks/pre-commit` programaticamente (hook local, nao versionado em `.github/workflows/`). Consumidor de fato e o fluxo humano de commit.
- Classificacao: Verde (Cirurgico) - confirmado via Challenge Gate C1.

## 5. Estrategia de Correcao Aprovada (Challenge Gate C2)

Substituir a heuristica de diff textual por comparacao de multiset de cabecalhos:

1. Extrair todos os cabecalhos `## [...]` de `git show HEAD:CHANGELOG.md`.
2. Extrair todos os cabecalhos `## [...]` de `git show :CHANGELOG.md` (versao staged/indice).
3. Bloquear apenas se algum cabecalho presente no conjunto de HEAD estiver ausente no conjunto staged (remocao liquida real) - independente de reordenacao/deslocamento posicional.
4. Mantem o contrato original (zero tolerancia a remocao real de versao historica - Challenge Gate C3: remocoes corretivas/intencionais continuam bloqueadas e exigem bypass manual documentado, sem caminho de excecao automatico no hook).

## 6. Plano de Rollback

Hook e artefato local, nao versionado em runtime critico (apenas pre-commit local via `core.hooksPath .githooks`). Rollback imediato e de baixissimo risco:
```bash
git checkout 0b9837e~1 -- .githooks/pre-commit
# ou, apos a correcao ser commitada:
git revert <commit-da-correcao> --no-commit -- .githooks/pre-commit
```

## 7. Safety Net / Testes Recomendados (para a etapa de implementacao)

- [ ] Teste de caracterizacao: commit sintetico que insere N >= 1 cabecalhos novos antes de um cabecalho existente -> deve passar (Green) apos a correcao.
- [ ] Teste de regressao: commit sintetico que remove deliberadamente um cabecalho historico sem readiciona-lo -> deve continuar bloqueando (Red -> bloqueio mantido).
- [ ] Teste de nao-regressao das demais 7 verificacoes do mesmo hook (linhas 22-113) - devem permanecer inalteradas e passando.

## 8. Proximos Passos (Workflow)

1. [OK] Etapa 1/5 - Triagem (@bug-triage) - concluida, aprovada via Challenge Gate.
2. Etapa 2/5 - @governance-maintainer: validar aderencia a R-043/R-044 e governanca do hook.
3. Etapa 3/5 - <stack>-arch-advisor correspondente (shell/governance): autoria tecnica do plano de implementacao formal, se exigido pelo workflow.
4. Etapa 4/5 - Implementacao (Red Test -> Correcao Cirurgica -> Green) via @agent-router.
5. Etapa 5/5 - Validacao de nao-regressao e fechamento.

## 9. Decisoes do Challenge Gate (registro)

| Pergunta | Resposta |
|---|---|
| C1 - Blast radius contido a .githooks/pre-commit:114-122? | Sim, confirmado |
| C2 - Aprova correcao pontual via comparacao de multiset? | Sim, aprovo |
| C3 - Manter zero tolerancia a remocao real (override manual)? | Sim, manter zero tolerancia |
| Aprovacao final do plano | Sim, gerar e prosseguir |
