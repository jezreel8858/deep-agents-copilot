"""
test_local_project_isolation.py — Suíte de testes para garantir 100% de conformidade com
as regras de isolamento e anonimização de projetos locais (R-038, R-043 e R-044).

Garante que:
1. Nenhum arquivo rastreado no repositório faz referência a projetos locais/externos privados.
2. As regras de gitignore para .github/projects.local.yaml e .github/instructions/local/ são rigorosamente respeitadas (R-043).
3. Caminhos absolutos de máquina local ou IDs de usuário reais nunca vazam para arquivos versionados.
4. O catálogo de agents (.github/agents/catalog.yaml) permanece 100% desacoplado de instâncias de projetos locais.
5. docs/ai-context/catalog.yaml foi extinto em favor da arquitetura limpa (Cenário 2).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import read_workflows_full_content

REPO_ROOT = Path(__file__).resolve().parents[2]
THIS_REPO_NAME = REPO_ROOT.name.lower()
THIS_REPO_TOKENS = {THIS_REPO_NAME, "deep-agents-copilot", "deep_agents_copilot", "deep agents copilot"}


def get_git_tracked_files(root: Path = REPO_ROOT) -> list[Path]:
    """Retorna arquivos rastreados + não rastreados e não ignorados (Emenda B7: planos novos untracked)."""
    p = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root, capture_output=True, text=True, encoding="utf-8",
    )
    if p.returncode != 0:
        pytest.fail(f"Falha ao executar 'git ls-files --cached --others --exclude-standard': {p.stderr}")
    seen: dict[str, Path] = {}
    for f in p.stdout.splitlines():
        if f.strip():
            seen.setdefault(f.strip(), root / f.strip())
    return list(seen.values())


_SCAN_SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".db", ".sqlite", ".jar", ".exe", ".dll", ".zip", ".gz", ".class", ".war"}
_SCAN_SKIP_FILENAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json"}
_SCAN_MAX_BYTES = 2_000_000
MIN_FORBIDDEN_IDENTIFIER_LEN = 5


def iter_scannable_files(root: Path = REPO_ROOT) -> list[tuple[Path, str]]:
    """Arquivos de texto visíveis ao Git (rastreados + untracked não ignorados), exceto binários/grandes/lockfiles."""
    result: list[tuple[Path, str]] = []
    for fpath in get_git_tracked_files(root):
        if not fpath.is_file() or fpath.suffix.lower() in _SCAN_SKIP_SUFFIXES or fpath.name in _SCAN_SKIP_FILENAMES:
            continue
        try:
            if fpath.stat().st_size > _SCAN_MAX_BYTES:
                continue
            result.append((fpath, fpath.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return result


def _parse_projects_fallback(text: str) -> list[dict]:
    """Parser tolerante (por linha) para overlay com YAML inválido (ex.: barras invertidas sem escape).

    Evita que um erro de sintaxe do overlay local resulte em conjunto vazio silencioso (Emenda B7).
    """
    projects: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        m_id = re.match(r'^\s*-\s*id:\s*"?([^"#\n]*?)"?\s*(?:#.*)?$', line)
        if m_id:
            current = {"id": m_id.group(1)}
            projects.append(current)
            continue
        m_kv = re.match(r'^\s*(name|path_externo):\s*"(.*?)"\s*(?:#.*)?$', line)
        if m_kv and current is not None:
            current[m_kv.group(1)] = m_kv.group(2).replace("\\\\", "\\")
    return projects


def get_forbidden_project_identifiers(root: Path = REPO_ROOT) -> set[str]:
    """Coleta dinamicamente todos os IDs e nomes de projetos locais externos registrados em projects.local.yaml."""
    forbidden = set()

    # Lê dinamicamente o overlay local da máquina do desenvolvedor (R-043)
    catalog_local = root / ".github" / "projects.local.yaml"
    if not catalog_local.exists():
        catalog_local = root / "docs" / "ai-context" / "catalog.local.yaml"

    if catalog_local.exists():
        try:
            text = catalog_local.read_text(encoding="utf-8")
            try:
                projetos = (yaml.safe_load(text) or {}).get("projetos", []) or []
            except yaml.YAMLError:
                projetos = _parse_projects_fallback(text)
            for proj in projetos:
                p_id = (proj.get("id") or "").strip().lower()
                p_name = (proj.get("name") or "").strip().lower()
                p_path = (proj.get("path_externo") or "").strip()

                # Projetos cujo path_externo resolve DENTRO da própria raiz deste repositório
                # (ex.: sub-projetos do monorepo como apps/web ou deploy/local-chat-gateway)
                # NÃO são projetos locais externos privados.
                if p_path:
                    try:
                        resolved = Path(p_path).resolve()
                        if resolved == root or root in resolved.parents:
                            continue
                    except Exception:
                        pass

                if p_id and len(p_id) >= MIN_FORBIDDEN_IDENTIFIER_LEN and p_id not in THIS_REPO_TOKENS:
                    forbidden.add(p_id)
                if p_name and len(p_name) >= MIN_FORBIDDEN_IDENTIFIER_LEN and p_name not in THIS_REPO_TOKENS:
                    forbidden.add(p_name)
        except Exception:
            pass

    return forbidden


# ─────────────────────────────────────────────────────────────
# 1. Vazamento de Identificadores de Projetos Locais
# ─────────────────────────────────────────────────────────────

def find_identifier_leaks(root: Path = REPO_ROOT, identifiers: set[str] | None = None) -> list[str]:
    """Varre arquivos visíveis ao Git (rastreados + untracked não ignorados) sob `root` por identificadores proibidos.

    Mensagens são mascaradas (ID-LOCAL): nunca expõem o identificador encontrado.
    """
    forbidden_targets = get_forbidden_project_identifiers(root) if identifiers is None else identifiers
    media_extensions = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".db", ".sqlite", ".jar"}
    leaks: list[str] = []

    patterns = [
        re.compile(rf"(?<![a-zA-Z0-9]){re.escape(target)}(?![a-zA-Z0-9])", re.IGNORECASE)
        for target in forbidden_targets
    ]

    for fpath in get_git_tracked_files(root):
        if not fpath.exists():
            continue
        if fpath.suffix.lower() in media_extensions or fpath.name in _SCAN_SKIP_FILENAMES:
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            rel_path = fpath.relative_to(root).as_posix()
            for pattern in patterns:
                if pattern.search(content):
                    leaks.append(f"[{rel_path}] contém referência a projeto local proibido (ID-LOCAL)")
                    break
        except Exception as e:
            leaks.append(f"[{fpath}] Erro ao ler arquivo: {e}")
    return leaks


def test_no_local_projects_referenced_in_git_tracked_files():
    """Valida R-038 e R-044: nenhum arquivo visível ao Git (rastreado ou untracked não ignorado) pode referenciar projetos locais externos."""
    leaks = find_identifier_leaks()
    assert not leaks, (
        f"Foram detectadas {len(leaks)} referências a projetos locais em arquivos rastreados (violação R-038/R-044):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


# ─────────────────────────────────────────────────────────────
# 2. Guardrails do Gitignore (R-043)
# ─────────────────────────────────────────────────────────────

def test_r043_gitignore_isolation_rules():
    """Valida R-043: .github/projects.local.yaml e .github/instructions/local/ devem estar no .gitignore e não rastreados."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore deve existir na raiz do repositório"

    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    assert ".github/projects.local.yaml" in gitignore_content, (
        ".gitignore deve ignorar '.github/projects.local.yaml' (R-043)"
    )
    assert ".github/instructions/local/" in gitignore_content, (
        ".gitignore deve ignorar '.github/instructions/local/' (R-043)"
    )

    # Valida que nenhum arquivo em local/ ou projects.local.yaml está rastreado no git
    p_catalog = subprocess.run(
        ["git", "ls-files", ".github/projects.local.yaml"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert not p_catalog.stdout.strip(), (
        ".github/projects.local.yaml NUNCA deve ser rastreado pelo git (violação R-043)"
    )

    p_local_instructions = subprocess.run(
        ["git", "ls-files", ".github/instructions/local/"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert not p_local_instructions.stdout.strip(), (
        f"Arquivos sob .github/instructions/local/ NÃO devem ser rastreados: {p_local_instructions.stdout.strip()}"
    )


# ─────────────────────────────────────────────────────────────
# 3. Detecção de Caminhos Absolutos de Máquina Local (R-044)
# ─────────────────────────────────────────────────────────────

def test_no_machine_specific_paths_in_tracked_files():
    """Valida R-044: nenhum arquivo rastreado pode conter caminhos de máquina reais ou IDs de usuário."""
    tracked_files = get_git_tracked_files()

    # Regex para caminhos de máquina específicos não-genéricos
    user_id_pattern = re.compile(r'C:\\Users\\(?!\{username\}|<user>|Public|Default)[a-zA-Z0-9_-]+\\', re.IGNORECASE)

    media_extensions = {".png", ".jpg", ".jpeg", ".ico", ".svg", ".pyc", ".db", ".sqlite", ".jar"}
    leaks: list[str] = []

    for fpath in tracked_files:
        if not fpath.exists():
            continue
        if fpath.suffix.lower() in media_extensions:
            continue

        rel_path = fpath.relative_to(REPO_ROOT)
        lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()

        for idx, line in enumerate(lines, 1):
            line_lower = line.lower()
            if any(term in line_lower for term in ["regex", "padrao", "placeholder", "removidos", "exemplo ilustrativo", "exemplos ilustrativos", "pre-commit"]):
                continue

            if user_id_pattern.search(line):
                leaks.append(f"[{rel_path}:{idx}] Caminho de usuário real de máquina: {line.strip()}")

    assert not leaks, (
        f"Foram detectados {len(leaks)} caminhos absolutos de máquina real (violação R-044):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


# ─────────────────────────────────────────────────────────────
# 4. Desacoplamento SSOT e Catálogo Único (Cenário 2 & R-043)
# ─────────────────────────────────────────────────────────────

def test_unique_catalog_and_zero_projects_in_shared_files():
    """Valida Cenário 2: .github/agents/catalog.yaml é o único catalog.yaml e não contém projetos."""
    # Valida que o antigo catalog.yaml em docs/ai-context foi extinto
    assert not (REPO_ROOT / "docs" / "ai-context" / "catalog.yaml").exists(), (
        "docs/ai-context/catalog.yaml deve ser extinto (Cenário 2 — Coesão em .github/)"
    )

    # Valida que .github/agents/catalog.yaml é o catálogo único de agents
    catalog_shared = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
    assert catalog_shared.exists(), ".github/agents/catalog.yaml deve existir como catálogo único"

    content = catalog_shared.read_text(encoding="utf-8")
    data = yaml.safe_load(content) or {}

    assert "projetos" not in data, (
        ".github/agents/catalog.yaml NÃO pode conter a chave 'projetos:'. "
        "Projetos devem ser declarados exclusivamente em .github/projects.local.yaml (R-043)."
    )

    assert "path_externo" not in content, (
        ".github/agents/catalog.yaml NÃO pode conter 'path_externo:' (R-043)."
    )

    # Valida que o template tracked de projetos existe
    template_tracked = REPO_ROOT / ".github" / "projects.local.yaml.example"
    assert template_tracked.exists(), ".github/projects.local.yaml.example deve existir como template rastreado"


# ─────────────────────────────────────────────────────────────
# 5. Genericidade Padronizada nos Artefatos de Workflow (R-038 & R-050)
# ─────────────────────────────────────────────────────────────

def test_generic_placeholders_in_workflow_and_router():
    """Valida que workflows.md (fatiado em .github/agents/workflows/, R-066/F3), agent-router
    e handoff usam placeholders genéricos padronizados."""
    content_wf = read_workflows_full_content(REPO_ROOT)
    assert "[PROJETO-ALVO]" in content_wf, "workflows.md (ou arquivos fatiados em workflows/) deve usar o placeholder genérico [PROJETO-ALVO]"

    router_agent = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
    assert router_agent.exists()
    content_router = router_agent.read_text(encoding="utf-8")
    assert "[PROJETO-ALVO]" in content_router, "agent-router deve usar o placeholder genérico [PROJETO-ALVO]"

    handoff_skill = REPO_ROOT / ".github" / "skills" / "handoff-governance" / "SKILL.md"
    assert handoff_skill.exists()
    content_handoff = handoff_skill.read_text(encoding="utf-8")
    assert "[PROJETO-ALVO]" in content_handoff, "handoff-governance/SKILL.md deve usar o placeholder genérico [PROJETO-ALVO]"


# ─────────────────────────────────────────────────────────────
# 6. Proibição de Caminhos Concretos de Projetos Locais em Governança (R-038 & R-044)
# ─────────────────────────────────────────────────────────────

def test_no_concrete_local_project_file_paths_in_governance_files():
    """Valida R-038 e R-044: workflows.md, prompts e suítes de teste de governança nunca devem
    conter caminhos reais de código ou features de projetos locais privados."""
    targets_to_check = [
        REPO_ROOT / ".github" / "agents" / "workflows.md",
        REPO_ROOT / ".github" / "prompts" / "craft-prompt.prompt.md",
        REPO_ROOT / ".github" / "agents" / "evals" / "casos-roteamento.yaml",
        REPO_ROOT / "tests" / "operational_flow" / "casos-workflows.yaml",
    ]

    # Snippets e caminhos característicos de projetos locais que devem ser genéricos
    forbidden_snippets = [
        "src/app/features/escala",
        "src/app/models/escala",
        "src/app/features/admin-global",
        "escala-list.component",
        "admin-global.component",
    ]

    leaks: list[str] = []
    for target in targets_to_check:
        if not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        rel_path = target.relative_to(REPO_ROOT)
        for snippet in forbidden_snippets:
            if snippet in content:
                leaks.append(f"[{rel_path}] contém caminho/termo de projeto local proibido: '{snippet}'")

    assert not leaks, (
        f"Foram detectados {len(leaks)} vazamentos de caminhos de projetos locais em artefatos de governança (violação R-038/R-044):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


# ─────────────────────────────────────────────────────────────
# 7. Hardening Emenda B (independente de projects.local.yaml)
# ─────────────────────────────────────────────────────────────

# Caminho absoluto de workspace de máquina (drive Windows ou /workspace/), exceto o próprio repo público.
_WORKSPACE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]+workspace[\\/]+|(?<![\w.~)\]-])/workspace/)")
_OWN_REPO_PATH = re.compile(r"^(?:public[\\/]+)?deep-agents-copilot", re.IGNORECASE)
# Env vars derivadas de projeto: qualquer prefixo diferente do placeholder <PROJETO> (ver _env_var_violations).
# Segmentos claramente genéricos após o prefixo (placeholders/exemplos): não são evidência de projeto real.
_GENERIC_SEGMENT = re.compile(r"^(?:meu-|projeto|exemplo|<|\.\.\.|\*)", re.IGNORECASE)
# Arquivos que DEFINEM a regra (exemplos ilustrativos) e fixtures de teste da app local-chat-gateway.
_PATH_EXEMPT_PREFIXES = ("CLAUDE.md", ".github/copilot-instructions.md", ".githooks/", "deploy/local-chat-gateway/tests/")
_ILLUSTRATIVE_TERMS = ("regex", "padrao", "placeholder", "removidos", "exemplo ilustrativo", "exemplos ilustrativos", "pre-commit")
_SELF_PATH = Path(__file__).resolve()


def _env_var_violations(line: str) -> bool:
    for m in re.finditer(r"([A-Za-z0-9_<>\-]+)_(?:STORAGE_STATE_PATH|TEST_USER|TEST_PASSWORD)\b", line):
        if m.group(1) != "<PROJETO>":
            return True
    return False


def find_workspace_and_env_leaks(root: Path = REPO_ROOT) -> list[str]:
    """Detecta caminho absoluto de workspace e env vars de projeto em arquivos visíveis ao Git sob `root`."""
    leaks: list[str] = []
    for fpath, content in iter_scannable_files(root):
        if fpath.resolve() == _SELF_PATH:
            continue
        rel_path = fpath.relative_to(root).as_posix()
        if rel_path.startswith(_PATH_EXEMPT_PREFIXES):
            continue
        for idx, line in enumerate(content.splitlines(), 1):
            lowered = line.lower()
            if any(term in lowered for term in _ILLUSTRATIVE_TERMS):
                continue
            for m in _WORKSPACE_PATH.finditer(line):
                tail = line[m.end():]
                if not _OWN_REPO_PATH.match(tail) and not _GENERIC_SEGMENT.match(tail):
                    leaks.append(f"[{rel_path}:{idx}] caminho absoluto de workspace (R-044)")
                    break
            if _env_var_violations(line):
                leaks.append(f"[{rel_path}:{idx}] env var derivada de projeto fora do placeholder <PROJETO> (R-038/R-044)")
    return leaks


def test_no_absolute_workspace_paths_or_project_env_vars_without_local_overlay():
    """Emenda B7 (b): independe de projects.local.yaml — proíbe caminho absoluto de workspace e env vars <X>_STORAGE_STATE_PATH/_TEST_USER/_TEST_PASSWORD."""
    leaks = find_workspace_and_env_leaks()
    assert not leaks, (
        f"Foram detectados {len(leaks)} vazamentos genéricos (caminho de workspace / env var de projeto):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


def test_no_local_project_identifiers_in_file_paths():
    """Emenda B7: nomes de arquivo/pasta visíveis ao Git não podem conter identificadores de projetos locais."""
    forbidden_targets = get_forbidden_project_identifiers()
    patterns = [
        re.compile(rf"(?<![a-zA-Z0-9]){re.escape(target)}(?![a-zA-Z0-9])", re.IGNORECASE)
        for target in forbidden_targets
    ]
    leaks = [
        f"[{f.relative_to(REPO_ROOT).as_posix()}] nome de arquivo contém projeto local proibido (ID-LOCAL)"
        for f in get_git_tracked_files()
        if any(pattern.search(f.relative_to(REPO_ROOT).as_posix()) for pattern in patterns)
    ]
    assert not leaks, (
        f"Foram detectados {len(leaks)} caminhos de arquivo com nome de projeto local (violação R-038/R-044):\n"
        + "\n".join(f"  - {leak}" for leak in leaks)
    )


def test_implementation_plans_are_covered_by_isolation_scan():
    """Emenda B7 (c): todo arquivo em docs/implementation-plans/ (tracked ou untracked) entra na varredura, salvo se ignorado pelo Git."""
    plans_dir = REPO_ROOT / "docs" / "implementation-plans"
    assert plans_dir.is_dir(), "docs/implementation-plans/ deve existir"
    scanned = {f.resolve() for f in get_git_tracked_files()}
    uncovered: list[str] = []
    for fpath in sorted(p for p in plans_dir.rglob("*") if p.is_file()):
        if fpath.resolve() in scanned:
            continue
        ignored = subprocess.run(["git", "check-ignore", "-q", str(fpath)], cwd=REPO_ROOT).returncode == 0
        if not ignored:
            uncovered.append(fpath.relative_to(REPO_ROOT).as_posix())
    assert not uncovered, f"Arquivos de docs/implementation-plans/ fora da varredura de isolamento: {uncovered}"


def test_forbidden_identifiers_not_empty_when_local_overlay_present():
    """Emenda B7 (d): com projects.local.yaml presente, um conjunto de identificadores vazio mascara o teste de vazamento."""
    local_catalog = REPO_ROOT / ".github" / "projects.local.yaml"
    if not local_catalog.exists():
        pytest.skip(".github/projects.local.yaml ausente (ambiente CI) — varredura por identificadores não aplicável")
    assert get_forbidden_project_identifiers(), (
        ".github/projects.local.yaml existe mas get_forbidden_project_identifiers() retornou vazio: "
        "overlay sem projetos externos, YAML inválido ou chaves 'id'/'name' ausentes — o teste de vazamento "
        "estaria mascarado (R-043/R-044). Registre o projeto via /add-project-context ou corrija o overlay."
    )


# ─────────────────────────────────────────────────────────────
# 8. Regressão Emenda D — repositório git temporário, parser de fallback, falsos positivos e detectores
#    (fixtures SOMENTE com identificadores sintéticos; mensagens mascaradas com ID-LOCAL)
# ─────────────────────────────────────────────────────────────

_ID_SINTETICO = "alfa-x1"
_ID_SINTETICO_2 = "projeto-ficticio-z9"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8", check=True)


@pytest.fixture
def repo_git_temporario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Repositório git efêmero e isolado (sem config global/sistema); nunca toca o repositório real."""
    if shutil.which("git") is None:
        pytest.skip("git ausente no ambiente de teste")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Teste Sintetico")
    _git(repo, "config", "user.email", "teste@example.invalid")
    return repo


def _escrever(repo: Path, rel: str, conteudo: str) -> Path:
    alvo = repo / rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(conteudo, encoding="utf-8")
    return alvo


def test_deve_detectar_arquivo_untracked_quando_contem_identificador_sintetico_antes_de_git_add(repo_git_temporario: Path):
    """D1: plano novo NÃO rastreado com id sintético é detectado sem nenhum `git add`."""
    _escrever(repo_git_temporario, "docs/implementation-plans/20260101-plano-novo.md", f"Referência ao {_ID_SINTETICO} aqui.\n")
    assert _git(repo_git_temporario, "ls-files", "--cached").stdout.strip() == ""
    leaks = find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO})
    assert len(leaks) == 1
    assert "plano-novo.md" in leaks[0]


def test_deve_ignorar_arquivo_gitignorado_quando_contem_identificador_sintetico(repo_git_temporario: Path):
    """D1: arquivos cobertos por .gitignore (ex.: overlay local) não entram na varredura."""
    _escrever(repo_git_temporario, ".gitignore", "segredo-local/\n")
    _escrever(repo_git_temporario, "segredo-local/nota.md", f"{_ID_SINTETICO}\n")
    _escrever(repo_git_temporario, "limpo.md", "sem referência\n")
    assert find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO}) == []


def test_deve_detectar_arquivo_rastreado_quando_contem_identificador_sintetico(repo_git_temporario: Path):
    """D1: arquivo rastreado (após add local no repo temporário) continua detectado."""
    _escrever(repo_git_temporario, "a.md", f"{_ID_SINTETICO_2}\n")
    _git(repo_git_temporario, "add", "a.md")
    assert len(find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO_2})) == 1


def test_deve_falhar_sem_varredura_de_nao_rastreados_quando_mutacao_aplicada(repo_git_temporario: Path, monkeypatch: pytest.MonkeyPatch):
    """Mutation sanity D1: removendo `--others` da listagem, o arquivo untracked escapa (a detecção real depende dela)."""
    _escrever(repo_git_temporario, "novo.md", f"{_ID_SINTETICO}\n")
    assert find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO}), "baseline deve detectar"

    real_run = subprocess.run

    def run_mutante(cmd, *args, **kwargs):
        if isinstance(cmd, list) and "--others" in cmd:
            cmd = [c for c in cmd if c not in ("--others", "--exclude-standard")]
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run_mutante)
    assert find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO}) == []


_OVERLAY_INVALIDO = (
    "projetos:\n"
    f'  - id: "{_ID_SINTETICO}"\n'
    '    name: "Projeto Ficticio Z9"\n'
    '    path_externo: "Z:\\pasta\\sintetica\\alfa"\n'
    f"  - id: {_ID_SINTETICO_2}\n"
    '    path_externo: "C:\pasta\invalida\sem-escape"\n'
)


def test_deve_usar_parser_de_fallback_quando_overlay_yaml_invalido(tmp_path: Path):
    """D2: YAML com barras sem escape falha no safe_load; o fallback retorna ids (nunca vazio)."""
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(_OVERLAY_INVALIDO)
    _escrever(tmp_path, ".github/projects.local.yaml", _OVERLAY_INVALIDO)
    ids = get_forbidden_project_identifiers(tmp_path)
    assert ids, "fallback não pode retornar conjunto vazio (ID-LOCAL)"
    assert {_ID_SINTETICO, _ID_SINTETICO_2} <= ids


def test_deve_parsear_ids_quando_fallback_recebe_texto_invalido():
    """D2: contrato direto do parser tolerante."""
    projetos = _parse_projects_fallback(_OVERLAY_INVALIDO)
    assert [p["id"] for p in projetos] == [_ID_SINTETICO, _ID_SINTETICO_2]


@pytest.mark.parametrize(
    ("identificador", "esperado"),
    [("abcd", False), ("abcde", True), ("abcdef", True)],
)
def test_deve_respeitar_tamanho_minimo_quando_carrega_identificadores(tmp_path: Path, identificador: str, esperado: bool):
    """D3: ids com len < MIN_FORBIDDEN_IDENTIFIER_LEN (palavra comum curta) são descartados; boundary == mínimo é aceito."""
    assert MIN_FORBIDDEN_IDENTIFIER_LEN == 5
    _escrever(tmp_path, ".github/projects.local.yaml", f'projetos:\n  - id: "{identificador}"\n')
    assert (identificador in get_forbidden_project_identifiers(tmp_path)) is esperado


@pytest.mark.parametrize(
    ("texto", "detecta"),
    [
        (f"ref {_ID_SINTETICO}", True),
        (f"{_ID_SINTETICO}\n", True),
        (f"{_ID_SINTETICO}x", False),
        (f"x{_ID_SINTETICO}", False),
        (f"{_ID_SINTETICO}2", False),
        (f"{_ID_SINTETICO}-extra", True),
    ],
)
def test_deve_respeitar_boundary_quando_id_vem_com_sufixo_ou_prefixo_alfanumerico(repo_git_temporario: Path, texto: str, detecta: bool):
    """D3: boundary alfanumérico — id colado a letra/dígito não é falso positivo; separador não alfanumérico é."""
    _escrever(repo_git_temporario, "f.md", texto)
    assert bool(find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO})) is detecta


def test_deve_ignorar_lockfile_quando_contem_identificador_sintetico(repo_git_temporario: Path):
    """D3: lockfiles (package-lock.json etc.) são ignorados na varredura."""
    for nome in sorted(_SCAN_SKIP_FILENAMES):
        _escrever(repo_git_temporario, nome, f"{_ID_SINTETICO}\n")
    assert find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO}) == []


def test_deve_mascarar_mensagem_quando_vazamento_detectado(repo_git_temporario: Path):
    """D3: a mensagem de falha usa ID-LOCAL e nunca o identificador encontrado."""
    _escrever(repo_git_temporario, "f.md", f"{_ID_SINTETICO}\n")
    (mensagem,) = find_identifier_leaks(repo_git_temporario, {_ID_SINTETICO})
    assert "ID-LOCAL" in mensagem
    assert _ID_SINTETICO not in mensagem


def test_deve_retornar_vazio_quando_nao_ha_identificadores(repo_git_temporario: Path):
    """D3: conjunto vazio de identificadores não gera falso positivo."""
    _escrever(repo_git_temporario, "f.md", f"{_ID_SINTETICO}\n")
    assert find_identifier_leaks(repo_git_temporario, set()) == []


@pytest.mark.parametrize(
    "linha",
    [
        "cd C:\\workspace\\empresa-ficticia\\app",
        "cd D:/workspace/cliente-ficticio-z9/app",
        "abrir /workspace/alfa-x1/src",
        "ALFA_X1_STORAGE_STATE_PATH=/tmp/x.json",
        "export ALFA_TEST_USER=fulano",
        "ALFA_TEST_PASSWORD=abc",
    ],
)
def test_deve_detectar_vazamento_quando_caminho_workspace_ou_env_var_de_projeto(repo_git_temporario: Path, linha: str):
    """D4: positivos — caminho absoluto de workspace e env vars derivadas de projeto."""
    _escrever(repo_git_temporario, "docs/nota.md", linha + "\n")
    assert find_workspace_and_env_leaks(repo_git_temporario)


@pytest.mark.parametrize(
    "linha",
    [
        "<PROJETO>_STORAGE_STATE_PATH=<caminho>",
        "<PROJETO>_TEST_USER e <PROJETO>_TEST_PASSWORD",
        "cd D:/workspace/<projeto>/app",
        "cd D:/workspace/projeto-exemplo/app",
        "cd D:/workspace/meu-projeto/app",
        "cd D:/workspace/public/deep-agents-copilot",
        "ver ./workspace/alfa-x1 relativo",
        "sem nada suspeito",
    ],
)
def test_deve_aceitar_quando_placeholders_ou_repo_proprio(repo_git_temporario: Path, linha: str):
    """D4: negativos — placeholders <PROJETO>/exemplo, repo próprio e caminhos relativos."""
    _escrever(repo_git_temporario, "docs/nota.md", linha + "\n")
    assert find_workspace_and_env_leaks(repo_git_temporario) == []


@pytest.mark.parametrize(
    "rel",
    ["CLAUDE.md", ".github/copilot-instructions.md", ".githooks/pre-commit", "deploy/local-chat-gateway/tests/t.py"],
)
def test_deve_isentar_arquivo_quando_prefixo_de_regra_ou_fixture(repo_git_temporario: Path, rel: str):
    """D4: arquivos que definem a regra / fixtures da app local-chat-gateway são isentos."""
    _escrever(repo_git_temporario, rel, "cd D:/workspace/empresa-ficticia/app\nALFA_TEST_USER=x\n")
    assert find_workspace_and_env_leaks(repo_git_temporario) == []


def test_deve_isentar_linha_quando_termo_ilustrativo(repo_git_temporario: Path):
    """D4: linha com termo ilustrativo (ex.: 'regex', 'placeholder') é isenta."""
    _escrever(repo_git_temporario, "docs/nota.md", "regex de exemplo: D:/workspace/empresa-ficticia/app\n")
    assert find_workspace_and_env_leaks(repo_git_temporario) == []


def test_deve_mascarar_mensagem_quando_vazamento_de_workspace(repo_git_temporario: Path):
    """D4: mensagens do detector não ecoam o caminho/nome sintético."""
    _escrever(repo_git_temporario, "docs/nota.md", "cd D:/workspace/empresa-ficticia/app\n")
    (mensagem,) = find_workspace_and_env_leaks(repo_git_temporario)
    assert "empresa-ficticia" not in mensagem
