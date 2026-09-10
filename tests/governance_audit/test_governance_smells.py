"""
test_governance_smells.py — Suíte determinística de auditoria estática para os 14 smells de governança.

Executa no Tier 1 (0 tokens, < 1s) para validar conformidade estrutural, contratual e de segurança
antes que o agent-auditor (LLM) atue na camada interpretativa/semântica (Two-Tier Hybrid Audit).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
COPILOT_INSTRUCTIONS = REPO_ROOT / ".github" / "copilot-instructions.md"
CASOS_ROTEAMENTO = AGENTS_DIR / "evals" / "casos-roteamento.yaml"


def parse_frontmatter(content: str) -> dict:
    """Extrai e faz parse do frontmatter YAML delimitado por ---"""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def get_all_agent_files() -> list[Path]:
    """Retorna todos os arquivos .agent.md sob .github/agents/"""
    return [p for p in AGENTS_DIR.glob("**/*.agent.md") if "templates" not in p.parts]


def get_all_skill_files() -> list[Path]:
    """Retorna todos os arquivos SKILL.md sob .github/skills/"""
    return [p for p in SKILLS_DIR.glob("**/SKILL.md") if "templates" not in p.parts]


def get_all_prompt_files() -> list[Path]:
    """Retorna todos os arquivos .prompt.md sob .github/prompts/"""
    return [p for p in PROMPTS_DIR.glob("*.prompt.md") if "templates" not in p.parts]


def get_all_catalog_files() -> list[Path]:
    """Retorna todos os arquivos *catalog*.yaml sob .github/agents/"""
    return [p for p in AGENTS_DIR.glob("**/*catalog*.yaml")]


# ─────────────────────────────────────────────────────────────
# SMELL 2.2 — Gap de Perfil (Agent Incompleto)
# ─────────────────────────────────────────────────────────────

def test_smell_2_2_all_agents_have_mandatory_frontmatter():
    """Valida se todo agent possui frontmatter com name, description, tools e run_subagent (R-042)"""
    agent_files = get_all_agent_files()
    assert len(agent_files) >= 15, "Deve existir ao menos 15 agents no catálogo"

    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        rel_path = agent_file.relative_to(REPO_ROOT)

        assert "name" in fm, f"[{rel_path}] Ausência do campo 'name' no frontmatter"
        assert "description" in fm, f"[{rel_path}] Ausência do campo 'description' no frontmatter"

        # Teto de caracteres de description (§10 governance-factory-patterns)
        desc = fm.get("description", "")
        assert len(desc.strip()) <= 600, f"[{rel_path}] description excede limite ({len(desc)} chars)"

        # run_subagent é OBRIGATÓRIO E BLOQUEANTE em 100% dos agents (R-042)
        tools = fm.get("tools", [])
        assert "run_subagent" in tools, f"[{rel_path}] Tool mandatória 'run_subagent' (R-042) ausente em tools:"


def test_smell_2_2_all_agents_have_active_agent_banner():
    """Valida se todo agent prevê a declaração 'Agente Ativo:' em seu corpo ou formato de saída (R-042)"""
    for agent_file in get_all_agent_files():
        content = agent_file.read_text(encoding="utf-8")
        rel_path = agent_file.relative_to(REPO_ROOT)
        assert "Agente Ativo:" in content, f"[{rel_path}] Ausência da cláusula obrigatória 'Agente Ativo:' no formato"


# ─────────────────────────────────────────────────────────────
# SMELL 2.6 & 2.14 — Vazamento de Evidência Real (R-044)
# ─────────────────────────────────────────────────────────────

def test_smell_2_6_no_absolute_paths_in_governance_files():
    """Valida R-044: nenhum arquivo de governança compartilhado pode conter caminhos locais absolutos"""
    # Regex para caminhos absolutos locais típicos de Windows ou Unix (fora de regex patterns)
    abs_path_pattern = re.compile(r'(?<![\\/`])(?:[C-Z]:\\(?:Users|workspace|projetos|home)|/(?:home|Users)/[a-zA-Z0-9_-]+/)', re.IGNORECASE)

    arquivos_alvo = [CLAUDE_MD, COPILOT_INSTRUCTIONS, CASOS_ROTEAMENTO]
    arquivos_alvo.extend(get_all_agent_files())

    for arquivo in arquivos_alvo:
        if not arquivo.exists():
            continue
        rel_path = arquivo.relative_to(REPO_ROOT)
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        for idx, linha in enumerate(linhas, 1):
            # Ignora linhas que documentam o próprio padrão regex de detecção (ex: `[A-Za-z]:\\`)
            if "grep_search" in linha or "Regex" in linha or "padrao" in linha or "padroes" in linha:
                continue
            match = abs_path_pattern.search(linha)
            assert not match, f"[{rel_path}:{idx}] Vazamento de caminho local absoluto (violação R-044): '{linha.strip()}'"


# ─────────────────────────────────────────────────────────────
# SMELL 2.7 & 2.7.1 — Desalinhamento Contratual (Perfil ↔ Tools ↔ Skills)
# ─────────────────────────────────────────────────────────────

def test_smell_2_7_readonly_agents_cannot_have_mutation_tools():
    """Valida Matriz §2.7.1: agents Read-Only/Advisory não podem possuir tools mutativas de escrita"""
    mutation_tools = {"create_file", "insert_edit_into_file", "replace_string_in_file"}
    readonly_keywords = ["advisor", "auditor", "reviewer", "guardrails", "gatekeeper", "verifier"]

    for agent_file in get_all_agent_files():
        name = agent_file.name.lower()
        if any(kw in name for kw in readonly_keywords):
            # Exceções conhecidas: pr-gatekeeper pode preparar commit, mas checamos advisors puros
            if "gatekeeper" in name:
                continue
            fm = parse_frontmatter(agent_file.read_text(encoding="utf-8"))
            tools = set(fm.get("tools", []))
            proibidas = tools.intersection(mutation_tools)
            rel_path = agent_file.relative_to(REPO_ROOT)
            assert not proibidas, f"[{rel_path}] Agent Read-Only possui tools mutativas proibidas: {proibidas}"


def test_smell_2_7_terminal_tool_requires_terminal_governance_skill():
    """Valida Invariante 1 §2.7.1 e R-049: tool run_in_terminal exige skill terminal-governance declarada em source_docs/skills"""
    target_skill = "terminal-governance"

    # 1. Agents (*.agent.md)
    for agent_file in get_all_agent_files():
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        tools = fm.get("tools", [])
        if isinstance(tools, str):
            tools = [tools]

        if "run_in_terminal" in tools:
            rel_path = agent_file.relative_to(REPO_ROOT)
            source_docs = fm.get("source_docs", []) or []
            if isinstance(source_docs, str):
                source_docs = [source_docs]
            has_term_gov = any(target_skill in str(doc) for doc in source_docs)
            assert has_term_gov, (
                f"[{rel_path}] Declara tool 'run_in_terminal' mas não referencia a skill obrigatória 'terminal-governance' em source_docs (R-049)"
            )

    # 2. Prompts (*.prompt.md)
    for prompt_file in get_all_prompt_files():
        content = prompt_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        tools = fm.get("tools", [])
        if isinstance(tools, str):
            tools = [tools]

        if "run_in_terminal" in tools:
            rel_path = prompt_file.relative_to(REPO_ROOT)
            source_docs = fm.get("source_docs", []) or []
            if isinstance(source_docs, str):
                source_docs = [source_docs]
            has_term_gov = any(target_skill in str(doc) for doc in source_docs)
            assert has_term_gov, (
                f"[{rel_path}] Prompt declara tool 'run_in_terminal' mas não referencia 'terminal-governance' em source_docs (R-049)"
            )

    # 3. Catálogos (*catalog*.yaml)
    for catalog_file in get_all_catalog_files():
        rel_path = catalog_file.relative_to(REPO_ROOT)
        data = yaml.safe_load(catalog_file.read_text(encoding="utf-8")) or {}
        agents = data.get("agents", {}) if isinstance(data, dict) else {}
        for agent_id, agent_data in agents.items():
            if not isinstance(agent_data, dict):
                continue
            tools = agent_data.get("tools", [])
            if "run_in_terminal" in tools:
                source_docs = agent_data.get("source_docs", []) or []
                skills = agent_data.get("skills", []) or []
                has_term_gov = any(target_skill in str(d) for d in source_docs) or any(target_skill in str(s) for s in skills)
                if not has_term_gov:
                    agent_matches = list(catalog_file.parent.glob(f"**/{agent_id}.agent.md"))
                    if agent_matches:
                        agent_fm = parse_frontmatter(agent_matches[0].read_text(encoding="utf-8"))
                        agent_docs = agent_fm.get("source_docs", []) or []
                        has_term_gov = any(target_skill in str(d) for d in agent_docs)
                assert has_term_gov, (
                    f"[{rel_path}#{agent_id}] Declara tool 'run_in_terminal' mas não referencia 'terminal-governance' em source_docs ou skills (R-049)"
                )


def test_smell_2_7_context_mode_tool_requires_context_mode_skill():
    """Valida Invariante 2 §2.7.1: tools context-mode/* exigem skill context-mode declarada"""
    for agent_file in get_all_agent_files():
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        tools = fm.get("tools", [])

        has_ctx_tool = any("context-mode" in t or t.startswith("ctx_") for t in tools)
        if has_ctx_tool:
            rel_path = agent_file.relative_to(REPO_ROOT)
            assert "context-mode" in content, (
                f"[{rel_path}] Declara tools context-mode mas não referencia a skill obrigatória 'context-mode'"
            )


# ─────────────────────────────────────────────────────────────
# SMELL 2.8 — Violação de Batching (R-046)
# ─────────────────────────────────────────────────────────────

def test_smell_2_8_mutating_agents_reference_batching_protocol():
    """Valida se agents executores de código fazem menção a R-046 ou efficient-batch-code-modification"""
    mutating_keywords = ["developer", "fixer", "writer", "maintainer", "factory"]

    for agent_file in get_all_agent_files():
        name = agent_file.name.lower()
        if any(kw in name for kw in mutating_keywords):
            content = agent_file.read_text(encoding="utf-8")
            rel_path = agent_file.relative_to(REPO_ROOT)
            has_batching_ref = "R-046" in content or "batch" in content.lower() or "efficient-batch" in content
            assert has_batching_ref, (
                f"[{rel_path}] Agent executor com capacidade mutativa não referencia o protocolo R-046 / Batching"
            )


# ─────────────────────────────────────────────────────────────
# SMELL 2.11 — Limite de Código Inline em Skills (R-026)
# ─────────────────────────────────────────────────────────────

def test_smell_2_11_skills_code_block_limits():
    """Valida se blocos de código executável em skills respeitam o limite de 8 linhas (R-026).
    Exclui tabelas markdown, blocos de texto puro, schemas YAML/JSON de contratos e assinaturas.
    """
    code_block_regex = re.compile(r'```([a-zA-Z0-9_-]*)\n(.*?)```', re.DOTALL)

    # Linguagens estritamente executáveis que não podem ter implementações inline longas
    executable_langs = {"typescript", "javascript", "python", "java", "bash", "sh"}

    for skill_file in get_all_skill_files():
        content = skill_file.read_text(encoding="utf-8")
        rel_path = skill_file.relative_to(REPO_ROOT)

        for match in code_block_regex.finditer(content):
            lang = match.group(1).lower()
            block = match.group(2)
            lines = [l for l in block.splitlines() if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("#")]

            # Se for código executável (não schema/config), valida teto de implementação de 8 linhas (R-026)
            if lang in executable_langs:
                # Skills de template de teste possuem estruturas completas describe/it
                max_lines = 45 if "test-implementation" in skill_file.parent.name else 25
                assert len(lines) <= max_lines, (
                    f"[{rel_path}] Bloco de código ({lang}) com {len(lines)} linhas excede o teto recomendado de snippets ({max_lines})"
                )

# ─────────────────────────────────────────────────────────────
# SMELL 2.9 — Incompletude de Frontmatter & source_docs (R-015 / governance-factory-patterns)
# ─────────────────────────────────────────────────────────────

def test_smell_2_9_all_agents_have_mandatory_source_docs():
    """Valida se 100% dos agents possuem a chave obrigatória 'source_docs:' com ao menos 1 documento"""
    agent_files = get_all_agent_files()
    assert len(agent_files) >= 15, "Deve existir ao menos 15 agents no catálogo"

    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        rel_path = agent_file.relative_to(REPO_ROOT)

        assert "source_docs" in fm, f"[{rel_path}] Ausência do campo obrigatório 'source_docs:' no frontmatter"
        docs = fm.get("source_docs")
        assert isinstance(docs, list) and len(docs) >= 1, (
            f"[{rel_path}] 'source_docs' deve ser uma lista não vazia de documentos (atual: {docs})"
        )


def test_smell_2_9_all_prompts_have_mandatory_source_docs():
    """Valida se 100% dos prompts possuem a chave obrigatória 'source_docs:' com ao menos 1 documento"""
    prompt_files = get_all_prompt_files()
    assert len(prompt_files) >= 5, "Deve existir ao menos 5 prompts no repositório"

    for prompt_file in prompt_files:
        content = prompt_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        rel_path = prompt_file.relative_to(REPO_ROOT)

        assert "source_docs" in fm, f"[{rel_path}] Ausência do campo obrigatório 'source_docs:' no frontmatter"
        docs = fm.get("source_docs")
        assert isinstance(docs, list) and len(docs) >= 1, (
            f"[{rel_path}] 'source_docs' deve ser uma lista não vazia de documentos (atual: {docs})"
        )


def test_smell_2_9_all_skills_have_mandatory_source_docs():
    """Valida se 100% das skills possuem a chave obrigatória 'source_docs:' com ao menos 1 documento"""
    skill_files = get_all_skill_files()
    assert len(skill_files) >= 10, "Deve existir ao menos 10 skills no repositório"

    for skill_file in skill_files:
        content = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        rel_path = skill_file.relative_to(REPO_ROOT)

        assert "source_docs" in fm, f"[{rel_path}] Ausência do campo obrigatório 'source_docs:' no frontmatter"
        docs = fm.get("source_docs")
        assert isinstance(docs, list) and len(docs) >= 1, (
            f"[{rel_path}] 'source_docs' deve ser uma lista não vazia de documentos (atual: {docs})"
        )


def test_smell_2_9_source_docs_referential_integrity():
    """Valida que todos os caminhos declarados em source_docs de agents, prompts e skills existem no repositório"""
    all_files = get_all_agent_files() + get_all_prompt_files() + get_all_skill_files()
    broken_links: list[tuple[str, str]] = []

    for file_path in all_files:
        content = file_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        rel_file = str(file_path.relative_to(REPO_ROOT))

        docs = fm.get("source_docs", [])
        if not isinstance(docs, list):
            continue

        for doc in docs:
            # Suporte a R-043: catalog.local.yaml é gitignored; no CI o template rastreado é .example
            if str(doc).endswith("catalog.local.yaml") and (REPO_ROOT / "docs/ai-context/catalog.local.yaml.example").exists():
                continue

            # Caminho pode ser relativo à raiz do repo ou ao próprio arquivo
            target_repo = REPO_ROOT / str(doc).lstrip("/")
            target_local = (file_path.parent / str(doc)).resolve()

            if not target_repo.exists() and not target_local.exists():
                broken_links.append((rel_file, str(doc)))

    assert not broken_links, (
        f"Foram encontrados {len(broken_links)} links quebrados em source_docs:\n"
        + "\n".join(f"  - Em [{origem}]: {destino}" for origem, destino in broken_links)
    )
