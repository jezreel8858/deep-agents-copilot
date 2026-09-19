"""
test_agnostic_governance_files.py — Suíte de testes para garantir 100% de agnosticismo
em arquivos de governança global e não-especialistas (R-038).

Garante que:
1. Arquivos globais de governança não contêm acoplamento com tecnologias, frameworks ou anotações concretas.
2. Exemplos em workflows e guias de governança utilizam identificadores genéricos canônicos.
3. Conhecimento específico de tecnologia/framework permanece restrito a sub-catálogos de domínio e adapters.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Arquivos que DEVEM ser 100% agnósticos de tecnologia, frameworks e anotações concretas
AGNOSTIC_GOVERNANCE_FILES = [
    Path(".github/agents/workflows.md"),
    Path(".github/agents/requirements-analyst.agent.md"),
    Path(".github/agents/business-rules-extractor.agent.md"),
    Path(".github/agents/refactor-planner.agent.md"),
    Path(".github/agents/test-strategy.agent.md"),
    Path(".github/agents/agent-auditor.agent.md"),
    Path(".github/agents/repo-hygiene-auditor.agent.md"),
    Path("docs/architecture/ARCHITECTURE_AND_GOVERNANCE_GUIDE.md"),
]

# Dicionário de termos tecnológicos concretos proibidos nos arquivos agnósticos
PROHIBITED_TECH_PATTERNS = {
    "Anotações de Frameworks Específicos": [
        r"@Transactional\b",
        r"@Entity\b",
        r"@RestController\b",
        r"@Component\b",
        r"@Autowired\b",
        r"@Injectable\b",
        r"@NgModule\b",
        r"@EmbeddedId\b",
    ],
    "Bibliotecas e Frameworks Concretos de Aplicação": [
        r"\bWebFlux\b",
        r"\bHibernate\b",
        r"\bTopLink\b",
        r"\bThymeleaf\b",
        r"\bOpenHTMLtoPDF\b",
        r"\bJasperReports\b",
        r"\bRabbitMQ\b",
        r"\bKafka\b",
        r"\bOpenJPA\b",
    ],
    "Protocolos e Stubs Específicos": [
        r"\bWSDL\b",
        r"\bJAX-WS\b",
        r"\bJAXB\b",
    ],
    "Tabelas ou Schemas Específicos de Negócio": [
        r"\bSMEM[A-Z0-9_]+\b",
        r"\bSMER[A-Z0-9_]+\b",
        r"\bMULTIEMPRESA\b",
    ],
}


def test_agnostic_governance_files_do_not_contain_concrete_technologies():
    """Valida R-038: Arquivos de governança global não devem conter termos, anotações
    ou bibliotecas concretas de aplicação nos seus fluxos normativos."""
    violations: list[str] = []

    for rel_path in AGNOSTIC_GOVERNANCE_FILES:
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            continue

        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()

        for category, patterns in PROHIBITED_TECH_PATTERNS.items():
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                for line_num, line in enumerate(lines, start=1):
                    # Ignora se for linha de comentário de regex/teste ou citação em tabela de mapeamento de sub-catálogos
                    if "exemplo:" in line.lower() and ("regex" in line.lower() or "padrao" in line.lower()):
                        continue

                    # Permite linhas da tabela de mapeamento de roles genéricos (§ 1.3 do workflows.md)
                    if rel_path == Path(".github/agents/workflows.md") and line_num <= 45:
                        continue

                    match = regex.search(line)
                    if match:
                        violations.append(
                            f"[{rel_path}:{line_num}] [{category}] Encontrado termo proibido '{match.group(0)}':\n  -> {line.strip()}"
                        )

    assert not violations, (
        f"Foram detectadas {len(violations)} violações de genericidade (R-038) em arquivos agnósticos:\n"
        + "\n".join(f"  - {v}" for v in violations[:20])
    )


def test_agnostic_files_exist_and_are_readable():
    """Garante que a lista de arquivos agnósticos monitorados existe no repositório."""
    for rel_path in AGNOSTIC_GOVERNANCE_FILES:
        file_path = REPO_ROOT / rel_path
        assert file_path.exists(), f"Arquivo agnóstico monitorado não encontrado: {rel_path}"

