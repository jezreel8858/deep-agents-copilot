# Referência do Diretório de Quarentena Sintética (`.github/agents/evals/synthetic/`)

Este documento descreve a estrutura, os artefatos, o contrato de curadoria humana e as invariantes de segurança da pasta `.github/agents/evals/synthetic/`.

## Propósito do Diretório

A pasta `.github/agents/evals/synthetic/` atua como zona isolada de **quarentena (Silver Dataset)** e de **candidatos de promoção** do pipeline de avaliação sintética do `@agent-router` (`tools/headless-governance-runner`):

- **Quarentena Silver Dataset (`casos-roteamento-silver-<AAAAMMDD-HHMMSS>.yaml`)**: arquivos gerados por `governance-runner --mode synth-export` (ou `--use-case synth-export`) contendo casos sintéticos nos quais a avaliação cega (`synth-eval`) detectou falha (`verdict: mismatch` / `unparseable`) ou proximidade de fronteira (`--include-near-boundary`).
- **Candidatos de Promoção (`promoted-<run_id>.yaml`)**: arquivos gerados por `governance-runner --mode synth-promote` (ou `--use-case synth-promote`) contendo exclusivamente os casos aprovados na curadoria humana e re-deduplicados em modo somente-leitura contra o Golden Set (`.github/agents/evals/casos-roteamento.yaml`).

| Padrão de Arquivo | Comando Gerador | Status de Curadoria | Papel na Governança |
|---|---|---|---|
| `casos-roteamento-silver-<AAAAMMDD-HHMMSS>.yaml` | `governance-runner --mode synth-export` | `pending` → `approved` / `rejected` | Quarentena **Silver Dataset** para revisão humana de divergências do roteador. |
| `promoted-<run_id>.yaml` | `governance-runner --mode synth-promote` | `approved` (re-deduplicado) | Artefato candidato pronto para cópia e inclusão manual via Pull Request no Golden Set. |
| `.github/agents/evals/casos-roteamento.yaml` | Curadoria humana via Pull Request | Canônico (Golden Set) | Fonte da verdade imutável em execução automática (contagens fixas `45/5/35/4`). |
| `.cache/routing_synth_history.db` | `synth-generate` / `synth-eval` / `synth-export` / `synth-promote` | Histórico operacional SQLite | Base local efêmera de execuções e deduplicação (nunca versionada no Git). |

## Contrato do Fluxo de Curadoria Humana

A promoção de um caso sintético para o Golden Set segue quatro etapas determinísticas com revisão humana obrigatória:

| Etapa | Entrada | Ação / Critério | Saída |
|---|---|---|---|
| **1. Exportação Silver** | Banco SQLite (`--eval-run-id`) | Execução de `governance-runner --mode synth-export` (default `--only-failures`) | `.github/agents/evals/synthetic/casos-roteamento-silver-<AAAAMMDD-HHMMSS>.yaml` |
| **2. Revisão Humana** | `casos-roteamento-silver-<AAAAMMDD-HHMMSS>.yaml` | Definir `curation_status: approved` (ou `review.status: approved`) e preencher `corrected_route` (ou `review.corrected_route`) | Arquivo Silver revisado e salvo em `.github/agents/evals/synthetic/` |
| **3. Geração de Candidato** | Arquivo Silver revisado + `--confirm` | Execução de `governance-runner --mode synth-promote` com re-dedup read-only contra o Golden Set | `.github/agents/evals/synthetic/promoted-<run_id>.yaml` |
| **4. Promoção ao Golden Set** | `promoted-<run_id>.yaml` | Inclusão manual via Pull Request em `.github/agents/evals/casos-roteamento.yaml` | Pull Request auditável preservando ou atualizando deliberadamente o Golden Set |

### Campos de Revisão no Arquivo Silver

Cada item exportado em `cases` no arquivo Silver possui os campos de curadoria avaliados pelo comando `synth-promote`:

- `curation_status` / `review.status`: estado da triagem humana (`pending` por padrão; deve ser alterado para `approved` para habilitar a promoção do item).
- `corrected_route` / `review.corrected_route`: rota canônica validada pelo revisor humano (obrigatória quando o status for `approved`).
- `review.reviewer` e `review.notes`: identificação opcional do revisor e justificativa técnica da decisão.

## Invariantes de Segurança e Isolamento

| Invariante | Descrição Técnica |
|---|---|
| **Golden Set Estritamente Read-Only (`CA-01`)** | O arquivo `.github/agents/evals/casos-roteamento.yaml` nunca é sobrescrito ou aberto para escrita pelos comandos `synth-*` (`synth-generate`, `synth-eval`, `synth-export`, `synth-promote`). As contagens canônicas `45/5/35/4` permanecem intactas. |
| **Banco SQLite Nunca Versionado no Git** | O arquivo `.cache/routing_synth_history.db` (e seus artefatos `-wal` e `-shm`) é ignorado pelo `.gitignore` e nunca é versionado no Git. O runner bloqueia qualquer caminho `--db` localizado dentro de `.github/`. |
| **Confinamento de Caminho (`allow_root`) e Prefixos** | `synth-export` e `synth-promote` validam os caminhos com `Path.resolve()` restritos a `.github/agents/evals/synthetic/`. Tentativas de *path traversal* (`..`), uso de symlinks fora de `allow_root`, exportação com prefixo `promoted-*` ou promoção de arquivo sem prefixo `casos-roteamento-silver-*` resultam em erro imediato (exit code `2`). |
| **Isolamento Anti-Glob nos Loaders e Testes** | Nenhum loader ou glob em `tools/headless-governance-runner` ou `tests/` varre `.github/agents/evals/synthetic/*.yaml` ao carregar o Golden Set, garantindo que arquivos Silver e `promoted-<run_id>.yaml` não alterem as contagens `45/5/35/4`. |
