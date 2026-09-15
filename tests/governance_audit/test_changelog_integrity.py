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


def test_pre_commit_hook_has_anti_truncation_guard():
    """
    Valida se o hook de pre-commit (.githooks/pre-commit) implementa
    a proteção determinística contra remoção de cabeçalhos de release do CHANGELOG.md.
    """
    assert PRE_COMMIT_HOOK_PATH.exists(), "Hook .githooks/pre-commit não encontrado!"
    hook_content = PRE_COMMIT_HOOK_PATH.read_text(encoding="utf-8")

    assert "CHANGELOG" in hook_content
    assert "Anti-Truncamento" in hook_content or "deleted_headers" in hook_content

