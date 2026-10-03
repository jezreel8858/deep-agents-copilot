"""
test_prompt_synthesis_output_format_governance.py — Testes determinísticos para validação
do redesenho do WORKFLOW-PROMPT-SYNTHESIS e migração global XML -> Markdown (R-055 / R-064).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_MD = REPO_ROOT / ".github" / "agents" / "workflows.md"
WORKFLOW_PROMPT_SYNTHESIS_FILE = REPO_ROOT / ".github" / "agents" / "workflows" / "workflow-prompt-synthesis.md"
CRAFT_PROMPT_MD = REPO_ROOT / ".github" / "prompts" / "craft-prompt.prompt.md"
PROMPT_STRUCTURING_AGENT = REPO_ROOT / ".github" / "agents" / "prompt-structuring.agent.md"
PROMPT_SKILL = REPO_ROOT / ".github" / "skills" / "prompt-engineering-patterns" / "SKILL.md"
REQUIREMENTS_ANALYST_AGENT = REPO_ROOT / ".github" / "agents" / "requirements-analyst.agent.md"
TEMPLATE_CANONICAL = REPO_ROOT / "templates" / "prompt-synthesis-output.md"


def test_no_residual_xml_prompt_synthesis():
    """Caso 1: Valida ausência de XML residual em workflows/workflow-prompt-synthesis.md
    (§3.9, fatiado de workflows.md — R-066/F3) e craft-prompt.prompt.md.

    Nota de escopo ([2.52.2]): `<execution_protocol>` é também o nome do bloco
    operacional legítimo de Plan-Then-Batch/R-066 (propagado por
    tools/agent_protocol_sync/sync_execution_protocol.py para todo .agent.md/*.prompt.md,
    incluindo o próprio craft-prompt.prompt.md). Esse bloco é removido do texto ANTES
    da varredura de tags XML residuais, para não colidir com o escaneamento do antigo
    formato de SAÍDA do WORKFLOW-PROMPT-SYNTHESIS (conceito distinto e não-relacionado)."""
    assert WORKFLOW_PROMPT_SYNTHESIS_FILE.is_file(), (
        f"Arquivo fatiado {WORKFLOW_PROMPT_SYNTHESIS_FILE} não encontrado (ver F3 — fatiamento de workflows.md)"
    )
    s39_section = WORKFLOW_PROMPT_SYNTHESIS_FILE.read_text(encoding="utf-8")
    cp_text_raw = CRAFT_PROMPT_MD.read_text(encoding="utf-8")
    # Remove o bloco operacional legítimo antes de escanear por XML residual (ver nota acima).
    cp_text = re.sub(r"<execution_protocol>[\s\S]*?</execution_protocol>", "", cp_text_raw)

    # Proibe tags XML canônicas residuais na seção 3.9 e craft-prompt
    prohibited_xml_tags = [
        "<role>", "</role>",
        "<project_context>", "</project_context>",
        "<grounded_files>", "</grounded_files>",
        "<acceptance_criteria>", "</acceptance_criteria>",
        "<execution_protocol>", "</execution_protocol>",
    ]
    for tag in prohibited_xml_tags:
        assert tag not in s39_section, f"Tag XML residual '{tag}' encontrada em workflows/workflow-prompt-synthesis.md"
        assert tag not in cp_text, f"Tag XML residual '{tag}' encontrada em craft-prompt.prompt.md (fora do bloco <execution_protocol> legítimo)"

    assert "XML canônico" not in s39_section, "Menção a 'XML canônico' residual em workflows/workflow-prompt-synthesis.md"
    assert "tags XML" not in s39_section, "Menção a 'tags XML' residual em workflows/workflow-prompt-synthesis.md"
    assert "tags XML" not in cp_text, "Menção a 'tags XML' residual em craft-prompt.prompt.md"


def test_prompt_structuring_and_skill_markdown_migration():
    """Caso 2: Valida migração global do prompt-structuring e skill para seções Markdown."""
    ps_text = PROMPT_STRUCTURING_AGENT.read_text(encoding="utf-8")
    skill_text = PROMPT_SKILL.read_text(encoding="utf-8")

    assert "<task>/<context>/<constraints>/<output_format>" not in ps_text, (
        "prompt-structuring.agent.md ainda contém menção à cadeia XML antiga"
    )
    assert "<task>/<context>/<constraints>/<output_format>" not in skill_text, (
        "prompt-engineering-patterns/SKILL.md ainda contém menção à cadeia XML antiga"
    )

    # Verifica presença das seções Markdown canônicas
    assert "## Tarefa" in ps_text
    assert "## Contexto" in ps_text
    assert "## Restrições e Não-Escopo" in ps_text
    assert "## Formato de Saída Esperado" in ps_text

    assert "## Tarefa" in skill_text
    assert "## Contexto" in skill_text
    assert "## Restrições e Não-Escopo" in skill_text
    assert "## Formato de Saída Esperado" in skill_text


def test_red_teaming_solution_space_checklist():
    """Caso 3: Valida checklist ativo de Red-Teaming de Solution Space e 4 critérios excludentes."""
    wf_text = WORKFLOW_PROMPT_SYNTHESIS_FILE.read_text(encoding="utf-8")
    cp_text = CRAFT_PROMPT_MD.read_text(encoding="utf-8")

    criterios = [
        "Classes/métodos internos",
        "Bibliotecas/frameworks/algoritmos não pedidos",
        "Arquitetura/design patterns prescritos",
        "Tecnologias não mencionadas",
    ]
    for c in criterios:
        assert c in wf_text, f"Critério '{c}' não encontrado em workflows/workflow-prompt-synthesis.md"

    assert "Quality Gate ativo e Red-Teaming analítico contra o Solution Space" in wf_text
    assert "consumo exclusivo downstream" in wf_text
    assert "consumo exclusivo downstream" in cp_text
    assert "templates/prompt-synthesis-output.md" in wf_text
    assert TEMPLATE_CANONICAL.exists(), "Template canônico templates/prompt-synthesis-output.md não existe"


def test_elicitation_round_bounds_5_to_10():
    """Caso 4: Valida limites de 5 a 10 rodadas e cláusula de teto explícitos."""
    wf_text = WORKFLOW_PROMPT_SYNTHESIS_FILE.read_text(encoding="utf-8")
    cp_text = CRAFT_PROMPT_MD.read_text(encoding="utf-8")
    ra_text = REQUIREMENTS_ANALYST_AGENT.read_text(encoding="utf-8")

    assert "5 a 10 rodadas" in wf_text
    assert "5 a 10 rodadas" in cp_text
    assert "5 a 10 rodadas" in ra_text

    # Cláusula de teto na 10ª rodada
    assert "10ª rodada" in wf_text
    assert "10ª rodada" in cp_text
    assert "10ª rodada" in ra_text
    assert "lacunas residuais" in wf_text.lower()
    assert "lacunas residuais" in cp_text.lower()


def test_typed_state_bag_parity():
    """Caso 5: Valida paridade dos campos novos no Typed State Bag do WORKFLOW-PROMPT-SYNTHESIS."""
    wf_text = WORKFLOW_PROMPT_SYNTHESIS_FILE.read_text(encoding="utf-8")

    # Extrai o trecho do YAML state bag em workflows/workflow-prompt-synthesis.md
    s39_idx = wf_text.find("### 3.9 WORKFLOW 9: `WORKFLOW-PROMPT-SYNTHESIS`")
    assert s39_idx != -1
    bag_start = wf_text.find("workflow_state:", s39_idx)
    assert bag_start != -1
    bag_end = wf_text.find("```", bag_start)
    assert bag_end != -1

    yaml_block = wf_text[bag_start:bag_end]
    state_bag = yaml.safe_load(yaml_block)

    assert state_bag["workflow_state"]["workflow_id"] == "WORKFLOW-PROMPT-SYNTHESIS"
    prompt_alvo = state_bag["workflow_state"]["prompt_alvo"]

    assert "rodadas_elicitacao_realizadas" in prompt_alvo
    assert prompt_alvo["rodadas_elicitacao_realizadas"] == 5
    assert "lacunas_residuais_declaradas" in prompt_alvo
    assert isinstance(prompt_alvo["lacunas_residuais_declaradas"], list)
    assert "red_teaming_solution_space" in prompt_alvo
    assert prompt_alvo["red_teaming_solution_space"]["aprovado"] is True
    assert prompt_alvo["formato_saida"] == "markdown_code_block"
    assert prompt_alvo["consumo_exclusivo_agents"] is True
    assert prompt_alvo["bloco_md_gerado"] is True
