"""
test_template_sections.py — Validação determinística de seções contra templates canônicos (Smell 2.9, 2.10, 2.11).

Implementa a regra de conformidade polimórfica (Disjunção 1-de-N):
Para contextos com mais de um template canônico (ex.: .github/agents/templates/ com
agent-template.md, operational-agent.md e research-agent.md), o artefato é considerado
conforme se possuir as seções requeridas por AO MENOS UM dos templates canônicos do contexto.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"


def extract_headings(file_path: Path) -> list[tuple[int, str]]:
    """Extrai cabeçalhos Markdown (# .. ######) ignorando frontmatter YAML e blocos de código."""
    text = file_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if text.startswith("---"):
        idx = text.find("\n---", 3)
        if idx != -1:
            text = text[idx + 4:]
    
    headings = []
    in_code = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
    return headings


def extract_h2_sections(file_path: Path) -> list[str]:
    """Retorna os títulos de nível 2 (##) do documento."""
    return [title for level, title in extract_headings(file_path) if level == 2]


def normalize_title(title: str) -> str:
    """Normaliza título removendo emojis, texto entre parênteses e caracteres não-alfanuméricos."""
    t = re.sub(r'\([^)]*\)', '', title)
    t = re.sub(r'[^\w\s]', '', t, flags=re.UNICODE).lower()
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def extract_canonical_concept(title: str) -> str:
    """
    Mapeia variações de redação de títulos para o conceito canônico estrutural correspondente.
    Exemplos:
      - 'CRÍTICO: ESCOPO CIRÚRGICO' -> 'escopo'
      - 'Processo Passo a Passo' ou 'Decision Tree' -> 'workflow'
      - 'Contrato Operacional' ou 'Formato de Saída' -> 'contrato_saida'
      - 'Retorno ao Router' -> 'retorno_router'
    """
    clean = normalize_title(title)
    if "escopo" in clean or "único trabalho" in clean or "unico trabalho" in clean:
        return "escopo"
    if any(k in clean for k in ["processo", "workflow", "decision tree", "fluxo", "padrões obrigatórios", "modos de operação", "protocolo"]):
        return "workflow"
    if any(k in clean for k in ["contrato", "formato de saída", "formato de saida", "saída", "saida", "resposta esperada"]):
        return "contrato_saida"
    if "retorno ao router" in clean:
        return "retorno_router"
    if any(k in clean for k in ["segurança", "seguranca", "guardrail", "antipadrões", "antipadroes", "diretrizes", "regras de autonomia", "regras"]):
        return "seguranca"
    if "checklist" in clean:
        return "checklist"
    if "combina com" in clean:
        return "combina_com"
    if any(k in clean for k in ["invocação", "invocacao", "uso", "sintaxe"]):
        return "invocacao_uso"
    if any(k in clean for k in ["problema resolvido", "objetivo", "filosofia", "contexto", "propósito"]):
        return "problema_resolvido"
    if any(k in clean for k in ["quando usar", "casos de uso", "cenários"]):
        return "quando_usar"
    if any(k in clean for k in ["padrões canônicos", "exemplos contrastantes", "boas práticas"]):
        return "padroes_exemplos"
    if any(k in clean for k in ["referências", "referencias", "documentação conexa"]):
        return "referencias"
    return clean


def get_template_concepts(template_path: Path) -> set[str]:
    """Extrai o conjunto de conceitos canônicos representados nas seções H2 do template."""
    h2s = extract_h2_sections(template_path)
    return set(extract_canonical_concept(h) for h in h2s)


def validate_artifact_sections_against_templates(
    artifact_path: Path,
    templates_dir: Path
) -> tuple[bool, str, dict[str, list[str]]]:
    """
    Regra Canônica de Disjunção 1-de-N:
    O artefato é válido se suas seções satisfizerem as seções de AO MENOS UM template canônico.

    Retorna:
      - is_valid (bool): True se atendeu a pelo menos um template.
      - matched_template (str): Nome do template correspondido (ou vazio se nenhum).
      - failures_by_template (dict): Mapa com seções faltantes para cada template avaliado.
    """
    tpl_files = sorted(templates_dir.glob("*.md"))
    assert len(tpl_files) >= 1, f"Diretório de templates vazio: {templates_dir}"

    artifact_h2s = extract_h2_sections(artifact_path)
    artifact_concepts = set(extract_canonical_concept(h) for h in artifact_h2s)

    failures = {}
    for tpl in tpl_files:
        required_concepts = get_template_concepts(tpl)
        missing = [c for c in sorted(required_concepts) if c not in artifact_concepts]
        if not missing:
            return True, tpl.name, {}
        failures[tpl.name] = missing

    return False, "", failures


# ─────────────────────────────────────────────────────────────
# 1. Testes Unitários do Motor de Validação Polimórfica (1-de-N)
# ─────────────────────────────────────────────────────────────

def test_polymorphic_disjunction_rule_logic(tmp_path: Path):
    """
    Valida se a regra 'ao menos um template' (1-de-N) funciona corretamente:
    - Artefato que atende ao Template A mas não ao Template B -> APROVADO
    - Artefato que atende ao Template B mas não ao Template A -> APROVADO
    - Artefato que não atende a nenhum -> REPROVADO com diagnóstico
    """
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()

    # Template A: Perfil Operacional (Escopo, Workflow, Contrato)
    (tpl_dir / "operational-tpl.md").write_text(
        "---\nname: op-tpl\n---\n# Template Op\n## 🛑 CRÍTICO: ESCOPO\n## 📋 Processo Passo a Passo\n## 🤝 Contrato Operacional\n",
        encoding="utf-8"
    )

    # Template B: Perfil Analítico (Escopo, Checklist, Retorno ao Router)
    (tpl_dir / "research-tpl.md").write_text(
        "---\nname: res-tpl\n---\n# Template Res\n## 🛑 CRÍTICO: ESCOPO\n## ✅ Checklist de Análise\n## 🔄 Retorno ao Router\n",
        encoding="utf-8"
    )

    # Caso 1: Artefato operacional (tem Escopo, Workflow, Contrato)
    art_op = tmp_path / "my-operational.md"
    art_op.write_text("# Agente Op\n## 🛑 CRÍTICO: ESCOPO CIRÚRGICO\n## 📋 Workflow Numerado\n## 🤝 Contrato Operacional\n", encoding="utf-8")
    valid_op, matched_tpl, _ = validate_artifact_sections_against_templates(art_op, tpl_dir)
    assert valid_op is True
    assert matched_tpl == "operational-tpl.md"

    # Caso 2: Artefato analítico (tem Escopo, Checklist, Retorno ao Router)
    art_res = tmp_path / "my-research.md"
    art_res.write_text("# Agente Res\n## 🛑 CRÍTICO: ESCOPO READ-ONLY\n## ✅ Checklist Antes de Concluir\n## 🔄 Retorno ao Router\n", encoding="utf-8")
    valid_res, matched_tpl, _ = validate_artifact_sections_against_templates(art_res, tpl_dir)
    assert valid_res is True
    assert matched_tpl == "research-tpl.md"

    # Caso 3: Artefato incompleto (tem apenas Escopo)
    art_bad = tmp_path / "my-incomplete.md"
    art_bad.write_text("# Agente Incompleto\n## 🛑 CRÍTICO: ESCOPO\n", encoding="utf-8")
    valid_bad, matched_tpl, failures = validate_artifact_sections_against_templates(art_bad, tpl_dir)
    assert valid_bad is False
    assert matched_tpl == ""
    assert "operational-tpl.md" in failures
    assert "research-tpl.md" in failures


# ─────────────────────────────────────────────────────────────
# 2. Integridade Estrutural dos Templates Canônicos do Repositório
# ─────────────────────────────────────────────────────────────

def test_all_contexts_have_non_empty_templates():
    """Valida se as pastas de templates existem e contêm templates válidos."""
    for context_name, tpl_dir in [("agents", AGENTS_DIR / "templates"), ("skills", SKILLS_DIR / "templates"), ("prompts", PROMPTS_DIR / "templates")]:
        assert tpl_dir.exists(), f"Diretório de templates não existe: {tpl_dir}"
        templates = list(tpl_dir.glob("*.md"))
        assert len(templates) >= 1, f"Nenhum template encontrado em {tpl_dir}"
        for tpl in templates:
            h2s = extract_h2_sections(tpl)
            assert len(h2s) >= 4, f"Template {tpl.name} em {context_name} deve ter ao menos 4 seções H2 (encontradas {len(h2s)})"


def test_agent_templates_multiplicity():
    """Valida se o contexto de agents possui os 3 arquétipos previstos (§10 governance-factory-patterns)."""
    agent_tpl_dir = AGENTS_DIR / "templates"
    expected_templates = {"agent-template.md", "operational-agent.md", "research-agent.md"}
    actual_templates = {p.name for p in agent_tpl_dir.glob("*.md")}
    assert expected_templates.issubset(actual_templates), (
        f"Contexto de agents deve conter ao menos os templates {expected_templates}; encontrados: {actual_templates}"
    )


# ─────────────────────────────────────────────────────────────
# 3. SMELL 2.9 — Conformidade Canônica de Seções para Agents
# ─────────────────────────────────────────────────────────────

def test_smell_2_9_all_agents_have_mandatory_scope_and_contract_sections():
    """
    Smell 2.9 (Tier 1): Todo agent em .github/agents/ deve possuir as seções invariantes de
    Escopo (CRÍTICO: ESCOPO) e Formato de Saída / Contrato Operacional.
    """
    agent_files = [p for p in AGENTS_DIR.glob("**/*.agent.md") if "templates" not in p.parts]
    assert len(agent_files) >= 30

    gaps = []
    for af in agent_files:
        concepts = set(extract_canonical_concept(h) for h in extract_h2_sections(af))
        rel_path = af.relative_to(REPO_ROOT)
        if "escopo" not in concepts:
            gaps.append(f"[{rel_path}] ausência da seção canônica de Escopo ('CRÍTICO: ESCOPO')")
        if "contrato_saida" not in concepts:
            gaps.append(f"[{rel_path}] ausência da seção de Contrato / Formato de Saída")

    assert not gaps, f"Smell 2.9: {len(gaps)} violações de seções invariantes em agents:\n" + "\n".join(gaps[:10])


def test_smell_2_9_root_agents_conform_to_canonical_agent_templates():
    """
    Smell 2.9 (Tier 1): Agents raiz (.github/agents/*.agent.md) devem possuir estrutura completa
    aderente a ao menos um dos 3 templates canônicos (Escopo, Workflow, Contrato/Saída, Retorno Router, Checklist).
    """
    agent_tpl_dir = AGENTS_DIR / "templates"
    root_agents = [p for p in AGENTS_DIR.glob("*.agent.md") if "templates" not in p.parts]
    assert len(root_agents) >= 20

    core_required = {"escopo", "workflow", "contrato_saida", "retorno_router", "checklist"}

    gaps = []
    for ra in root_agents:
        concepts = set(extract_canonical_concept(h) for h in extract_h2_sections(ra))
        # O agent-router central é o ponto de entrada, portanto despacha e não retorna a si mesmo
        if ra.name == "agent-router.agent.md":
            concepts.add("retorno_router")
        missing = core_required - concepts
        if missing:
            rel_path = ra.relative_to(REPO_ROOT)
            gaps.append(f"[{rel_path}] faltam seções canônicas de template: {missing}")

    assert not gaps, f"Smell 2.9: {len(gaps)} root agents divergem da estrutura canônica:\n" + "\n".join(gaps)


# ─────────────────────────────────────────────────────────────
# 4. SMELL 2.10 — Conformidade Canônica de Seções para Prompts
# ─────────────────────────────────────────────────────────────

def test_smell_2_10_all_prompts_have_mandatory_scope_section():
    """
    Smell 2.10 (Tier 1): Todo prompt (.prompt.md) deve possuir o bloco delimitador
    '## 🛑 CRÍTICO: ESCOPO E NÃO-ESCOPO' em conformidade com prompt-template.md.
    """
    prompt_files = [p for p in PROMPTS_DIR.glob("*.prompt.md") if "templates" not in p.parts]
    assert len(prompt_files) >= 15

    gaps = []
    for pf in prompt_files:
        concepts = set(extract_canonical_concept(h) for h in extract_h2_sections(pf))
        if "escopo" not in concepts:
            rel_path = pf.relative_to(REPO_ROOT)
            gaps.append(f"[{rel_path}] ausência da seção obrigatória 'CRÍTICO: ESCOPO E NÃO-ESCOPO'")

    assert not gaps, f"Smell 2.10: {len(gaps)} prompts sem seção de escopo:\n" + "\n".join(gaps)


# ─────────────────────────────────────────────────────────────
# 5. SMELL 2.11 — Conformidade Canônica de Seções para Skills
# ─────────────────────────────────────────────────────────────

def test_smell_2_11_all_skills_have_mandatory_operational_sections():
    """
    Smell 2.11 (Tier 1): Toda skill (SKILL.md) deve possuir ao menos as seções de orientação de uso
    ('Quando Usar') ou de validação/checklist em conformidade com skill-template.md.
    """
    skill_files = [p for p in SKILLS_DIR.glob("**/SKILL.md") if "templates" not in p.parts]
    assert len(skill_files) >= 30

    gaps = []
    for sf in skill_files:
        h2s = extract_h2_sections(sf)
        concepts = set(extract_canonical_concept(h) for h in h2s)
        rel_path = sf.relative_to(REPO_ROOT)

        # Toda skill deve ter orientação de uso/escopo ou diretrizes
        has_usage_or_rules = any(c in concepts for c in ["quando_usar", "problema_resolvido", "workflow", "seguranca", "escopo"])
        if not has_usage_or_rules:
            gaps.append(f"[{rel_path}] ausência de seções de orientação ('Quando Usar' / 'Diretrizes')")

    assert not gaps, f"Smell 2.11: {len(gaps)} skills sem seções operacionais mínimas:\n" + "\n".join(gaps)


# ─────────────────────────────────────────────────────────────
# 6. GATE DE HOMOLOGAÇÃO DE SEÇÕES (ANTI-AD-HOC SECTIONS / TEMPLATE WHITELIST)
# ─────────────────────────────────────────────────────────────

PROHIBITED_DOC_SECTIONS_NON_ROUTERS = {
    "docs sempre anexadas",
    "regras herdadas",
    "catálogo / conhecimento base",
    "catalogo / conhecimento base",
    "skills associadas",
    "source docs",
}


def test_homologation_gate_no_unhomologated_sections_in_agents():
    """
    Gate de Homologação: Garante que nenhum agent não-router possua seções redundantes
    ou não homologadas em templates canônicos (ex.: Docs Sempre Anexadas, Regras Herdadas,
    Catálogo / Conhecimento Base, Skills Associadas).
    Toda dependência documental DEVE residir no frontmatter 'source_docs:' (SSOT).
    Inclusões de novas seções exigem homologação prévia em agent-template.md/operational/research.
    """
    non_router_agents = [
        p for p in AGENTS_DIR.glob("**/*.agent.md")
        if "router" not in p.name and "templates" not in p.parts
    ]
    assert len(non_router_agents) >= 70

    violations = []
    for agent_file in non_router_agents:
        rel_path = agent_file.relative_to(REPO_ROOT)
        h2s = extract_h2_sections(agent_file)
        for h in h2s:
            clean_h = h.lower()
            for prohibited in PROHIBITED_DOC_SECTIONS_NON_ROUTERS:
                if prohibited in clean_h:
                    violations.append(f"[{rel_path}] Seção não homologada/proibida: '## {h}'")

    assert not violations, (
        f"Gate de Homologação falhou: {len(violations)} seções não homologadas em agents:\n"
        + "\n".join(violations)
        + "\n-> Toda dependência documental deve residir no frontmatter 'source_docs:'. "
        "Novas seções exigem atualização prévia do template canônico correspondente."
    )


def test_homologation_gate_no_unhomologated_sections_in_prompts():
    """
    Gate de Homologação: Garante que nenhum prompt (.prompt.md) possua seções
    não homologadas de pré-carregamento documental (ex.: Source Docs, Docs Sempre Anexadas,
    Regras Herdadas, Catálogo). Dependências residem exclusivamente no frontmatter 'source_docs:'.
    """
    prompt_files = [p for p in PROMPTS_DIR.glob("*.prompt.md") if "templates" not in p.parts]
    assert len(prompt_files) >= 15

    prohibited_prompt_sections = {
        "source docs",
        "docs sempre anexadas",
        "regras herdadas",
        "catálogo / conhecimento base",
        "catalogo / conhecimento base",
        "skills associadas",
    }

    violations = []
    for prompt_file in prompt_files:
        rel_path = prompt_file.relative_to(REPO_ROOT)
        h2s = extract_h2_sections(prompt_file)
        for h in h2s:
            clean_h = h.lower()
            for prohibited in prohibited_prompt_sections:
                if prohibited in clean_h:
                    violations.append(f"[{rel_path}] Seção não homologada/proibida: '## {h}'")

    assert not violations, (
        f"Gate de Homologação falhou: {len(violations)} seções não homologadas em prompts:\n"
        + "\n".join(violations)
        + "\n-> Prompts devem utilizar frontmatter 'source_docs:' e aderir a prompt-template.md."
    )


def test_homologation_gate_no_unhomologated_sections_in_skills():
    """
    Gate de Homologação: Garante que nenhuma skill (SKILL.md) possua seções não homologadas
    de catálogo ou herança (ex.: Regras Herdadas, Docs Sempre Anexadas, Catálogo / Conhecimento Base).
    Skills devem aderir estritamente à arquitetura Progressive Disclosure de skill-template.md.
    """
    skill_files = [p for p in SKILLS_DIR.glob("**/SKILL.md") if "templates" not in p.parts]
    assert len(skill_files) >= 30

    prohibited_skill_sections = {
        "docs sempre anexadas",
        "catálogo / conhecimento base",
        "catalogo / conhecimento base",
        "skills associadas",
    }

    violations = []
    for skill_file in skill_files:
        rel_path = skill_file.relative_to(REPO_ROOT)
        h2s = extract_h2_sections(skill_file)
        for h in h2s:
            clean_h = h.lower()
            for prohibited in prohibited_skill_sections:
                if prohibited in clean_h:
                    violations.append(f"[{rel_path}] Seção não homologada/proibida: '## {h}'")

    assert not violations, (
        f"Gate de Homologação falhou: {len(violations)} seções não homologadas em skills:\n"
        + "\n".join(violations)
        + "\n-> Skills devem aderir estritamente à estrutura de skill-template.md."
    )


def test_homologation_gate_blocks_unhomologated_injections(tmp_path: Path):
    """
    Valida empiricamente que o gate de homologação bloqueia qualquer injeção ad-hoc de seções
    não homologadas em agents, prompts ou skills caso um template prévio não autorize.
    """
    dummy_agent = tmp_path / "dummy.agent.md"
    dummy_agent.write_text(
        "---\nname: dummy\n---\n# Dummy Agent\n## 🛑 CRÍTICO: ESCOPO\n## 📌 Docs Sempre Anexadas (pre-fetch obrigatório)\n",
        encoding="utf-8"
    )

    h2s = extract_h2_sections(dummy_agent)
    has_unhomologated = any(
        any(p in h.lower() for p in PROHIBITED_DOC_SECTIONS_NON_ROUTERS)
        for h in h2s
    )
    assert has_unhomologated is True, "Gate deveria identificar a seção não homologada como violação"
