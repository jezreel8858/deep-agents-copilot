"""
test_harness_engineering_governance.py — Validação determinística da governança de Harness Engineering (R-061).

Garante que:
1. CLAUDE.md formaliza a regra normativa R-061.
2. A skill harness-engineering-patterns possui frontmatter canônico válido (name, tier, category, triggers).
3. .github/skills/.index.json registra formalmente a skill harness-engineering-patterns.
4. .github/skills/README.md referencia a skill harness-engineering-patterns em sua listagem.
"""

from pathlib import Path
import json
import re
from tests.governance_audit._helpers import remediation

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent


def test_claude_md_contains_r061():
    """Garante que a regra normativa R-061 está formalizada em CLAUDE.md."""
    claude_path = WORKSPACE_ROOT / "CLAUDE.md"
    assert claude_path.exists(), remediation(
        f"Arquivo {claude_path} não encontrado.",
        fix_hint="Restaurar o arquivo normativo CLAUDE.md na raiz do repositório."
    )
    content = claude_path.read_text(encoding="utf-8")
    assert "R-061" in content, remediation(
        "Regra R-061 não encontrada em CLAUDE.md.",
        fix_hint="Adicionar a seção normativa 'R-061 — Diagnóstico de Harness-vs-Modelo e Poda Anti-Bloat' em CLAUDE.md."
    )


def test_harness_engineering_skill_frontmatter():
    """Garante que a skill harness-engineering-patterns existe e possui frontmatter válido."""
    skill_path = WORKSPACE_ROOT / ".github" / "skills" / "harness-engineering-patterns" / "SKILL.md"
    assert skill_path.exists(), remediation(
        f"Arquivo {skill_path} não encontrado.",
        fix_hint="Criar a skill canônica em .github/skills/harness-engineering-patterns/SKILL.md."
    )
    content = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert match, remediation(
        f"Frontmatter YAML não encontrado no topo de {skill_path}.",
        fix_hint="Adicionar delimitadores '---' e metadados no início do arquivo SKILL.md."
    )
    fm = match.group(1)
    assert "name: harness-engineering-patterns" in fm, remediation(
        "Campo 'name' inválido ou ausente no frontmatter.",
        fix_hint="Definir 'name: harness-engineering-patterns' no frontmatter da skill."
    )
    assert "tier: 1" in fm, remediation(
        "Campo 'tier' inválido ou ausente no frontmatter.",
        fix_hint="Definir 'tier: 1' no frontmatter da skill."
    )
    assert "category: process" in fm, remediation(
        "Campo 'category' inválido ou ausente no frontmatter.",
        fix_hint="Definir 'category: process' no frontmatter da skill."
    )
    assert "triggers:" in fm, remediation(
        "Lista 'triggers' ausente no frontmatter.",
        fix_hint="Adicionar lista declarativa de triggers em PT-BR no frontmatter da skill."
    )


def test_index_json_contains_harness_engineering_skill():
    """Garante que a skill harness-engineering-patterns está registrada em .index.json."""
    index_path = WORKSPACE_ROOT / ".github" / "skills" / ".index.json"
    assert index_path.exists(), remediation(
        f"Arquivo {index_path} não encontrado.",
        fix_hint="Restaurar o catálogo estruturado .index.json em .github/skills/."
    )
    with index_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data.get("skills", [])
    assert isinstance(skills, list), remediation(
        "Chave 'skills' de .index.json deve ser uma lista de objetos (schema canônico do catálogo).",
        fix_hint="Restaurar 'skills' como array JSON (não objeto/dict) em .github/skills/.index.json."
    )
    matches = [s for s in skills if s.get("name") == "harness-engineering-patterns"]
    assert matches, remediation(
        "Skill 'harness-engineering-patterns' não encontrada na lista 'skills' de .index.json.",
        fix_hint="Adicionar objeto {'name': 'harness-engineering-patterns', ...} na lista de skills de .github/skills/.index.json."
    )
    entry = matches[0]
    assert entry.get("tier") == 1, remediation(
        "Tier de 'harness-engineering-patterns' em .index.json deve ser 1.",
        fix_hint="Configurar 'tier: 1' no registro da skill em .index.json."
    )
    assert entry.get("category") == "process", remediation(
        "Categoria de 'harness-engineering-patterns' em .index.json deve ser 'process'.",
        fix_hint="Configurar 'category: \"process\"' no registro da skill em .index.json."
    )


def test_skills_readme_references_harness_engineering():
    """Garante que o catálogo em .github/skills/README.md referencia a nova skill."""
    readme_path = WORKSPACE_ROOT / ".github" / "skills" / "README.md"
    assert readme_path.exists(), remediation(
        f"Arquivo {readme_path} não encontrado.",
        fix_hint="Restaurar o arquivo .github/skills/README.md."
    )
    content = readme_path.read_text(encoding="utf-8")
    assert "`harness-engineering-patterns`" in content, remediation(
        "Skill `harness-engineering-patterns` não encontrada na listagem de .github/skills/README.md.",
        fix_hint="Adicionar linha com a skill na tabela '3) Skills Atuais' de .github/skills/README.md."
    )


def test_structured_intake_patterns_contains_grill_me_protocol():
    """Garante que structured-intake-patterns formaliza o protocolo de Grilling Cético ('Grill Me')."""
    skill_path = WORKSPACE_ROOT / ".github" / "skills" / "structured-intake-patterns" / "SKILL.md"
    assert skill_path.exists(), remediation(
        f"Arquivo {skill_path} não encontrado.",
        fix_hint="Restaurar a skill canônica structured-intake-patterns."
    )
    content = skill_path.read_text(encoding="utf-8")
    assert "Grilling Cético" in content or "Grill Me" in content, remediation(
        "Protocolo de Grilling Cético ('Grill Me') não encontrado em structured-intake-patterns/SKILL.md.",
        fix_hint="Adicionar a seção canônica 'Protocolo de Grilling Cético (\"Grill Me\")' em structured-intake-patterns/SKILL.md."
    )


def test_task_decomposition_contains_tracer_bullets():
    """Garante que task-decomposition-patterns formaliza Tracer Bullets (Vertical Slicing)."""
    skill_path = WORKSPACE_ROOT / ".github" / "skills" / "task-decomposition-patterns" / "SKILL.md"
    assert skill_path.exists(), remediation(
        f"Arquivo {skill_path} não encontrado.",
        fix_hint="Restaurar a skill canônica task-decomposition-patterns."
    )
    content = skill_path.read_text(encoding="utf-8")
    assert "Tracer Bullets" in content or "Vertical Slicing" in content, remediation(
        "Estratégia 'Tracer Bullets' ou 'Vertical Slicing' não encontrada em task-decomposition-patterns/SKILL.md.",
        fix_hint="Adicionar 'Tracer Bullets (Vertical Slicing)' na tabela e orientações de task-decomposition-patterns/SKILL.md."
    )


def test_context_md_template_exists_and_valid():
    """Garante que o template canônico CONTEXT.template.md existe e possui seções estruturadas."""
    template_path = WORKSPACE_ROOT / "docs" / "agent-context" / "templates" / "CONTEXT.template.md"
    assert template_path.exists(), remediation(
        f"Arquivo {template_path} não encontrado.",
        fix_hint="Criar o template canônico docs/agent-context/templates/CONTEXT.template.md."
    )
    content = template_path.read_text(encoding="utf-8")
    assert "Termos de Domínio" in content, remediation(
        "Seção 'Termos de Domínio' ausente em CONTEXT.template.md.",
        fix_hint="Adicionar tabela de Termos de Domínio e Definições Canônicas em CONTEXT.template.md."
    )
    assert "Invariantes de Negócio" in content, remediation(
        "Seção 'Invariantes de Negócio' ausente em CONTEXT.template.md.",
        fix_hint="Adicionar seção de Invariantes de Negócio Não-Negociáveis em CONTEXT.template.md."
    )
    assert "Anti-Termos" in content, remediation(
        "Seção 'Anti-Termos' ausente em CONTEXT.template.md.",
        fix_hint="Adicionar tabela de Anti-Termos em CONTEXT.template.md."
    )


def test_wiring_of_new_skills_in_consumer_agents():
    """Valida o wiring determinístico das novas skills e templates nos frontmatters dos agents consumidores."""
    expected_wirings = {
        # Wiring 1: harness-engineering-patterns
        ".github/agents/agent-router.agent.md": [
            ".github/skills/harness-engineering-patterns/SKILL.md",
            ".github/skills/agent-evals-lab/SKILL.md",
            ".github/skills/prompt-engineering-patterns/SKILL.md",
        ],
        ".github/agents/agent-auditor.agent.md": [
            ".github/skills/harness-engineering-patterns/SKILL.md",
        ],
        ".github/agents/governance-maintainer.agent.md": [
            ".github/skills/harness-engineering-patterns/SKILL.md",
        ],
        ".github/agents/tech-solution-architect.agent.md": [
            ".github/skills/harness-engineering-patterns/SKILL.md",
            ".github/skills/agent-evals-lab/SKILL.md",
            ".github/skills/requirements-engineering-patterns/SKILL.md",
        ],
        # Wiring 2 & 3: agent-evals-lab & prompt-engineering-patterns
        ".github/agents/governance-factory.agent.md": [
            ".github/skills/agent-evals-lab/SKILL.md",
            ".github/skills/prompt-engineering-patterns/SKILL.md",
        ],
        # Wiring 4: structured-intake-patterns
        ".github/agents/test-strategy.agent.md": [
            ".github/skills/structured-intake-patterns/SKILL.md",
        ],
        ".github/agents/business-rules-extractor.agent.md": [
            ".github/skills/structured-intake-patterns/SKILL.md",
        ],
        ".github/agents/requirements-analyst.agent.md": [
            ".github/skills/structured-intake-patterns/SKILL.md",
        ],
        # Wiring 6: CONTEXT.template.md
        ".github/agents/docs-engineer.agent.md": [
            "docs/agent-context/templates/CONTEXT.template.md",
        ],
        ".github/agents/adapter-generator.agent.md": [
            "docs/agent-context/templates/CONTEXT.template.md",
        ],
    }

    for agent_rel_path, required_docs in expected_wirings.items():
        agent_path = WORKSPACE_ROOT / agent_rel_path
        assert agent_path.exists(), remediation(
            f"Arquivo de agente {agent_path} não encontrado.",
            fix_hint=f"Restaurar o agente em {agent_rel_path}."
        )
        content = agent_path.read_text(encoding="utf-8")
        fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        assert fm_match, remediation(
            f"Frontmatter não encontrado em {agent_rel_path}.",
            fix_hint=f"Adicionar frontmatter YAML canônico em {agent_rel_path}."
        )
        fm_text = fm_match.group(1)
        sd_match = re.search(r"source_docs:\s*\n((?:  - [^\n]+(?:\n|$))+)", fm_text)
        assert sd_match, remediation(
            f"Seção source_docs ausente no frontmatter de {agent_rel_path}.",
            fix_hint=f"Adicionar source_docs no frontmatter de {agent_rel_path}."
        )
        source_docs = [line.strip().replace("- ", "") for line in sd_match.group(1).strip().split("\n") if line.strip()]

        for req_doc in required_docs:
            assert req_doc in source_docs, remediation(
                f"Referência obrigatória '{req_doc}' ausente no source_docs de {agent_rel_path}.",
                fix_hint=f"Adicionar '- {req_doc}' à lista source_docs em {agent_rel_path}."
            )
