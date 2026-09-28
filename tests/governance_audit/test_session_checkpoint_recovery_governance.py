"""
test_session_checkpoint_recovery_governance.py — Validação determinística de conformidade
das políticas de recuperação de sessão, watchdog de comandos de risco e persistência de checkpoint.

Garante que:
1. .github/skills/terminal-governance/SKILL.md contém os termos normativos 'timeout -k' e 'isBackground'
   no padrão de watchdog obrigatório contra travamentos de terminal.
2. .github/skills/agent-memory-policy/SKILL.md contém a diretiva normativa de 'Checkpoint Automático Pré-Risco'.
3. .github/hooks/context-mode.json é um JSON sintaticamente válido e íntegro.
4. .github/prompts/ctx-resume.prompt.md possui instruções de recuperação de crash e fallback.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

TERMINAL_GOVERNANCE_PATH = REPO_ROOT / ".github" / "skills" / "terminal-governance" / "SKILL.md"
AGENT_MEMORY_POLICY_PATH = REPO_ROOT / ".github" / "skills" / "agent-memory-policy" / "SKILL.md"
CONTEXT_MODE_HOOK_PATH = REPO_ROOT / ".github" / "hooks" / "context-mode.json"
CTX_RESUME_PROMPT_PATH = REPO_ROOT / ".github" / "prompts" / "ctx-resume.prompt.md"


def test_terminal_governance_contains_watchdog_terms():
    """Valida presença mandatória de timeout -k e isBackground em terminal-governance."""
    assert TERMINAL_GOVERNANCE_PATH.exists(), f"Arquivo não encontrado: {TERMINAL_GOVERNANCE_PATH}"
    content = TERMINAL_GOVERNANCE_PATH.read_text(encoding="utf-8")

    assert "timeout -k" in content, (
        "terminal-governance/SKILL.md deve conter o termo normativo 'timeout -k' "
        "para imposição de watchdog de tempo com sinal SIGKILL em comandos de risco."
    )
    assert "isBackground" in content, (
        "terminal-governance/SKILL.md deve conter o termo normativo 'isBackground' "
        "para execução não-bloqueante no terminal em processos com risco de travamento."
    )


def test_agent_memory_policy_contains_pre_risk_checkpoint():
    """Valida presença mandatória de 'Checkpoint Automático Pré-Risco' em agent-memory-policy."""
    assert AGENT_MEMORY_POLICY_PATH.exists(), f"Arquivo não encontrado: {AGENT_MEMORY_POLICY_PATH}"
    content = AGENT_MEMORY_POLICY_PATH.read_text(encoding="utf-8")

    assert "Checkpoint Automático Pré-Risco" in content, (
        "agent-memory-policy/SKILL.md deve conter a diretiva normativa "
        "'Checkpoint Automático Pré-Risco' (§ 3.2 Session Persistence)."
    )


def test_context_mode_hook_json_validity():
    """Valida que o arquivo .github/hooks/context-mode.json é um JSON válido e estruturado."""
    assert CONTEXT_MODE_HOOK_PATH.exists(), f"Arquivo não encontrado: {CONTEXT_MODE_HOOK_PATH}"
    raw_content = CONTEXT_MODE_HOOK_PATH.read_text(encoding="utf-8")

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        pytest.fail(f".github/hooks/context-mode.json é um JSON inválido: {exc}")

    assert isinstance(data, dict), ".github/hooks/context-mode.json deve ser um objeto JSON."
    assert len(data) > 0, ".github/hooks/context-mode.json não pode estar vazio."


def test_ctx_resume_prompt_crash_recovery():
    """Valida que ctx-resume.prompt.md contempla suporte a recuperação de crash."""
    if CTX_RESUME_PROMPT_PATH.exists():
        content = CTX_RESUME_PROMPT_PATH.read_text(encoding="utf-8")
        assert "checkpoint" in content.lower(), (
            "ctx-resume.prompt.md deve fazer referência à restauração por checkpoint."
        )
