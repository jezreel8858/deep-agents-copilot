"""Configurações globais e fixtures para a suíte unitária de local_chat_gateway."""

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[4]
_pkg_src = _repo_root / "deploy" / "local-chat-gateway" / "src"
_core_src = _repo_root / "src"

for p in [str(_pkg_src), str(_core_src)]:
    if p not in sys.path:
        sys.path.insert(0, p)
