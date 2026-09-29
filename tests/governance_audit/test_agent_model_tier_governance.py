"""
test_agent_model_tier_governance.py — Validação determinística de modelo e tier de agents (R-021 e R-055 Q3).

Quality Gate determinístico que garante:
1. Nenhum agent (.github/agents/**/*.agent.md) fixa permanentemente modelo de tier premium
   (ex.: contendo 'Opus' no valor) sem uma exceção formalmente documentada (campo model_exception_reason).
2. Todo escalonamento de modelo para tier premium deve ser pontual (por chamada/tarefa via sinal 🧠
   em run_subagent conforme R-021), nunca uma característica permanente do agent no catálogo.
3. Agentes com modelo premium autorizados pela governança (§9 governance-factory-patterns) possuem
   exceção justificada em conformidade com o Portão de Reúso Sistêmico (R-055).
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tests.governance_audit._helpers import remediation

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

# Agentes autorizados por governança a utilizar modelo premium (§9 governance-factory-patterns)
ALLOWED_PREMIUM_AGENTS = {
    "tech-solution-architect",
    "debugger",
}


def extract_frontmatter(file_path: Path) -> dict:
    """Extrai e faz parse do frontmatter YAML delimitado por --- em um arquivo markdown.

    Args:
        file_path: Caminho do arquivo a ser inspecionado.

    Returns:
        Dicionário com os metadados do frontmatter parseados.
    """
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            return yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            return {}
    return {}


def is_premium_tier_model(model: str) -> bool:
    """Verifica se a string de modelo indica tier premium/máximo (ex.: Opus).

    Args:
        model: Identificador do modelo configurado no frontmatter.

    Returns:
        True se o modelo pertencer à família premium restrita, False caso contrário.
    """
    if not model:
        return False
    return "opus" in model.lower()


def get_all_agent_files() -> list[Path]:
    """Retorna a lista de todos os arquivos de agents operacionais, excluindo templates.

    Returns:
        Lista de Paths apontando para cada .agent.md do repositório.
    """
    return [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "templates" not in p.parts
    ]


def test_deve_bloquear_modelo_premium_sem_excecao_documentada_em_agents() -> None:
    """Valida que nenhum agent define modelo premium fixo sem justificativa de exceção (R-021).

    R-021 (Model Routing Signal): Escalonamento de modelo para tier premium (ex.: Claude Opus)
    é estritamente pontual (por tarefa/despacho via sinal 🧠 em run_subagent) e NUNCA permanente
    no catálogo para papéis de execução genérica ou contínua.
    """
    agent_files = get_all_agent_files()
    assert len(agent_files) >= 50, f"Catálogo incompleto: apenas {len(agent_files)} agents encontrados."

    violations: list[str] = []

    for agent_file in agent_files:
        fm = extract_frontmatter(agent_file)
        model = str(fm.get("model", "")).strip()
        stem = agent_file.name.replace(".agent.md", "")
        rel_path = agent_file.relative_to(REPO_ROOT)

        if is_premium_tier_model(model):
            exception_reason = str(fm.get("model_exception_reason", "")).strip()
            if not exception_reason and stem not in ALLOWED_PREMIUM_AGENTS:
                violations.append(
                    f"[{rel_path}] Declara modelo premium '{model}' sem exceção formal documentada."
                )

    assert not violations, remediation(
        f"Violação de R-021: {len(violations)} agent(s) com modelo premium fixo não autorizado:\n"
        + "\n".join(violations),
        fix_hint=(
            "Altere 'model:' para 'Gemini 3.8 Flash' (operacional/test-writer) ou 'Claude Sonnet 5' "
            "(deliberativo/planejamento). Escalonamentos de modelo devem ser PONTUAIS via sinal 🧠 "
            "em run_subagent (R-021), nunca fixados permanentemente no catálogo. Para exceções "
            "arquiteturais estritas, adicione 'model_exception_reason: \"<justificativa>\"' no frontmatter."
        ),
    )


def test_deve_validar_que_agentes_com_excecao_premium_possuem_justificativa_formal() -> None:
    """Garante que agents da allowlist com modelo premium contenham model_exception_reason formal."""
    agent_files = get_all_agent_files()

    for agent_file in agent_files:
        stem = agent_file.name.replace(".agent.md", "")
        if stem in ALLOWED_PREMIUM_AGENTS:
            fm = extract_frontmatter(agent_file)
            model = str(fm.get("model", "")).strip()
            rel_path = agent_file.relative_to(REPO_ROOT)

            assert is_premium_tier_model(model), remediation(
                f"[{rel_path}] Agente homologado para premium '{stem}' não possui modelo Opus configurado.",
                fix_hint=f"Verifique se o modelo de {rel_path} foi alterado indevidamente.",
            )

            exception_reason = str(fm.get("model_exception_reason", "")).strip()
            assert exception_reason, remediation(
                f"[{rel_path}] Agente homologado '{stem}' deve declarar 'model_exception_reason:' formal no frontmatter.",
                fix_hint=f"Adicione 'model_exception_reason: \"...\"' no frontmatter de {rel_path}.",
            )


def test_deve_falhar_quando_novo_agente_operacional_declarar_modelo_opus_sem_excecao(tmp_path: Path) -> None:
    """Sensor determinístico: comprova que novo agent sintético com modelo Opus é reprovado."""
    bad_agent = tmp_path / "synthetic-worker.agent.md"
    bad_agent.write_text(
        "---\n"
        "name: synthetic-worker\n"
        "model: \"Claude Opus 5.5\"\n"
        "tools: ['list_dir', 'run_subagent']\n"
        "---\n"
        "# Perfil Operacional\n",
        encoding="utf-8",
    )

    fm = extract_frontmatter(bad_agent)
    model = str(fm.get("model", "")).strip()
    exception_reason = str(fm.get("model_exception_reason", "")).strip()
    is_allowed = bad_agent.name.replace(".agent.md", "") in ALLOWED_PREMIUM_AGENTS

    has_violation = is_premium_tier_model(model) and not exception_reason and not is_allowed
    assert has_violation is True, "Sensor de governança deve detectar agente não autorizado com modelo premium"
