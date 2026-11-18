"""Sensor determinístico do contrato do agent-root (raiz declarada — ADR-0015 / R-037 / R-062 / R-063 / R-068).

Casos S1–S3 e S5–S11 do plano de testes do agent-root. Somente leitura, sem rede e sem escrita.
Compensa a exceção por nome de agent-root nos filtros de test_context_mode_precedence_governance.py (T-08).
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
AGENT_ROOT_FILE = AGENTS_DIR / "agent-root.agent.md"
ROUTING_GRAPH_FILE = AGENTS_DIR / "routing-graph.yaml"
INVARIANTES_FILE = AGENTS_DIR / "workflows" / "invariantes-e-protocolos.md"
ADR_DIR = REPO_ROOT / "docs" / "adr"
COPILOT_INSTRUCTIONS_FILE = REPO_ROOT / ".github" / "copilot-instructions.md"

EXPECTED_TOOLS = frozenset(
    {
        "ask_questions",
        "run_subagent",
        "context-mode/ctx_index",
        "context-mode/ctx_search",
        "context-mode/ctx_resume",
    }
)
DIRECT_EDIT_TOOLS = frozenset(
    {"replace_string_in_file", "insert_edit_into_file", "create_file", "edit"}
)

# Curingas congelados (de, para). Curinga novo exige atualizar ADR-0015, esta lista e o plano.
KNOWN_WILDCARD_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
        ("*downstream", "codegraph-engine"),
        ("*downstream", "agent-router"),
        ("agent-router", "*downstream"),
    }
)

BODY_WARN_BYTES = 1900
BODY_HARD_BYTES = 2048
M2_CEILING_BYTES = 19557
M2_WARN_SLACK_BYTES = 100

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.fixture(scope="module")
def agent_root_parts() -> tuple[dict, str]:
    """Retorna (frontmatter, corpo) do agent-root.agent.md."""
    match = _FRONTMATTER_RE.match(_read(AGENT_ROOT_FILE))
    assert match, "agent-root.agent.md deve possuir frontmatter YAML delimitado por ---"
    return yaml.safe_load(match.group(1)), match.group(2)


@pytest.fixture(scope="module")
def grafo() -> dict:
    return yaml.safe_load(_read(ROUTING_GRAPH_FILE))


def test_s1_tools_exatas_do_agent_root(agent_root_parts) -> None:
    """S1) O frontmatter declara exatamente as 5 tools canônicas."""
    frontmatter, _ = agent_root_parts
    tools = frontmatter["tools"]
    assert len(tools) == len(set(tools)) == 5, f"Esperadas 5 tools únicas, obtidas: {tools}"
    assert set(tools) == EXPECTED_TOOLS, f"Tools divergentes: {sorted(set(tools) ^ EXPECTED_TOOLS)}"


def test_s2_no_agent_root_unico_no_grafo(grafo) -> None:
    """S2) Exatamente 1 nó id: agent-root em nos."""
    ids = [n["id"] for n in grafo["nos"] if n["id"] == "agent-root"]
    assert len(ids) == 1, f"Esperado 1 nó agent-root, encontrados {len(ids)}"


def test_s3_no_agent_root_e_downstream(grafo) -> None:
    """S3) O nó agent-root tem tipo downstream."""
    no = next(n for n in grafo["nos"] if n["id"] == "agent-root")
    assert no["tipo"] == "downstream", f"Tipo esperado downstream, obtido {no['tipo']}"


def test_s5_sem_aresta_de_entrada_para_agent_root(grafo) -> None:
    """S5) Nenhuma aresta tem para: agent-root."""
    entrada = [a for a in grafo["arestas"] if a.get("para") == "agent-root"]
    assert not entrada, f"agent-root não pode ser destino de arestas: {entrada}"


def test_s6_sem_aresta_router_para_root_e_curingas_congelados(grafo) -> None:
    """S6) Sem aresta agent-router→agent-root; curingas restritos a KNOWN_WILDCARD_EDGES (pares (de, para))."""
    arestas = grafo["arestas"]
    router_para_root = [a for a in arestas if a.get("de") == "agent-router" and a.get("para") == "agent-root"]
    assert not router_para_root, "Aresta explícita agent-router→agent-root é proibida (ADR-0015)"

    curingas = {
        (a["de"], a["para"])
        for a in arestas
        if isinstance(a.get("de"), str)
        and isinstance(a.get("para"), str)
        and (a["de"].startswith("*") or a["para"].startswith("*"))
    }
    assert curingas == KNOWN_WILDCARD_EDGES, (
        "Curingas divergem de KNOWN_WILDCARD_EDGES; atualize ADR-0015, KNOWN_WILDCARD_EDGES e o plano "
        f"com justificativa. Novos: {sorted(curingas - KNOWN_WILDCARD_EDGES)}; "
        f"removidos: {sorted(KNOWN_WILDCARD_EDGES - curingas)}"
    )


def test_s7_corpo_do_agent_root_dentro_de_2kb(agent_root_parts) -> None:
    """S7) Corpo ≤ 2.048 B (falha dura); > 1.900 B emite warning de folga."""
    _, body = agent_root_parts
    size = len(body.encode("utf-8"))
    assert size <= BODY_HARD_BYTES, (
        f"Corpo do agent-root com {size} B excede {BODY_HARD_BYTES} B; reduza o corpo "
        "(corte o checklist) ou abra novo plano."
    )
    if size > BODY_WARN_BYTES:
        warnings.warn(
            f"Corpo do agent-root com {size} B (> {BODY_WARN_BYTES} B): folga para o teto de "
            f"{BODY_HARD_BYTES} B quase esgotada.",
            stacklevel=2,
        )


def test_s8_corpo_aponta_ao_kernel_sem_duplica_lo(agent_root_parts) -> None:
    """S8) O corpo cita o kernel e o contrato normativo, sem copiar o loop do kernel."""
    _, body = agent_root_parts
    assert "Raiz = Executor de Workflow (R-068)" in body
    assert "invariantes-e-protocolos.md" in body
    assert "Alvo = 1ª etapa" not in body, "O corpo não pode duplicar o loop do kernel"


def test_s9_excecao_unica_em_invariantes_e_adr_existe() -> None:
    """S9) invariantes-e-protocolos.md tem exatamente 1 heading da raiz declarada e o ADR-0015 existe."""
    headings = re.findall(r"^#{1,6}\s+Raiz declarada \(@agent-root", _read(INVARIANTES_FILE), re.MULTILINE)
    assert len(headings) == 1, f"Esperado 1 heading 'Raiz declarada (@agent-root', encontrados {len(headings)}"
    assert list(ADR_DIR.glob("0015-*.md")), "ADR-0015 (raiz declarada) deve existir em docs/adr"


def test_s10_guarda_de_folga_do_kernel_m2() -> None:
    """S10) copilot-instructions.md ≤ 19.557 B (falha dura); folga < 100 B emite warning (D-3)."""
    size = COPILOT_INSTRUCTIONS_FILE.stat().st_size
    assert size <= M2_CEILING_BYTES, (
        f"copilot-instructions.md com {size} B excede o teto M2 de {M2_CEILING_BYTES} B; mova conteúdo "
        "para invariantes-e-protocolos.md e abra novo plano antes de acrescentar ao kernel."
    )
    folga = M2_CEILING_BYTES - size
    if folga < M2_WARN_SLACK_BYTES:
        warnings.warn(
            f"Folga M2 de {folga} B (< {M2_WARN_SLACK_BYTES} B): mova conteúdo para "
            "invariantes-e-protocolos.md; novo plano antes de acrescentar ao kernel.",
            stacklevel=2,
        )


def test_s11_perfil_do_agent_root(agent_root_parts) -> None:
    """S11) Perfil: sem ctx_batch/ctx_execute, sem edição direta, cláusulas, ❌, H1 e H2 canônicos."""
    frontmatter, body = agent_root_parts
    for proibido in ("ctx_batch", "ctx_execute"):
        assert proibido not in body, f"Corpo do agent-root não deve citar {proibido}"
    assert not (set(frontmatter["tools"]) & DIRECT_EDIT_TOOLS), "agent-root não pode ter tools de edição direta"
    for clausula in ("CLAUSE_OTEL_PASSTHROUGH", "CLAUSE_CONTEXT_HYDRATION", "❌"):
        assert clausula in body, f"Corpo do agent-root deve conter {clausula}"
    linhas = body.split("\n")
    assert "# Perfil Operacional" in linhas, "H1 canônico '# Perfil Operacional' ausente"
    h2 = [linha for linha in linhas if linha.startswith("## ")]
    for secao in ("ESCOPO", "Protocolo", "Formato de Saída", "Checklist"):
        assert any(secao in linha for linha in h2), f"H2 contendo '{secao}' ausente. H2 encontrados: {h2}"
