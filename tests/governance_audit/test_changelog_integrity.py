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


def test_anti_truncation_hook_e2e_git_commit_simulation(tmp_path: Path):
    """
    Teste de Regressão Ponta-a-Ponta (E2E) via subprocess em repositório Git temporário:
    Executa commits reais exercitando o script pre-commit com core.hooksPath.
    Valida:
    1. Commit inicial com CHANGELOG.md passa (HEAD vazio sem falso positivo).
    2. Commit inserindo múltiplas versões novas antes de uma existente passa (eliminação do falso positivo).
    3. Commit com remoção líquida real de versão histórica é bloqueado com saída explicativa.
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

