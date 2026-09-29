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
