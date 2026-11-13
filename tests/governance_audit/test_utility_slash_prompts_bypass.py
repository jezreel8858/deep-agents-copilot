"""
test_utility_slash_prompts_bypass.py — Validação determinística do Fast-Path / Bypass Canônico
(router_bypass: utility | slash_workflow) para Slash Prompts Explícitos frente a R-037 e R-063.

Quality Gate que garante:
a) Os 8 prompts utility (ctx-*, commit, health) declaram router_bypass: utility, não possuem tools de
   mutação de código nem run_in_terminal, e proíbem invocar @agent-router;
b) Os 13 prompts slash_workflow (craft-prompt, add-project-context, connect-integration-graphs,
   deep-search, del-project-context, eval-workflows, implement, init-context, plan, review,
   strategic-review, validate, visualize-graph) declaram router_bypass: slash_workflow e proíbem
   invocar @agent-router na triagem inicial;
c) agent-router.prompt.md é o único .prompt.md que NÃO declara router_bypass;
d) CLAUDE.md, .github/copilot-instructions.md e .github/agents/agent-router.agent.md documentam
   o bypass/guard de Slash Prompts (router_bypass).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
AGENT_ROUTER_PATH = REPO_ROOT / ".github" / "agents" / "agent-router.agent.md"
ROUTER_TEMPLATE_PATH = REPO_ROOT / ".github" / "agents" / "templates" / "router-agent.md"
PROMPT_TEMPLATE_PATH = PROMPTS_DIR / "templates" / "prompt-template.md"

ALLOWED_UTILITY_PROMPTS = {
    "ctx-status.prompt.md",
    "ctx-doctor.prompt.md",
    "ctx-insight.prompt.md",
    "ctx-resume.prompt.md",
    "ctx-checkpoint.prompt.md",
    "ctx-start.prompt.md",
    "commit.prompt.md",
    "health.prompt.md",
}

ALLOWED_SLASH_WORKFLOW_PROMPTS = {
    "add-project-context.prompt.md",
    "connect-integration-graphs.prompt.md",
    "craft-prompt.prompt.md",
    "deep-search.prompt.md",
    "del-project-context.prompt.md",
    "eval-workflows.prompt.md",
    "implement.prompt.md",
    "init-context.prompt.md",
    "plan.prompt.md",
    "review.prompt.md",
    "strategic-review.prompt.md",
    "validate.prompt.md",
    "visualize-graph.prompt.md",
}

FORBIDDEN_MUTATION_OR_TERMINAL_TOOLS = {
    "run_in_terminal",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "insert_edit_into_file",
    "create_file",
    "edit_file",
    "run_subagent",
}


def _extract_frontmatter(text: str) -> str:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    return match.group(1) if match else ""


def _extract_declared_tools(frontmatter: str) -> set[str]:
    inline_match = re.search(r"^tools:\s*\[(.*?)\]", frontmatter, re.MULTILINE | re.DOTALL)
    if inline_match:
        return {
            t.strip().strip("'\"")
            for t in inline_match.group(1).split(",")
            if t.strip()
        }
    block_match = re.search(r"^tools:\s*\r?\n((?:\s*-\s*.+\r?\n?)+)", frontmatter, re.MULTILINE)
    if block_match:
        return {
            re.sub(r"^\s*-\s*", "", line).strip().strip("'\"")
            for line in block_match.group(1).splitlines()
            if line.strip()
        }
    return set()


def test_utility_prompts_declare_router_bypass_and_no_mutation_or_terminal_tools():
    """a) Os 8 prompts utility (ctx-*, commit, health) declaram router_bypass: utility, não possuem tools de mutação de código nem run_in_terminal, e proíbem invocar @agent-router."""
    assert len(ALLOWED_UTILITY_PROMPTS) == 8
    for filename in sorted(ALLOWED_UTILITY_PROMPTS):
        prompt_path = PROMPTS_DIR / filename
        assert prompt_path.exists(), f"Prompt utilitário ausente: {filename}"
        content = prompt_path.read_text(encoding="utf-8")
        frontmatter = _extract_frontmatter(content)
        assert re.search(r"^router_bypass:\s*utility\s*$", frontmatter, re.MULTILINE), (
            f"{filename} DEVE declarar 'router_bypass: utility' no frontmatter YAML"
        )
        assert "@agent-router" in content and "run_subagent" in content, (
            f"{filename} DEVE conter diretriz explícita de não invocar @agent-router nem delegar via run_subagent"
        )
        declared_tools = _extract_declared_tools(frontmatter)
        assert declared_tools, f"{filename} DEVE declarar lista explícita de tools no frontmatter"
        forbidden_found = declared_tools.intersection(FORBIDDEN_MUTATION_OR_TERMINAL_TOOLS)
        assert not forbidden_found, (
            f"{filename} com router_bypass: utility possui tools proibidas: {sorted(forbidden_found)}"
        )


def test_slash_workflow_prompts_declare_router_bypass_and_forbid_initial_router_triage():
    """b) Os 13 prompts slash_workflow declaram router_bypass: slash_workflow e proíbem invocar @agent-router na triagem inicial."""
    assert len(ALLOWED_SLASH_WORKFLOW_PROMPTS) == 13
    for filename in sorted(ALLOWED_SLASH_WORKFLOW_PROMPTS):
        prompt_path = PROMPTS_DIR / filename
        assert prompt_path.exists(), f"Prompt slash_workflow ausente: {filename}"
        content = prompt_path.read_text(encoding="utf-8")
        frontmatter = _extract_frontmatter(content)
        assert re.search(r"^router_bypass:\s*slash_workflow\s*$", frontmatter, re.MULTILINE), (
            f"{filename} DEVE declarar 'router_bypass: slash_workflow' no frontmatter YAML"
        )
        assert "@agent-router" in content and "router_bypass: slash_workflow" in content, (
            f"{filename} DEVE conter diretriz explícita proibindo invocar @agent-router na triagem inicial"
        )


def test_agent_router_prompt_is_only_prompt_without_router_bypass():
    """c) agent-router.prompt.md é o único .prompt.md que NÃO declara router_bypass."""
    all_prompts = {p.name for p in PROMPTS_DIR.glob("*.prompt.md")}
    expected_with_bypass = ALLOWED_UTILITY_PROMPTS | ALLOWED_SLASH_WORKFLOW_PROMPTS
    assert all_prompts - expected_with_bypass == {"agent-router.prompt.md"}, (
        f"Apenas agent-router.prompt.md deve ficar sem router_bypass. Diferença: {all_prompts ^ (expected_with_bypass | {'agent-router.prompt.md'})}"
    )

    router_prompt_content = (PROMPTS_DIR / "agent-router.prompt.md").read_text(encoding="utf-8")
    router_frontmatter = _extract_frontmatter(router_prompt_content)
    assert not re.search(r"^router_bypass\s*:", router_frontmatter, re.MULTILINE), (
        "agent-router.prompt.md NÃO deve declarar router_bypass"
    )


def test_canonical_docs_and_router_guard_document_router_bypass():
    """d) CLAUDE.md, .github/copilot-instructions.md, agent-router.agent.md e templates documentam o bypass/guard de Slash Prompts (router_bypass)."""
    claude_content = CLAUDE_PATH.read_text(encoding="utf-8")
    copilot_content = COPILOT_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
    agent_router_content = AGENT_ROUTER_PATH.read_text(encoding="utf-8")
    router_template_content = ROUTER_TEMPLATE_PATH.read_text(encoding="utf-8")
    prompt_template_content = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")

    for doc_name, doc_content in [
        ("CLAUDE.md", claude_content),
        (".github/copilot-instructions.md", copilot_content),
        (".github/prompts/templates/prompt-template.md", prompt_template_content),
    ]:
        assert "router_bypass: utility" in doc_content and "slash_workflow" in doc_content, (
            f"{doc_name} DEVE documentar 'router_bypass: utility | slash_workflow'"
        )

    assert "router_bypass" in agent_router_content and "Guard Defensivo de Slash Prompts" in agent_router_content, (
        ".github/agents/agent-router.agent.md DEVE declarar o Guard Defensivo de Slash Prompts (router_bypass)"
    )
    assert "router_bypass" in router_template_content and "Guard Defensivo de Slash Prompts" in router_template_content, (
        ".github/agents/templates/router-agent.md DEVE declarar o Guard Defensivo de Slash Prompts (router_bypass)"
    )
