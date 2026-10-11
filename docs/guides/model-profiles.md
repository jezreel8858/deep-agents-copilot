# Guia de Uso — Perfis de Modelos (model-profiles) e Allowlist

Este guia orienta desenvolvedores sobre como alternar o consumo de modelos LLM em agents (`.agent.md`) e prompts (`.prompt.md`) entre perfis pré-definidos (`default`, `economico`, `balanceado`) ou customizados, mantendo a governança do repositório íntegra e sem risco de vazamento de dados locais ou edições indesejadas em commits.

---

## 1. Visão Geral e Conceitos

- **Fonte Canônica Única:** `model-profiles.yaml` define os tiers e os perfis pré-definidos versionados no repositório.
- **Overlay Local (R-043):** `model-profiles.local.yaml` (gitignored) permite definir perfis personalizados sem poluir o repositório compartilhado.
- **In-Place Seguro (Decisão D4'):** As variantes são aplicadas diretamente no clone local, alterando **exclusivamente a linha `model:`** no frontmatter dos arquivos alvo. O corpo, instruções e metadados de governança permanecem intactos.
- **Allowlist Governada:** Todo modelo deve constar em `model-allowlist.yaml` com status `pinnable: true`. Modelos com mais de 30 dias de verificação emitem alertas de frescor.

---

## 2. Perfis Disponíveis

| Perfil | Objetivo | Principais Modelos Mapeados |
|---|---|---|
| `default` | Padrão canônico do repositório | Claude Opus 5.5 (arquitetura/debug complexo), Claude Sonnet 5.5 (routers/desenvolvedores), Gemini 3.8 Flash (operacionais/testes) |
| `balanceado` | Relação equilibrada custo x raciocínio | Claude Sonnet 5.5 (orquestração), Gemini 3.8 Flash (tarefas analíticas e operacionais) |
| `economico` | Redução máxima de consumo/créditos | Claude Haiku 5.5 (orquestração e standard), Gemini 3.8 Flash (tarefas leves) |

> ⚠️ **Aviso de Perda de Qualidade (D5):** Perfis rebaixados (`balanceado`, `economico`) reduzem significativamente a capacidade de raciocínio lógico em decomposições arquiteturais complexas, refatorações multi-arquivo e diagnósticos de erros sutis. Ao aplicar um perfil econômico, esteja ciente de que agents de arquitetura e planejamento operarão com capacidade analítica reduzida.

---

## 3. Comandos Principais (`tools.model_profiles`)

O gerador opera via CLI em módulo Python:

```bash
# 1. Listar perfis disponíveis (built-in e locais)
python -m tools.model_profiles list

# 2. Verificar status atual do repositório (perfil ativo, alvos modificados, drift)
python -m tools.model_profiles status

# 3. Aplicar um perfil no clone local
python -m tools.model_profiles apply economico
# (exibe resumo, aviso de qualidade e requer confirmação antes de gravar)

# 4. Restaurar o perfil padrão canônico (default)
python -m tools.model_profiles restore

# 5. Inicializar arquivo de perfil local (cria model-profiles.local.yaml a partir do exemplo)
python -m tools.model_profiles init

# 6. Diagnóstico de integridade, lock, hooks e permissões
python -m tools.model_profiles doctor
```

---

## 4. Limitações de IDE e Passo Obrigatório pós-Troca (D7)

O Copilot e a IDE realizam cache em memória dos frontmatters de agents e prompts carregados no início da sessão.

Ao executar `apply` ou `restore`:
1. **VS Code:** Abra a Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) e execute:
   ```text
   Developer: Reload Window
   ```
   Ou inicie uma nova janela / thread de Chat.
2. **JetBrains:** Feche e reabra o painel do GitHub Copilot Chat (ou reinicie a IDE se o modelo não atualizar no seletor).
3. **Copilot CLI (Risco Residual RR2):** O Copilot CLI executado dentro do mesmo clone utilizará a variante configurada no arquivo enquanto o perfil estiver ativo.

---

## 5. Fluxo de Git Seguro (`suspend → pull → resume`)

Como as variantes são gravadas in-place no clone local, o Git impedirá `git pull`, `git merge` ou `git rebase` se os arquivos estiverem modificados no working tree.

**Fluxo recomendado:**
```bash
# 1. Suspender temporariamente o perfil ativo (reverte working tree para HEAD)
python -m tools.model_profiles suspend

# 2. Atualizar o repositório
git pull --rebase origin main

# 3. Reativar o perfil que estava em uso
python -m tools.model_profiles resume
```

---

## 6. Proibição Estrita de `skip-worktree`

É **estritamente proibido** utilizar `git update-index --skip-worktree` ou `--assume-unchanged` para ocultar alterações de `model:`.
- **Motivo:** O `skip-worktree` mascara drifts, é ignorado por `git stash`, gera conflitos opacos de sobrescrita silenciosa durante rebase e deixa o repositório em estado inconsistente em caso de crash.
- O projeto adota **in-place visível com restore garantido** via `.model-profiles/state.json` e journal write-ahead.

---

## 7. Rollback de Emergência

Caso ocorra interrupção de processo, crash da máquina ou estado inconsistente:
```bash
# Opção A (Automática via ferramenta):
python -m tools.model_profiles doctor --repair

# Opção B (Garantia do Git para arquivos de governança):
git checkout -- .github/agents .github/prompts
python -m tools.model_profiles restore --force
```

---

## 8. Defesa Contra Vazamento em Commits (Pre-Commit e CI)

Para evitar que variantes locais sejam commitadas por acidente no repositório compartilhado:
1. **Guard de Pre-Commit (`.githooks/pre-commit`):**
   - Aborta o commit se `.model-profiles/state.json` indicar perfil ativo e houver alterações em `model:`.
   - Bloqueia qualquer alteração em `model:` que não inclua a atualização correspondente de `model-profiles.yaml` no mesmo commit.
2. **Escape Controlado:**
   - Para mudanças canônicas intencionais nos modelos do repositório, faça o commit conjunto alterando `model-profiles.yaml`.
   - Em caso de necessidade emergencial, o bypass do hook pode ser feito via `git commit --no-verify`.
3. **Guard de CI (`routing-quality-gate.yml`):**
   - O CI executa a checagem de paridade e allowlist (`test_model_profiles_parity.py` e `test_model_allowlist_governance.py`). Se qualquer variante in-place ou modelo fora da allowlist vazar para o PR, o pipeline falhará imediatamente.
