"""Leitura de YAMLs de configuracao (somente leitura)."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml
from tools.model_profiles.errors import RefusalError
def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RefusalError(f"nao foi possivel ler {path.name}: {exc}", "CONFIG") from exc
    if not isinstance(data, dict):
        raise RefusalError(f"{path.name} deve ser um mapeamento YAML", "CONFIG")
    return data
