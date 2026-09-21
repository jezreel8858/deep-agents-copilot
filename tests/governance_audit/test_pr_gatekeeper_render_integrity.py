"""
test_pr_gatekeeper_render_integrity.py — Validação determinística contra corrupção de blocos de código
(```bash, ````markdown, ```diff) e formatação de Pull Request em pr-gatekeeper e correlatos.

Garante que:
1. pr-gatekeeper.agent.md NÃO encapsula a resposta inteira em um bloco markdown global.
2. pr-gatekeeper.agent.md declara no bloco CRÍTICO os guardrails anti-corrupção de markdown.
3. pr-gatekeeper.agent.md estrutura a saída em 5 blocos isolados e autocontidos.
4. commit.prompt.md mantém paridade com os 5 blocos e diretrizes anti-corrupção.
5. Todos os blocos de código em pr-gatekeeper.agent.md e prompts/agents correlatos são balanceados e válidos.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"


def test_pr_gatekeeper_no_outer_markdown_fence_in_output_format():
    """Valida que ## Formato de Saída não é encapsulado por um outer code block."""
    pr_file = AGENTS_DIR / "pr-gatekeeper.agent.md"
    assert pr_file.exists(), "pr-gatekeeper.agent.md deve existir"
    content = pr_file.read_text(encoding="utf-8")

    formato_idx = content.find("## Formato de Saída")
    assert formato_idx != -1, "Deve conter a seção ## Formato de Saída"

    next_section_idx = content.find("## Checklist Antes de Gerar PR", formato_idx)
    assert next_section_idx != -1, "Deve conter a seção seguinte"

    formato_slice = content[formato_idx:next_section_idx].strip()
    lines = formato_slice.splitlines()

    # Logo após ## Formato de Saída, não deve haver fence imediatamente abrindo toda a seção
    non_empty = [l.strip() for l in lines[1:] if l.strip()]
    first_meaningful = non_empty[0] if non_empty else ""
    assert not first_meaningful.startswith("```markdown"), (
        "## Formato de Saída NUNCA deve iniciar encapsulando toda a resposta em ```markdown"
    )
    assert not first_meaningful.startswith("````markdown"), (
        "## Formato de Saída NUNCA deve iniciar encapsulando toda a resposta em ````markdown"
    )


def test_pr_gatekeeper_critical_anti_corruption_guardrails():
    """Valida guardrails anti-corrupção no bloco CRÍTICO de pr-gatekeeper.agent.md."""
    pr_file = AGENTS_DIR / "pr-gatekeeper.agent.md"
    content = pr_file.read_text(encoding="utf-8")

    critico_idx = content.find("## CRÍTICO: ESCOPO DO AGENT")
    assert critico_idx != -1, "Deve conter a seção ## CRÍTICO: ESCOPO DO AGENT"

    dt_idx = content.find("## Decision Tree", critico_idx)
    critico_slice = content[critico_idx:dt_idx]

    assert "NUNCA encapsular a resposta inteira em um único bloco de código markdown global" in critico_slice, (
        "CRÍTICO deve proibir encapsulamento global em bloco markdown"
    )
    assert "NÃO aninhar blocos de código com a mesma quantidade de backticks" in critico_slice, (
        "CRÍTICO deve proibir aninhamento de blocos de mesma quantidade de backticks"
    )
    assert "4 backticks" in critico_slice or "````markdown" in critico_slice, (
        "CRÍTICO deve instruir o uso de 4 backticks para artefato copiável de descrição de PR"
    )


def test_pr_gatekeeper_isolated_artifacts_blocks():
    """Valida que a seção de saída define com clareza os 5 blocos isolados e autocontidos."""
    pr_file = AGENTS_DIR / "pr-gatekeeper.agent.md"
    content = pr_file.read_text(encoding="utf-8")

    assert "Bloco 1: Mensagem de Commit" in content
    assert "Bloco 2: Comando para Aplicação Manual do Commit" in content
    assert "Bloco 3: Título do PR" in content
    assert "Bloco 4: Descrição do PR" in content
    assert "Bloco 5: CHANGELOG.md" in content

    # Validar que a descrição do PR utiliza delimitador de 4 backticks
    assert "````markdown" in content, (
        "A descrição do PR no formato de saída deve usar 4 backticks para isolamento seguro"
    )


def test_commit_prompt_anti_corruption_parity():
    """Valida que commit.prompt.md incorpora diretrizes de isolamento dos 5 blocos e anti-corrupção."""
    prompt_file = PROMPTS_DIR / "commit.prompt.md"
    assert prompt_file.exists()
    content = prompt_file.read_text(encoding="utf-8")

    assert "Bloco 1 (Mensagem de Commit)" in content
    assert "Bloco 2 (Comando para Execução Manual)" in content
    assert "Bloco 3 (Título do PR)" in content
    assert "Bloco 4 (Descrição do PR)" in content
    assert "Bloco 5 (CHANGELOG.md" in content

    assert "Anti-Corrupção de Markdown" in content, (
        "commit.prompt.md deve possuir diretriz explícita Anti-Corrupção de Markdown"
    )


def test_no_unclosed_or_malformed_code_fences_in_pr_gatekeeper():
    """Valida rigorosamente o balanceamento de code fences em pr-gatekeeper.agent.md."""
    pr_file = AGENTS_DIR / "pr-gatekeeper.agent.md"
    content = pr_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    stack = []
    for idx, line in enumerate(lines, 1):
        m = re.match(r"^(\`{3,})", line.strip())
        if m:
            fence = m.group(1)
            fence_len = len(fence)
            if not stack:
                stack.append((fence_len, idx, line))
            else:
                top_len, top_idx, top_line = stack[-1]
                if fence_len == top_len:
                    stack.pop()
                elif fence_len < top_len:
                    # Nested fence inside larger fence (e.g. ``` inside ````)
                    pass
                else:
                    pytest.fail(
                        f"Linha {idx}: Fence de tamanho {fence_len} inválido dentro de fence de tamanho {top_len} (aberto na linha {top_idx})"
                    )

    assert len(stack) == 0, f"pr-gatekeeper.agent.md possui blocos de código não fechados: {stack}"


def test_all_governance_agents_and_prompts_code_fences_closed():
    """Valida que nenhum arquivo de agente ou prompt possui blocos de código não fechados."""
    target_dirs = [AGENTS_DIR, PROMPTS_DIR]

    for d in target_dirs:
        for file_path in d.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            stack = []
            for idx, line in enumerate(lines, 1):
                m = re.match(r"^(\`{3,})", line.strip())
                if m:
                    fence = m.group(1)
                    fence_len = len(fence)
                    if not stack:
                        stack.append((fence_len, idx, line))
                    else:
                        top_len, top_idx, _ = stack[-1]
                        if fence_len == top_len:
                            stack.pop()

            assert len(stack) == 0, f"{file_path.name} possui bloco de código não fechado na linha {stack[0][1]}"
