"""Utilitarios compartilhados pelos testes de governanca do runtime embutido (dados reais do repo, sem rede)."""
from __future__ import annotations
import re
import shutil
import subprocess
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
SCRIPTS = ["lib/resolve.sh", "bootstrap-mvnd.sh", "mvn-test.sh", "py-test.sh"]
SCRIPT_DIR = REPO / "scripts" / "dev"
LOCK = SCRIPT_DIR / "tools.lock"
SKILL = REPO / ".github" / "skills" / "embedded-runtime-governance" / "SKILL.md"
SKILL_NAME = "embedded-runtime-governance"
AGENT_GLOBS = [
    "backend/spring-boot/spring-boot-{developer,test-engineer}",
    "backend/spring-reactive/spring-reactive-{developer,test-engineer}",
    "backend/ejb/ejb-{developer,test-engineer}",
    "backend/struts/struts-{developer,test-engineer}",
    "backend/python/python-{arch-advisor,developer,router,test-engineer}",
    "pr-gatekeeper",
    "runtime-verifier",
]
MACHINE_PATH = re.compile(
    r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/|/home/[a-z]|workspace[\\/]",
    re.I,
)
BASH = shutil.which("bash")
def agent_files() -> list[Path]:
    out: list[Path] = []
    base = REPO / ".github" / "agents"
    for pat in AGENT_GLOBS:
        m = re.match(r"(.*)\{(.*)\}(.*)", pat)
        names = [m.group(1) + o + m.group(3) for o in m.group(2).split(",")] if m else [pat]
        out += [base / f"{n}.agent.md" for n in names]
    return out
def parse_lock(text: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = line[1:-1]
            sections[cur] = {}
        elif "=" in line and cur:
            k, v = line.split("=", 1)
            sections[cur][k.strip()] = v.strip()
    return sections
def git_mode(rel: str) -> str | None:
    r = subprocess.run(["git", "ls-files", "-s", rel], cwd=REPO, capture_output=True, text=True, timeout=30)
    return r.stdout.split()[0] if r.stdout.strip() else None
def run_bash(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, *args], cwd=REPO, capture_output=True, text=True, timeout=timeout)
