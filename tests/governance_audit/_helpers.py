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

import datetime
from pathlib import Path
import re
from typing import Any
import yaml

# Regex ancorada tolerante a BOM e CRLF para extração de frontmatter YAML
FRONTMATTER_REGEX = re.compile(r"^\s*---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


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


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML SafeLoader determinístico que rejeita chaves duplicadas no mesmo nível de mapeamento."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    f"Chave duplicada encontrada no YAML: '{key}'",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def safe_load_yaml_unique(content_or_stream: str | Any) -> Any:
    """Carrega YAML garantindo que chaves duplicadas lançam ConstructorError."""
    return yaml.load(content_or_stream, Loader=UniqueKeySafeLoader)


def extract_frontmatter_model(file_path: Path) -> str:
    """Extrai e valida model: do frontmatter de um arquivo markdown (.agent.md ou .prompt.md).

    Lê obrigatoriamente com utf-8-sig e regex ancorada tolerante a CRLF e BOM.
    Lança ValueError explicativo caso o frontmatter seja inválido ou o campo model: esteja ausente.
    """
    text = file_path.read_text(encoding="utf-8-sig")
    m = FRONTMATTER_REGEX.match(text)
    if not m:
        raise ValueError(
            f"Arquivo '{file_path.as_posix()}' não possui frontmatter delimitado por '---' válido."
        )

    try:
        data = safe_load_yaml_unique(m.group(1))
    except Exception as e:
        raise ValueError(
            f"Erro ao processar YAML do frontmatter de '{file_path.as_posix()}': {e}"
        ) from e

    if not isinstance(data, dict):
        raise ValueError(
            f"Frontmatter de '{file_path.as_posix()}' não é um dicionário YAML válido."
        )

    model = data.get("model")
    if not model or not isinstance(model, str) or not model.strip():
        raise ValueError(
            f"Campo 'model:' ausente, vazio ou não-string no frontmatter de '{file_path.as_posix()}'."
        )

    return model.strip()


def is_governance_target_file(file_path: Path, agents_dir: Path, prompts_dir: Path) -> bool:
    """Determina se o arquivo markdown é um agent ou prompt governado que DEVE conter model:.

    Exclui documentações e workflows (README.md, QUICK-START.md, workflows.md, workflows/**).
    """
    try:
        rel = file_path.relative_to(agents_dir).as_posix()
        if rel in ("README.md", "workflows.md") or rel.startswith("workflows/"):
            return False
        return True
    except ValueError:
        pass

    try:
        rel = file_path.relative_to(prompts_dir).as_posix()
        if rel in ("README.md", "QUICK-START.md"):
            return False
        return True
    except ValueError:
        pass

    return False


def collect_repo_frontmatter_files(repo_root: Path) -> dict[str, tuple[Path, str]]:
    """Coleta e valida todos os arquivos de agents e prompts do repositório.

    Retorna um dicionário {canonical_key: (file_path, model_name)}.
    FALHA explicitamente listando todos os arquivos que estiverem sem model: ou com frontmatter inválido.
    """
    from tools.model_profiles.resolver import get_canonical_key

    agents_dir = repo_root / ".github" / "agents"
    prompts_dir = repo_root / ".github" / "prompts"

    result: dict[str, tuple[Path, str]] = {}
    errors: list[str] = []

    for search_dir in (agents_dir, prompts_dir):
        if not search_dir.exists():
            continue
        for md_file in sorted(search_dir.rglob("*.md")):
            if not is_governance_target_file(md_file, agents_dir, prompts_dir):
                continue
            try:
                model_name = extract_frontmatter_model(md_file)
                key = get_canonical_key(md_file, agents_dir=agents_dir, prompts_dir=prompts_dir)
                if key in result:
                    errors.append(f"Chave canônica duplicada '{key}' entre {md_file} e {result[key][0]}")
                result[key] = (md_file, model_name)
            except Exception as e:
                errors.append(f"{md_file.relative_to(repo_root).as_posix()}: {e}")

    if errors:
        raise AssertionError(
            f"Varredura de frontmatter falhou para {len(errors)} arquivo(s):\n"
            + "\n".join(f" - {err}" for err in errors)
        )

    return result


def check_allowlist_freshness(
    verified_date: datetime.date,
    freshness_days: int = 30,
    as_of_date: datetime.date | None = None,
) -> tuple[bool, str | None]:
    """Função pura para validação de frescor de allowlist.

    Rejeita datas no futuro (ValueError).
    Retorna (is_fresh: bool, warning_message: str | None).
    """
    if as_of_date is None:
        as_of_date = datetime.date.today()

    if verified_date > as_of_date:
        raise ValueError(
            f"Data de verificação '{verified_date}' está no futuro em relação a '{as_of_date}'"
        )

    age_days = (as_of_date - verified_date).days
    if age_days > freshness_days:
        msg = (
            f"Allowlist com {age_days} dias desde a última verificação ({verified_date}) "
            f"(limite: {freshness_days} dias). Recomenda-se rodar refresh de allowlist."
        )
        return False, msg

    return True, None


def load_allowlist(repo_root: Path) -> dict[str, Any]:
    """Carrega model-allowlist.yaml com UniqueKeySafeLoader."""
    allowlist_path = repo_root / "model-allowlist.yaml"
    assert allowlist_path.exists(), "model-allowlist.yaml deve existir na raiz do repositório"
    content = allowlist_path.read_text(encoding="utf-8")
    data = safe_load_yaml_unique(content)
    assert isinstance(data, dict), "model-allowlist.yaml deve ser um dicionário YAML válido"
    return data


def load_profiles(repo_root: Path) -> dict[str, Any]:
    """Carrega model-profiles.yaml com UniqueKeySafeLoader."""
    profiles_path = repo_root / "model-profiles.yaml"
    assert profiles_path.exists(), "model-profiles.yaml deve existir na raiz do repositório"
    content = profiles_path.read_text(encoding="utf-8")
    data = safe_load_yaml_unique(content)
    assert isinstance(data, dict), "model-profiles.yaml deve ser um dicionário YAML válido"
    return data
