"""
test_changelog_integrity.py — Quality Gate de Integridade e Anti-Truncamento do CHANGELOG.md

Garante que o histórico de releases é cumulativo, estritamente decrescente em Semver,
possui volume mínimo de linhas e preserva todas as versões âncoras históricas do projeto,
prevenindo truncamentos acidentais por agentes ou edições incorretas.
"""

from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
PRE_COMMIT_HOOK_PATH = REPO_ROOT / ".githooks" / "pre-commit"

MIN_LINE_COUNT: int = 400
MAX_LINE_COUNT: int = 1000
MAX_BULLET_LENGTH: int = 200
MAX_BULLETS_PER_RELEASE: int = 12

# Versões marcos obrigatórias que jamais podem desaparecer do histórico
HISTORICAL_ANCHOR_VERSIONS = [
    "1.0.0",
    "1.1.0",
    "1.2.0",
    "1.3.0",
    "1.6.0",
    "2.0.0",
    "2.5.0",
    "2.8.0",
    "2.8.5",
    "2.8.7",
    "2.8.8",
    "2.8.9",
    "2.8.10",
]

RELEASE_HEADER_PATTERN = re.compile(
    r"^##\s+\[(\d+\.\d+\.\d+)\]\s+—\s+(\d{4}-\d{2}-\d{2})",
    re.MULTILINE
)


@pytest.fixture
def changelog_text() -> str:
    assert CHANGELOG_PATH.exists(), "CHANGELOG.md não encontrado na raiz do repositório!"
    return CHANGELOG_PATH.read_text(encoding="utf-8")


def test_changelog_minimum_volume_and_release_count(changelog_text: str):
    """
    Gate de Volume Mínimo (Anti-Truncamento):
    CHANGELOG.md deve possuir ao menos 400 linhas e 25 versões registradas.
    Se um edit truncar o arquivo para poucas linhas, este teste falha imediatamente.
    """
    lines = changelog_text.splitlines()
    assert len(lines) >= 400, (
        f"CHANGELOG.md aparenta ter sido truncado! Encontradas apenas {len(lines)} linhas (mínimo esperado: 400)."
    )

    matches = RELEASE_HEADER_PATTERN.findall(changelog_text)
    assert len(matches) >= 25, (
        f"Número de releases encontradas ({len(matches)}) é inferior ao mínimo histórico esperado (25)."
    )


def test_changelog_preserves_all_historical_anchor_versions(changelog_text: str):
    """
    Gate de Âncoras Históricas:
    Garante que versões chave (desde a 1.0.0 até as mais recentes) estão presentes no documento.
    """
    matches = RELEASE_HEADER_PATTERN.findall(changelog_text)
    found_versions = {v for v, _ in matches}

    missing = [v for v in HISTORICAL_ANCHOR_VERSIONS if v not in found_versions]
    assert not missing, (
        f"CHANGELOG.md perdeu versões históricas obrigatórias: {missing}. "
        "O histórico do changelog é estritamente aditivo e não pode ser suprimido."
    )


def test_changelog_versions_in_strictly_descending_semver_order(changelog_text: str):
    """
    Gate de Ordenação Cronológica e Semver:
    As versões devem estar ordenadas de forma estritamente decrescente (da mais nova para a mais antiga).
    """
    matches = RELEASE_HEADER_PATTERN.findall(changelog_text)
    assert matches, "Nenhum cabeçalho de versão encontrado no CHANGELOG.md!"

    parsed_versions = []
    for v_str, date_str in matches:
        parts = tuple(map(int, v_str.split(".")))
        parsed_versions.append((parts, v_str, date_str))

    for i in range(len(parsed_versions) - 1):
        curr_ver, curr_str, _ = parsed_versions[i]
        next_ver, next_str, _ = parsed_versions[i + 1]
        assert curr_ver > next_ver, (
            f"Inconsistência de ordenação no CHANGELOG.md: versão [{curr_str}] "
            f"aparece antes de [{next_str}], violando a ordem decrescente semver."
        )


def test_changelog_header_syntax_uniformity(changelog_text: str):
    """
    Gate de Sintaxe:
    Todo cabeçalho de versão deve seguir o padrão: '## [X.Y.Z] — YYYY-MM-DD'.
    """
    h2_release_lines = [
        line.strip() for line in changelog_text.splitlines()
        if line.strip().startswith("## [")
    ]
    assert len(h2_release_lines) >= 25

    for line in h2_release_lines:
        match = re.match(r"^##\s+\[\d+\.\d+\.\d+\]\s+—\s+\d{4}-\d{2}-\d{2}$", line)
        assert match, f"Cabeçalho de release fora do padrão formal: '{line}'"


def test_anti_truncation_simulation_detects_history_loss():
    """
    Teste de Regressão / Simulação:
    Valida que a lógica do gate detecta e rejeita um changelog truncado simulado.
    """
    truncated_content = """# CHANGELOG
## [2.8.10] — 2026-09-14
### Refatorado
- Apenas uma alteração isolada sem o histórico anterior.
"""
    lines = truncated_content.splitlines()
    assert len(lines) < 400

    matches = RELEASE_HEADER_PATTERN.findall(truncated_content)
    found_versions = {v for v, _ in matches}

    # Deve acusar perda de âncoras históricas
    missing = [v for v in HISTORICAL_ANCHOR_VERSIONS if v not in found_versions]
    assert "1.0.0" in missing
    assert "2.0.0" in missing


def extract_changelog_release_headers(text: str) -> list[str]:
    """Extrai todas as linhas que definem cabeçalhos de release (## [...])."""
    return [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^##\s+\[", line.strip())
    ]


def find_missing_changelog_headers(head_content: str, staged_content: str) -> list[str]:
    """
    Compara o conjunto de cabeçalhos de release entre HEAD e a versão staged (índice),
    servindo como helper rápido em nível de teste unitário.

    Nota de fidelidade: este helper Python utiliza conjunto (set) para verificação rápida de
    presença em casos sem duplicatas. A semântica estrita de multiset linha a linha (sensível a
    duplicatas via 'comm -23') é exercitada diretamente contra o hook bash real no teste E2E
    'test_anti_truncation_hook_blocks_duplicate_header_removal_safe_by_default'.

    Retorna a lista de cabeçalhos presentes em HEAD mas ausentes no staged (remoção líquida).
    Se HEAD estiver vazio (primeiro commit do changelog), retorna lista vazia (sem bloqueio).
    """
    head_headers = extract_changelog_release_headers(head_content)
    if not head_headers:
        return []

    staged_headers = set(extract_changelog_release_headers(staged_content))
    return [h for h in head_headers if h not in staged_headers]


def test_pre_commit_hook_has_anti_truncation_guard():
    """
    Valida se o hook de pre-commit (.githooks/pre-commit) implementa
    a proteção determinística contra remoção de cabeçalhos de release do CHANGELOG.md
    baseada em multiset (HEAD vs staged), e não a heurística ingênua de diff unificado.
    """
    assert PRE_COMMIT_HOOK_PATH.exists(), "Hook .githooks/pre-commit não encontrado!"
    hook_content = PRE_COMMIT_HOOK_PATH.read_text(encoding="utf-8")

    assert "CHANGELOG" in hook_content
    assert "Anti-Truncamento" in hook_content
    assert "headers_head" in hook_content
    assert "headers_staged" in hook_content
    assert "comm -23" in hook_content
    # Garante que a heurística antiga ingênua de diff com grep foi removida
    assert "deleted_headers=$(git diff --cached -- CHANGELOG.md | grep -E" not in hook_content


def test_anti_truncation_multiset_avoids_false_positive_when_new_versions_inserted_before_existing():
    """
    Teste de Regressão — Bugfix Anti-Truncamento / Falso Positivo:
    Cenário: Inserção de múltiplas entradas novas de versão ANTES de um cabeçalho existente.
    
    No algoritmo de Myers diff, inserções múltiplas no mesmo bloco podem gerar
    pares de remoção/adição textual (-## [X.Y.Z] e +## [X.Y.Z]), causando falso positivo
    na checagem antiga por diff textual.
    
    A nova checagem por multiset verifica a presença líquida do cabeçalho existente no staged.
    Como todas as versões de HEAD permanecem presentes no staged, a verificação NÃO deve bloquear.
    """
    head_changelog = """# CHANGELOG

## [2.51.5] — 2026-09-10
### Corrigido
- Correção pontual 1.

## [2.51.4] — 2026-09-08
### Adicionado
- Recurso anterior.
"""

    # Inserção de N=5 versões novas no topo, deslocando 2.51.5 e 2.51.4 para baixo
    staged_changelog = """# CHANGELOG

## [2.52.4] — 2026-09-14
### Adicionado
- Versão 2.52.4.

## [2.52.3] — 2026-09-13
### Adicionado
- Versão 2.52.3.

## [2.52.2] — 2026-09-12
### Adicionado
- Versão 2.52.2.

## [2.52.1] — 2026-09-11
### Adicionado
- Versão 2.52.1.

## [2.52.0] — 2026-09-10
### Adicionado
- Versão 2.52.0.

## [2.51.5] — 2026-09-10
### Corrigido
- Correção pontual 1.

## [2.51.4] — 2026-09-08
### Adicionado
- Recurso anterior.
"""

    missing = find_missing_changelog_headers(head_changelog, staged_changelog)
    assert missing == [], (
        f"Falso positivo detectado! Cabeçalhos reportados indevidamente como ausentes: {missing}"
    )


def test_anti_truncation_multiset_blocks_real_net_removal_of_historical_header():
    """
    Garante que a nova lógica de multiset CONTINUA bloqueando qualquer remoção líquida real
    de versão histórica (cabeçalho presente em HEAD mas suprimido em staged).
    """
    head_changelog = """# CHANGELOG

## [2.51.5] — 2026-09-10
### Corrigido
- Correção pontual 1.

## [2.51.4] — 2026-09-08
### Adicionado
- Versão que será removida indevidamente.

## [2.51.3] — 2026-09-05
### Adicionado
- Versão preservada.
"""

    # Staged removeu a 2.51.4
    staged_changelog = """# CHANGELOG

## [2.52.0] — 2026-09-12
### Adicionado
- Nova versão.

## [2.51.5] — 2026-09-10
### Corrigido
- Correção pontual 1.

## [2.51.3] — 2026-09-05
### Adicionado
- Versão preservada.
"""

    missing = find_missing_changelog_headers(head_changelog, staged_changelog)
    assert len(missing) == 1
    assert "## [2.51.4] — 2026-09-08" in missing


def test_anti_truncation_multiset_empty_head_does_not_block():
    """
    Garante que quando HEAD está vazio (ex.: commit inicial adicionando CHANGELOG.md),
    a verificação não bloqueia e não gera falso positivo.
    """
    head_changelog = ""
    staged_changelog = """# CHANGELOG

## [1.0.0] — 2026-01-01
### Inicial
- Lançamento inicial.
"""

    missing = find_missing_changelog_headers(head_changelog, staged_changelog)
    assert missing == []


@pytest.mark.slow
def test_anti_truncation_hook_e2e_git_commit_simulation(tmp_path: Path):
    """
    Teste de Regressão Ponta-a-Ponta (E2E) via subprocess em repositório Git temporário:
    Executa commits reais exercitando o script pre-commit com core.hooksPath.
    Valida:
    1. Commit inicial com CHANGELOG.md passa (HEAD vazio sem falso positivo).
    2. Commit inserindo múltiplas versões novas antes de uma existente passa (eliminação do falso positivo).
    3. Commit com remoção líquida real de versão histórica é bloqueado com saída explicativa.

    NOTA DE PERFORMANCE (marcado @pytest.mark.slow): cada `git commit` real aqui
    dispara o hook bash `.githooks/pre-commit`, que por sua vez spawna ~10-15
    processos filhos (git diff/grep/sed/comm). No Windows + Git-for-Windows
    (MSYS2), quando o subprocess Python usa `capture_output=True` (stdio via
    pipes anônimos, sem console real), o spawn de processos MSYS2 fica
    drasticamente mais lento (medido: ~30s por `git commit` isolado vs. <1s
    rodando o mesmo comando interativamente no bash). Este teste soma 3 commits,
    podendo levar 1-2+ minutos nesse ambiente. Não é um bug de lógica do teste —
    é uma característica conhecida do MSYS2/Cygwin com I/O redirecionado.
    Execute explicitamente com `pytest -m slow`; excluído do loop rápido padrão.
    """
    import os
    import shutil
    import subprocess

    git_bin = shutil.which("git")
    if not git_bin:
        pytest.skip("Git não disponível no ambiente para teste E2E do hook")

    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Governance Maintainer Test"
    env["GIT_AUTHOR_EMAIL"] = "governance-test@example.com"
    env["GIT_COMMITTER_NAME"] = "Governance Maintainer Test"
    env["GIT_COMMITTER_EMAIL"] = "governance-test@example.com"

    # Inicializa repo temporário
    subprocess.run([git_bin, "init"], cwd=tmp_path, check=True, capture_output=True)

    # Configura e instala o hook pre-commit atualizado
    hooks_dir = tmp_path / ".githooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-commit"
    hook_file.write_text(PRE_COMMIT_HOOK_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    hook_file.chmod(0o755)

    subprocess.run([git_bin, "config", "core.hooksPath", ".githooks"], cwd=tmp_path, check=True)

    # 1. Commit inicial: CHANGELOG.md com versão 1.0.0
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# CHANGELOG\n\n## [1.0.0] — 2026-01-01\n- Versão inicial.\n", encoding="utf-8")
    subprocess.run([git_bin, "add", "CHANGELOG.md"], cwd=tmp_path, check=True)
    res_init = subprocess.run(
        [git_bin, "commit", "-m", "chore: initial changelog"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    assert res_init.returncode == 0, f"Commit inicial falhou indevidamente: {res_init.stderr}"

    # 2. Inserção de versões novas antes de 1.0.0 (cenário de falso positivo do Myers diff)
    changelog.write_text(
        "# CHANGELOG\n\n"
        "## [1.2.0] — 2026-01-03\n- Versão 1.2.0.\n\n"
        "## [1.1.0] — 2026-01-02\n- Versão 1.1.0.\n\n"
        "## [1.0.0] — 2026-01-01\n- Versão inicial.\n",
        encoding="utf-8"
    )
    subprocess.run([git_bin, "add", "CHANGELOG.md"], cwd=tmp_path, check=True)
    res_additive = subprocess.run(
        [git_bin, "commit", "-m", "feat: add 1.1.0 and 1.2.0"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    assert res_additive.returncode == 0, (
        f"Falso positivo no hook! Inserção aditiva de versões foi bloqueada: {res_additive.stderr}"
    )

    # 3. Remoção líquida real de versão histórica (1.1.0 removida)
    changelog.write_text(
        "# CHANGELOG\n\n"
        "## [1.3.0] — 2026-01-04\n- Versão 1.3.0.\n\n"
        "## [1.2.0] — 2026-01-03\n- Versão 1.2.0.\n\n"
        "## [1.0.0] — 2026-01-01\n- Versão inicial.\n",
        encoding="utf-8"
    )
    subprocess.run([git_bin, "add", "CHANGELOG.md"], cwd=tmp_path, check=True)
    res_removal = subprocess.run(
        [git_bin, "commit", "-m", "bad: remove 1.1.0"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    assert res_removal.returncode != 0, "Hook falhou em bloquear a remoção líquida da versão 1.1.0!"
    combined_output = res_removal.stdout + res_removal.stderr
    assert "Anti-Truncamento" in combined_output
    assert "## [1.1.0] — 2026-01-02" in combined_output

@pytest.mark.slow
def test_anti_truncation_hook_blocks_duplicate_header_removal_safe_by_default(tmp_path: Path):
    """
    Teste de Regressão / Semântica Multiset do Hook Bash Real:
    Exercita o script .githooks/pre-commit real via subprocess em repositório Git temporário.

    Cenário: HEAD contém um cabeçalho de versão duplicado (ex.: '## [2.51.5] — 2026-10-04'
    aparecendo 2x por erro histórico anterior). O desenvolvedor tenta commitar uma versão
    staged que remove apenas 1 das 2 ocorrências, mantendo 1 cabeçalho.

    Comportamento esperado (Seguro por Padrão / Safe by Default):
    O comando 'comm -23' opera sobre streams ordenados linha a linha e é sensível a duplicatas
    (semântica de multiset). Por ser incapaz de distinguir entre a limpeza de uma duplicata
    ilegítima e uma perda inadvertida de histórico, o hook bloqueia o commit por precaução.
    Este é um comportamento seguro por padrão conhecido e aceito para um guard de governança.

    NOTA DE PERFORMANCE (marcado @pytest.mark.slow): ver nota equivalente em
    `test_anti_truncation_hook_e2e_git_commit_simulation` — cada `git commit`
    real aqui é lento no Windows/MSYS2 por redirecionamento de stdio via pipes.
    """
    import os
    import shutil
    import subprocess

    git_bin = shutil.which("git")
    if not git_bin:
        pytest.skip("Git não disponível no ambiente para teste E2E do hook")

    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Governance Maintainer Test"
    env["GIT_AUTHOR_EMAIL"] = "governance-test@example.com"
    env["GIT_COMMITTER_NAME"] = "Governance Maintainer Test"
    env["GIT_COMMITTER_EMAIL"] = "governance-test@example.com"

    # Inicializa repo temporário
    subprocess.run([git_bin, "init"], cwd=tmp_path, check=True, capture_output=True)

    # Configura e instala o hook pre-commit atualizado com permissão de execução POSIX
    hooks_dir = tmp_path / ".githooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-commit"
    hook_file.write_text(PRE_COMMIT_HOOK_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    hook_file.chmod(0o755)

    subprocess.run([git_bin, "config", "core.hooksPath", ".githooks"], cwd=tmp_path, check=True)

    # 1. Commit inicial contendo cabeçalho de versão duplicado (erro histórico simulado no HEAD)
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# CHANGELOG\n\n"
        "## [2.51.5] — 2026-10-04\n- Correção duplicada A.\n\n"
        "## [2.51.5] — 2026-10-04\n- Correção duplicada B.\n\n"
        "## [1.0.0] — 2026-01-01\n- Versão inicial.\n",
        encoding="utf-8"
    )
    subprocess.run([git_bin, "add", "CHANGELOG.md"], cwd=tmp_path, check=True)
    res_init = subprocess.run(
        [git_bin, "commit", "-m", "chore: initial changelog with duplicate header"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )
    assert res_init.returncode == 0, f"Commit inicial falhou indevidamente: {res_init.stderr}"

    # 2. Commit staged que remove apenas 1 das 2 ocorrências (mantendo 1 cabeçalho)
    changelog.write_text(
        "# CHANGELOG\n\n"
        "## [2.51.5] — 2026-10-04\n- Correção unificada.\n\n"
        "## [1.0.0] — 2026-01-01\n- Versão inicial.\n",
        encoding="utf-8"
    )
    subprocess.run([git_bin, "add", "CHANGELOG.md"], cwd=tmp_path, check=True)
    res_removal = subprocess.run(
        [git_bin, "commit", "-m", "fix: remove duplicate 2.51.5 header"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )

    # Bloqueado intencionalmente: comm -23 detecta a ausência da 2ª ocorrência de HEAD no staged
    assert res_removal.returncode != 0, (
        "Hook deveria ter bloqueado a remoção da duplicata sob semântica multiset do comm -23 (comportamento seguro por padrão)!"
    )
    combined_output = res_removal.stdout + res_removal.stderr
    assert "Anti-Truncamento" in combined_output
    assert "## [2.51.5] — 2026-10-04" in combined_output


# ============================================================================
# Sensores Determinísticos de Concisão e Teto Anti-Bloat (Onda 4B — R-055 Q3)
# ============================================================================

BULLET_LINE_PATTERN = re.compile(r"^\s*-\s+")
NESTED_BULLET_PATTERN = re.compile(r"^ {2,}-\s+")


def _extract_release_sections(text: str) -> dict[str, list[tuple[int, str]]]:
    """
    Extrai as linhas pertencentes a cada seção de release `## [X.Y.Z]` do CHANGELOG.md.
    Retorna um dicionário mapeando a versão `X.Y.Z` para uma lista de tuplas `(line_number, line_text)`.
    """
    sections: dict[str, list[tuple[int, str]]] = {}
    current_version: str | None = None

    for idx, line in enumerate(text.splitlines(), start=1):
        header_match = re.match(r"^##\s+\[(\d+\.\d+\.\d+)\]", line)
        if header_match:
            current_version = header_match.group(1)
            sections.setdefault(current_version, [])
            continue
        if line.startswith("## ["):
            current_version = None
            continue
        if current_version is not None:
            sections[current_version].append((idx, line))

    return sections


def _find_bullet_length_violations(
    text: str, max_length: int = MAX_BULLET_LENGTH
) -> list[tuple[str, int, int]]:
    r"""
    Inspeciona todos os bullets (`^\s*-\s+`) dentro das seções de release e retorna
    as violações como tuplas `(version, line_number, length)` onde `len(line) > max_length`.
    """
    violations: list[tuple[str, int, int]] = []
    for version, lines in _extract_release_sections(text).items():
        for line_no, line in lines:
            if BULLET_LINE_PATTERN.match(line) and len(line) > max_length:
                violations.append((version, line_no, len(line)))
    return violations


def _find_release_bullet_count_and_nesting_violations(
    text: str, max_bullets: int = MAX_BULLETS_PER_RELEASE
) -> tuple[dict[str, int], list[tuple[str, int]]]:
    r"""
    Verifica por seção de release `## [X.Y.Z]`:
    1) Se a contagem total de bullets (`^\s*-\s+`) excede `max_bullets`;
    2) Se existem sub-bullets aninhados (`^ {2,}-\s+`).
    """
    count_violations: dict[str, int] = {}
    nested_violations: list[tuple[str, int]] = []

    for version, lines in _extract_release_sections(text).items():
        bullet_count = 0
        for line_no, line in lines:
            if BULLET_LINE_PATTERN.match(line):
                bullet_count += 1
            if NESTED_BULLET_PATTERN.match(line):
                nested_violations.append((version, line_no))
        if bullet_count > max_bullets:
            count_violations[version] = bullet_count

    return count_violations, nested_violations


def test_changelog_maximum_line_ceiling_anti_bloat(changelog_text: str):
    """
    Gate de Teto Máximo de Linhas (Anti-Bloat):
    Valida que o CHANGELOG.md possui <= MAX_LINE_COUNT (1000) linhas,
    prevenindo regressão de Context Bloat e garantindo concisão histórica.
    """
    lines = changelog_text.splitlines()
    assert len(lines) <= MAX_LINE_COUNT, (
        f"CHANGELOG.md excedeu o teto máximo anti-bloat! "
        f"Encontradas {len(lines)} linhas (máximo permitido: {MAX_LINE_COUNT}). "
        "Execute compactação semântica in-place preservando todas as versões históricas."
    )


def test_changelog_does_not_exceed_max_line_count(changelog_text: str):
    """
    Alias de conformidade com especificação Gherkin S1 da Onda 4B:
    Assegura que o total de linhas do CHANGELOG.md permanece <= MAX_LINE_COUNT (1000).
    """
    test_changelog_maximum_line_ceiling_anti_bloat(changelog_text)


def test_changelog_bullet_conciseness_budget(changelog_text: str):
    r"""
    Gate de Concisão de Bullets:
    Valida que todo bullet (`^\s*-\s+`) dentro das seções de release do CHANGELOG.md
    possui `len(line) <= MAX_BULLET_LENGTH` (200 caracteres Unicode).
    """
    violations = _find_bullet_length_violations(changelog_text, MAX_BULLET_LENGTH)
    assert not violations, (
        f"Bullets no CHANGELOG.md excedem o limite de {MAX_BULLET_LENGTH} caracteres: "
        f"{violations}"
    )


def test_changelog_bullets_respect_max_length(changelog_text: str):
    """
    Alias de conformidade com especificação Gherkin S2 da Onda 4B:
    Garante que nenhum bullet nas seções de release ultrapassa MAX_BULLET_LENGTH (200).
    """
    test_changelog_bullet_conciseness_budget(changelog_text)


def test_changelog_max_bullets_per_release_budget(changelog_text: str):
    """
    Gate de Densidade Máxima por Release:
    Valida que nenhuma seção de release `## [X.Y.Z]` do CHANGELOG.md possui mais de
    `MAX_BULLETS_PER_RELEASE` (12) bullets nem sub-bullets aninhados.
    """
    count_violations, nested_violations = _find_release_bullet_count_and_nesting_violations(
        changelog_text, MAX_BULLETS_PER_RELEASE
    )
    assert not count_violations, (
        f"Seções de release no CHANGELOG.md excedem o teto de {MAX_BULLETS_PER_RELEASE} bullets: "
        f"{count_violations}"
    )
    assert not nested_violations, (
        f"Sub-bullets aninhados ('  - ') detectados nas seções de release do CHANGELOG.md: "
        f"{nested_violations}"
    )


def test_changelog_releases_respect_max_bullets_per_section(changelog_text: str):
    """
    Alias de conformidade com especificação Gherkin S3 da Onda 4B:
    Garante que cada seção `## [X.Y.Z]` respeita o limite de MAX_BULLETS_PER_RELEASE (12) bullets.
    """
    test_changelog_max_bullets_per_release_budget(changelog_text)


def test_changelog_preserves_all_historical_version_headers(changelog_text: str):
    """
    Alias de conformidade com especificação Gherkin S3 da Onda 4B:
    Confirma a preservação integral de todas as versões em HISTORICAL_ANCHOR_VERSIONS.
    """
    test_changelog_preserves_all_historical_anchor_versions(changelog_text)


def test_changelog_preserves_r060_architecture_milestone(changelog_text: str):
    """
    Gate de Marco Arquitetural R-060:
    Garante que a seção `## [2.33.0]` preserva explicitamente a referência ao marco `R-060`.
    """
    sections = _extract_release_sections(changelog_text)
    assert "2.33.0" in sections, "Seção histórica ## [2.33.0] não encontrada no CHANGELOG.md!"
    section_body = "\n".join(line for _, line in sections["2.33.0"])
    assert "R-060" in section_body, (
        "A seção ## [2.33.0] deve preservar explicitamente a referência ao marco arquitetural 'R-060'."
    )


@pytest.mark.parametrize(
    ("bullet_body_len", "should_violate"),
    [
        (MAX_BULLET_LENGTH - 2, False),  # Exatamente 198 chars + "- " (2 chars) = 200 (limite exato permitido)
        (MAX_BULLET_LENGTH - 1, True),   # Exatamente 199 chars + "- " (2 chars) = 201 (violação de fronteira)   # Exatamente 199 chars + "- " (2 chars) = 201 (violação de fronteira)
        (350, True),                     # Violação severa (> 200 chars)
    ],
)
def test_synthetic_bullet_conciseness_boundary_detection(bullet_body_len: int, should_violate: bool):
    """
    Teste Unitário Sintético (Boundary Value Analysis para MAX_BULLET_LENGTH):
    Valida que o detector acusa falha determinística quando um bullet sintético excede
    200 caracteres (ex.: 201 chars) e aceita exatamente 200 caracteres.
    """
    synthetic_bullet = "- " + ("a" * bullet_body_len)
    synthetic_changelog = (
        "# CHANGELOG\n\n"
        "## [2.99.0] — 2026-11-16\n"
        "### Added\n"
        f"{synthetic_bullet}\n"
    )
    violations = _find_bullet_length_violations(synthetic_changelog, MAX_BULLET_LENGTH)
    if should_violate:
        assert len(violations) == 1
        version, line_no, length = violations[0]
        assert version == "2.99.0"
        assert line_no == 5
        assert length == bullet_body_len + 2
    else:
        assert violations == []


@pytest.mark.parametrize(
    ("num_bullets", "should_violate"),
    [
        (1, False),
        (MAX_BULLETS_PER_RELEASE, False),      # 12 bullets (no limite exato permitido)
        (MAX_BULLETS_PER_RELEASE + 1, True),   # 13 bullets (violação de fronteira)
        (20, True),                            # Violação severa
    ],
)
def test_synthetic_max_bullets_per_release_boundary_detection(num_bullets: int, should_violate: bool):
    """
    Teste Unitário Sintético (Boundary Value Analysis para MAX_BULLETS_PER_RELEASE):
    Valida que o detector acusa falha quando uma release sintética excede 12 bullets
    (ex.: 13 bullets) e aceita até 12 bullets, além de detectar sub-bullets aninhados.
    """
    bullets_block = "\n".join(f"- Item sintético {i}." for i in range(1, num_bullets + 1))
    synthetic_changelog = (
        "# CHANGELOG\n\n"
        "## [2.99.0] — 2026-11-16\n"
        "### Changed\n"
        f"{bullets_block}\n\n"
        "## [1.0.0] — 2026-01-01\n"
        "- Release inicial enxuta.\n"
    )
    count_violations, nested_violations = _find_release_bullet_count_and_nesting_violations(
        synthetic_changelog, MAX_BULLETS_PER_RELEASE
    )
    assert nested_violations == []
    if should_violate:
        assert count_violations == {"2.99.0": num_bullets}
    else:
        assert count_violations == {}


def test_synthetic_nested_bullet_detection():
    """
    Teste Unitário Sintético (Anti-Aninhamento):
    Valida que sub-bullets indentados ('  - ') dentro de uma seção de release são detectados.
    """
    synthetic_changelog = (
        "# CHANGELOG\n\n"
        "## [2.99.0] — 2026-11-16\n"
        "- Bullet principal válido.\n"
        "  - Sub-bullet aninhado proibido.\n"
    )
    _, nested_violations = _find_release_bullet_count_and_nesting_violations(
        synthetic_changelog, MAX_BULLETS_PER_RELEASE
    )
    assert nested_violations == [("2.99.0", 5)]
