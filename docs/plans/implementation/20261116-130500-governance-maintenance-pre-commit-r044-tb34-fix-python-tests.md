---
status: "APPROVED"
approved: true
reviewer: "@plan-critic"
review_verdict: "PASS_WITH_NITS"
review_rounds: 2
review_tier1: "PASS"
author: "@python-arch-advisor"
plan_type: "implementation"
created_at: "2026-11-16T13:05:00Z"
allowed_files:
  - "tests/governance_audit/test_local_project_isolation.py"
  - "tests/governance_audit/test_synth_waves_prompt.py"
  - "tests/governance_audit/test_model_profiles_parity.py"
rollback_plan: "Snapshot prévio em tmp/pre-commit-py-snapshot/ e reversão atômica não-destrutiva via git diff -- tests/governance_audit/test_local_project_isolation.py tests/governance_audit/test_synth_waves_prompt.py tests/governance_audit/test_model_profiles_parity.py > tmp/pre-commit-py-delta.patch seguido de git apply -R tmp/pre-commit-py-delta.patch (sem uso de git checkout -- ou git reset --hard)."
tier: "light"
plan_ref: "docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md"
lessons_extracted: true
lessons_applied_to: ["plan-conformance-patterns"]
lessons_at: "2026-11-16"
related-planning-doc: "docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md"
session_id: "sess-20261116-eval-workflows-gov"
workflow_id: "WORKFLOW-GOVERNANCE-MAINTENANCE"
workflow_trace_id: "wt-20261116-eval-workflows-gov-01"
parent_plan_ref: "docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md"
critic_rubric_gaps: []
critic_findings_summary:
  rounds: 2
  blockers: 0
  majors: 0
  minors: 0
  nits: 0
  last_verdict: "PASS_WITH_NITS"
  author_ref: "@python-arch-advisor"
---

# Plano de Implementação (Gate 2 — Camada C Python Tests): Blindagem TDD para R-044 e TB-34 no Pre-Commit

## 1. Contexto e Escopo

Este plano de implementação detalha exclusivamente a **Camada C (Testes de Auditoria em Python / pytest)** derivada do plano de governança `docs/plans/governance/20261116-123000-pre-commit-r044-tb34-fix.md`, garantindo paridade estrita entre a suíte `pytest tests/governance_audit/` e os bloqueios estáticos do hook `.githooks/pre-commit` (R-044 de isolamento de caminhos locais e TB-34 de paridade/higienização da chave `model:` em agents e prompts).

### Diagnóstico de Evidências no Repositório (Inspeção Factual)

1. **Lacuna em `tests/governance_audit/test_local_project_isolation.py` (743 linhas)**:
   - Na seção `# 3. Detecção de Caminhos Absolutos de Máquina Local (R-044)` (linhas 206–241), a função `test_no_machine_specific_paths_in_tracked_files()` (linha 210) compila na linha 215 apenas `user_id_pattern` restrito ao prefixo `C:\\Users\\` (excluindo placeholders de usuário e perfis `Public`/`Default`).
   - Essa expressão não detecta caminhos no padrão `[LETRA_DRIVE]:\workspace` nem diretórios home Unix (`/home/...`, `/Users/...`), razão pela qual a suíte Python passava em falso-negativo enquanto `.githooks/pre-commit` (linha 58) barrava commits aplicando a regex `([A-Za-z]:\\(Users|workspace)|/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/)` sobre `.github/**`.
2. **Acoplamento a Caminho Local em `tests/governance_audit/test_synth_waves_prompt.py` (58 linhas)**:
   - A função `test_deve_exigir_cwd_explicito_e_resolucao_token_sdk()` (linhas 39–49, correspondente à Regra 3 do prompt `synth-waves.prompt.md`) aceita caminho absoluto literal de máquina Windows nas linhas 43–44 como alternativa a `${workspaceFolder}`, além de não auditar a ausência de matches da regex R-044 no arquivo `.github/prompts/synth-waves.prompt.md`.
   - *Nota de auditoria complementar sobre planos correlatos*: a inspeção de `docs/plans/implementation/20261116-120500-bug-fix-synth-waves-timeout.md` (linhas 33, 110 e 121) e `docs/plans/bug-triage/20261116-120000-bug-fix-synth-waves-timeout.md` (linha 39) confirmou que esses documentos contêm ocorrências literais do caminho de diretório de trabalho local da máquina (fora de `.github/**`, onde o hook `.githooks/pre-commit` L58 filtra apenas `^\.github/`, mas relevantes para higienização documental na Camada B).
3. **Lacuna de Paridade TB-34 em `tests/governance_audit/test_model_profiles_parity.py` (351 linhas)**:
   - O arquivo define `REPO_ROOT = Path(__file__).resolve().parents[2]` (linha 39), `PROFILES_PATH = REPO_ROOT / "model-profiles.yaml"` (linha 40), `AGENTS_DIR = REPO_ROOT / ".github" / "agents"` (linha 42) e `PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"` (linha 43).
   - Embora `test_default_profile_parity_with_frontmatters()` (linhas 86–109) compare o modelo extraído via `collect_repo_frontmatter_files(REPO_ROOT)` contra o perfil `default` resolvido (`resolve_profile("default", profiles)` e `resolve_target_model(key, tier, resolved_default)`), não há asserção explícita sobre a linha bruta `model:` do frontmatter garantindo que: (a) nenhum arquivo `.github/agents/*.agent.md` ou `.github/prompts/*.prompt.md` contenha o sufixo de provedor `(copilot)` na chave `model:`; e (b) toda linha `model:` nos agents e prompts mapeados em `model-profiles.yaml` (`PROFILES_PATH`) esteja delimitada por aspas duplas (`model: "..."`) e coincida exatamente com o modelo resolvido do perfil `default`.

---

## 2. Arquivos no Escopo (`allowed_files`)

| Arquivo | Linhas Atuais | Tipo de Mudança | Responsabilidade na Entrega |
| :--- | :---: | :--- | :--- |
| `tests/governance_audit/test_local_project_isolation.py` | `742 \n / 743 linhas` (`wc -l` / `splitlines()`) | Modificação cirúrgica (L210–L241) | Expandir a validação de R-044 para aplicar também a regex literal de `.githooks/pre-commit` L58 sobre `.github/**` com isenções seguras para metatexto de regex e placeholders. |
| `tests/governance_audit/test_synth_waves_prompt.py` | `57 \n / 58 linhas` (`wc -l` / `splitlines()`) | Modificação cirúrgica (L39–L58) | Atualizar a Regra 3 (`test_regra3_cwd_absoluto_no_sandbox` / alias compatível) exigindo `${workspaceFolder}` (ou `WORKSPACE_ROOT`) e proibir qualquer match da regex R-044 em `.github/prompts/synth-waves.prompt.md`. |
| `tests/governance_audit/test_model_profiles_parity.py` | `350 \n / 351 linhas` (`wc -l` / `splitlines()`) | Adição de teste (após L109 ou L351) | Adicionar teste de regressão TB-34 validando ausência de sufixo `(copilot)`, formatação entre aspas duplas na linha `model:` e igualdade com o perfil `default` de `PROFILES_PATH`. |

---

## 3. Especificação Técnica das Tarefas (`[PYTHON_TEST_TASKS]` / `[BACKEND_TASKS]`)

### `[PYTHON_TEST_TASKS]` / `[BACKEND_TASKS]`

#### Tarefa B1 — Expandir detecção R-044 em `tests/governance_audit/test_local_project_isolation.py`

- **Alvo**: `tests/governance_audit/test_local_project_isolation.py` (região das linhas 210–241).
- **Mudança Técnica**:
  1. Definir constante compilada na seção 3 (`_WINDOWS_USER_PATH_RE` para o padrão existente na linha 215 e `_PRECOMMIT_R044_PATH_RE = re.compile(r"([A-Za-z]:\\(Users|workspace)|/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/)")`) espelhando exatamente a expressão da linha 58 de `.githooks/pre-commit`.
  2. Em `test_no_machine_specific_paths_in_tracked_files()`, além da checagem global por `_WINDOWS_USER_PATH_RE`, verificar para todos os arquivos rastreados sob `.github/` (`rel_path.parts and rel_path.parts[0] == ".github"`) se alguma linha casa com `_PRECOMMIT_R044_PATH_RE`.
  3. Preservar e refinar o filtro de isenção por linha para não gerar falso-positivo em linhas que documentam a própria expressão regular (`[A-Za-z]:\\(Users|workspace)`, `([A-Za-z]:\\`) ou que utilizam placeholders canônicos (delimitadores angulares de placeholder, `[LETRA_DRIVE]`, `{username}`) ou metatexto descritivo de regras (`"regex"`, `"padrao"`, `"placeholder"`, `"removidos"`, `"exemplo ilustrativo"`, `"exemplos ilustrativos"`, `"pre-commit"`), conforme o trecho-alvo abaixo:

```python
_WINDOWS_USER_PATH_RE = re.compile(
    r'C:\\Users\\(?!\{username\}|<user>|Public|Default)[a-zA-Z0-9_-]+\\',
    re.IGNORECASE,
)
_PRECOMMIT_R044_PATH_RE = re.compile(
    r'([A-Za-z]:\\(Users|workspace)|/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/)'
)
_REGEX_DOC_EXEMPT_TOKENS = (
    "([A-Za-z]:\\\\(Users|workspace)",
    "[LETRA_DRIVE]",
    "{username}",
    "<user>",
    "<path",
    "<caminho",
    "<...>",
)
```

- **Isenção Estrita para `_PRECOMMIT_R044_PATH_RE` (Prevenção de Falsos-Negativos)**: Para o novo padrão `_PRECOMMIT_R044_PATH_RE` (regex da linha 58 do `.githooks/pre-commit`), a isenção por linha **NÃO** deve usar palavras amplas como `"pre-commit"` ou `"regex"`, devendo restringir-se estritamente a linhas que contenham a própria definição literal do grupo regex (`([A-Za-z]:\(Users|workspace)`) ou placeholders explícitos (`[LETRA_DRIVE]`, `{username}`), evitando falsos-negativos.
- **Critério de Aceite B1**: Qualquer ocorrência de caminho local casando com `_PRECOMMIT_R044_PATH_RE` em `.github/**` (fora das isenções de documentação da regex/placeholders) falha o teste com mensagem indicando `[rel_path:idx]`.

#### Tarefa B2 — Blindar Regra 3 e R-044 em `tests/governance_audit/test_synth_waves_prompt.py`

- **Estado Atual Verificado de `.github/prompts/synth-waves.prompt.md` (Camada A Concluída)**: `.github/prompts/synth-waves.prompt.md` já foi atualizado na Camada A, contendo atualmente `${workspaceFolder}` e `0` matches da regex de R-044.

- **Alvo**: `tests/governance_audit/test_synth_waves_prompt.py` (linhas 39–58).
- **Mudança Técnica**:
  1. Importar `re` no topo do módulo e definir `_R044_LOCAL_PATH_RE = re.compile(r"([A-Za-z]:\\(Users|workspace)|/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/)")`.
  2. Atualizar a verificação da Regra 3 — expondo `test_regra3_cwd_absoluto_no_sandbox()` (e mantendo `test_deve_exigir_cwd_explicito_e_resolucao_token_sdk()` invocando a mesma validação) — para:
     - Exigir a presença de `"cwd"` e de `"${workspaceFolder}" in content or "WORKSPACE_ROOT" in content` (removendo a aceitação de caminhos absolutos literais de máquina Windows nas antigas linhas 43–44);
     - Exigir `"COPILOT_SDK_TOKEN" in content` e `"gh auth token" in content`;
     - Verificar explicitamente que `_R044_LOCAL_PATH_RE.search(content) is None`, garantindo que `.github/prompts/synth-waves.prompt.md` não contém nenhum match da regex de R-044.
- **Critério de Aceite B2**: O arquivo `tests/governance_audit/test_synth_waves_prompt.py` próprio fica 100% livre de caminhos absolutos literais e falha imediatamente caso `.github/prompts/synth-waves.prompt.md` reintroduza qualquer caminho local que viole R-044.

#### Tarefa B3 — Adicionar auditoria de formato `model:` e ausência de `(copilot)` em `tests/governance_audit/test_model_profiles_parity.py`

- **Alvo**: `tests/governance_audit/test_model_profiles_parity.py` (constantes existentes `PROFILES_PATH`, `AGENTS_DIR`, `PROMPTS_DIR` nas linhas 40–43; inserção após `test_default_profile_parity_with_frontmatters` na linha 110 ou ao final do arquivo na linha 351).
- **Mudança Técnica**:
  1. Implementar `test_frontmatter_model_raw_line_quotes_no_copilot_and_default_parity()` que carrega `PROFILES_PATH` (`model-profiles.yaml` na raiz do repositório via `yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))` ou `load_profiles(REPO_ROOT)`) e resolve o perfil `default` via `resolve_profile("default", data["profiles"])`.
  2. Iterar sobre todos os arquivos `.github/agents/*.agent.md` (`AGENTS_DIR.glob("*.agent.md")`) e `.github/prompts/*.prompt.md` (`PROMPTS_DIR.glob("*.prompt.md")`), extraindo o bloco YAML do frontmatter (entre os delimitadores `---`).
  3. Para cada arquivo que declara a chave `model:` no frontmatter (e para todos os agents e prompts mapeados em `tier_map` de `PROFILES_PATH`):
     - Localizar a linha bruta `^model:\s*(.+)$` dentro do frontmatter;
     - Assegurar que o valor bruto **não** contém o sufixo de provedor `(copilot)` (case-insensitive, espelhando a checagem TB-34 do `.githooks/pre-commit`);
     - Assegurar que a linha `model:` nos agents e prompts mapeados em `model-profiles.yaml` (`PROFILES_PATH`) está entre aspas duplas (`raw_val.startswith('"') and raw_val.endswith('"')`) e que o valor sem aspas coincide exatamente com o modelo esperado do perfil `default` (`resolve_target_model(key, tier, resolved_default)`).
- **Critério de Aceite B3**: Qualquer agent ou prompt com `(copilot)` na linha `model:`, com valor `model:` sem aspas duplas ou divergente do perfil `default` de `PROFILES_PATH` falha determinísticamente no pytest.

---

## 4. Análise de Blast Radius e Contratos

| Dimensão | Avaliação |
| :--- | :--- |
| **Escopo de Mutação** | Restrito exclusivamente a 3 arquivos de teste em `tests/governance_audit/`. Nenhum código de runtime, hook Git ou definição de agente é modificado nesta camada. |
| **Acoplamento com Outras Camadas** | Depende da conclusão da Camada B (higienização de `.github/prompts/*.prompt.md` e remoção do caminho literal em `.github/prompts/synth-waves.prompt.md`) para passar em estado **TDD Green**; se executado antes da Camada B, opera em estado **TDD Red** esperado, comprovando a eficácia dos testes. |
| **Performance de Execução** | Leitura em memória de arquivos Markdown já existentes no repositório; impacto de tempo adicional estimado inferior a 50ms na suíte `tests/governance_audit/`. |
| **Compatibilidade de Nomenclatura** | Em `test_synth_waves_prompt.py`, manter compatibilidade com os testes existentes adicionando `test_regra3_cwd_absoluto_no_sandbox` sem quebrar coletores que invoquem as 4 funções anteriores. |

---

## 5. Estratégia de Rollback Não-Destrutivo

Em conformidade estrita com as regras de segurança operacional (proibição de `git checkout --` e `git reset --hard`), qualquer reversão das alterações nos 3 arquivos de teste deve seguir o protocolo atômico abaixo:

1. **Snapshot Pré-Execução**:
   ```bash
   mkdir -p tmp/pre-commit-py-snapshot
   cp tests/governance_audit/test_local_project_isolation.py tmp/pre-commit-py-snapshot/
   cp tests/governance_audit/test_synth_waves_prompt.py tmp/pre-commit-py-snapshot/
   cp tests/governance_audit/test_model_profiles_parity.py tmp/pre-commit-py-snapshot/
   ```
2. **Geração de Patch e Reversão Segura**:
   ```bash
   git diff -- tests/governance_audit/test_local_project_isolation.py tests/governance_audit/test_synth_waves_prompt.py tests/governance_audit/test_model_profiles_parity.py > tmp/pre-commit-py-delta.patch
   git apply -R tmp/pre-commit-py-delta.patch
   ```
3. **Fallback por Cópia Direta do Snapshot**:
   Caso o patch reverso encontre conflito parcial, restaurar a partir de `tmp/pre-commit-py-snapshot/*.py` via `fs.copyFileSync` no sandbox `ctx_execute`.

---

## 6. Alternativas Rejeitadas (Mini-ADR)

1. **Alternativa Rejeitada 1 — Invocar `.githooks/pre-commit` via subprocesso Bash dentro do pytest**:
   - *Motivo da rejeição*: O hook `.githooks/pre-commit` opera apenas sobre a área de staging (`git diff --cached`) e exige ambiente POSIX/sh com objetos staged específicos. Em execuções de CI ou local com working tree limpa, `git diff --cached` retorna vazio e não audita os arquivos reais do repositório. Testar diretamente a árvore de arquivos em Python garante cobertura determinística em qualquer estado do índice Git.
2. **Alternativa Rejeitada 2 — Confiar apenas no parser YAML (`yaml.safe_load`) em `test_model_profiles_parity.py`**:
   - *Motivo da rejeição*: O parser YAML converte tanto `model: Claude Haiku 4.5` (sem aspas) quanto `model: "Claude Haiku 4.5"` (com aspas) para a mesma `str` Python, ocultando divergências de formatação que o script `scripts/switch-model-profile.py` ou hooks baseados em linha bruta exigem padronizadas entre aspas duplas.

---

## 7. Portão de Qualidade R-055 (Auto-Auditoria Q1 / Q2 / Q3)

- **Q1 (Completude de Escopo e Contratos)**: Os 3 arquivos listados em `allowed_files` foram inspecionados linha a linha (742 `\n` / 743 `splitlines()`, 57 `\n` / 58 `splitlines()` e 350 `\n` / 351 `splitlines()`, respectivamente) e todas as assinaturas, constantes (`REPO_ROOT`, `PROFILES_PATH`, `AGENTS_DIR`, `PROMPTS_DIR`) e expressões regulares estão alinhadas à fonte real.
- **Q2 (Isolamento R-043/R-044 e Higiene de Sintaxe)**: O plano não referencia artefatos locais ignorados, não utiliza placeholders angulares fora de blocos de código cercados e não contém nenhum caminho absoluto literal de máquina local.
- **Q3 (Verificabilidade TDD e Rollback Seguro)**: Cada tarefa (B1, B2, B3) possui asserções determinísticas mapeadas em cenários Gherkin verificáveis via `pytest` e plano de rollback não-destrutivo baseado em snapshot + `git apply -R`.

---

## 8. Cenários de Teste BDD (Gherkin)

```gherkin
Funcionalidade: Paridade entre testes de governança Python e bloqueios R-044 / TB-34 do pre-commit

  Cenário: Detecção de caminho absoluto de workspace ou home em .github/** (Tarefa B1)
    Dado que a função test_no_machine_specific_paths_in_tracked_files audita os arquivos rastreados em .github/**
    Quando um arquivo em .github/prompts/ ou .github/agents/ contiver um caminho casando com a regex de R-044 fora de linhas de documentação da própria regex ou placeholders
    Então o teste em tests/governance_audit/test_local_project_isolation.py deve falhar apontando o arquivo e o número da linha

  Cenário: Isenção de linhas que documentam a própria regex R-044 ou placeholders (Tarefa B1)
    Dado um arquivo rastreado em .github/** que documenta a expressão regular ([A-Za-z]:\(Users|workspace)) ou placeholders como [LETRA_DRIVE]
    Quando test_no_machine_specific_paths_in_tracked_files for executado
    Então nenhuma violação falso-positiva deve ser reportada para essa linha documental

  Cenário: Regra 3 do prompt synth-waves exige variável de workspace e zero caminhos locais R-044 (Tarefa B2)
    Dado o arquivo .github/prompts/synth-waves.prompt.md auditado por tests/governance_audit/test_synth_waves_prompt.py
    Quando test_regra3_cwd_absoluto_no_sandbox for executado
    Então o teste deve confirmar a presença de ${workspaceFolder} (ou WORKSPACE_ROOT) e validar que a regex R-044 não possui nenhum match no conteúdo do prompt

  Cenário: Paridade da linha model: entre aspas duplas e sem sufixo (copilot) (Tarefa B3)
    Dado o catálogo raiz model-profiles.yaml (PROFILES_PATH) e os diretórios .github/agents/ e .github/prompts/
    Quando os testes de tests/governance_audit/test_model_profiles_parity.py forem executados
    Então nenhum arquivo .agent.md ou .prompt.md deve possuir o sufixo (copilot) na chave model:
    E todos os agents e prompts mapeados em model-profiles.yaml devem possuir a linha model: entre aspas duplas coincidindo exatamente com o perfil default
```
