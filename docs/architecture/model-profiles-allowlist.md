# Arquitetura Técnica — Perfis de Modelos e Allowlist (D4')

Este documento descreve as decisões de arquitetura e o modelo formal de dados para o sistema de controle de custo de modelos de LLM em agents e prompts.

---

## 1. Contexto e Decisão Central (D4')

O repositório padroniza modelos nos frontmatters de `.github/agents/**/*.agent.md` e `.github/prompts/**/*.prompt.md`. Para suportar o controle de custo em ambientes locais sem degradar a estabilidade nem criar dependência de extensões exclusivas de uma única IDE:
- **Decisão D4':** Modificação **in-place visível no clone local**, restrita estritamente à linha `model:`.
- **Reversibilidade:** T2 com restore determinístico por linha baseado no hash do blob de HEAD (`git show HEAD:<path>`).
- **Alternativas descartadas:**
  - *skip-worktree:* Rejeitada por mascarar drifts, quebrar o `git stash` e inviabilizar pulls limpos.
  - *Diretórios de usuário exclusivos:* Rejeitada por falta de paridade entre VS Code, JetBrains e Copilot CLI.

---

## 2. Camadas de Resolução de Modelo (D2 e Precedência)

A resolução de modelo para qualquer agent ou prompt obedece à seguinte ordem estrita de precedência:
```text
agents / prompts (override explícito)
        │
        ▼
tiers (tier_map de model-profiles.yaml)
        │
        ▼
extends (herança de perfil base)
        │
        ▼
default (perfil padrão canônico)
```

- **Detecção de Ciclos:** Qualquer herança circular em `extends` é detectada de forma determinística antes de qualquer aplicação.
- **Validação de Chaves:** Chaves duplicadas em arquivos YAML disparam erro imediato no loader (`safe_load_yaml_unique`).

---

## 3. Hierarquia de Custo (D6)

- Em qualquer grafo de delegação derivado de `routing-graph.yaml`, um subagente não pode utilizar um modelo com custo superior ao do agente pai.
- Rebaixamentos nos perfis `balanceado` ou `economico` propagam-se em cascata para os roteadores e orquestradores quando aplicável, respeitando `model_exception_reason`.

---

## 4. Allowlist de Modelos em 3 Camadas (D8)

1. **Allowlist Estática Versionada (`model-allowlist.yaml`):** Fonte canônica declarativa contendo o catálogo de modelos homologados, provedores (`anthropic`, `google`, `openai`, `xai`, `github`), faixas de custo (`cost_rank`) e flag `pinnable`.
2. **Job Agendado de Atualização (`.github/workflows/model-allowlist-refresh.yml`):** Execução periódica (cron semanal / dispatch manual) para verificar aposentadorias (`retirement_date`) e atualizações de catálogo.
3. **Auditoria de Frescor:** Modelos cujo `verified_at` exceda 30 dias acionam avisos na suíte de testes de governança, garantindo manutenção contínua sem quebrar builds.

---

## 5. Garantias de Integridade e Proteção contra Vazamento

- **Proteção do Catálogo Canônico:** `catalog.yaml` e `routing-graph.yaml` nunca são modificados pelo sistema de perfis locais.
- **Pre-commit Guard:** `.githooks/pre-commit` impede commits de arquivos staged contendo linhas `model:` divergentes do default ou com perfil ativo.
- **CI Parity Guard:** O workflow `routing-quality-gate.yml` executa os testes de paridade (`test_model_profiles_parity.py`) e allowlist (`test_model_allowlist_governance.py`) em todo PR e push.
