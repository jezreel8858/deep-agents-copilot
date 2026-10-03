"""
Invariants test for sync_execution_protocol.py (R-059 / R-060 / R-051).

Garante que o script de sincronização de protocolo de execução:
1. Retorna exit code 0 (drift=0) no estado atual do repositório com --check.
2. É idempotente: rodar --apply duas vezes consecutivas resulta em zero arquivos
   modificados na segunda execução.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "tools" / "agent_protocol_sync" / "sync_execution_protocol.py"


def test_sync_execution_protocol_check_returns_zero():
    """Valida que o estado atual do repositório possui drift=0 em relação ao fragmento canônico."""
    cmd = [sys.executable, str(SCRIPT_PATH), "--check"]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"sync_execution_protocol.py --check falhou com exit code {proc.returncode}.\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "Agents com drift detectado: 0" in proc.stdout


def test_sync_execution_protocol_apply_is_idempotent():
    """Valida que execuções sucessivas de --apply não causam re-modificações (idempotência estrita)."""
    # 1ª execução de apply
    cmd_apply = [sys.executable, str(SCRIPT_PATH), "--apply"]
    proc1 = subprocess.run(cmd_apply, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc1.returncode == 0, f"1ª execução de --apply falhou: {proc1.stderr}"

    # 2ª execução de apply: deve ter 0 atualizações e 0 drift
    proc2 = subprocess.run(cmd_apply, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc2.returncode == 0, f"2ª execução de --apply falhou: {proc2.stderr}"
    assert "Agents com drift detectado: 0" in proc2.stdout
    assert "Agents corrigidos nesta execucao" not in proc2.stdout
def test_arquivos_sem_ctx_tool_sao_excluidos_do_bloco():
    """Garante determinísticamente que arquivos .agent.md e .prompt.md sem
    ferramentas context-mode/ctx_* declaradas em tools: NUNCA contenham o bloco
    <execution_protocol> (prevenção de instrução morta)."""
    try:
        import yaml
    except ImportError:
        yaml = None

    agents_dir = REPO_ROOT / ".github" / "agents"
    prompts_dir = REPO_ROOT / ".github" / "prompts"

    files_to_check: list[Path] = []
    files_to_check.extend([p for p in sorted(agents_dir.glob("**/*.agent.md")) if "templates" not in p.parts])
    files_to_check.extend([p for p in sorted(prompts_dir.glob("**/*.prompt.md")) if "templates" not in p.parts])

    assert len(files_to_check) > 100, f"Esperado > 100 arquivos para checagem, encontrado {len(files_to_check)}"

    violations: list[str] = []
    for fp in files_to_check:
        text = fp.read_text(encoding="utf-8")
        tools: list[str] = []
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                if yaml is not None:
                    try:
                        data = yaml.safe_load(parts[1]) or {}
                        raw_tools = data.get("tools", [])
                        if isinstance(raw_tools, list):
                            tools = [str(t) for t in raw_tools]
                        elif isinstance(raw_tools, str):
                            tools = [raw_tools]
                    except Exception:
                        pass
                if not tools:
                    in_tools = False
                    for line in parts[1].splitlines():
                        if re.match(r"^tools:\s*$", line):
                            in_tools = True
                            continue
                        elif in_tools and re.match(r"^\s+-\s+(.*)$", line):
                            m = re.match(r"^\s+-\s+(.*)$", line)
                            if m:
                                tools.append(m.group(1).strip().strip("'").strip('"'))
                        elif in_tools and (line.startswith(" ") or line.startswith("	")):
                            continue
                        elif in_tools:
                            in_tools = False
                        inline_m = re.match(r"^tools:\s*\[(.*)\]", line)
                        if inline_m:
                            items = [x.strip().strip("'").strip('"') for x in inline_m.group(1).split(",") if x.strip()]
                            tools.extend(items)

        has_ctx = any(isinstance(t, str) and t.startswith("context-mode/ctx_") for t in tools)
        has_block = "<execution_protocol>" in text or "</execution_protocol>" in text

        if not has_ctx and has_block:
            violations.append(
                f"{fp.relative_to(REPO_ROOT)}: sem context-mode/ctx_* em tools:, "
                f"mas contém bloco <execution_protocol>"
            )

    assert not violations, (
        f"{len(violations)} arquivo(s) sem context-mode/ctx_* contêm o bloco <execution_protocol>:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
