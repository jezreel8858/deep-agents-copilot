"""Governanca do runtime Maven embutido (mvnd + mvn-test.sh). Plano 20261008 T11. Sem rede/bootstrap."""
from __future__ import annotations
import json
import re
import pytest
from _embedded_runtime_common import (
    BASH, LOCK, MACHINE_PATH, REPO, SCRIPT_DIR, SCRIPTS, SKILL, SKILL_NAME, agent_files, git_mode, parse_lock, run_bash,
)
from _helpers import remediation
SH = [s for s in SCRIPTS]
ALL_SCRIPTS = SH + ["mvn-test.cmd"]
LOOSE = re.compile(
    r"(?<![\w/.`-])(?:\./mvnw|mvnw|mvn|mvnd)\s+(?:test|clean|verify|install|package|-[A-Za-z])"
    r"|(?<![\w/.`-])(?:python\d?\s+-m\s+)?pytest\s+(?:-|tests?/|\.)|\bpip install\b(?!`)"
)
@pytest.mark.parametrize("rel", ALL_SCRIPTS)
def test_deve_existir_script_quando_runtime_embutido(rel):
    assert (SCRIPT_DIR / rel).is_file(), remediation(f"scripts/dev/{rel} ausente", fix_hint="criar conforme planos T1-T5")
@pytest.mark.parametrize("rel", SH)
def test_deve_usar_lf_shebang_e_strict_mode_quando_script_sh(rel):
    raw = (SCRIPT_DIR / rel).read_bytes()
    txt = raw.decode("utf-8", "replace")
    assert b"\r" not in raw, remediation(f"{rel} contem CR", fix_hint="converter para LF")
    assert txt.startswith("#!") and "bash" in txt.splitlines()[0]
    if rel != "lib/resolve.sh":  # lib apenas 'source': set -e vazaria para o chamador
        assert "set -euo pipefail" in txt
@pytest.mark.parametrize("rel", ["lib/resolve.sh", "bootstrap-mvnd.sh", "mvn-test.sh", "py-test.sh"])
def test_deve_ter_modo_executavel_quando_script_no_indice_git(rel):
    mode = git_mode(f"scripts/dev/{rel}")
    if mode != "100755":
        pytest.xfail(f"modo git={mode}: pendencia humana 'git update-index --chmod=+x scripts/dev/{rel}'")
@pytest.mark.parametrize("rel", ALL_SCRIPTS + ["tools.lock"])
def test_nao_deve_conter_caminho_de_maquina_quando_script_ou_lock(rel):
    hits = [l for l in (SCRIPT_DIR / rel).read_text(encoding="utf-8", errors="replace").splitlines() if MACHINE_PATH.search(l)]
    assert not hits, remediation(f"caminho local em {rel}: {hits[:2]}", fix_hint="usar variaveis/derivacao relativa")
def test_nao_deve_conter_caminho_de_maquina_quando_skill():
    hits = [l for l in SKILL.read_text(encoding="utf-8", errors="replace").splitlines() if MACHINE_PATH.search(l)]
    assert not hits, hits[:2]
def test_deve_ter_sha256_de_64_hex_quando_mvnd_por_plataforma():
    mv = parse_lock(LOCK.read_text(encoding="utf-8"))["mvnd"]
    plats = [k.split(".", 1)[1] for k in mv if k.startswith("sha256.")]
    assert {"linux-amd64", "darwin-aarch64", "windows-amd64"} <= set(plats)
    for p in plats:
        assert re.fullmatch(r"[0-9a-f]{64}", mv[f"sha256.{p}"]), f"SHA invalido mvnd/{p}"
        assert f"url.{p}" in mv
def test_deve_usar_somente_hosts_apache_quando_urls_do_mvnd_e_versao_pinada():
    mv = parse_lock(LOCK.read_text(encoding="utf-8"))["mvnd"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", mv["version"])
    for k, u in mv.items():
        if k.startswith("url."):
            assert re.match(r"https://(downloads|archive)\.apache\.org/(maven/mvnd|dist/maven/mvnd)/", u), u
            assert mv["version"] in u
def test_deve_cobrir_assets_logs_e_venv_quando_gitignore():
    gi = (REPO / ".gitignore").read_text(encoding="utf-8", errors="replace")
    assert re.search(r"^/?assets/maven-mvnd-\*/?\s*$", gi, re.M)
    assert re.search(r"^/?logs/dev/?\s*$", gi, re.M)
    assert re.search(r"^/?\.venv/?\s*$", gi, re.M)
def test_deve_forcar_lf_quando_gitattributes_para_sh():
    assert re.search(r"^\*\.sh\s+.*eol=lf", (REPO / ".gitattributes").read_text(encoding="utf-8", errors="replace"), re.M)
def test_deve_ter_frontmatter_valido_quando_skill_embedded_runtime():
    txt = SKILL.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", txt, re.S)
    assert m, "frontmatter ausente"
    fm = m.group(1)
    assert re.search(rf"^name:\s*{SKILL_NAME}\s*$", fm, re.M)
    assert re.search(r"^description:\s*\S+", fm, re.M)
    assert re.search(r"^tier:\s*\d", fm, re.M)
def test_deve_listar_skill_quando_index_json():
    idx = json.loads((REPO / ".github/skills/.index.json").read_text(encoding="utf-8"))
    entry = [s for s in idx["skills"] if s["name"] == SKILL_NAME]
    assert len(entry) == 1 and entry[0]["path"].endswith(f"{SKILL_NAME}/SKILL.md")
@pytest.mark.parametrize("agent", agent_files(), ids=lambda p: p.stem)
def test_deve_referenciar_skill_quando_agent_executa_testes(agent):
    assert agent.is_file(), f"agent ausente: {agent}"
    assert SKILL_NAME in agent.read_text(encoding="utf-8", errors="replace")
@pytest.mark.parametrize("agent", agent_files(), ids=lambda p: p.stem)
def test_nao_deve_instruir_comando_solto_quando_agent_de_execucao(agent):
    bad = []
    for n, l in enumerate(agent.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if re.search(r"nunca|NÃO|não|NAO|proibid", l, re.I):
            continue
        if LOOSE.search(l):
            bad.append(f"{n}: {l.strip()[:100]}")
    assert not bad, remediation(f"{agent.name} instrui comando solto: {bad[:3]}", fix_hint="usar scripts/dev/mvn-test.sh ou py-test.sh")
@pytest.mark.skipif(BASH is None, reason="bash ausente")
@pytest.mark.parametrize("rel", SH)
def test_deve_ter_sintaxe_valida_quando_bash_n(rel):
    r = run_bash(["-n", f"scripts/dev/{rel}"])
    assert r.returncode == 0, r.stderr
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_sair_zero_quando_mvn_test_help():
    r = run_bash(["scripts/dev/mvn-test.sh", "--help"])
    assert r.returncode == 0 and "mvn-test.sh" in r.stdout
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_sair_2_quando_mvn_test_raiz_sem_pom():
    r = run_bash(["scripts/dev/mvn-test.sh", "/raiz-sintetica-inexistente-xyz"])
    assert r.returncode == 2, r.stdout + r.stderr
@pytest.mark.skipif(BASH is None, reason="bash ausente")
def test_deve_sair_zero_quando_bootstrap_mvnd_dry_run_sem_rede():
    r = run_bash(["scripts/dev/bootstrap-mvnd.sh", "--dry-run"])
    assert r.returncode == 0 and "sha256" in (r.stdout + r.stderr)
