#!/usr/bin/env python3
"""dev_watch — Sobe o Deep Agents Gateway localmente (fora do Docker) em modo
develop com auto-reload (watch), fazendo bootstrap COMPLETO e automatico das
dependencias (zero comandos extras na 1a execucao).

Uso:
    python dev_watch.py
    python dev_watch.py --port 8081
    python dev_watch.py --no-reload       # util para debugger attachado (sem hot-reload)
    python dev_watch.py --reinstall       # forca reinstalacao das dependencias editaveis
    python dev_watch.py --no-bootstrap    # pula criacao de venv/instalacao (modo rapido,
                                           # assume que tudo ja esta instalado)

O QUE ESTE SCRIPT FAZ AUTOMATICAMENTE (sem exigir nenhum comando manual):
    1. Cria `.venv` neste diretorio se nao existir (1a execucao).
    2. Instala `governance-runner` (editable, de `tools/headless-governance-runner`)
       e `deep-agents-gateway[dev,sdk]` (editable) se ainda nao estiverem
       presentes no venv -- `[sdk]` = integracao REAL com o Copilot SDK; sem
       ele, o gateway responderia sempre com o stub deterministico.
    3. Reexecuta a si mesmo com o Python do `.venv` se o interpretador atual
       (`python`/`py` do PATH) for outro -- evita a classe de erro
       "did not find executable at ...python.exe" causada por shims de
       Python quebrados/desatualizados no PATH (bug real, 2026-10-02).
    4. Gera `.env` a partir de `.env.example` se `.env` nao existir, com
       `GATEWAY_API_KEY`/`WEB_ACCESS_CODE` aleatorios seguros (nunca
       "change-me") -- dispensa copia manual + edicao do arquivo.
    5. Resolve os paths de `.env` que tem DEFAULT de CONTAINER
       (`GOVERNANCE_GRAPH_PATH`, `GOVERNANCE_GITHUB_DIR`,
       `PROJECTS_LOCAL_YAML`, `GATEWAY_WORKSPACE_DIR`, `GATEWAY_DB_PATH`)
       para os equivalentes do host (raiz do monorepo).
    6. Avisa (sem bloquear) se `secrets/copilot_token` estiver ausente/vazio
       -- essa e a UNICA credencial que o script nao pode gerar sozinho
       (token pessoal do GitHub Copilot).
    7. Sobe o uvicorn com `--reload` apontando para `src/`.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import uuid
from pathlib import Path

GATEWAY_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATEWAY_DIR.parent.parent  # deploy/local-chat-gateway -> deploy -> raiz
GITHUB_DIR = REPO_ROOT / ".github"
_VENV_DIR = GATEWAY_DIR / ".venv"
_RUNNER_DIR = REPO_ROOT / "tools" / "headless-governance-runner"



def _porta_ocupada(host: str, port: int) -> bool:
    """Checagem best-effort de porta ja vinculada (fail-fast amigavel, Windows-first).

    Bug real investigado (2026-10-04): reexecucoes rapidas de `dev_watch.py`
    (ex.: apos um crash do uvicorn que nao libera a porta a tempo) falhavam
    com um traceback cru do `OSError`/`[WinError 10048]` do proprio uvicorn,
    sem nenhuma orientacao de como liberar a porta. Tenta vincular (`bind`) a
    `(host, port)`: se falhar com `OSError`, a porta ja esta em uso por
    outro processo; o socket e sempre fechado (`with`) antes do uvicorn
    tentar de fato subir.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.bind((host, port))
        except OSError:
            return True
        return False

def _venv_python_path() -> Path:
    """Caminho do interpretador Python dentro de `GATEWAY_DIR/.venv` (multi-OS)."""
    return (
        _VENV_DIR / "Scripts" / "python.exe"
        if os.name == "nt"
        else _VENV_DIR / "bin" / "python"
    )


def _executar(cmd: list[str], *, descricao: str) -> None:
    """Executa `cmd`, abortando com mensagem amigavel (sem traceback cru) em falha."""
    print(f"[dev_watch] {descricao} ...")
    resultado = subprocess.run(cmd)
    if resultado.returncode != 0:
        print(
            f"[dev_watch] ERRO: falha ao '{descricao}' (exit code "
            f"{resultado.returncode}). Comando: {' '.join(cmd)}",
            file=sys.stderr,
        )
        raise SystemExit(resultado.returncode)


def _ensure_venv() -> Path:
    """Cria `.venv` neste diretorio se ainda nao existir (1a execucao)."""
    venv_python = _venv_python_path()
    if venv_python.exists():
        return venv_python

    _executar(
        [sys.executable, "-m", "venv", str(_VENV_DIR)],
        descricao=f"criando venv em {_VENV_DIR}",
    )
    if not venv_python.exists():
        print(
            f"[dev_watch] ERRO: venv criado, mas python nao encontrado em "
            f"{venv_python}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    _executar(
        [str(venv_python), "-m", "pip", "install", "-q", "--upgrade", "pip"],
        descricao="atualizando pip no venv novo",
    )
    return venv_python


def _pacote_disponivel(venv_python: Path, modulo: str) -> bool:
    """Verifica se `modulo` e importavel no Python de `venv_python`.

    Evita custo de subprocess quando o processo ATUAL ja e esse mesmo
    interpretador (tipicamente apos o reexec) -- tenta importar diretamente;
    caso contrario, spawna um processo filho descartavel so para o teste.
    """
    if Path(sys.executable).resolve() == venv_python.resolve():
        try:
            __import__(modulo)
            return True
        except ImportError:
            return False
    resultado = subprocess.run(
        [str(venv_python), "-c", f"import {modulo}"],
        capture_output=True,
    )
    return resultado.returncode == 0


def _instalar_dependencias(venv_python: Path, *, forcar: bool = False) -> None:
    """Instala `governance-runner` + `deep-agents-gateway[dev,sdk]` se ausentes.

    Idempotente: cada pacote so e (re)instalado se `forcar=True` ou se o
    import correspondente falhar no venv -- reexecucoes do script nao pagam
    o custo de reinstalar dependencias ja satisfeitas.
    """
    falta_runner = forcar or not _pacote_disponivel(venv_python, "governance_runner")
    falta_gateway = forcar or not _pacote_disponivel(venv_python, "local_chat_gateway")
    falta_uvicorn = forcar or not _pacote_disponivel(venv_python, "uvicorn")
    falta_sdk = forcar or not _pacote_disponivel(venv_python, "copilot")

    if falta_runner:
        if not _RUNNER_DIR.exists():
            print(
                f"[dev_watch] ERRO: dependencia local 'governance-runner' nao "
                f"encontrada em {_RUNNER_DIR}",
                file=sys.stderr,
            )
            raise SystemExit(1)
        _executar(
            [str(venv_python), "-m", "pip", "install", "-q", "-e", str(_RUNNER_DIR)],
            descricao="instalando dependencia local 'governance-runner' (editable)",
        )

    if falta_gateway or falta_uvicorn or falta_sdk:
        _executar(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-q",
                "-e",
                f"{GATEWAY_DIR}[dev,sdk]",
            ],
            descricao="instalando 'deep-agents-gateway[dev,sdk]' (editable, 1a vez pode levar ~1min)",
        )


def _reexec_no_venv_se_necessario(venv_python: Path) -> None:
    """Reexecuta este script com o Python de `venv_python`, se preciso.

    Evita a classe de erro "did not find executable at ...python.exe": o
    `python`/`py` do PATH pode ser um shim quebrado alheio a este projeto.
    So reexecuta quando `sys.executable` atual nao e esse mesmo interprete
    -- idempotente (a 2a execucao, ja dentro do venv, nao reexecuta de novo).
    """
    executavel_atual = Path(sys.executable).resolve()
    if executavel_atual == venv_python.resolve():
        return  # Ja estamos rodando dentro do venv correto.

    print(
        f"[dev_watch] Interpretador atual ({executavel_atual}) nao e o venv "
        f"do gateway -- reexecutando com {venv_python}",
        file=sys.stderr,
    )
    resultado = subprocess.run(
        [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]]
    )
    raise SystemExit(resultado.returncode)


# Mapeia: nome da env var -> path local default (so aplicado se a variavel
# ainda carrega o valor DEFAULT de container, nunca sobrescreve um valor
# customizado que o dev ja tenha definido explicitamente no shell/.env com
# um path fora do container, ex.: "D:\\workspace\\...").
_CONTAINER_DEFAULTS_TO_LOCAL: dict[str, tuple[str, Path]] = {
    "GOVERNANCE_GRAPH_PATH": (
        "/governance/.github/agents/routing-graph.yaml",
        GITHUB_DIR / "agents" / "routing-graph.yaml",
    ),
    "GOVERNANCE_GITHUB_DIR": (
        "/governance/.github",
        GITHUB_DIR,
    ),
    "PROJECTS_LOCAL_YAML": (
        "/governance/.github/projects.local.yaml",
        GITHUB_DIR / "projects.local.yaml",
    ),
    "GATEWAY_WORKSPACE_DIR": (
        "/workspaces",
        REPO_ROOT,
    ),
}


def _garantir_dot_env() -> None:
    """Gera `.env` a partir de `.env.example` se ausente, com valores seguros.

    Substitui os placeholders `GATEWAY_API_KEY=change-me` e
    `WEB_ACCESS_CODE=change-me` por valores aleatorios unicos (`uuid4`) --
    dispensa o passo manual `cp .env.example .env` + edicao. Nunca
    sobrescreve um `.env` ja existente (preserva customizacoes do dev).
    """
    env_path = GATEWAY_DIR / ".env"
    if env_path.exists():
        return

    example_path = GATEWAY_DIR / ".env.example"
    if not example_path.exists():
        print(
            f"[dev_watch] AVISO: nem .env nem .env.example encontrados em "
            f"{GATEWAY_DIR}.",
            file=sys.stderr,
        )
        return

    print("[dev_watch] .env ausente -- gerando a partir de .env.example ...")
    conteudo = example_path.read_text(encoding="utf-8")
    conteudo = conteudo.replace(
        "GATEWAY_API_KEY=change-me", f"GATEWAY_API_KEY={uuid.uuid4()}"
    )
    conteudo = conteudo.replace(
        "WEB_ACCESS_CODE=change-me", f"WEB_ACCESS_CODE={uuid.uuid4().hex[:16]}"
    )
    env_path.write_text(conteudo, encoding="utf-8")
    print(
        f"[dev_watch] .env criado em {env_path} com GATEWAY_API_KEY/"
        "WEB_ACCESS_CODE gerados automaticamente."
    )


def _resolver_env_local() -> None:
    """Carrega `.env` e substitui defaults de container por paths locais.

    So atua sobre variaveis AUSENTES do shell e cujo valor em `.env` ainda
    seja literalmente o default de container documentado acima -- preserva
    qualquer customizacao explicita feita pelo desenvolvedor.
    """
    env_path = GATEWAY_DIR / ".env"

    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]

        load_dotenv(env_path, override=False)
    except ImportError:
        _carregar_dotenv_manual(env_path)

    for var_name, (container_default, local_path) in _CONTAINER_DEFAULTS_TO_LOCAL.items():
        valor_atual = os.environ.get(var_name, "")
        if valor_atual in ("", container_default):
            os.environ[var_name] = str(local_path)
            print(f"[dev_watch] {var_name} -> {local_path}")

    # GATEWAY_DB_PATH: default de producao e "/app/data/gateway.db" (inexistente
    # fora do container); usa um arquivo SQLite local dentro deste diretorio.
    db_path = os.environ.get("GATEWAY_DB_PATH", "")
    if db_path in ("", "/app/data/gateway.db"):
        data_dir = GATEWAY_DIR / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        os.environ["GATEWAY_DB_PATH"] = str(data_dir / "gateway.dev.db")
        print(f"[dev_watch] GATEWAY_DB_PATH -> {os.environ['GATEWAY_DB_PATH']}")

    # Telemetria OTel/Langfuse em modo dev (bug real reportado pelo usuario,
    # 2026-10-02): `config.Settings` le a variavel PADRAO
    # "OTEL_EXPORTER_OTLP_ENDPOINT" (nao "GATEWAY_OTEL_EXPORTER_OTLP_
    # ENDPOINT"). O `docker-compose.yml` traduz uma para a outra dentro do
    # container (ver comentario la sobre por que os nomes sao DELIBERADAMENTE
    # distintos -- evitar herdar silenciosamente "127.0.0.1:4318" de uma
    # variavel de SHELL usada pela telemetria da IDE) -- mas essa traducao
    # SO acontecia no Docker; rodando via `dev_watch.py` (fora do Docker),
    # preencher "GATEWAY_OTEL_EXPORTER_OTLP_ENDPOINT" no `.env` NUNCA tinha
    # efeito algum, e toda a telemetria (`telemetry.py`) ficava
    # silenciosamente em no-op -- sem nenhum erro visivel, exatamente como
    # reportado ("Langfuse nao recebe dados do chat em modo dev"). Replica
    # aqui a MESMA traducao do compose, com um detalhe a mais: o default de
    # DEV (ao contrario do Docker, que aponta para o hostname interno
    # "otel-collector") e o proxy OTel STANDALONE do host documentado em
    # `docs/context/setup-telemetry-copilot.md` ("otel-proxy", publicado em
    # "127.0.0.1:4318") -- o MESMO coletor ja usado pela telemetria da IDE.
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        endpoint_gateway = os.environ.get("GATEWAY_OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
        endpoint_efetivo = endpoint_gateway or "http://127.0.0.1:4318"
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = endpoint_efetivo
        print(
            f"[dev_watch] OTEL_EXPORTER_OTLP_ENDPOINT -> {endpoint_efetivo} "
            "(telemetria OTel/Langfuse ativa em modo dev)"
        )

    # Garante binding local explicito mesmo que GATEWAY_BIND esteja vazio.
    os.environ.setdefault("GATEWAY_BIND", "127.0.0.1")
    os.environ.setdefault("GATEWAY_PORT", "8080")


def _carregar_dotenv_manual(env_path: Path) -> None:
    """Fallback sem a lib `python-dotenv` (nem sempre instalada no venv do gateway)."""
    if not env_path.exists():
        return
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        valor = valor.strip()
        os.environ.setdefault(chave, valor)


def _verificar_secret_token() -> None:
    """Avisa (sem bloquear) se `secrets/copilot_token` estiver ausente/vazio.

    Unica credencial que este script NAO consegue gerar sozinho (token
    pessoal do GitHub Copilot) -- cria o diretorio `secrets/` se faltar,
    para o dev so precisar colar o token no arquivo.
    """
    secrets_dir = GATEWAY_DIR / "secrets"
    secrets_dir.mkdir(exist_ok=True)
    token_file = secrets_dir / "copilot_token"
    if not token_file.exists() or not token_file.read_text(encoding="utf-8").strip():
        print(
            "[dev_watch] AVISO: secrets/copilot_token ausente/vazio -- o "
            "gateway vai responder em modo STUB ate voce colocar um "
            "PAT/token real do Copilot SDK la, ex.:\n"
            f'    echo "<seu-token>" > {token_file}',
            file=sys.stderr,
        )


def _validar_pre_requisitos() -> None:
    """Checagem rapida e amigavel antes de subir o uvicorn (fail-fast local).

    Checagens de dependencia (`local_chat_gateway`/`copilot` importaveis) ja
    sao garantidas pelo bootstrap (`_ensure_venv`/`_instalar_dependencias`)
    antes do reexec -- esta funcao so valida configuracao (`.env`/grafo).
    """
    if os.environ.get("GATEWAY_API_KEY", "change-me") == "change-me":
        print(
            "[dev_watch] ERRO: GATEWAY_API_KEY esta 'change-me' em .env. "
            "Defina um valor real antes de continuar.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    grafo = Path(os.environ["GOVERNANCE_GRAPH_PATH"])
    if not grafo.exists():
        print(
            f"[dev_watch] ERRO: GOVERNANCE_GRAPH_PATH nao existe: {grafo}",
            file=sys.stderr,
        )
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host", default=None, help="Override de GATEWAY_BIND (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Override de GATEWAY_PORT (default: 8080)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Desativa o hot-reload (util com debugger attachado via breakpoint)",
    )
    parser.add_argument(
        "--no-bootstrap",
        action="store_true",
        help="Pula criacao de venv/instalacao de dependencias (assume ja prontos)",
    )
    parser.add_argument(
        "--reinstall",
        action="store_true",
        help="Forca reinstalacao das dependencias editaveis mesmo se ja presentes",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
    )
    args = parser.parse_args()

    if not args.no_bootstrap:
        venv_python = _ensure_venv()
        _instalar_dependencias(venv_python, forcar=args.reinstall)
    else:
        venv_python = _venv_python_path()

    if venv_python.exists():
        _reexec_no_venv_se_necessario(venv_python)

    _garantir_dot_env()
    _resolver_env_local()
    _verificar_secret_token()
    _validar_pre_requisitos()

    host = args.host or os.environ.get("GATEWAY_BIND", "127.0.0.1")
    port = args.port or int(os.environ.get("GATEWAY_PORT", "8080"))

    if _porta_ocupada(host, port):
        print(
            f"[dev_watch] ERRO: a porta {port} ja esta em uso em {host}. "
            "Libere-a antes de continuar (PowerShell):\n"
            f"    Get-NetTCPConnection -LocalPort {port} | "
            "Select-Object -Property OwningProcess\n"
            "    Stop-Process -Id <PID> -Force\n"
            f"Ou use outra porta: python dev_watch.py --port {port + 1}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    import uvicorn

    print(
        f"[dev_watch] Subindo Deep Agents Gateway em http://{host}:{port} "
        f"(reload={'OFF' if args.no_reload else 'ON'}, permission_mode="
        f"{os.environ.get('GATEWAY_PERMISSION_MODE', 'read_only')})"
    )
    uvicorn.run(
        "local_chat_gateway.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=not args.no_reload,
        reload_dirs=[str(GATEWAY_DIR / "src")],
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()


