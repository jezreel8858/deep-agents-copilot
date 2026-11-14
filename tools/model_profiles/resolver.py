"""
resolver.py — Resolução hierárquica e pura de perfis de modelos (D2 / Mini-ADR 1).

Quality Gate e motor determinístico que implementa:
- get_canonical_key: mapeamento de caminhos para chaves canônicas via relative_to sem resolve() nem split.
- get_tier_for_key: mapeamento seguro de chave para tier com mensagem amigável no lugar de KeyError cru.
- normalize_model_name: validação de tipo e higienização de string.
- resolve_profile: resolução em camadas (extends) com detecção determinística de ciclos ordenados.
- resolve_target_model: aplicação estrita da precedência D2 (agents/prompts > tiers).
- validate_profile_keys: validação estrita da forma canônica prompt:<nome> e rejeição de prefixo em agents.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def get_canonical_key(
    file_path: Path,
    agents_dir: Path | None = None,
    prompts_dir: Path | None = None,
) -> str:
    """Mapeia um caminho de arquivo (.agent.md ou .prompt.md) para sua chave única em tier_map.

    Utiliza relative_to sem resolve() nem split de string arbitrária.
    """
    # Se os diretórios não foram fornecidos, deduz a partir da hierarquia do arquivo
    if prompts_dir is None:
        for parent in file_path.parents:
            if parent.name == "prompts" and parent.parent.name == ".github":
                prompts_dir = parent
                break

    if agents_dir is None:
        for parent in file_path.parents:
            if parent.name == "agents" and parent.parent.name == ".github":
                agents_dir = parent
                break

    if prompts_dir is not None:
        try:
            rel = file_path.relative_to(prompts_dir)
            posix = rel.as_posix()
            if posix.startswith("templates/"):
                sub = posix[len("templates/"):]
                if sub.endswith(".prompt.md"):
                    sub = sub[:-len(".prompt.md")]
                elif sub.endswith(".md"):
                    sub = sub[:-len(".md")]
                return f"prompt:templates/{sub}"
            stem = file_path.name
            if stem.endswith(".prompt.md"):
                stem = stem[:-len(".prompt.md")]
            elif stem.endswith(".md"):
                stem = stem[:-len(".md")]
            return f"prompt:{stem}"
        except ValueError:
            pass

    if agents_dir is not None:
        try:
            rel = file_path.relative_to(agents_dir)
            posix = rel.as_posix()
            if posix.startswith("templates/"):
                sub = posix[len("templates/"):]
                if sub.endswith(".agent.md"):
                    sub = sub[:-len(".agent.md")]
                elif sub.endswith(".md"):
                    sub = sub[:-len(".md")]
                return f"templates/{sub}"
            stem = file_path.name
            if stem.endswith(".agent.md"):
                stem = stem[:-len(".agent.md")]
            elif stem.endswith(".md"):
                stem = stem[:-len(".md")]
            return stem
        except ValueError:
            pass

    return file_path.stem


def get_tier_for_key(target_key: str, key_to_tier: dict[str, str]) -> str:
    """Retorna o tier correspondente a uma chave canônica com mensagem clara no lugar de KeyError cru."""
    if target_key not in key_to_tier:
        raise KeyError(
            f"Chave '{target_key}' não encontrada no tier_map de model-profiles.yaml. "
            "Certifique-se de que o artefato possui entrada correspondente em tier_map."
        )
    return key_to_tier[target_key]


def normalize_model_name(name: Any) -> str:
    """Valida que o nome do modelo é uma string não vazia e aplica strip."""
    if not isinstance(name, str):
        raise TypeError(f"Nome do modelo deve ser string, recebido {type(name).__name__}: {name!r}")
    stripped = name.strip()
    if not stripped:
        raise ValueError("Nome do modelo não pode ser vazio")
    return stripped


def validate_profile_keys(
    profile_name: str,
    profile_data: dict[str, Any],
    valid_agent_keys: set[str] | None = None,
    valid_prompt_keys: set[str] | None = None,
) -> None:
    """Valida as chaves declaradas em agents: e prompts: de um perfil.

    Garante que chaves de prompt usam compulsoriamente a forma canônica 'prompt:<nome>'
    e que chaves de agent não usam prefixo 'prompt:'.
    """
    agents = profile_data.get("agents") or {}
    prompts = profile_data.get("prompts") or {}

    for k in agents.keys():
        if k.startswith("prompt:"):
            raise ValueError(
                f"Perfil '{profile_name}': chave de agent '{k}' não deve conter o prefixo 'prompt:'."
            )
        if valid_agent_keys is not None and k not in valid_agent_keys:
            raise KeyError(
                f"Perfil '{profile_name}': chave de agent '{k}' não consta no tier_map de agents."
            )

    for k in prompts.keys():
        if not k.startswith("prompt:"):
            raise ValueError(
                f"Perfil '{profile_name}': chave de prompt '{k}' deve usar a forma canônica 'prompt:<nome>'."
            )
        if valid_prompt_keys is not None and k not in valid_prompt_keys:
            raise KeyError(
                f"Perfil '{profile_name}': chave de prompt '{k}' não consta no tier_map de prompts."
            )


def resolve_profile(
    profile_name: str,
    all_profiles: dict[str, Any],
    visited: list[str] | None = None,
) -> dict[str, Any]:
    """Resolve recursivamente um perfil aplicando a cadeia de extends (com detecção ordenada de ciclos)."""
    if visited is None:
        visited = []

    if profile_name in visited:
        cycle_path = " -> ".join(visited + [profile_name])
        raise ValueError(f"Ciclo detectado em extends: {cycle_path}")

    if profile_name not in all_profiles:
        raise KeyError(f"Perfil '{profile_name}' não encontrado na configuração")

    raw = all_profiles[profile_name]
    if not isinstance(raw, dict):
        raise TypeError(f"Perfil '{profile_name}' deve ser um dicionário")

    extends_target = raw.get("extends")
    if extends_target:
        if extends_target not in all_profiles:
            raise KeyError(
                f"Perfil base '{extends_target}' referenciado por '{profile_name}' não existe na configuração"
            )
        base = resolve_profile(extends_target, all_profiles, visited + [profile_name])
    else:
        base = {"tiers": {}, "agents": {}, "prompts": {}, "description": "", "quality_warning": None}

    # Merges tolerantes a null/ausência
    merged_tiers = dict(base.get("tiers") or {})
    raw_tiers = raw.get("tiers") or {}
    for t, m in raw_tiers.items():
        merged_tiers[t] = normalize_model_name(m)

    merged_agents = dict(base.get("agents") or {})
    raw_agents = raw.get("agents") or {}
    for a, m in raw_agents.items():
        if a.startswith("prompt:"):
            raise ValueError(f"Perfil '{profile_name}': chave de agent '{a}' não deve conter 'prompt:'")
        merged_agents[a] = normalize_model_name(m)

    merged_prompts = dict(base.get("prompts") or {})
    raw_prompts = raw.get("prompts") or {}
    for p, m in raw_prompts.items():
        if not p.startswith("prompt:"):
            raise ValueError(f"Perfil '{profile_name}': chave de prompt '{p}' deve usar a forma canônica 'prompt:<nome>'")
        merged_prompts[p] = normalize_model_name(m)

    # Herança de description e quality_warning
    raw_desc = raw.get("description")
    description = raw_desc if raw_desc is not None else base.get("description", "")

    raw_warning = raw.get("quality_warning")
    quality_warning = raw_warning if raw_warning is not None else base.get("quality_warning")

    return {
        "description": description,
        "quality_warning": quality_warning,
        "tiers": merged_tiers,
        "agents": merged_agents,
        "prompts": merged_prompts,
    }


def resolve_target_model(
    target_key: str,
    tier_name: str,
    resolved_profile: dict[str, Any],
) -> str:
    """Aplica a regra de precedência D2: agents/prompts > tiers."""
    prompts = resolved_profile.get("prompts") or {}
    agents = resolved_profile.get("agents") or {}
    tiers = resolved_profile.get("tiers") or {}

    if target_key.startswith("prompt:"):
        if target_key in prompts:
            return prompts[target_key]
    else:
        if target_key in agents:
            return agents[target_key]

    if tier_name not in tiers:
        raise KeyError(
            f"Tier '{tier_name}' (requerido por '{target_key}') não encontrado nos tiers do perfil."
        )

    return tiers[tier_name]
