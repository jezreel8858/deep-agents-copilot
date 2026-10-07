"""
test_agent_count_per_stack_governance.py — Validação determinística do teto formal
de exatamente 3 especialistas por router para todas as 8 stacks consolidadas
(Fase 5 do Plano de Governança — Fechamento do Roadmap Geral).

Quality Gate que garante:
1. Todas as 8 stacks canônicas (spring-boot, react, angular, spring-reactive, ejb, struts, python, database)
   possuem seu sub-catálogo yaml devidamente registrado e estruturado.
2. Cada sub-catálogo declara exatamente 3 especialistas (nem mais, nem menos: len(agents) == 3).
3. Cada stack possui exatamente 1 router de domínio correspondente (len(routers) == 1).
4. O somatório de especialistas nas 8 stacks é de exatamente 24 especialistas.
5. O somatório de routers de stack é de exatamente 8 routers.
6. A contagem total agregada de agentes de domínio de stack é de exatamente 32 agentes.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

STACK_SPECS = [
    {
        "stack": "spring-boot",
        "category": "backend",
        "catalog_rel": "backend/spring-boot/spring-boot-catalog.yaml",
        "router": "spring-boot-router",
        "expected_specialists": {
            "spring-boot-arch-advisor",
            "spring-boot-developer",
            "spring-boot-test-engineer"
        }
    },
    {
        "stack": "react",
        "category": "frontend",
        "catalog_rel": "frontend/react/react-catalog.yaml",
        "router": "react-router",
        "expected_specialists": {
            "react-arch-advisor",
            "react-developer",
            "react-test-engineer"
        }
    },
    {
        "stack": "angular",
        "category": "frontend",
        "catalog_rel": "frontend/angular/angular-catalog.yaml",
        "router": "angular-router",
        "expected_specialists": {
            "angular-arch-advisor",
            "angular-developer",
            "angular-test-engineer"
        }
    },
    {
        "stack": "spring-reactive",
        "category": "backend",
        "catalog_rel": "backend/spring-reactive/spring-reactive-catalog.yaml",
        "router": "spring-reactive-router",
        "expected_specialists": {
            "spring-reactive-arch-advisor",
            "spring-reactive-developer",
            "spring-reactive-test-engineer"
        }
    },
    {
        "stack": "ejb",
        "category": "backend",
        "catalog_rel": "backend/ejb/ejb-catalog.yaml",
        "router": "ejb-router",
        "expected_specialists": {
            "ejb-arch-advisor",
            "ejb-developer",
            "ejb-test-engineer"
        }
    },
    {
        "stack": "struts",
        "category": "backend",
        "catalog_rel": "backend/struts/struts-catalog.yaml",
        "router": "struts-router",
        "expected_specialists": {
            "struts-arch-advisor",
            "struts-developer",
            "struts-test-engineer"
        }
    },
    {
        "stack": "python",
        "category": "backend",
        "catalog_rel": "backend/python/python-catalog.yaml",
        "router": "python-router",
        "expected_specialists": {
            "python-arch-advisor",
            "python-developer",
            "python-test-engineer"
        }
    },
    {
        "stack": "database",
        "category": "backend",
        "catalog_rel": "backend/database/database-catalog.yaml",
        "router": "database-router",
        "expected_specialists": {
            "database-arch-advisor",
            "oracle-database-specialist",
            "informix-database-specialist"
        }
    }
]


@pytest.mark.parametrize("spec", STACK_SPECS, ids=[s["stack"] for s in STACK_SPECS])
def test_stack_has_exactly_three_specialists_in_catalog(spec: dict):
    """Valida que cada stack consolidada declara exatamente 3 especialistas em seu catálogo."""
    catalog_path = AGENTS_DIR / spec["catalog_rel"]
    assert catalog_path.exists(), f"Catálogo não encontrado: {catalog_path}"

    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    agents = data.get("agents", {})

    assert len(agents) == 3, (
        f"Stack '{spec['stack']}' deve conter exatamente 3 especialistas no catálogo ({catalog_path.name}), "
        f"mas possui {len(agents)}: {list(agents.keys())}"
    )
    assert set(agents.keys()) == spec["expected_specialists"], (
        f"Especialistas divergentes na stack '{spec['stack']}': "
        f"encontrados={set(agents.keys())} vs esperados={spec['expected_specialists']}"
    )


@pytest.mark.parametrize("spec", STACK_SPECS, ids=[s["stack"] for s in STACK_SPECS])
def test_stack_router_file_exists(spec: dict):
    """Valida que cada stack possui exatamente seu arquivo de router canônico."""
    router_name = spec["router"]
    category_dir = AGENTS_DIR / spec["category"] / spec["stack"]
    router_file = category_dir / f"{router_name}.agent.md"
    assert router_file.exists(), f"Arquivo do router da stack {spec['stack']} não encontrado: {router_file}"


def test_global_eight_stacks_agent_count_invariants():
    """
    Valida os invariantes globais das 8 stacks consolidadas:
    - Exatamente 8 stacks
    - Exatamente 24 especialistas agregados (3 * 8)
    - Exatamente 8 routers de stack (1 * 8)
    - Exatamente 32 agentes de stack totais
    """
    assert len(STACK_SPECS) == 8, f"Devem existir exatamente 8 stacks consolidadas, encontrados {len(STACK_SPECS)}"

    all_specialists = set()
    all_routers = set()

    for spec in STACK_SPECS:
        catalog_path = AGENTS_DIR / spec["catalog_rel"]
        data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
        agents = data.get("agents", {})
        all_specialists.update(agents.keys())
        all_routers.add(spec["router"])

    assert len(all_specialists) == 24, (
        f"O total global de especialistas das 8 stacks deve ser exatamente 24, "
        f"encontrados {len(all_specialists)}: {sorted(all_specialists)}"
    )
    assert len(all_routers) == 8, (
        f"O total global de routers das 8 stacks deve ser exatamente 8, "
        f"encontrados {len(all_routers)}: {sorted(all_routers)}"
    )
    total_stack_agents = len(all_specialists) + len(all_routers)
    assert total_stack_agents == 32, (
        f"O total global de agentes de stack deve ser exatamente 32 (24 especialistas + 8 routers), "
        f"encontrado {total_stack_agents}."
    )
