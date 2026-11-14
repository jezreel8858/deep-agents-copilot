"""Allowlist de modelos (pinnable/status/aposentadoria/frescor) e mapa de cost_rank."""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from tools.model_profiles import config
from tools.model_profiles.findings import ERROR, WARN, Finding
RETIREMENT_WINDOW_DAYS = 30
def _to_date(value: Any) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value)) if value else None
@dataclass(frozen=True)
class AllowedModel:
    name: str
    status: str
    pinnable: bool
    retirement_date: dt.date | None
    cost_rank: int | None
@dataclass(frozen=True)
class Allowlist:
    models: dict[str, AllowedModel]
    verified_at: dt.date | None
    freshness_days: int
    def rank_by_model(self) -> dict[str, int | None]:
        return {name: m.cost_rank for name, m in self.models.items()}
    def age_days(self, today: dt.date | None = None) -> int | None:
        if self.verified_at is None:
            return None
        return ((today or dt.date.today()) - self.verified_at).days
    def is_stale(self, today: dt.date | None = None) -> bool:
        age = self.age_days(today)
        return age is None or age > self.freshness_days
    def check(self, model: str, today: dt.date | None = None) -> list[Finding]:
        entry = self.models.get(model)
        if entry is None:
            return [Finding("UNKNOWN_MODEL", f"'{model}' nao consta na allowlist", ERROR)]
        out = _status_findings(entry)
        soon = _retirement_finding(entry, today or dt.date.today())
        return out + ([soon] if soon else [])
def _status_findings(entry: AllowedModel) -> list[Finding]:
    if not entry.pinnable:
        return [Finding("NOT_PINNABLE", f"'{entry.name}' nao e pinavel via frontmatter", ERROR)]
    if entry.status == "retired":
        return [Finding("RETIRED", f"'{entry.name}' esta aposentado", ERROR)]
    if entry.status == "deprecated":
        return [Finding("DEPRECATED", f"'{entry.name}' esta deprecated", WARN)]
    return []
def _retirement_finding(entry: AllowedModel, today: dt.date) -> Finding | None:
    if entry.retirement_date is None or entry.status == "retired":
        return None
    days = (entry.retirement_date - today).days
    if days <= RETIREMENT_WINDOW_DAYS:
        return Finding("RETIREMENT_SOON",
                       f"'{entry.name}' sera aposentado em {entry.retirement_date} ({days} dias)", WARN)
    return None
def load(path: Path) -> Allowlist:
    data = config.load_yaml(path)
    models = {}
    for raw in data.get("models") or []:
        models[raw["name"]] = AllowedModel(
            name=raw["name"], status=str(raw.get("status", "")),
            pinnable=bool(raw.get("pinnable", False)),
            retirement_date=_to_date(raw.get("retirement_date")),
            cost_rank=raw.get("cost_rank"))
    return Allowlist(models, _to_date(data.get("verified_at")),
                     int(data.get("freshness_days", 30)))
