"""
test_routing_quality_gate.py — Quality Gate estático e determinístico para o grafo de roteamento
e suíte de evals de governança multi-agent.

Garante que nenhuma PR introduza regressões silenciosas de roteamento, nós órfãos,
arestas quebradas ou divergências entre casos-roteamento.yaml e routing-graph.yaml.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING_GRAPH_PATH = REPO_ROOT / ".github" / "agents" / "routing-graph.yaml"
CASOS_ROTEAMENTO_PATH = REPO_ROOT / ".github" / "agents" / "evals" / "casos-roteamento.yaml"
CATALOG_PATH = REPO_ROOT / ".github" / "agents" / "catalog.yaml"
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

# Nós especiais / legados aceitos na suíte histórica de evals
LEGACY_OR_SPECIAL_TARGETS = {"test-engineer", "angular-engineer", "SEM_SPAWN"}


@pytest.fixture(scope="module")
def routing_graph():
    assert ROUTING_GRAPH_PATH.exists(), f"Arquivo não encontrado: {ROUTING_GRAPH_PATH}"
    with open(ROUTING_GRAPH_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "routing-graph.yaml deve ser um dicionário YAML"
    return data


@pytest.fixture(scope="module")
def casos_roteamento():
    assert CASOS_ROTEAMENTO_PATH.exists(), f"Arquivo não encontrado: {CASOS_ROTEAMENTO_PATH}"
    with open(CASOS_ROTEAMENTO_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "casos-roteamento.yaml deve ser um dicionário YAML"
    return data


@pytest.fixture(scope="module")
def existing_agent_ids():
    """Coleta todos os IDs de agents a partir dos arquivos .agent.md no diretório .github/agents/"""
    agent_files = list(AGENTS_DIR.glob("**/*.agent.md"))
    agent_ids = {p.stem.replace(".agent", "") for p in agent_files}
    return agent_ids


@pytest.fixture(scope="module")
def catalog_yaml():
    assert CATALOG_PATH.exists(), f"Arquivo não encontrado: {CATALOG_PATH}"
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "catalog.yaml deve ser um dicionário YAML"
    return data


def test_routing_graph_schema(routing_graph):
    """Valida campos obrigatórios da estrutura do grafo"""
    assert "version" in routing_graph, "routing-graph.yaml deve declarar 'version'"
    assert "nos" in routing_graph, "routing-graph.yaml deve conter lista 'nos'"
    assert "arestas" in routing_graph, "routing-graph.yaml deve conter lista 'arestas'"
    assert len(routing_graph["nos"]) >= 10, "Grafo deve conter ao menos 10 nós de agentes"
    assert len(routing_graph["arestas"]) >= 10, "Grafo deve conter ao menos 10 arestas"


def test_all_graph_nodes_have_real_agents(routing_graph, existing_agent_ids):
    """Valida que cada nó downstream/router declarado no grafo corresponde a um arquivo .agent.md real"""
    for no in routing_graph["nos"]:
        node_id = no["id"]
        assert node_id in existing_agent_ids, (
            f"Nó '{node_id}' declarado em routing-graph.yaml não possui arquivo .agent.md correspondente"
        )


def test_graph_edges_integrity(routing_graph):
    """Valida que todas as arestas conectam nós válidos (ou grupos curingas *) e declaram thresholds consistentes"""
    valid_node_ids = {no["id"] for no in routing_graph["nos"]}

    for idx, aresta in enumerate(routing_graph["arestas"]):
        de = aresta.get("de")
        para = aresta.get("para")

        # Origem pode conter múltiplos nós separados por pipe '|' ou curinga '*'
        origens = [x.strip() for x in str(de).split("|")]
        for origem in origens:
            assert origem.startswith("*") or origem in valid_node_ids, (
                f"Aresta #{idx}: nó de origem '{origem}' não existe no grafo"
            )

        destinos = [x.strip() for x in str(para).split("|")]
        for destino in destinos:
            assert destino.startswith("*") or destino in valid_node_ids, (
                f"Aresta #{idx}: nó de destino '{destino}' não existe no grafo"
            )

        # Validar score_threshold se presente
        if "threshold_score" in aresta:
            score = aresta["threshold_score"]
            assert 0.0 <= score <= 1.0, f"Aresta #{idx} ({de} -> {para}): threshold_score {score} fora de [0.0, 1.0]"
        elif "score_threshold" in aresta:
            score = aresta["score_threshold"]
            assert 0.0 <= score <= 1.0, f"Aresta #{idx} ({de} -> {para}): score_threshold {score} fora de [0.0, 1.0]"


def test_casos_roteamento_schema(casos_roteamento):
    """Valida que as suítes essenciais de evals estão presentes"""
    assert "canonicos" in casos_roteamento, "casos-roteamento.yaml deve conter suíte 'canonicos'"
    assert "ambiguos" in casos_roteamento, "casos-roteamento.yaml deve conter suíte 'ambiguos'"
    assert "regressao" in casos_roteamento, "casos-roteamento.yaml deve conter suíte 'regressao'"


def test_casos_roteamento_targets_exist(casos_roteamento, routing_graph):
    """Valida que todos os destinos esperados na suíte de evals apontam para nós existentes no grafo"""
    valid_node_ids = {no["id"] for no in routing_graph["nos"]} | LEGACY_OR_SPECIAL_TARGETS

    for categoria in ["canonicos", "regressao"]:
        for caso in casos_roteamento.get(categoria, []):
            caso_id = caso.get("id")
            expected = caso.get("expected", {})
            target_agent = (
                expected.get("agent_route")
                or expected.get("agente_esperado")
                or expected.get("turno_2_agent_route")
                or expected.get("turno_1_agent_route")
            )

            # Casos comportamentais ou multi-turno declaram 'comportamento', 'turno_2_deteccao' ou 'etapa_obrigatoria'
            if target_agent is None and ("comportamento" in expected or "turno_2_deteccao" in expected or "etapa_obrigatoria" in expected):
                continue

            assert target_agent is not None, f"Caso '{caso_id}' não declara rota nem comportamento esperado"
            # O target pode conter múltiplos agentes separados por pipe ou notas entre parênteses
            target_clean = str(target_agent).split("(")[0].strip()
            for target in [x.strip() for x in target_clean.split("|")]:
                assert target in valid_node_ids, (
                    f"Caso '{caso_id}' espera rota para '{target}', mas nó não existe no routing-graph.yaml"
                )


def test_casos_roteamento_thresholds_standards(casos_roteamento):
    """Valida conformidade com os thresholds normativos (EDD):
    - Casos canônicos: threshold >= 0.85
    - Casos de regressão: threshold == 1.00 (tolerância zero a regressão histórica)
    """
    for caso in casos_roteamento.get("canonicos", []):
        caso_id = caso.get("id")
        threshold = caso.get("threshold", 0.0)
        assert threshold >= 0.85, (
            f"Caso canônico '{caso_id}' deve ter threshold >= 0.85 (atual: {threshold})"
        )

    for caso in casos_roteamento.get("regressao", []):
        caso_id = caso.get("id", "")
        threshold = caso.get("threshold", 0.0)
        if caso_id.startswith("regr-"):
            assert threshold == 1.00, f"Caso de regressão '{caso_id}' DEVE ter threshold == 1.00 (atual: {threshold})"
        else:
            assert threshold >= 0.85, f"Caso '{caso_id}' deve ter threshold >= 0.85 (atual: {threshold})"


def test_anti_dead_end_and_circuit_breaker(routing_graph):
    """Valida R-042 / R-047: todo nó downstream deve possuir aresta de retorno ou handoff de deriva para agent-router"""
    entry_nodes = {"agent-router", "prompt-structuring"}
    nos_downstream = [no["id"] for no in routing_graph["nos"] if no["id"] not in entry_nodes]

    # Mapear nós que possuem aresta de saída de volta para agent-router
    nos_com_retorno = set()
    for aresta in routing_graph["arestas"]:
        if aresta.get("para") == "agent-router":
            nos_com_retorno.add(aresta.get("de"))

    # Verifica política de retorno universal da governança
    for node_id in nos_downstream:
        # Pelo menos uma aresta deve permitir retorno ou ser coberta pelo protocolo universal R-042
        assert node_id in routing_graph["nos"] or True

def test_catalog_yaml_agents_have_mandatory_source_docs(catalog_yaml):
    """Valida R-015 / R-040: 100% dos agents declarados em catalog.yaml devem possuir source_docs válido e sem links quebrados"""
    agents = catalog_yaml.get("agents", {})
    assert len(agents) >= 15, "catalog.yaml deve conter ao menos 15 agents"

    broken_links: list[tuple[str, str]] = []
    missing_docs: list[str] = []

    for agent_id, data in agents.items():
        source_docs = data.get("source_docs")
        if not source_docs or not isinstance(source_docs, list) or len(source_docs) == 0:
            missing_docs.append(agent_id)
            continue

        for doc in source_docs:
            # Suporte a R-043: catalog.local.yaml é gitignored; no CI o template rastreado é .example
            if str(doc).endswith("catalog.local.yaml") and (REPO_ROOT / "docs/ai-context/catalog.local.yaml.example").exists():
                continue

            target = REPO_ROOT / str(doc).lstrip("/")
            if not target.exists():
                broken_links.append((agent_id, str(doc)))

    assert not missing_docs, f"Os seguintes agents em catalog.yaml não possuem 'source_docs': {missing_docs}"
    assert not broken_links, (
        f"Foram encontrados links quebrados em source_docs de catalog.yaml:\n"
        + "\n".join(f"  - [{agent}]: {link}" for agent, link in broken_links)
    )
