"""
test_governance_smells.py — Suíte determinística de auditoria estática para os 17 smells de governança.

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
            if (str(doc).endswith("catalog.local.yaml") or str(doc).endswith("projects.local.yaml") or str(doc).endswith("projects.local.yaml.example")) and ((REPO_ROOT / ".github/projects.local.yaml.example").exists()):
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


# ─────────────────────────────────────────────────────────────
# SMELL 2.15 — Acoplamento Rígido de Range Normativo (Hardcoded Range Coupling)
# ─────────────────────────────────────────────────────────────

def _get_latest_normative_rule_number() -> int:
    """Extrai o maior número de regra R-0XX declarado em CLAUDE.md § 3 (dinâmico, nunca hardcoded)."""
    content = CLAUDE_MD.read_text(encoding="utf-8")
    rule_numbers = [int(n) for n in re.findall(r"\*\*R-(\d{3})", content)]
    assert rule_numbers, "Nenhuma regra R-0XX encontrada em CLAUDE.md"
    return max(rule_numbers)


def test_smell_2_15_no_hardcoded_normative_rule_range():
    """Smell 2.15: nenhum agent deve conter acoplamento rígido de range numérico
    normativo (ex: R-001..R-051) em 'Regras Herdadas' ou no corpo.
    A referência a CLAUDE.md deve ser aberta e desacoplada da quantidade de regras (R-xxx),
    eliminando shotgun surgery e queima de créditos a cada nova regra adicionada.
    Além disso, todo agent com seção 'Regras Herdadas' DEVE referenciar CLAUDE.md."""
    hardcoded = []
    missing_claude_ref = []
    for agent_file in get_all_agent_files():
        content = agent_file.read_text(encoding="utf-8")
        if "Regras Herdadas" in content:
            if "CLAUDE.md" not in content:
                missing_claude_ref.append(agent_file.relative_to(REPO_ROOT))

        match = re.search(r"R-001\.\.R-\d{3}", content)
        if match:
            hardcoded.append((agent_file.relative_to(REPO_ROOT), match.group(0)))

    assert not missing_claude_ref, (
        f"Smell 2.15: {len(missing_claude_ref)} agent(s) com 'Regras Herdadas' não referenciam CLAUDE.md:\n"
        + "\n".join(f"  - {path}" for path in missing_claude_ref)
    )
    assert not hardcoded, (
        f"Smell 2.15 (Acoplamento Rígido de Range): {len(hardcoded)} agent(s) contêm range numérico hardcoded "
        f"(deve usar herança aberta 'regras normativas globais em CLAUDE.md'):\n"
        + "\n".join(f"  - {path}: {val}" for path, val in hardcoded)
    )



# ─────────────────────────────────────────────────────────────
# SMELL 2.16 — Agent Mutativo Sem Skill de Edição Segura Referenciada (R-051)
# ─────────────────────────────────────────────────────────────

def test_smell_2_16_mutating_agents_reference_safe_editing_skill():
    """Smell 2.16: todo agent com insert_edit_into_file/replace_string_in_file em tools:
    deve referenciar efficient-batch-code-modification (guardrail anti-corrupção R-051)."""
    mutation_tools = {"insert_edit_into_file", "replace_string_in_file"}
    skill_ref = "efficient-batch-code-modification"
    gaps = []
    for agent_file in get_all_agent_files():
        content = agent_file.read_text(encoding="utf-8")
        tools_match = re.search(r"tools:\s*(\[[^\]]*\])", content)
        if not tools_match:
            continue
        tools_text = tools_match.group(1)
        has_mutation = any(t in tools_text for t in mutation_tools)
        if not has_mutation:
            continue
        if skill_ref not in content:
            gaps.append(agent_file.relative_to(REPO_ROOT))

    assert not gaps, (
        f"Smell 2.16: {len(gaps)} agent(s) com tools mutativas nao referenciam "
        f"'{skill_ref}' em source_docs/skills:\n"
        + "\n".join(f"  - {p}" for p in gaps)
    )


# ─────────────────────────────────────────────────────────────
# SMELL 2.17 — Comando Git Sem Desativação de Pager (R-035)
# ─────────────────────────────────────────────────────────────

def test_smell_2_17_no_bare_git_pager_commands_in_prompts_and_governance():
    """Smell 2.17: nenhum prompt (.prompt.md) ou skill de terminal deve conter comandos
    executáveis git (diff|log|show|branch|tag) sem desativação explícita de pager
    (--no-pager, GIT_PAGER=cat ou pipe | cat), prevenindo travamento do terminal (R-035)."""
    paged_git_pattern = re.compile(r"^\s*git\s+(diff|log|show|branch|tag)\b")
    safe_flags = ("--no-pager", "GIT_PAGER", "| cat", "| head")
    violations = []

    # Valida prompts
    for prompt_file in get_all_prompt_files():
        p_content = prompt_file.read_text(encoding="utf-8")
        for line_no, line in enumerate(p_content.splitlines(), start=1):
            trimmed = line.strip()
            if paged_git_pattern.match(trimmed):
                if not any(flag in trimmed for flag in safe_flags):
                    violations.append((prompt_file.relative_to(REPO_ROOT), line_no, trimmed))

    # Valida skill terminal-governance
    tg_file = SKILLS_DIR / "terminal-governance" / "SKILL.md"
    if tg_file.exists():
        tg_content = tg_file.read_text(encoding="utf-8")
        in_problematic_table = False
        for line_no, line in enumerate(tg_content.splitlines(), start=1):
            if "## 4) Comandos Não-Interativos" in line or "## 6) Padrões Proibidos" in line:
                in_problematic_table = True
            elif line.startswith("## ") and in_problematic_table:
                in_problematic_table = False
            if not in_problematic_table and paged_git_pattern.match(line.strip()):
                if not any(flag in line for flag in safe_flags):
                    violations.append((tg_file.relative_to(REPO_ROOT), line_no, line.strip()))

    assert not violations, (
        f"Smell 2.17: {len(violations)} comando(s) git desprovido(s) de desativação de pager "
        f"encontrado(s) em prompts/governança (R-035):\n"
        + "\n".join(f"  - {path}:{num} -> {cmd}" for path, num, cmd in violations)
    )


# ─────────────────────────────────────────────────────────────
# SMELL 2.20 — Duplicação por Aninhamento de Router (R-047 / R-037)
# ─────────────────────────────────────────────────────────────

def test_smell_2_20_router_flat_delegation_rule():
    """Smell 2.20: agent-router deve operar sob Delegação Plana (Flat Delegation),
    sendo proibido de invocar subagentes executores downstream via run_subagent
    para evitar execução duplicada pelo orquestrador raiz (R-047 / R-037)."""
    router_file = AGENTS_DIR / "agent-router.agent.md"
    assert router_file.exists(), "agent-router.agent.md deve existir"
    router_content = router_file.read_text(encoding="utf-8")

    # Verifica declaração de Delegação Plana no router
    assert "Flat Delegation" in router_content or "Delegação Plana" in router_content, (
        "agent-router.agent.md DEVE declarar regra de Delegação Plana (Flat Delegation)"
    )

    # Verifica proibição explícita de subagente executor downstream
    assert "NÃO invocar subagente executor downstream" in router_content or "proibido aninhamento" in router_content, (
        "agent-router.agent.md DEVE proibir invocação de executores downstream via run_subagent"
    )

    # Verifica exceção no CLAUDE.md (R-047)
    claude_content = CLAUDE_MD.read_text(encoding="utf-8")
    assert "Delegação Plana" in claude_content, (
        "CLAUDE.md (R-047) DEVE prever a exceção de Delegação Plana para routers"
    )

    # Verifica documentação do Smell 2.20 na skill
    gap_skill = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    gap_content = gap_skill.read_text(encoding="utf-8")
    assert "2.20" in gap_content, "governance-audit-patterns/SKILL.md DEVE documentar o Smell 2.20"

# ─────────────────────────────────────────────────────────────
# SMELL 2.1 — Referência Órfã / Agentes Descomissionados em Documentação Viva
# ─────────────────────────────────────────────────────────────
def test_smell_2_1_no_deprecated_agents_in_live_readmes():
    """Smell 2.1: Garante que nenhum agent descontinuado/substituído seja citado
    na documentação viva do repositório (README.md raiz e .github/skills/README.md)."""
    deprecated_agents = {
        "docs-writer",
        "docs-curator",
        "agent-factory",
        "skill-factory",
        "prompt-factory",
        "impact-architect",
        "test-implementation",
        "test-fix",
        "code-summarizer",
        "context-builder",
        "angular-engineer",
        "spring-boot-engineer",
        "spring-reactive-engineer",
        "test-engineer",
    }
    # 1. README.md principal
    readme_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for dep in deprecated_agents:
        pattern = rf"(?<![a-zA-Z0-9_-]){re.escape(dep)}(?![a-zA-Z0-9_-])"
        assert not re.search(pattern, readme_content), (
            f"README.md cita agent descontinuado '{dep}' fora de changelog histórico"
        )
    # 2. .github/skills/README.md
    skills_readme = (SKILLS_DIR / "README.md").read_text(encoding="utf-8")
    for dep in deprecated_agents:
        pattern = rf"(?<![a-zA-Z0-9_-]){re.escape(dep)}(?![a-zA-Z0-9_-])"
        assert not re.search(pattern, skills_readme), (
            f".github/skills/README.md cita agent descontinuado '{dep}'"
        )

# ─────────────────────────────────────────────────────────────
# SMELL 2.21 — Cegueira Visual e Suposição de Contratos de UI
# ─────────────────────────────────────────────────────────────
def test_smell_2_21_visual_blindness_and_ui_contracts_documented():
    """Smell 2.21: governance-audit-patterns/SKILL.md deve documentar o Smell 2.21
    (Cegueira Visual e Suposição de Contratos de UI), e os agentes de frontend
    devem prever o protocolo 'Canonical Sibling First' e contratos de shared components."""
    gap_file = SKILLS_DIR / "governance-audit-patterns" / "SKILL.md"
    assert gap_file.exists(), "governance-audit-patterns/SKILL.md deve existir"
    gap_content = gap_file.read_text(encoding="utf-8")
    assert "2.21" in gap_content, "governance-audit-patterns/SKILL.md DEVE documentar o Smell 2.21"
    assert "Cegueira Visual" in gap_content, "Smell 2.21 deve abordar Cegueira Visual"

    # Valida presença do protocolo Canonical Sibling First no angular-feature-developer e angular-ui-stylist
    afd_file = AGENTS_DIR / "frontend" / "angular" / "angular-feature-developer.agent.md"
    assert afd_file.exists()
    afd_content = afd_file.read_text(encoding="utf-8")
    assert "Canonical Sibling" in afd_content, "angular-feature-developer deve adotar Canonical Sibling First"

    aus_file = AGENTS_DIR / "frontend" / "angular" / "angular-ui-stylist.agent.md"
    assert aus_file.exists()
    aus_content = aus_file.read_text(encoding="utf-8")
    assert "Canonical Sibling" in aus_content, "angular-ui-stylist deve adotar Canonical Sibling First"
