"""
Validação Operacional: Circuit Breaker de Falhas, Rollback Atômico e Context Offloading
Garante que o ecossistema multi-agente possui mecanismos de contenção de loops e prevenção de context bloat.
"""

import hashlib
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
HANDOFF_SKILL_PATH = BASE_DIR / ".github" / "skills" / "handoff-governance" / "SKILL.md"
SAFETY_SKILL_PATH = BASE_DIR / ".github" / "skills" / "agent-safety-guardrails" / "SKILL.md"


class MultiAgentCircuitBreaker:
    """Implementação canônica do Circuit Breaker com Retry Budget para agentes."""
    def __init__(self, max_retries_per_step: int = 2):
        self.max_retries = max_retries_per_step
        self.consecutive_failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def record_success(self):
        self.consecutive_failures = 0
        self.state = "CLOSED"

    def record_failure(self) -> str:
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_retries:
            self.state = "OPEN"
        return self.state

    def can_execute(self) -> bool:
        return self.state != "OPEN"


class ContextOffloadingManager:
    """Avaliador de limiar para Offloading de Artefatos em Handoffs."""
    BYTE_THRESHOLD = 2048
    LINE_THRESHOLD = 50

    @classmethod
    def should_offload(cls, content: str) -> bool:
        byte_size = len(content.encode("utf-8"))
        line_count = len(content.splitlines())
        return byte_size > cls.BYTE_THRESHOLD or line_count > cls.LINE_THRESHOLD

    @classmethod
    def create_pointer(cls, artifact_path: str, content: str, summary: str) -> dict:
        content_bytes = content.encode("utf-8")
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        return {
            "tipo": "pointer",
            "artifact_ref": artifact_path,
            "hash": f"sha256:{sha256_hash}",
            "tamanho_bytes": len(content_bytes),
            "resumo_executivo": summary
        }


def test_circuit_breaker_trips_to_open_after_2_failures():
    """Garante que o circuit breaker transiciona para OPEN após 2 falhas consecutivas."""
    cb = MultiAgentCircuitBreaker(max_retries_per_step=2)
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # Primeira falha
    cb.record_failure()
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # Segunda falha consecutiva: desarma o circuito
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_execute() is False

    # Recuperação após aprovação/reset
    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True


def test_context_offloading_threshold_logic():
    """Valida que artefatos pequenos permanecem inline e grandes geram ponteiro."""
    small_content = "const x = 1;\nconsole.log(x);"
    assert ContextOffloadingManager.should_offload(small_content) is False

    # Mais de 50 linhas
    long_content = "\n".join([f"line_{i} = {i}" for i in range(60)])
    assert ContextOffloadingManager.should_offload(long_content) is True

    # Mais de 2048 bytes
    heavy_content = "A" * 2500
    assert ContextOffloadingManager.should_offload(heavy_content) is True

    # Validação do formato do ponteiro gerado
    pointer = ContextOffloadingManager.create_pointer(
        artifact_path="docs/architecture/spec.md",
        content=heavy_content,
        summary="Especificação de arquitetura de alta escala."
    )
    assert pointer["tipo"] == "pointer"
    assert pointer["artifact_ref"] == "docs/architecture/spec.md"
    assert pointer["hash"].startswith("sha256:")
    assert pointer["tamanho_bytes"] == 2500
    assert len(pointer["resumo_executivo"]) > 0


def test_handoff_governance_skill_documents_circuit_breaker_and_offloading():
    """Garante que a skill handoff-governance documenta formalmente o Retry Budget e o Offloading."""
    with open(HANDOFF_SKILL_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Circuit Breaker de Falhas & Retry Budget" in content
    assert "MAX_RETRIES_PER_STEP = 2" in content
    assert "Protocolo de Rollback Atômico de Workspace" in content
    assert "Governança de Context Engineering & Offloading de Artefatos em Handoffs" in content
    assert "2 KB / 50 Linhas" in content
    assert 'tipo: "pointer"' in content


def test_safety_guardrails_documents_mcp_security_section():
    """Garante que agent-safety-guardrails documenta as regras de segurança MCP da NSA/CSA 2026."""
    with open(SAFETY_SKILL_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Segurança de Ferramentas MCP e Sandboxing" in content
    assert "Zona 1 (Read-Only / Consulta)" in content
    assert "Zona 2 (Mutating / Alteração de Código)" in content
    assert "Tool Squatting e Rug Pulls" in content
    assert "Parameter Tampering" in content

