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
