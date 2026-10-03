# Plano de Implementação — Negação persistente de shell (git status/diff) + Logging em arquivo (.tmp)

> Autoria: `python-arch-advisor` (Etapa 2 — Plano de Implementação, WORKFLOW-BUG-FIX, R-064).
> Insumo: `docs/plans/20261004-bugfix-shell-permission-persistente-logging-arquivo.md` (gate aprovado).
> Modo: 100% Advisory — nenhum arquivo foi alterado na autoria deste documento.

## 0. Pré-requisitos verificados nesta auditoria

- `permission_policy.comando_terminal_e_seguro` (linhas 208-233): assinatura `(comando: str) -> bool`, recursão de encadeamento já existente (linhas 213-224) opera **antes** de qualquer unwrap hoje — ponto de inserção do Fix 2 deve ficar **entre** a checagem de `_COMANDOS_BLOQUEADOS_SEMPRE` (linha 211) e a checagem de encadeamento (linha 213), delegando por recursão simples (`return comando_terminal_e_seguro(interno)`) para reaproveitar TUDO que já existe (encadeamento, git, utilitários) sobre o texto desembrulhado.
- Confirmados os 5 consumidores do blast radius 🟡 como **delegações**, não reimplementações: `routes._conservative_permission_handler` → `tool_call_nao_escrita_e_segura` → `comando_terminal_e_seguro`; `routes._governance_permission_handler` → idem; `sdk_session._identificador_e_seguro_nativo` (×2, linhas 377-388 e 1227-1238) → `_comando_shell_e_seguro` → `comando_terminal_e_seguro` (via `full_command_text`); `permission_policy._comando_batch_item_e_seguro` (linha 341) → `comando_terminal_e_seguro` direto. **Conclusão: o diff cirúrgico do Fix 2 fica 100% contido em `permission_policy.py`, zero alteração nos outros 4 arquivos** — a correção propaga automaticamente por composição de função já existente (R-055).
- `tests/unit/test_permission_policy.py:553-625`: fixtures existentes cobrem comando bare (nunca wrapper) — confirma o gap de cobertura apontado no plano de planejamento; casos de borda já cobertos (vazio, mutante, destrutivo, encadeamento `&&`) que **devem continuar passando inalterados** (regressão).
- `config.py`: padrão uniforme `Field(default=..., alias="ENV_VAR")`, com `@field_validator(..., mode="before")` para normalizar string vazia — novos campos de logging devem seguir o MESMO padrão.
- `app.py:_lifespan`/`create_app()`: ponto único de bootstrap de infraestrutura no startup (mesmo local onde `custom_agents`/`commands_catalog` são carregados uma única vez) — local correto para chamar `configurar_logging()`.
- `dev_watch.py:406-424`: `host`/`port` resolvidos antes do `uvicorn.run(...)` — ponto de inserção natural da checagem de porta é logo após a resolução de `host`/`port` (linha 407) e antes do `print`/`uvicorn.run` (linha 411).
- `Dockerfile.dockerignore`: já existe e é o ÚNICO arquivo de ignore ativo para o build (BuildKit); `deploy/local-chat-gateway/.gitignore` está vazio (confirmado).

---

## 1. Diff Cirúrgico Proposto (pseudo-diffs — NÃO implementado)

### 1.1 Fix 1 — `dev_watch.py` (verificação de porta ocupada)

```diff
--- a/deploy/local-chat-gateway/dev_watch.py
+++ b/deploy/local-chat-gateway/dev_watch.py
@@
+import socket
+
+
+def _porta_ocupada(host: str, port: int) -> bool:
+    """Checagem best-effort de porta ja vinculada (fail-fast amigavel, Windows-first).
+
+    Bug real investigado (2026-10-04): usuario reportou negacao persistente de
+    shell mesmo apos 2 restarts via `dev_watch.py` -- hipotese H1 (confianca
+    alta) e processo `uvicorn`/worker de reload orfao ainda vinculado a porta
+    8080 (comum no Windows quando o terminal e fechado sem Ctrl+C limpo),
+    servindo codigo ANTERIOR a correcao ja presente em
+    `permission_policy.py`/`sdk_session.py`. Esta checagem NAO mata o
+    processo antigo (fora de escopo/perigoso fazer isso automaticamente) --
+    apenas detecta a condicao e falha com mensagem clara em vez de deixar o
+    uvicorn tentar (e falhar silenciosamente/de forma ambigua) o bind.
+    """
+    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
+        sock.settimeout(0.5)
+        return sock.connect_ex((host, port)) == 0
+
+
 def main() -> None:
     ...
     host = args.host or os.environ.get("GATEWAY_BIND", "127.0.0.1")
     port = args.port or int(os.environ.get("GATEWAY_PORT", "8080"))
 
+    if _porta_ocupada(host, port):
+        print(
+            f"[dev_watch] ERRO: a porta {port} em {host} ja esta em uso -- "
+            "provavelmente um processo uvicorn/worker de reload anterior "
+            "nao foi encerrado corretamente (comum no Windows ao fechar o "
+            "terminal sem Ctrl+C). Isso faz o gateway continuar servindo "
+            "CODIGO ANTIGO, mascarando correcoes ja aplicadas.\n"
+            "Para identificar e encerrar o processo antigo no Windows "
+            "(PowerShell):\n"
+            f"    Get-NetTCPConnection -LocalPort {port} | "
+            "Select-Object OwningProcess\n"
+            "    Stop-Process -Id <PID> -Force\n"
+            "Ou use outra porta: python dev_watch.py --port 8081",
+            file=sys.stderr,
+        )
+        raise SystemExit(1)
+
     import uvicorn
```

- Contrato de uso preservado (nenhuma flag nova obrigatória; `--port` já existe como via de escape).
- Mensagem de erro é Windows-first (conforme ambiente do usuário) mas não impede uso em outros SOs (checagem via `socket` é portável).

### 1.2 Fix 2 — `permission_policy.py` (unwrap de shell wrapper)

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/permission_policy.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/permission_policy.py
@@
+import re
+
+
+#: Invólucros comuns de shell nativo detectados ANTES da checagem de
+#: git/utilitários -- bug real investigado (2026-10-04, H2, Challenge Gate
+#: C1/C3 aprovados): o SDK pode entregar `full_command_text`/`command` como
+#: `powershell -Command "git status"` (Windows) em vez do comando bare
+#: `"git status"`, fazendo `comando_terminal_e_seguro` cair sempre no
+#: fallback "nao reconhecido => inseguro" mesmo para comandos 100% read-only.
+#: Grupo de captura (1) extrai o comando interno (ainda cru, com aspas).
+_PADROES_WRAPPER_SHELL: tuple[re.Pattern[str], ...] = (
+    re.compile(
+        r"^(?:powershell(?:\.exe)?|pwsh(?:\.exe)?)(?:\s+-\w+)*\s+-c(?:ommand)?\s+(.+)$"
+    ),
+    re.compile(r"^cmd(?:\.exe)?\s+/c\s+(.+)$"),
+    re.compile(r"^(?:bash|sh)\s+-(?:lc|c)\s+(.+)$"),
+)
+
+
+def _desembrulhar_shell_wrapper(normalizado: str) -> str | None:
+    """Extrai o comando interno de um invólucro de shell nativo, se houver.
+
+    Fail-closed: invólucro reconhecido mas sem conteúdo interno (ex.:
+    `"powershell -command"` sozinho, ou aspas desbalanceadas) retorna
+    `None` -- `comando_terminal_e_seguro` trata `None` como "sem unwrap",
+    nunca como "seguro por omissão".
+    """
+    for padrao in _PADROES_WRAPPER_SHELL:
+        match = padrao.match(normalizado)
+        if not match:
+            continue
+        interno = match.group(1).strip()
+        if len(interno) >= 2 and interno[0] in "\"'" and interno[-1] == interno[0]:
+            interno = interno[1:-1].strip()
+        return interno or None
+    return None
+
+
 def comando_terminal_e_seguro(comando: str) -> bool:
     ...
     normalizado = (comando or "").strip().lower()
     if not normalizado:
         return False
     if any(bloqueado in normalizado for bloqueado in _COMANDOS_BLOQUEADOS_SEMPRE):
         return False
+    interno = _desembrulhar_shell_wrapper(normalizado)
+    if interno is not None:
+        # Recursao simples: reaplica a MESMA funcao (encadeamento, git,
+        # utilitarios, bloqueios) sobre o texto desembrulhado -- nunca um
+        # caminho de validacao paralelo/duplicado (R-055).
+        return comando_terminal_e_seguro(interno)
     if any(sep in normalizado for sep in _SEPARADORES_ENCADEAMENTO):
         ...  # inalterado
```

- **Assinatura inalterada** (`comando_terminal_e_seguro(comando: str) -> bool`) — nenhum dos 5 consumidores precisa de qualquer alteração de código.
- **Encadeamento preservado:** `"powershell -Command \"git status && git diff\""` → unwrap extrai `git status && git diff` → recursão cai na checagem de encadeamento já existente (linha 213-224) → cada segmento passa por `comando_terminal_e_seguro` novamente → ambos são git read-only → `True`.
- **Nunca enfraquece a heurística:** comando mutante disfarçado (`"powershell -Command \"git commit -m x\""`) desembrulha para `"git commit -m x"`, que já é negado pela checagem de `_GIT_SUBCOMANDOS_MUTACAO` existente — mesmo código, sem bypass.

### 1.3 Fix 3 — Logging em arquivo (`.tmp/gateway.log`)

```diff
--- /dev/null
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/logging_config.py
@@
+"""logging_config — RotatingFileHandler em ADICAO ao stdout (nunca substitui).
+
+Gap de observabilidade investigado em 2026-10-04: `logging.getLogger(__name__)`
+e usado em 10 modulos (`agent_catalog.py`, `auth.py`, `governance_pipeline.py`,
+`permission_policy.py`, `projects_catalog.py`, `prompts_catalog.py`,
+`sdk_session.py`, `telemetry.py`, `turn_recorder.py`, `api/routes.py`), mas
+nenhum handler de arquivo era configurado -- logs dependiam 100% do handler
+default do uvicorn (stdout), perdidos ao fechar o terminal.
+"""
+from __future__ import annotations
+
+import logging
+from logging.handlers import RotatingFileHandler
+from pathlib import Path
+
+_FORMATO = "%(asctime)s %(levelname)s %(name)s: %(message)s"
+_CONFIGURADO = False
+
+
+def configurar_logging(
+    log_file: str | Path,
+    *,
+    max_bytes: int = 5_242_880,
+    backup_count: int = 3,
+    level: int = logging.INFO,
+) -> None:
+    """Adiciona `RotatingFileHandler` ao root logger (idempotente).
+
+    Idempotencia: chamadas repetidas (ex.: testes instanciando `create_app()`
+    varias vezes, ou hot-reload do uvicorn reexecutando o modulo) NAO
+    duplicam o handler -- `_CONFIGURADO` e um guard de processo.
+    """
+    global _CONFIGURADO
+    if _CONFIGURADO:
+        return
+    caminho = Path(log_file)
+    caminho.parent.mkdir(parents=True, exist_ok=True)
+    handler = RotatingFileHandler(
+        caminho, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
+    )
+    handler.setFormatter(logging.Formatter(_FORMATO))
+    handler.setLevel(level)
+    root = logging.getLogger()
+    root.addHandler(handler)  # ADICAO -- StreamHandler do uvicorn permanece intacto
+    if root.level > level:
+        root.setLevel(level)
+    _CONFIGURADO = True
```

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/config.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/config.py
@@
+    gateway_log_file: str = Field(
+        default=".tmp/gateway.log", alias="GATEWAY_LOG_FILE"
+    )
+    gateway_log_max_bytes: int = Field(
+        default=5_242_880, alias="GATEWAY_LOG_MAX_BYTES"
+    )
+    gateway_log_backup_count: int = Field(
+        default=3, alias="GATEWAY_LOG_BACKUP_COUNT"
+    )
```

```diff
--- a/deploy/local-chat-gateway/src/local_chat_gateway/app.py
+++ b/deploy/local-chat-gateway/src/local_chat_gateway/app.py
@@
+from local_chat_gateway.logging_config import configurar_logging
@@
     resolved_settings = settings if settings is not None else get_settings()
     resolved_settings.validate_startup()
+    configurar_logging(
+        resolved_settings.gateway_log_file,
+        max_bytes=resolved_settings.gateway_log_max_bytes,
+        backup_count=resolved_settings.gateway_log_backup_count,
+    )
```

```diff
--- a/deploy/local-chat-gateway/.gitignore
+++ b/deploy/local-chat-gateway/.gitignore
@@
+.tmp/
```

```diff
--- a/deploy/local-chat-gateway/Dockerfile.dockerignore
+++ b/deploy/local-chat-gateway/Dockerfile.dockerignore
@@
 .coverage
+.tmp/
+**/.tmp/
 tests/
```

- Caminho `.tmp/gateway.log` é relativo ao CWD do processo (local via `dev_watch.py` → `deploy/local-chat-gateway/.tmp/gateway.log`; dentro do container, resolvido lazy em runtime — como o serviço roda `read_only: true` + `tmpfs` em `/tmp` conforme README, **validar durante a Etapa 3** se o CWD do container permite criar `.tmp/` ou se é necessário usar `/tmp/gateway.log` lá; sem impacto no caminho local confirmado pelo usuário).
- Nenhum módulo dos 10 que usam `getLogger(__name__)` precisa de alteração — todos propagam para o root logger por padrão (comportamento stdlib já correto).

---

## 2. Sequência TDD Estrita (Red → Green → Regressão)

### 2.1 `tests/unit/test_permission_policy.py` (Fix 2 — safety net PRIMEIRO)

| # | Teste novo | O que valida |
|---|---|---|
| T1 | `test_deve_considerar_seguro_comando_git_envolto_em_powershell_command` | `'powershell -Command "git --no-pager status"'` → `True` |
| T2 | `test_deve_considerar_seguro_comando_git_envolto_em_powershell_exe` | `'powershell.exe -Command "git status"'` → `True` |
| T3 | `test_deve_considerar_seguro_comando_git_envolto_em_cmd_c` | `'cmd /c "git status"'` → `True` |
| T4 | `test_deve_considerar_seguro_comando_git_envolto_em_cmd_c_sem_aspas` | `'cmd.exe /c git status'` → `True` |
| T5 | `test_deve_considerar_seguro_comando_git_envolto_em_bash_lc` | `'bash -lc "git status"'` → `True` |
| T6 | `test_deve_considerar_seguro_comando_utilitario_envolto_em_bash_c_aspas_simples` | `"bash -c 'ls -la'"` → `True` |
| T7 (caso EXPLÍCITO exigido pelo gate) | `test_deve_considerar_seguro_encadeamento_dentro_de_wrapper_powershell` | `'powershell -Command "git status && git diff"'` → `True` |
| T8 | `test_deve_considerar_inseguro_comando_mutante_envolto_em_wrapper` | `'powershell -Command "git commit -m x"'` → `False` |
| T9 | `test_deve_considerar_inseguro_destrutivo_envolto_em_wrapper` | `'powershell -Command "rm -rf /"'` → `False` |
| T10 | `test_deve_considerar_inseguro_encadeamento_misto_dentro_de_wrapper` | `'powershell -Command "git status && git push origin main"'` → `False` |
| T11 (fail-closed) | `test_deve_considerar_inseguro_wrapper_sem_comando_interno` | `"powershell -Command"` → `False` (sem crash) |
| T12 (regressão, roda igual) | `test_deve_autorizar_run_in_terminal_com_comando_git_read_only_wrapped` | `tool_call_nao_escrita_e_segura("run_in_terminal", {"command": 'powershell -Command "git status"'})` → `True` (prova a propagação pelos 5 consumidores sem alterá-los) |

> **Obrigatório antes de T1-T12:** rodar a suite EXISTENTE (`test_deve_considerar_seguro_comando_git_read_only_ou_utilitario`, `test_deve_considerar_inseguro_comando_mutante_ou_destrutivo`, linhas 553-599) como baseline Green — nenhuma dessas pode regredir após o diff §1.2.

### 2.2 `tests/unit/test_sdk_session.py` (regressão dos 2 call-sites duplicados)

| # | Teste novo | O que valida |
|---|---|---|
| T13 | `test_comando_shell_e_seguro_aceita_full_command_text_envolto_em_powershell` | Mock de `PermissionRequestShell` com `full_command_text='powershell -Command "git status"'` e `commands=[...read_only=True]` → `_comando_shell_e_seguro(...)` → `True` |

### 2.3 Novo `tests/unit/test_dev_watch_port_check.py` (Fix 1)

> Checar PRIMEIRO se já existe arquivo de teste para `dev_watch.py` (não confirmado nesta auditoria — `dev_watch.py` está na raiz do gateway, fora de `src/`, pode não ter cobertura dedicada). Se ausente, criar o arquivo; se existente, adicionar a classe.

| # | Teste novo | O que valida |
|---|---|---|
| T14 | `test_porta_ocupada_detecta_socket_em_uso` | Abre um `socket.socket().bind(("127.0.0.1", 0))` real (porta efêmera), chama `_porta_ocupada("127.0.0.1", porta_do_bind)` → `True` |
| T15 | `test_porta_ocupada_retorna_false_para_porta_livre` | Porta efêmera NÃO vinculada → `False` |
| T16 | `test_main_falha_fast_com_mensagem_clara_quando_porta_ocupada` | Com mock/monkeypatch de `_porta_ocupada` → `True` e demais dependências mockadas, `main()` levanta `SystemExit(1)` com mensagem contendo "ja esta em uso" |

### 2.4 Novo `tests/unit/test_logging_config.py` (Fix 3)

| # | Teste novo | O que valida |
|---|---|---|
| T17 | `test_configurar_logging_cria_diretorio_pai_se_ausente` | `tmp_path / "sub" / "gateway.log"` (dir não existe) → após chamada, diretório existe |
| T18 | `test_configurar_logging_adiciona_handler_sem_remover_stream_handler_existente` | Root logger com `StreamHandler` pré-existente → após `configurar_logging(...)`, `StreamHandler` original ainda presente + novo `RotatingFileHandler` adicionado |
| T19 | `test_configurar_logging_e_idempotente_nao_duplica_handler` | 2 chamadas sucessivas → apenas 1 `RotatingFileHandler` no root logger |
| T20 | `test_configurar_logging_formato_inclui_timestamp_nivel_modulo` | Loga mensagem via `logging.getLogger("local_chat_gateway.x").info("teste")`, lê o arquivo, regex `\d{4}-\d{2}-\d{2}.*INFO.*local_chat_gateway\.x.*teste` |
| T21 | `test_configurar_logging_respeita_max_bytes_e_backup_count` | Assert `handler.maxBytes`/`handler.backupCount` == valores passados |

> **Nota de isolamento de teste:** `_CONFIGURADO` é estado de módulo global — os testes T17-T21 DEVEM resetar `logging_config._CONFIGURADO = False` e limpar handlers do root logger em fixture `setup`/`teardown` (`caplog`/fixture dedicada), para não vazar estado entre testes nem para o resto da suíte (`pytest -v` roda os ~233 testes no mesmo processo).

### 2.5 `tests/unit/test_config.py` (novos campos de Settings)

| # | Teste novo | O que valida |
|---|---|---|
| T22 | `test_settings_gateway_log_file_default` | `Settings().gateway_log_file == ".tmp/gateway.log"` |
| T23 | `test_settings_gateway_log_max_bytes_e_backup_count_default` | Defaults `5_242_880`/`3` |
| T24 | `test_settings_gateway_log_file_le_de_env_var` | Via `monkeypatch.setenv("GATEWAY_LOG_FILE", ...)` → `Settings().gateway_log_file` reflete o valor |

---

## 3. Subtasks Executáveis por `@python-bug-fixer`

- `[S]` T-01 — Confirmar se `tests/unit/test_dev_watch_port_check.py` (ou cobertura equivalente de `dev_watch.py`) já existe; se não, planejar o arquivo novo. **Bloqueante para T-02.**
- `[S]` T-02 — Escrever T14-T16 (Red), confirmar falha pelo motivo correto (função `_porta_ocupada` ainda não existe).
- `[P]` T-03 — Aplicar diff §1.1 (`dev_watch.py`): `_porta_ocupada` + checagem fail-fast em `main()`. Rodar T14-T16 até Green.
- `[S]` T-04 — Rodar a suíte EXISTENTE de `test_permission_policy.py` (linhas 553-625) como baseline confirmado Green, ANTES de qualquer alteração em `comando_terminal_e_seguro` (safety net dos 5 consumidores, Challenge Gate C1/C3).
- `[S]` T-05 — Escrever T1-T13 (Red) em `test_permission_policy.py` + `test_sdk_session.py`, confirmar falha pelo motivo correto (wrapper não reconhecido → `False` onde deveria ser `True`).
- `[P]` T-06 — Aplicar diff §1.2 (`permission_policy.py`): `_PADROES_WRAPPER_SHELL`, `_desembrulhar_shell_wrapper`, ponto de inserção dentro de `comando_terminal_e_seguro`. Rodar T1-T13 até Green **e** reconfirmar T-04 (baseline) ainda Green — zero regressão nos 5 consumidores.
- `[S]` T-07 — Escrever T17-T24 (Red) em `test_logging_config.py` (módulo novo) + `test_config.py`.
- `[P]` T-08 — Criar `logging_config.py` (diff §1.3) + aplicar diffs em `config.py` (3 novos campos) e `app.py` (wiring em `create_app()`). Rodar T17-T24 até Green.
- `[S]` T-09 — Aplicar diffs de infraestrutura: `.gitignore` local (`+.tmp/`) e `Dockerfile.dockerignore` (`+.tmp/`, `+**/.tmp/`).
- `[S]` T-10 — Atualizar `README.md` do gateway: seção de troubleshooting para "porta 8080 ocupada" (Fix 1, com os mesmos comandos PowerShell do diff §1.1) e nota sobre `.tmp/gateway.log` (Fix 3).
- `[S]` T-11 — Rodar suíte completa (`pytest -v --tb=short`), confirmar baseline (232/233 conforme plano de planejamento) + 21 testes novos (T1-T24 menos sobreposições), zero regressões. Rodar `mypy --strict` sobre os 4 arquivos alterados + `logging_config.py` novo (tipagem estrita, `X | None` PEP 604 consistente com o projeto).
- `[S]` T-12 — Atualizar `.env.example` com `GATEWAY_LOG_FILE`, `GATEWAY_LOG_MAX_BYTES`, `GATEWAY_LOG_BACKUP_COUNT` (comentários explicando default local `.tmp/gateway.log` e rotação).
- `[S]` T-13 — Reprodução manual do incidente original (critério de aceitação #1 abaixo) via `python dev_watch.py` + `git --no-pager status` através de `pr-gatekeeper`, confirmando ausência de "Negado pela politica local".

Legenda: `[S]` = sequencial (depende do anterior); `[P]` = pode ser paralelizado com a subtask `[S]` imediatamente anterior já concluída (mesmo arquivo, mas fases Red/Green distintas e isoladas por fix).

---

## 4. Critérios de Aceitação Objetivos

1. `python dev_watch.py` seguido de `git --no-pager status` via `pr-gatekeeper` retorna sucesso (sem `"Negado pela politica local"`), reproduzindo exatamente os passos do incidente relatado pelo usuário.
2. Subir `python dev_watch.py` com a porta já ocupada por um processo anterior falha com `SystemExit(1)` e mensagem acionável (PowerShell `Get-NetTCPConnection`), em vez de comportamento ambíguo/silencioso.
3. `comando_terminal_e_seguro('powershell -Command "git status && git diff"')` → `True`; `comando_terminal_e_seguro('powershell -Command "git commit -m x"')` → `False` (teste explícito exigido pelo gate, T7/T8).
4. Suite completa (`pytest deploy/local-chat-gateway/tests -v`) passa 100%, incluindo os 232 testes baseline + todos os novos (T1-T24), zero regressões.
5. `mypy --strict deploy/local-chat-gateway/src/local_chat_gateway` passa sem erros novos.
6. Após subir o gateway e executar ao menos 1 interação de chat, `deploy/local-chat-gateway/.tmp/gateway.log` existe, contém entradas com timestamp/nível/módulo, e o stdout do uvicorn continua a exibir logs normalmente (Fix 3 é aditivo, nunca substitutivo).
7. `git status` no repositório após os testes NÃO mostra `.tmp/` como arquivo rastreado (confirma `.gitignore` local efetivo).

## 5. Rollback Plan

- Fix 1: reverter diff de `dev_watch.py` — nenhuma mudança de estado persistente, rollback trivial (apenas código).
- Fix 2: reverter diff de `permission_policy.py` — função volta ao comportamento anterior (sem unwrap); nenhum dos 5 consumidores precisa de rollback adicional pois nenhum foi alterado.
- Fix 3: reverter diffs de `logging_config.py` (deletar), `config.py`, `app.py`, `.gitignore`, `Dockerfile.dockerignore`; arquivo `.tmp/gateway.log` eventualmente criado em disco não é rastreado por git (sem impacto em rollback de código) — pode ser apagado manualmente se desejado.

---

## 6. Handoff

`python-arch-advisor` → `@python-bug-fixer` (motivo: plano de implementação aprovado no gate R-064 pelo usuário; próxima etapa do WORKFLOW-BUG-FIX exige escrita de código/testes, fora do escopo read-only deste agente).

