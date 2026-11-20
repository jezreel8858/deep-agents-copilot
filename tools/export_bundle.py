"""Empacotador em Bundles por Stack & Exportador Multi-Runtime (P8).

Exporta sub-ecossistemas de stack (spring-boot, angular, python, react, ejb,
struts, database ou core) resolvendo transitivamente agents, sub-catálogos,
skills e referências para múltiplos runtimes:
  - copilot (.github/agents, .github/skills, .github/copilot-instructions.md)
  - claude-code (.claude/agents, .claude/skills, CLAUDE.md)
  - cursor (.cursor/rules/*.mdc)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_ROOT = REPO_ROOT / ".github" / "agents"
SKILLS_ROOT = REPO_ROOT / ".github" / "skills"

SKILL_REF_RE = re.compile(r"\.github/skills/([a-z0-9_-]+)/([A-Za-z0-9_./-]+)")
CORE_AGENTS = ("agent-root", "agent-router")


@dataclass
class ExportedArtifact:
    source_relpath: str
    target_relpath: str
    kind: str
    sha256: str
    size_bytes: int


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover_available_stacks(agents_root: Path = AGENTS_ROOT) -> dict[str, Path]:
    """Descobre todos os sub-catálogos de stack disponíveis em .github/agents/{backend,frontend}."""
    stacks: dict[str, Path] = {}
    for layer in ("backend", "frontend"):
        layer_dir = agents_root / layer
        if not layer_dir.exists():
            continue
        for catalog_file in sorted(layer_dir.glob("*/*-catalog.yaml")):
            stack_name = catalog_file.parent.name
            stacks[stack_name] = catalog_file
    return stacks


def _find_agent_md(agent_id: str, agents_root: Path = AGENTS_ROOT) -> Path | None:
    direct = agents_root / f"{agent_id}.agent.md"
    if direct.exists():
        return direct
    matches = sorted(agents_root.rglob(f"{agent_id}.agent.md"))
    return matches[0] if matches else None


def resolve_stack_dependencies(
    stack: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Resolve todos os arquivos de agents, catálogos e skills necessários para uma stack."""
    agents_root = repo_root / ".github" / "agents"
    skills_root = repo_root / ".github" / "skills"
    available_stacks = discover_available_stacks(agents_root)

    if stack != "core" and stack not in available_stacks:
        valid = ", ".join(["core", *sorted(available_stacks.keys())])
        raise ValueError(f"Stack desconhecida '{stack}'. Stacks disponíveis: {valid}")

    agent_ids: list[str] = list(CORE_AGENTS)
    skill_names: set[str] = {"agent-contracts", "handoff-governance", "context-mode"}
    extra_files: list[Path] = []

    central_catalog_path = agents_root / "catalog.yaml"
    central_catalog = (
        yaml.safe_load(central_catalog_path.read_text(encoding="utf-8")) or {}
        if central_catalog_path.exists()
        else {}
    )
    central_agents = central_catalog.get("agents") or {}

    if stack != "core":
        sub_catalog_path = available_stacks[stack]
        extra_files.append(sub_catalog_path)
        sub_catalog = yaml.safe_load(sub_catalog_path.read_text(encoding="utf-8")) or {}

        router_cfg = sub_catalog.get("router") or {}
        if router_cfg.get("id"):
            agent_ids.append(str(router_cfg["id"]))
        for sk in router_cfg.get("skills") or []:
            skill_names.add(str(sk))

        for ag_key, ag_cfg in (sub_catalog.get("agents") or {}).items():
            ag_id = str((ag_cfg or {}).get("id") or ag_key)
            if ag_id not in agent_ids:
                agent_ids.append(ag_id)
            for sk in (ag_cfg or {}).get("skills") or []:
                skill_names.add(str(sk))
    else:
        for ag_id in sorted(central_agents.keys()):
            if not ag_id.endswith("-router") or ag_id == "agent-router":
                if ag_id not in agent_ids:
                    agent_ids.append(ag_id)

    agent_files: list[Path] = []
    for ag_id in agent_ids:
        entry = central_agents.get(ag_id) or {}
        for sk in entry.get("related_skills") or []:
            skill_names.add(str(sk))

        md_path = _find_agent_md(ag_id, agents_root)
        if md_path and md_path.exists():
            agent_files.append(md_path)
            md_text = md_path.read_text(encoding="utf-8", errors="replace")
            for match in SKILL_REF_RE.finditer(md_text):
                skill_names.add(match.group(1))

    skill_files: list[Path] = []
    for sk_name in sorted(skill_names):
        sk_dir = skills_root / sk_name
        if not sk_dir.exists() or not sk_dir.is_dir():
            continue
        for file_path in sorted(sk_dir.rglob("*")):
            if file_path.is_file() and "__pycache__" not in file_path.parts:
                skill_files.append(file_path)

    return {
        "stack": stack,
        "agent_ids": agent_ids,
        "skills": sorted(skill_names),
        "agent_files": agent_files,
        "skill_files": skill_files,
        "extra_files": extra_files,
    }


def _strip_frontmatter(md_text: str) -> tuple[dict[str, Any], str]:
    if md_text.startswith("---"):
        parts = md_text.split("---", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2].lstrip("\r\n")
    return {}, md_text


def export_bundle(
    stack: str,
    target: str,
    output_dir: Path,
    repo_root: Path = REPO_ROOT,
    create_zip: bool = False,
) -> dict[str, Any]:
    """Materializa o bundle da stack no diretório de saída para o runtime escolhido."""
    if target not in {"copilot", "claude-code", "cursor"}:
        raise ValueError(f"Target inválido '{target}'. Use: copilot, claude-code ou cursor.")

    resolved = resolve_stack_dependencies(stack=stack, repo_root=repo_root)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exported: list[ExportedArtifact] = []

    def _write_artifact(src_rel: str, dst_rel: str, kind: str, content_bytes: bytes) -> None:
        dst_path = output_dir / dst_rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.write_bytes(content_bytes)
        exported.append(
            ExportedArtifact(
                source_relpath=src_rel,
                target_relpath=dst_rel,
                kind=kind,
                sha256=_sha256_bytes(content_bytes),
                size_bytes=len(content_bytes),
            )
        )

    # 1. Instruções raiz por runtime
    copilot_instr = repo_root / ".github" / "copilot-instructions.md"
    claude_md = repo_root / "CLAUDE.md"
    if target == "copilot" and copilot_instr.exists():
        _write_artifact(
            ".github/copilot-instructions.md",
            ".github/copilot-instructions.md",
            "instructions",
            copilot_instr.read_bytes(),
        )
    elif target == "claude-code" and claude_md.exists():
        _write_artifact(
            "CLAUDE.md",
            "CLAUDE.md",
            "instructions",
            claude_md.read_bytes(),
        )

    # 2. Agents
    for ag_path in resolved["agent_files"]:
        src_rel = ag_path.relative_to(repo_root).as_posix()
        raw_bytes = ag_path.read_bytes()
        if target == "copilot":
            _write_artifact(src_rel, src_rel, "agent", raw_bytes)
        elif target == "claude-code":
            dst_rel = f".claude/agents/{ag_path.name.replace('.agent.md', '.md')}"
            _write_artifact(src_rel, dst_rel, "agent", raw_bytes)
        elif target == "cursor":
            text = raw_bytes.decode("utf-8", errors="replace")
            meta, body = _strip_frontmatter(text)
            slug = ag_path.name.replace(".agent.md", "")
            desc = str(meta.get("description") or f"Agent {slug}").replace('"', "'")
            mdc = f'---\ndescription: "{desc}"\nalwaysApply: false\n---\n\n{body}'
            _write_artifact(src_rel, f".cursor/rules/agent-{slug}.mdc", "agent_rule", mdc.encode("utf-8"))

    # 3. Skills & Referências
    for sk_path in resolved["skill_files"]:
        src_rel = sk_path.relative_to(repo_root).as_posix()
        rel_inside_skills = sk_path.relative_to(repo_root / ".github" / "skills").as_posix()
        raw_bytes = sk_path.read_bytes()
        if target == "copilot":
            _write_artifact(src_rel, src_rel, "skill", raw_bytes)
        elif target == "claude-code":
            _write_artifact(src_rel, f".claude/skills/{rel_inside_skills}", "skill", raw_bytes)
        elif target == "cursor" and sk_path.name == "SKILL.md":
            text = raw_bytes.decode("utf-8", errors="replace")
            meta, body = _strip_frontmatter(text)
            skill_slug = sk_path.parent.name
            desc = str(meta.get("description") or f"Skill {skill_slug}").replace('"', "'")
            mdc = f'---\ndescription: "{desc}"\nalwaysApply: false\n---\n\n{body}'
            _write_artifact(src_rel, f".cursor/rules/skill-{skill_slug}.mdc", "skill_rule", mdc.encode("utf-8"))

    # 4. Sub-catálogos da stack
    for extra_path in resolved["extra_files"]:
        src_rel = extra_path.relative_to(repo_root).as_posix()
        raw_bytes = extra_path.read_bytes()
        if target == "copilot":
            _write_artifact(src_rel, src_rel, "catalog", raw_bytes)
        elif target == "claude-code":
            _write_artifact(src_rel, f".claude/catalogs/{extra_path.name}", "catalog", raw_bytes)

    manifest = {
        "bundle_version": "1.0.0",
        "stack": stack,
        "target": target,
        "agents_included": resolved["agent_ids"],
        "skills_included": resolved["skills"],
        "files_count": len(exported),
        "files": [asdict(item) for item in exported],
    }
    manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
    (output_dir / "bundle-manifest.json").write_bytes(manifest_bytes)

    zip_path_str: str | None = None
    if create_zip:
        zip_path = output_dir.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_on_disk in sorted(output_dir.rglob("*")):
                if file_on_disk.is_file():
                    zf.write(file_on_disk, file_on_disk.relative_to(output_dir).as_posix())
        zip_path_str = str(zip_path)

    return {
        "verdict": "PASS",
        "stack": stack,
        "target": target,
        "output_dir": str(output_dir),
        "zip_archive": zip_path_str,
        "agents_count": len(resolved["agent_ids"]),
        "skills_count": len(resolved["skills"]),
        "files_count": len(exported) + 1,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Empacotador em Bundles por Stack & Exportador Multi-Runtime (P8)."
    )
    parser.add_argument(
        "--stack",
        default="spring-boot",
        help="Nome da stack (ex.: spring-boot, angular, python, react, ejb, struts, database ou core).",
    )
    parser.add_argument(
        "--target",
        choices=("copilot", "claude-code", "cursor"),
        default="copilot",
        help="Runtime de destino do bundle.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Diretório de destino (padrão: dist/bundles/<stack>-<target>).",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Empacota também em arquivo .zip portátil.",
    )
    parser.add_argument(
        "--list-stacks",
        action="store_true",
        help="Lista as stacks disponíveis e encerra.",
    )
    args = parser.parse_args(argv)

    if args.list_stacks:
        stacks = sorted(["core", *discover_available_stacks().keys()])
        print(json.dumps({"available_stacks": stacks}, indent=2))
        return 0

    out_dir = args.output or (REPO_ROOT / "dist" / "bundles" / f"{args.stack}-{args.target}")
    summary = export_bundle(
        stack=args.stack,
        target=args.target,
        output_dir=out_dir.resolve(),
        create_zip=args.zip,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(main())