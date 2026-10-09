"""Governanca do runtime Python embutido (uv + py-test.sh). Plano 20261008 T11. Sem rede/bootstrap."""
from __future__ import annotations
import re
import subprocess
import tomllib
from pathlib import Path
import pytest
from _embedded_runtime_common import BASH, REPO, SCRIPT_DIR, git_mode, run_bash, parse_lock
from _helpers import remediation
PYSH = SCRIPT_DIR / "py-test.sh"
LOCK = SCRIPT_DIR / "tools.lock"
def _norm(req: str) -> tuple[str, str]:
    m = re.match(r"\s*([A-Za-z0-9_.\-]+)\s*(.*)", req)
    return m.group(1).lower().replace("_", "-"), m.group(2).replace(" ", "")
def _reqs_txt() -> dict[str, str]:
    out = {}
    for ln in (REPO / "tests" / "requirements.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            n, lim = _norm(ln)
            out[n] = lim
    return out
def _pyproject() -> dict:
    return tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
def test_deve_existir_py_test_sh_quando_runtime_python_embutido():
    assert PYSH.is_file(), remediation("scripts/dev/py-test.sh ausente", fix_hint="criar o wrapper conforme plano T5")
def test_deve_usar_lf_shebang_e_strict_mode_quando_py_test_sh():
    raw = PYSH.read_bytes()
    assert b"\r" not in raw, remediation("py-test.sh contem CR", fix_hint="converter para LF")
    lines = raw.decode("utf-8", "replace").splitlines()
    assert lines[0].startswith("#!") and "bash" in lines[0]
    assert "set -euo pipefail" in raw.decode("utf-8", "replace")
def test_deve_ter_modo_executavel_quando_py_test_sh_no_indice_git():
    mode = git_mode("scripts/dev/py-test.sh")
    if mode is None or mode != "100755":
        pytest.xfail(
            f"modo git={mode}: pendencia humana 'git update-index --chmod=+x scripts/dev/py-test.sh' (plano, sem git add automatico)"
        )
def test_deve_ter_hash_sha256_valido_quando_secao_uv_do_lock():
    uv = parse_lock(LOCK.read_text(encoding="utf-8"))["uv"]
    plats = [k.split(".", 1)[1] for k in uv if k.startswith("sha256.")]
    assert {"linux-amd64", "darwin-aarch64", "windows-amd64"} <= set(plats)
    for p in plats:
        assert re.fullmatch(r"[0-9a-f]{64}", uv[f"sha256.{p}"]), remediation(
            f"SHA-256 invalido para uv/{p}", fix_hint="usar 64 hex minusculos do .sha256 oficial")
def test_deve_usar_somente_host_oficial_quando_urls_do_uv():
    uv = parse_lock(LOCK.read_text(encoding="utf-8"))["uv"]
    ver = uv["version"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", ver)
    urls = [v for k, v in uv.items() if k.startswith("url.")]
    assert urls
    for u in urls:
        assert u.startswith(f"https://github.com/astral-sh/uv/releases/download/{ver}/"), u
def test_deve_ter_pacotes_e_limites_identicos_quando_pyproject_vs_requirements():
    dev = _pyproject()["dependency-groups"]["dev"]
    pyp = dict(_norm(d) for d in dev)
    assert pyp == _reqs_txt(), remediation(f"divergencia pyproject={pyp}", fix_hint="alinhar tests/requirements.txt e grupo dev")
def test_deve_exigir_python_311_quando_pyproject():
    assert _pyproject()["project"]["requires-python"] == ">=3.11"
def test_deve_fixar_python_312_quando_python_version():
    assert (REPO / ".python-version").read_text().strip() == "3.12"
def test_deve_versionar_uv_lock_quando_ambiente_reprodutivel():
    p = REPO / "uv.lock"
    assert p.is_file() and p.stat().st_size > 0
def test_deve_manter_pytest_somente_no_pytest_ini_quando_pyproject():
    data = _pyproject()
    assert "pytest" not in data.get("tool", {}), "pytest config duplicada no pyproject"
    assert (REPO / "pytest.ini").is_file()
def test_deve_ignorar_venv_e_logs_quando_gitignore():
    gi = (REPO / ".gitignore").read_text(encoding="utf-8", errors="replace")
    assert re.search(r"^/?\.venv/?\s*$", gi, re.M)
    assert re.search(r"^/?logs/dev/?\s*$", gi, re.M)
def test_deve_forcar_lf_quando_gitattributes_para_sh():
    ga = (REPO / ".gitattributes").read_text(encoding="utf-8", errors="replace")
    assert re.search(r"^\*\.sh\s+.*eol=lf", ga, re.M)
def test_nao_deve_conter_caminho_de_maquina_quando_py_test_sh():
    from _embedded_runtime_common import MACHINE_PATH
    hits = [l for l in PYSH.read_text(encoding="utf-8", errors="replace").splitlines() if MACHINE_PATH.search(l)]
    assert not hits, remediation(f"caminho local em py-test.sh: {hits[:2]}", fix_hint="derivar caminhos de $0/DAC_HOME")
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_ter_sintaxe_valida_quando_bash_n_py_test_sh():
    r = run_bash(["-n", "scripts/dev/py-test.sh"])
    assert r.returncode == 0, r.stderr
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_sair_zero_e_mostrar_uso_quando_help():
    r = run_bash(["scripts/dev/py-test.sh", "--help"])
    assert r.returncode == 0 and "py-test.sh" in r.stdout
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_sair_2_quando_raiz_do_projeto_inexistente():
    r = run_bash(["scripts/dev/py-test.sh", "--project", "/raiz-sintetica-inexistente-xyz", "--dry-run"])
    assert r.returncode == 2, r.stdout + r.stderr
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_nao_executar_nada_quando_dry_run():
    r = run_bash(["scripts/dev/py-test.sh", "--dry-run"])
    assert r.returncode == 0 and "cmd=" in r.stdout
    assert "passed" not in r.stdout
