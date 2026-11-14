"""Lock exclusivo `.model-profiles/lock` (PID + timestamp) com retomada de lock obsoleto."""
from __future__ import annotations

import contextlib
import json
import logging
import math
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Iterator

from tools.model_profiles.errors import ModelProfilesError

logger = logging.getLogger(__name__)

STATE_DIR = ".model-profiles"
LOCK_NAME = "lock"
STALE_AFTER_SECONDS = 3600
_UNREADABLE_GRACE = 10


class LockError(ModelProfilesError):
    code = "LOCKED"


def lock_path(repo: Path) -> Path:
    return repo / STATE_DIR / LOCK_NAME


def _pid_alive_windows(pid: int) -> bool:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return ctypes.get_last_error() == 5  # acesso negado => existe
    code = wintypes.DWORD()
    ok = kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
    kernel32.CloseHandle(handle)
    return bool(ok) and code.value == 259  # STILL_ACTIVE


def pid_alive(pid: int) -> bool:
    """Nunca usa os.kill no Windows (TerminateProcess)."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        return _pid_alive_windows(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _parse(data: dict) -> tuple[int, float] | None:
    """(pid, timestamp) validados por tipo/faixa; None => malformado."""
    pid, ts = data.get("pid"), data.get("timestamp")
    if isinstance(pid, bool) or not isinstance(pid, int) or not 0 < pid < 2**31:
        return None
    if isinstance(ts, bool) or not isinstance(ts, (int, float)) or not math.isfinite(ts):
        return None
    return pid, float(ts)


def _identity(data: dict | None) -> tuple | None:
    return None if data is None else (data.get("pid"), data.get("timestamp"), data.get("token"))


def is_stale(path: Path) -> bool:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return True
    data = _read(path)
    if data is None:  # ainda sendo escrito ou corrompido
        return time.time() - mtime > _UNREADABLE_GRACE
    parsed = _parse(data)
    if parsed is None:  # pid/timestamp malformados => lock corrompido
        logger.warning("lock malformado (pid/timestamp invalidos): %s", path)
        return True
    pid, ts = parsed
    return time.time() - ts > STALE_AFTER_SECONDS or not pid_alive(pid)


def lock_state(repo: Path) -> str:
    """'absent' | 'live' | 'stale'."""
    path = lock_path(repo)
    if not path.exists():
        return "absent"
    return "stale" if is_stale(path) else "live"


def _try_create(path: Path) -> str | None:
    """Cria o lock com O_EXCL; devolve o token proprio ou None se ja existe."""
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return None
    token = uuid.uuid4().hex
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump({"pid": os.getpid(), "timestamp": time.time(), "token": token}, fh)
    return token


def _unique_name(path: Path) -> Path:
    return path.with_name(f"{LOCK_NAME}.{os.getpid()}.{uuid.uuid4().hex}.claim")


def _put_back(claimed: Path, path: Path) -> None:
    """Devolve o lock tomado por engano sem sobrescrever um novo dono."""
    try:
        os.link(claimed, path)
    except FileExistsError:
        pass  # outro processo ja criou um lock novo
    except OSError:
        with contextlib.suppress(OSError):
            if not path.exists():
                os.rename(claimed, path)
    with contextlib.suppress(OSError):
        claimed.unlink()


def _claim_stale(path: Path) -> bool:
    """Rename atomico para nome unico; relê (pid,timestamp) antes de remover. False => perdeu."""
    before = _identity(_read(path))
    claimed = _unique_name(path)
    try:
        os.rename(path, claimed)
    except FileNotFoundError:
        return True  # alguem removeu primeiro; basta tentar criar
    except OSError:
        return False
    if _identity(_read(claimed)) != before or not is_stale(claimed):
        _put_back(claimed, path)  # era um lock vivo que substituiu o obsoleto
        return False
    with contextlib.suppress(OSError):
        claimed.unlink()
    return True


def _owner(path: Path) -> object:
    pid = (_read(path) or {}).get("pid")
    return pid if isinstance(pid, int) and not isinstance(pid, bool) else "?"


def _acquire(path: Path) -> str:
    for _ in range(3):
        token = _try_create(path)
        if token:
            return token
        if not is_stale(path) or not _claim_stale(path):
            raise LockError(f"outra instancia (pid {_owner(path)}) mantem {STATE_DIR}/{LOCK_NAME}")
        logger.warning("lock obsoleto reivindicado: %s", path)
    raise LockError(f"nao foi possivel adquirir {STATE_DIR}/{LOCK_NAME}")


def _release(path: Path, token: str) -> None:
    """So remove lock legivel com token E pid proprios (rename atomico + verificacao)."""
    claimed = _unique_name(path)
    try:
        os.rename(path, claimed)
    except OSError:
        return
    data = _read(claimed)
    if data is not None and data.get("token") == token and data.get("pid") == os.getpid():
        try:
            claimed.unlink()
        except OSError:
            logger.warning("nao foi possivel remover %s", claimed)
    else:
        _put_back(claimed, path)


@contextlib.contextmanager
def exclusive_lock(repo: Path) -> Iterator[None]:
    path = lock_path(repo)
    path.parent.mkdir(exist_ok=True)
    token = _acquire(path)
    try:
        yield
    finally:
        _release(path, token)
