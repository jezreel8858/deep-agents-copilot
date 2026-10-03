"""
_helpers.py — Utilitários compartilhados para a suíte de auditoria estática de governança.

Implementa o padrão "Positive Prompt Injection" (Böckeler/Fowler — Thoughtworks, 2026):
sensores computacionais (testes determinísticos) devem retornar mensagens de falha que já
contêm a instrução de remediação, fechando o ciclo cibernético de auto-correção do agente
sem exigir uma nova rodada de raciocínio inferencial (LLM) apenas para descobrir "o que
fazer a seguir". Isso reduz o custo de tokens do ciclo feedback -> correção.

Ver: governance-audit-patterns/SKILL.md § 2.28 (Smell — Mensagem de Sensor Sem Remediação
Acionável / Non-Actionable Assertion Message).
"""
from __future__ import annotations

from pathlib import Path


def remediation(message: str, *, fix_hint: str) -> str:
    """Formata uma mensagem de assert com bloco de remediação acionável.

    Args:
        message: descrição objetiva do que falhou (deve incluir `[arquivo:linha]` quando
            aplicável, seguindo a convenção já usada na suíte).
        fix_hint: instrução imperativa, específica e executável de como corrigir a
            violação (nome do campo a adicionar, valor esperado, arquivo a editar).

    Returns:
        Mensagem multilinha pronta para uso em `assert cond, remediation(...)`.
    """
    return f"{message}\n  REMEDIATION: {fix_hint}"


def read_workflows_full_content(repo_root: Path) -> str:
    """Reconstrói o conteúdo completo e equivalente ao antigo `workflows.md`
    monolítico, concatenando o índice raiz + os 9 arquivos de workflow +
    o arquivo transversal de invariantes/protocolos (R-066 / F3 — fatiamento
    de `.github/agents/workflows.md` em `.github/agents/workflows/`).

    Use esta função em vez de `(AGENTS_DIR / "workflows.md").read_text()` sempre
    que o teste precisar fazer `assert <string> in content` contra qualquer seção
    do antigo arquivo monolítico — o conteúdo normativo foi apenas reorganizado
    fisicamente, nunca removido.
    """
    agents_dir = repo_root / ".github" / "agents"
    index_path = agents_dir / "workflows.md"
    workflows_dir = agents_dir / "workflows"

    parts: list[str] = []
    if index_path.is_file():
        parts.append(index_path.read_text(encoding="utf-8"))
    if workflows_dir.is_dir():
        for p in sorted(workflows_dir.glob("*.md")):
            parts.append(p.read_text(encoding="utf-8"))
    return "\n".join(parts)


