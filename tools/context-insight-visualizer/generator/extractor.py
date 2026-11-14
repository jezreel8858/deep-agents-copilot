#!/usr/bin/env python3
"""
extractor.py — Extrator de Telemetria Local do Context Mode
===========================================================
Lê bases de dados SQLite e snapshots JSON locais gerados pelo context-mode:
  - ~/.claude/context-mode/sessions/*.db (e fallback JetBrains)
  - ~/.claude/context-mode/sessions/stats-pid-*.json
  - ~/.claude/context-mode/content/*.db

Aplica regras de introspecção defensiva (PRAGMA table_info),
agregação resiliente e higienização/anonimização de caminhos locais (R-044).
"""

import glob
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_known_agents() -> set:
    """Carrega dinamicamente a lista de agentes do catálogo e inclui agentes canônicos."""
    known = {
        "adapter-generator", "agent-auditor", "agent-router",
        "analysis-architect", "angular-arch-advisor", "angular-developer",
        "angular-router", "angular-test-engineer",
        "binding-initializer", "bug-triage", "business-rules-extractor", "codegraph-engine",
        "code-review", "code-style-enforcer", "code-summarizer", "compliance-guardrails",
        "context-builder", "database-specialist", "debugger", "deep-search", "devops-engineer",
        "docs-engineer", "ejb-arch-advisor", "ejb-developer",
        "ejb-perf-tuner", "ejb-router",
        "ejb-test-engineer", "feature-planner", "governance-factory", "performance-agent",
        "pr-gatekeeper", "prompt-structuring", "refactor-planner", "requirements-analyst",
        "runtime-verifier", "security-reviewer", "spring-boot-arch-advisor", "spring-boot-developer",
        "spring-boot-perf-tuner",
        "spring-boot-router", "spring-boot-test-engineer",
        "spring-reactive-arch-advisor", "spring-reactive-developer",
        "spring-reactive-resilience-tuner",
        "spring-reactive-router", "spring-reactive-test-engineer",
        "test-strategy", "search", "angular-engineer", "docs-curator", "docs-writer", "agent-factory",
        "prompt-factory", "code-summarizer"
    }
    current_path = Path(__file__).resolve().parent
    candidates = [
        current_path.parent.parent.parent / ".github" / "agents",
        Path.cwd() / ".github" / "agents",
    ]
    for c in candidates:
        if c.exists():
            for f in c.rglob("*.agent.md"):
                known.add(f.name.replace(".agent.md", "").lower())
            break
    return known


SUBAGENT_PATTERNS = [
    re.compile(r'run_subagent\([^)]*agentName[:=]\s*["\']([a-zA-Z0-9_\-]+)["\']', re.IGNORECASE),
    re.compile(r'agentName["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]+)["\']', re.IGNORECASE),
    re.compile(r'Custom Agent\s*["\']([a-zA-Z0-9_\-]+)["\']', re.IGNORECASE),
    re.compile(r'Delegando para\s*@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'Delegado:\s*@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'Handoff:\s*@?[a-zA-Z0-9_\-]+\s*→\s*@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'(?:sub_agent|subagent)\s+(?:para\s+|de\s+)?@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'subagent[:\s]+@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
]

DIRECT_PATTERNS = [
    re.compile(r'@([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'(?:invoque|chame|use|rotei para)\s+(?:o\s+)?(?:agent\s+)?@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'Follow instructions in \[([a-zA-Z0-9_\-]+)\]\(.*\.prompt\.md\)', re.IGNORECASE),
    re.compile(r'(?:^|\s)/([a-zA-Z0-9_\-]+)', re.IGNORECASE),
    re.compile(r'Agente Ativo:\s*@?([a-zA-Z0-9_\-]+)', re.IGNORECASE),
]


def sanitize_project_name(project_dir: str) -> str:
    """Higieniza o caminho do projeto para exibição sem expor nomes de usuário (R-044)."""
    if not project_dir or project_dir in (".", "__unknown__", "unknown"):
        return "Workspace Raiz"
    p = project_dir.replace("\\", "/").rstrip("/")
    # Se terminar em bin ou similar de IDE
    if "JetBrains" in p and p.endswith("/bin"):
        return "JetBrains IDE Session"
    parts = p.split("/")
    return parts[-1] if parts else "Workspace"


def resolve_default_directories(
    custom_sessions_dir: Optional[str] = None,
    custom_content_dir: Optional[str] = None
) -> Tuple[List[Path], List[Path], List[Path]]:
    """Localiza todas as pastas de dados e logs do Context Mode ignorando node_modules e caches."""
    home = Path.home()

    # 1. Sessions dirs (Claude Code, JetBrains, etc.)
    sessions_dirs: List[Path] = []
    if custom_sessions_dir:
        sp = Path(custom_sessions_dir).expanduser()
        if sp.exists() and "node_modules" not in str(sp):
            sessions_dirs.append(sp)
    if not sessions_dirs:
        candidates = [
            home / ".claude" / "context-mode" / "sessions",
            home / ".config" / "JetBrains" / "context-mode" / "sessions",
            home / "AppData" / "Roaming" / "JetBrains" / "context-mode" / "sessions",
            home / "AppData" / "Local" / "JetBrains" / "context-mode" / "sessions",
            home / ".context-mode" / "sessions",
        ]
        for candidate in candidates:
            if candidate.exists() and "node_modules" not in str(candidate) and candidate not in sessions_dirs:
                sessions_dirs.append(candidate)

    # 2. Content dirs
    content_dirs: List[Path] = []
    if custom_content_dir:
        cp = Path(custom_content_dir).expanduser()
        if cp.exists() and "node_modules" not in str(cp):
            content_dirs.append(cp)
    if not content_dirs:
        candidates = [
            home / ".claude" / "context-mode" / "content",
            home / ".config" / "JetBrains" / "context-mode" / "content",
            home / "AppData" / "Roaming" / "JetBrains" / "context-mode" / "content",
            home / "AppData" / "Local" / "JetBrains" / "context-mode" / "content",
        ]
        for candidate in candidates:
            if candidate.exists() and "node_modules" not in str(candidate) and candidate not in content_dirs:
                content_dirs.append(candidate)

    # 3. PostToolUse debug logs (contém histórico de chamadas run_subagent)
    log_candidates = [
        home / ".config" / "JetBrains" / "context-mode" / "posttooluse-debug.log",
        home / "AppData" / "Roaming" / "JetBrains" / "context-mode" / "posttooluse-debug.log",
        home / ".claude" / "context-mode" / "posttooluse-debug.log",
    ]
    debug_logs = [p for p in log_candidates if p.exists() and "node_modules" not in str(p)]

    return sessions_dirs, content_dirs, debug_logs




def detect_agent_in_text(text: str, known_agents: Any) -> Optional[str]:
    """Detecta menção a um agente conhecido do catálogo no texto do evento."""
    if not text or not known_agents:
        return None
    text_l = text.lower()
    for ag in known_agents:
        ag_l = ag.lower()
        if f"@{ag_l}" in text_l or f'"{ag_l}"' in text_l or f"'{ag_l}'" in text_l or f"subagent_type={ag_l}" in text_l or f"agent_name={ag_l}" in text_l or f" {ag_l} " in f" {text_l} ":
            return ag
    return None


def _epoch_to_iso(val: Any) -> str:
    """Converte epoch ms, epoch s ou string ISO em ISO-8601 UTC."""
    if val is None or val == "":
        return ""
    if isinstance(val, (int, float)):
        ts = float(val)
        if ts > 1e11:
            ts = ts / 1000.0
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception:
            return str(val)
    s = str(val).strip()
    if s.isdigit():
        ts = float(s)
        if ts > 1e11:
            ts = ts / 1000.0
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception:
            return s
    return s


def _is_doctor_synthetic(session_id: Optional[str], worktree: Optional[str] = None, body: Optional[str] = None) -> bool:
    """Detecta sessões/eventos sintéticos gerados pelo 'context-mode doctor'."""
    sid = (session_id or "").strip()
    wt = (worktree or "").strip()
    bd = (body or "").strip()
    if sid == "context-mode-doctor-hook-runs" or sid.startswith("context-mode-doctor"):
        return True
    if "cm-doctor-runs-" in wt:
        return True
    if bd.startswith("context-mode doctor sample line"):
        return True
    return False


def discover_v2_databases(
    custom_data_dir: Optional[str] = None,
    custom_sessions_dir: Optional[str] = None,
    custom_content_dir: Optional[str] = None,
) -> Tuple[List[Path], List[Path]]:
    """
    Descobre bancos SQLite do context-mode v2.1.10 (<root>/projects/<key>/context.db).
    Retorna (data_roots, db_files).
    Precedência:
      1. custom_data_dir (--data-dir)
      2. env CONTEXT_MODE_DATA_DIR
      3. custom_sessions_dir / custom_content_dir (se contiverem projects/*/context.db ou context.db)
      4. Default roots: ~/.config/JetBrains/context-mode, ~/.context-mode, ~/.claude/context-mode
    Ignora backups/, v1-aside-*, node_modules e .cache.
    """
    candidate_roots: List[Path] = []
    env_dir = os.environ.get("CONTEXT_MODE_DATA_DIR", "").strip()

    if custom_data_dir:
        candidate_roots.append(Path(custom_data_dir).expanduser())
    elif env_dir:
        candidate_roots.append(Path(env_dir).expanduser())
    elif custom_sessions_dir or custom_content_dir:
        for c in (custom_sessions_dir, custom_content_dir):
            if c:
                candidate_roots.append(Path(c).expanduser())
    else:
        home = Path.home()
        default_candidates = [
            home / ".config" / "JetBrains" / "context-mode",
            home / ".context-mode",
            home / ".claude" / "context-mode",
        ]
        for env_var in ("APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME"):
            val = os.environ.get(env_var)
            if val:
                default_candidates.append(Path(val) / "JetBrains" / "context-mode")
                default_candidates.append(Path(val) / "context-mode")
        for cand in default_candidates:
            if cand.exists() and cand not in candidate_roots:
                candidate_roots.append(cand)

    active_roots: List[Path] = []
    db_files: List[Path] = []

    def _is_excluded(p: Path) -> bool:
        parts_lower = [part.lower() for part in p.parts]
        for bad in ("backups", "node_modules", ".cache", ".git"):
            if bad in parts_lower:
                return True
        if any(part.startswith("v1-aside") for part in parts_lower):
            return True
        return False

    for root in candidate_roots:
        if not root.exists():
            continue
        found_in_root = False
        if root.is_file() and root.name.endswith(".db") and not _is_excluded(root):
            db_files.append(root)
            active_roots.append(root.parent)
            continue

        direct_db = root / "context.db"
        if direct_db.is_file() and not _is_excluded(direct_db) and direct_db not in db_files:
            db_files.append(direct_db)
            found_in_root = True

        projects_dir = root / "projects"
        if projects_dir.is_dir() and not _is_excluded(projects_dir):
            for db_path in sorted(projects_dir.glob("*/context.db")):
                if db_path.is_file() and not _is_excluded(db_path) and db_path not in db_files:
                    db_files.append(db_path)
                    found_in_root = True

        if found_in_root and root not in active_roots:
            active_roots.append(root)

    return active_roots, db_files


class ContextDataExtractor:
    """Extrator unificado de telemetria e armazenamento local do Context Mode (v2.1.10 + fallback v1)."""

    def __init__(
        self,
        sessions_dir: Optional[str] = None,
        content_dir: Optional[str] = None,
        data_dir: Optional[str] = None,
        legacy_v1: bool = False,
    ):
        self.custom_data_dir = data_dir
        self.custom_sessions_dir = sessions_dir
        self.custom_content_dir = content_dir
        self.legacy_v1 = legacy_v1
        self.warnings: List[str] = []

        self.v2_roots, self.v2_db_files = ([], [])
        if not self.legacy_v1:
            self.v2_roots, self.v2_db_files = discover_v2_databases(
                custom_data_dir=data_dir,
                custom_sessions_dir=sessions_dir,
                custom_content_dir=content_dir,
            )

        self.sessions_dirs, self.content_dirs, self.debug_logs = resolve_default_directories(
            sessions_dir, content_dir
        )

        # Se v2 encontrou bancos (ou se data_dir/CONTEXT_MODE_DATA_DIR foi passado sem legacy_v1)
        self.use_v2 = (not self.legacy_v1) and (
            len(self.v2_db_files) > 0
            or bool(data_dir)
            or bool(os.environ.get("CONTEXT_MODE_DATA_DIR", "").strip())
        )

        if self.use_v2:
            self.source_paths: List[str] = [str(p) for p in self.v2_roots + self.v2_db_files + self.debug_logs]
        else:
            self.source_paths = [str(p) for p in self.sessions_dirs + self.content_dirs + self.debug_logs]

    def extract_all(self) -> Dict[str, Any]:
        """Executa a extração completa (v2.1.10 unificado em projects/*/context.db ou legado v1)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        otel_data = self._read_otel_spans()

        if self.use_v2:
            v2_events_data, stats_pid_data, schema_version, doctor_filtered = self._read_events_and_cost_v2()
            content_dbs_data = self._read_content_v2()
            if otel_data["spansCount"] == 0:
                self.warnings.append("Nenhum span OTel nativo encontrado (fallback: telemetria SQLite v2 em uso).")
            if not self.v2_db_files:
                self.warnings.append("Nenhum banco projects/<key>/context.db do Context Mode v2 localizado.")
            project_keys = [db.parent.name for db in self.v2_db_files]
            return {
                "meta": {
                    "generatedAt": now_iso,
                    "contextModeVersion": "2.1.10",
                    "schemaVersion": schema_version,
                    "dataRoots": [str(r) for r in self.v2_roots],
                    "projectKeys": project_keys,
                    "doctorEventsFiltered": doctor_filtered,
                    "sourcePaths": self.source_paths,
                    "warnings": self.warnings,
                    "statsPidCount": stats_pid_data.get("filesCount", 0),
                    "sessionDbsCount": v2_events_data.get("dbsCount", 0),
                    "contentDbsCount": content_dbs_data.get("dbsCount", 0),
                },
                "sessions": v2_events_data.get("sessions", []),
                "eventsSummary": v2_events_data.get("eventsSummary", {}),
                "statsPid": stats_pid_data,
                "content": content_dbs_data,
                "otelSpans": otel_data,
            }

        session_dbs_data = self._read_session_databases()
        stats_pid_data = self._read_stats_pid_files()
        content_dbs_data = self._read_content_databases()
        if otel_data["spansCount"] == 0:
            self.warnings.append("Nenhum span OTel nativo encontrado (fallback: heurística de regex em uso).")
        if not self.sessions_dirs:
            self.warnings.append("Nenhum diretório de sessões do Context Mode localizado na máquina.")
        if not self.content_dirs:
            self.warnings.append("Nenhum diretório de conteúdo do Context Mode localizado na máquina.")
        return {
            "meta": {
                "generatedAt": now_iso,
                "contextModeVersion": "legacy",
                "schemaVersion": 1,
                "dataRoots": [str(p) for p in self.sessions_dirs],
                "projectKeys": [],
                "doctorEventsFiltered": 0,
                "sourcePaths": self.source_paths,
                "warnings": self.warnings,
                "statsPidCount": stats_pid_data.get("filesCount", 0),
                "sessionDbsCount": session_dbs_data.get("dbsCount", 0),
                "contentDbsCount": content_dbs_data.get("dbsCount", 0),
            },
            "sessions": session_dbs_data.get("sessions", []),
            "eventsSummary": session_dbs_data.get("eventsSummary", {}),
            "statsPid": stats_pid_data,
            "content": content_dbs_data,
            "otelSpans": otel_data,
        }

    def _read_events_and_cost_v2(self) -> Tuple[Dict[str, Any], Dict[str, Any], int, int]:
        """Lê eventos, sessões e métricas de custo/economia dos bancos context.db v2.1.10."""
        all_sessions: List[Dict[str, Any]] = []
        seen_session_ids = set()
        total_events_count = 0
        total_errors_count = 0
        total_prompts_count = 0
        total_reads_count = 0
        total_writes_count = 0
        hourly_counts: Dict[int, int] = {h: 0 for h in range(24)}
        date_sessions_map: Dict[str, Dict[str, int]] = {}
        tool_counts: Dict[str, int] = {}
        mcp_tool_counts: Dict[str, Dict[str, int]] = {}
        project_agg: Dict[str, Dict[str, Any]] = {}
        subagent_events: List[Dict[str, Any]] = []
        decisions_list: List[Dict[str, Any]] = []
        detailed_events: List[Dict[str, Any]] = []
        all_events_for_correlation: List[Tuple[datetime, str, str]] = []
        session_proj_map: Dict[str, str] = {}
        agent_stats: Dict[str, Dict[str, int]] = {}
        known_agents = load_known_agents()

        total_sandbox_bytes = 0
        total_returned_bytes = 0
        total_cost_calls = 0
        by_tool_cost: Dict[str, Dict[str, int]] = {}
        schema_version = 6
        doctor_filtered = 0

        read_tools = {"read", "read_file", "grep", "grep_search", "glob", "file_search", "list_dir", "ctx_search", "ctx_index", "ctx_fetch_and_index", "view"}
        write_tools = {"edit", "write", "create_file", "replace_string_in_file", "insert_edit_into_file", "multi_edit"}

        for db_file in self.v2_db_files:
            try:
                conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                cur = conn.cursor()
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

                if "meta" in tables:
                    try:
                        row = cur.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                        if row and str(row[0]).isdigit():
                            schema_version = max(schema_version, int(row[0]))
                    except Exception:
                        pass

                if "events" not in tables:
                    conn.close()
                    continue

                rows = cur.execute(
                    "SELECT seq, session_id, worktree, agent, kind, tool, key, path, ok, exit_code, "
                    "bytes, body, turn, sandbox_bytes, returned_bytes, created_at "
                    "FROM events ORDER BY created_at ASC, seq ASC"
                ).fetchall()

                # Agrupamento de sessões neste DB
                db_sessions: Dict[str, Dict[str, Any]] = {}

                for (
                    seq, s_id, worktree, agent_col, kind, tool, key_col, path_col,
                    ok, exit_code, ev_bytes, body, turn, sb_bytes, ret_bytes, created_at
                ) in rows:
                    if _is_doctor_synthetic(s_id, worktree, body):
                        doctor_filtered += 1
                        continue

                    s_id = s_id or f"unknown-{db_file.parent.name}"
                    worktree = worktree or str(db_file.parent)
                    proj_name = sanitize_project_name(worktree)
                    session_proj_map[s_id] = proj_name
                    iso_ts = _epoch_to_iso(created_at)
                    kind_l = (kind or "").lower()
                    tool_str = (tool or key_col or kind or "unknown").strip()
                    tool_l = tool_str.lower()
                    sb_b = int(sb_bytes or 0)
                    ret_b = int(ret_bytes or 0)
                    ev_b = int(ev_bytes or 0)

                    # Métricas de economia / cost
                    if kind_l == "cost" or sb_b > 0 or ret_b > 0:
                        eff_sb = sb_b if sb_b > 0 else ev_b
                        eff_ret = ret_b
                        total_sandbox_bytes += eff_sb
                        total_returned_bytes += eff_ret
                        total_cost_calls += 1
                        t_key = tool_str if tool_str and tool_str != "cost" else "ctx_execute"
                        if t_key not in by_tool_cost:
                            by_tool_cost[t_key] = {"calls": 0, "bytesReturned": 0, "sandboxBytes": 0}
                        by_tool_cost[t_key]["calls"] += 1
                        by_tool_cost[t_key]["bytesReturned"] += eff_ret
                        by_tool_cost[t_key]["sandboxBytes"] += eff_sb

                    # Sessão
                    if s_id not in db_sessions:
                        db_sessions[s_id] = {
                            "sessionId": s_id,
                            "projectDir": worktree,
                            "projectName": proj_name,
                            "startedAt": iso_ts,
                            "lastEventAt": iso_ts,
                            "minMs": created_at if isinstance(created_at, (int, float)) else 0,
                            "maxMs": created_at if isinstance(created_at, (int, float)) else 0,
                            "eventCount": 0,
                            "compactCount": 0,
                        }
                    sess = db_sessions[s_id]
                    sess["eventCount"] += 1
                    sess["lastEventAt"] = iso_ts
                    if isinstance(created_at, (int, float)):
                        if sess["minMs"] == 0 or created_at < sess["minMs"]:
                            sess["minMs"] = created_at
                            sess["startedAt"] = iso_ts
                        if created_at > sess["maxMs"]:
                            sess["maxMs"] = created_at
                            sess["lastEventAt"] = iso_ts

                    total_events_count += 1

                    # Contadores de erro, prompt, leitura e escrita
                    is_err = (ok == 0) or (kind_l == "toolerr") or (exit_code is not None and int(exit_code) != 0)
                    if is_err:
                        total_errors_count += 1

                    if kind_l == "prompt":
                        total_prompts_count += 1
                    elif kind_l == "edit" or tool_l in write_tools:
                        total_writes_count += 1
                    elif kind_l == "file" or tool_l in read_tools:
                        total_reads_count += 1
                    elif kind_l == "cmd":
                        total_reads_count += 1

                    # Horário e data
                    dt_obj = None
                    if iso_ts:
                        try:
                            dt_obj = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
                            hourly_counts[dt_obj.hour] = hourly_counts.get(dt_obj.hour, 0) + 1
                            d_str = dt_obj.strftime("%Y-%m-%d")
                            if d_str not in date_sessions_map:
                                date_sessions_map[d_str] = {"sessions": 0, "events": 0, "compacts": 0, "_sids": set()}
                            date_sessions_map[d_str]["events"] += 1
                            date_sessions_map[d_str]["_sids"].add(s_id)
                        except Exception:
                            pass

                    # Projeto
                    if proj_name not in project_agg:
                        project_agg[proj_name] = {"name": proj_name, "sessions": 0, "events": 0, "compacts": 0, "errors": 0, "_sids": set()}
                    project_agg[proj_name]["events"] += 1
                    project_agg[proj_name]["_sids"].add(s_id)
                    if is_err:
                        project_agg[proj_name]["errors"] += 1

                    # Ferramentas
                    if kind_l not in ("prompt", "cost"):
                        t_label = (tool or kind or "unknown").strip()
                        tool_counts[t_label] = tool_counts.get(t_label, 0) + 1
                        is_mcp = t_label.startswith("ctx_") or t_label.startswith("mcp_") or t_label in ("execute", "batch_execute", "search", "index", "fetch_and_index", "stats", "doctor")
                        if is_mcp:
                            srv = "context-mode"
                            m_key = f"{srv}:{t_label}"
                            if m_key not in mcp_tool_counts:
                                mcp_tool_counts[m_key] = {"server": srv, "tool": t_label, "count": 0, "errors": 0}
                            mcp_tool_counts[m_key]["count"] += 1
                            if is_err:
                                mcp_tool_counts[m_key]["errors"] += 1

                    # Decisões
                    if kind_l == "decision" and body:
                        decisions_list.append({
                            "sessionId": s_id,
                            "projectName": proj_name,
                            "timestamp": iso_ts,
                            "type": tool or "decision",
                            "text": str(body)[:500],
                        })

                    # Agentes e Subagentes (detecção em body/key/agent)
                    combined_text = f"{agent_col or ''} {tool or ''} {key_col or ''} {body or ''}"
                    matched_agent = detect_agent_in_text(combined_text, known_agents)
                    is_sub = "subagent" in tool_l or "run_subagent" in tool_l or kind_l == "subagent" or "[handoff]" in combined_text.lower()
                    if matched_agent:
                        if matched_agent not in agent_stats:
                            agent_stats[matched_agent] = {"direct": 0, "subagent": 0, "total": 0}
                        if is_sub:
                            agent_stats[matched_agent]["subagent"] += 1
                        else:
                            agent_stats[matched_agent]["direct"] += 1
                        agent_stats[matched_agent]["total"] += 1

                    if is_sub and dt_obj:
                        subagent_events.append({
                            "sessionId": s_id,
                            "project": proj_name,
                            "createdAt": iso_ts,
                            "timestamp": dt_obj,
                            "agent": matched_agent or agent_col or "subagent",
                            "rawData": str(body or key_col or "")[:200],
                        })

                    if dt_obj:
                        all_events_for_correlation.append((dt_obj, s_id, combined_text[:200]))

                    if len(detailed_events) < 400:
                        detailed_events.append({
                            "sessionId": s_id,
                            "projectName": proj_name,
                            "timestamp": iso_ts,
                            "type": kind or "event",
                            "category": tool or kind or "general",
                            "priority": 2 if is_err else 1,
                            "data": str(body or path_col or key_col or "")[:240],
                        })

                for s_id, s_info in db_sessions.items():
                    if s_id in seen_session_ids:
                        continue
                    seen_session_ids.add(s_id)
                    dur_min = 0.0
                    if s_info["maxMs"] > s_info["minMs"] > 0:
                        diff_ms = s_info["maxMs"] - s_info["minMs"]
                        if s_info["maxMs"] < 1e11:  # caso timestamp estivesse em segundos
                            dur_min = round(diff_ms / 60.0, 1)
                        else:
                            dur_min = round(diff_ms / 60000.0, 1)
                    all_sessions.append({
                        "sessionId": s_info["sessionId"],
                        "projectDir": s_info["projectDir"],
                        "projectName": s_info["projectName"],
                        "startedAt": s_info["startedAt"],
                        "lastEventAt": s_info["lastEventAt"],
                        "durationMin": dur_min,
                        "eventCount": s_info["eventCount"],
                        "compactCount": 0,
                    })

                conn.close()
            except Exception as exc:
                self.warnings.append(f"Falha ao ler banco v2 {db_file.name}: {exc}")

        # Incorpora logs de subagent JSONL e debug logs (mesma lógica do v1)
        self._enrich_agents_from_jsonl_and_logs(
            known_agents, agent_stats, subagent_events, all_events_for_correlation, session_proj_map
        )

        # Formata séries
        sessions_by_date = []
        for d_str in sorted(date_sessions_map.keys()):
            entry = date_sessions_map[d_str]
            sessions_by_date.append({
                "date": d_str,
                "sessions": len(entry["_sids"]),
                "events": entry["events"],
                "compacts": entry["compacts"],
            })

        projects_list = []
        for p_name, p_info in project_agg.items():
            projects_list.append({
                "name": p_name,
                "sessions": len(p_info["_sids"]),
                "events": p_info["events"],
                "compacts": p_info["compacts"],
                "errors": p_info["errors"],
            })
        projects_list.sort(key=lambda x: x["events"], reverse=True)

        total_tools_sum = sum(tool_counts.values()) or 1
        tool_usage_list = [
            {"tool": k, "count": v, "percentage": round((v / total_tools_sum) * 100, 1)}
            for k, v in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        mcp_tools_list = sorted(mcp_tool_counts.values(), key=lambda x: x["count"], reverse=True)
        subagent_analysis = self._analyze_subagent_bursts(subagent_events)

        total_agent_inv = sum(v["total"] for v in agent_stats.values()) or 1
        agent_invocations_list = [
            {
                "agent": ag,
                "direct": st["direct"],
                "subagent": st["subagent"],
                "total": st["total"],
                "percentage": round((st["total"] / total_agent_inv) * 100, 1),
            }
            for ag, st in sorted(agent_stats.items(), key=lambda x: x[1]["total"], reverse=True)
        ]

        all_sessions.sort(key=lambda x: x.get("startedAt") or "", reverse=True)
        decisions_list.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
        detailed_events.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

        bytes_saved = max(0, total_sandbox_bytes - total_returned_bytes)
        tokens_saved = int(round(bytes_saved / 4.0))
        dollars_saved = round((tokens_saved / 1_000_000.0) * 3.0, 2)

        stats_pid_data = {
            "filesCount": len(self.v2_db_files),
            "totalCalls": total_cost_calls,
            "bytesReturned": total_returned_bytes,
            "sandboxBytes": total_sandbox_bytes,
            "bytesSaved": bytes_saved,
            "tokensSavedLifetime": tokens_saved,
            "dollarsSavedLifetime": dollars_saved,
            "byTool": by_tool_cost,
        }

        events_data = {
            "dbsCount": len(self.v2_db_files),
            "sessions": all_sessions,
            "eventsSummary": {
                "totalEvents": total_events_count,
                "totalErrors": total_errors_count,
                "totalPrompts": total_prompts_count,
                "totalReads": total_reads_count,
                "totalWrites": total_writes_count,
                "hourlyPattern": [{"hour": h, "count": hourly_counts[h]} for h in range(24)],
                "sessionsByDate": sessions_by_date,
                "toolUsage": tool_usage_list,
                "mcpTools": mcp_tools_list,
                "projects": projects_list,
                "subagents": subagent_analysis,
                "agentInvocations": agent_invocations_list,
                "decisions": decisions_list[:200],
                "detailedEvents": detailed_events[:250],
            },
        }
        return events_data, stats_pid_data, schema_version, doctor_filtered

    def _enrich_agents_from_jsonl_and_logs(
        self,
        known_agents: List[str],
        agent_stats: Dict[str, Dict[str, int]],
        subagent_events: List[Dict[str, Any]],
        all_events_for_correlation: List[Tuple[datetime, str, str]],
        session_proj_map: Dict[str, str],
    ) -> None:
        """Lê logs/subagent-telemetry.jsonl do repositório para enriquecer subagentes em modo v2."""
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        jsonl_candidates = [
            repo_root / "tools" / "context-insight-visualizer" / "logs" / "subagent-telemetry.jsonl",
        ]
        for jf in jsonl_candidates:
            if not jf.is_file():
                continue
            try:
                for line in jf.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    ag = rec.get("subagent_type") or rec.get("agent") or detect_agent_in_text(json.dumps(rec), known_agents)
                    if ag:
                        ag_clean = ag.lstrip("@").strip()
                        if ag_clean not in agent_stats:
                            agent_stats[ag_clean] = {"direct": 0, "subagent": 0, "total": 0}
                        agent_stats[ag_clean]["subagent"] += 1
                        agent_stats[ag_clean]["total"] += 1
            except Exception:
                pass

    def _read_content_v2(self) -> Dict[str, Any]:
        """Lê sources e chunks (FTS5) dos bancos context.db v2.1.10 com degradação graciosa."""
        total_sources = 0
        total_chunks = 0
        total_size_bytes = 0
        sources_list: List[Dict[str, Any]] = []
        chunks_by_source: Dict[Any, List[Dict[str, Any]]] = {}

        for db_file in self.v2_db_files:
            proj_key = db_file.parent.name
            try:
                conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                cur = conn.cursor()
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

                if "sources" in tables:
                    try:
                        s_rows = cur.execute(
                            "SELECT id, label, kind, chunk_count, bytes_total, created_at "
                            "FROM sources ORDER BY created_at DESC LIMIT 250"
                        ).fetchall()
                        for sid, slabel, skind, c_cnt, b_tot, c_at in s_rows:
                            # Ignora fontes sintéticas do doctor
                            if "context-mode-doctor" in str(slabel or "") or "cm-doctor-runs-" in str(slabel or ""):
                                continue
                            total_sources += 1
                            c_cnt_int = int(c_cnt or 0)
                            b_tot_int = int(b_tot or 0)
                            total_chunks += c_cnt_int
                            total_size_bytes += b_tot_int
                            composite_id = f"{proj_key}:{sid}" if len(self.v2_db_files) > 1 else sid
                            sanitized_label = str(slabel or "").replace("\\", "/")
                            sources_list.append({
                                "id": composite_id,
                                "rawId": sid,
                                "dbHash": proj_key,
                                "label": sanitized_label,
                                "kind": skind or "text",
                                "chunkCount": c_cnt_int,
                                "codeChunkCount": c_cnt_int if (skind or "") == "file" else 0,
                                "bytesTotal": b_tot_int,
                                "indexedAt": _epoch_to_iso(c_at),
                                "filePath": sanitized_label,
                            })
                    except Exception as exc:
                        self.warnings.append(f"Falha ao ler tabela sources em {proj_key}: {exc}")

                if "chunks" in tables:
                    try:
                        c_rows = cur.execute(
                            "SELECT source_id, title, length(body), substr(body, 1, 280) "
                            "FROM chunks LIMIT 800"
                        ).fetchall()
                        for src_id, title, body_len, preview in c_rows:
                            if preview and "context-mode doctor sample line" in str(preview):
                                continue
                            composite_id = f"{proj_key}:{src_id}" if len(self.v2_db_files) > 1 else src_id
                            if composite_id not in chunks_by_source:
                                chunks_by_source[composite_id] = []
                            if len(chunks_by_source[composite_id]) < 25:
                                chunks_by_source[composite_id].append({
                                    "title": title or "Chunk",
                                    "contentType": "markdown",
                                    "sizeBytes": int(body_len or 0),
                                    "preview": (preview or "").strip(),
                                })
                    except Exception as exc:
                        self.warnings.append(f"FTS5/chunks indisponível em {proj_key} (degradação graciosa): {exc}")

                conn.close()
            except Exception as exc:
                self.warnings.append(f"Falha ao ler conteúdo v2 em {db_file.name}: {exc}")

        return {
            "dbsCount": len(self.v2_db_files),
            "totalSources": total_sources,
            "totalChunks": total_chunks,
            "totalSizeBytes": total_size_bytes,
            "sources": sources_list,
            "chunksBySource": chunks_by_source,
        }

    def _read_session_databases(self) -> Dict[str, Any]:
        """Lê todos os arquivos *.db dentro dos diretórios de sessões (ignorando node_modules e caches)."""
        if not self.sessions_dirs:
            return {"dbsCount": 0, "sessions": [], "eventsSummary": {}}

        db_files: List[Path] = []
        for s_dir in self.sessions_dirs:
            if s_dir.exists():
                for p in s_dir.glob("*.db"):
                    if "node_modules" not in str(p) and ".cache" not in str(p) and p not in db_files:
                        db_files.append(p)

        all_sessions: List[Dict[str, Any]] = []
        seen_session_ids = set()

        total_events_count = 0
        total_errors_count = 0
        total_prompts_count = 0
        total_reads_count = 0
        total_writes_count = 0
        hourly_counts: Dict[int, int] = {h: 0 for h in range(24)}
        date_sessions_map: Dict[str, Dict[str, int]] = {}
        tool_counts: Dict[str, int] = {}
        mcp_tool_counts: Dict[str, Dict[str, int]] = {}
        project_agg: Dict[str, Dict[str, Any]] = {}
        subagent_events: List[Dict[str, Any]] = []
        decisions_list: List[Dict[str, Any]] = []
        detailed_events: List[Dict[str, Any]] = []
        all_events_for_correlation: List[Tuple[datetime, str, str]] = []
        session_proj_map: Dict[str, str] = {}
        agent_stats: Dict[str, Dict[str, int]] = {}
        known_agents = load_known_agents()

        for db_file in db_files:
            try:
                conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                cur = conn.cursor()

                # 1. Verifica tabelas existentes
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

                # 2. Leitura de session_meta
                if "session_meta" in tables:
                    cols = [c[1] for c in cur.execute("PRAGMA table_info(session_meta)").fetchall()]
                    select_cols = ["session_id", "project_dir", "started_at", "last_event_at", "event_count", "compact_count"]
                    avail_cols = [c for c in select_cols if c in cols]
                    
                    query = f"SELECT {', '.join(avail_cols)} FROM session_meta ORDER BY started_at DESC"
                    rows = cur.execute(query).fetchall()

                    for r in rows:
                        row_dict = dict(zip(avail_cols, r))
                        s_id = row_dict.get("session_id", "unknown")
                        if s_id in seen_session_ids:
                            continue
                        seen_session_ids.add(s_id)
                        p_dir = row_dict.get("project_dir") or "__unknown__"
                        session_proj_map[s_id] = p_dir
                        started = row_dict.get("started_at")
                        last_ev = row_dict.get("last_event_at")
                        ev_cnt = row_dict.get("event_count") or 0
                        cp_cnt = row_dict.get("compact_count") or 0

                        # Duração em minutos
                        duration_min = 0.0
                        if started and last_ev:
                            try:
                                dt1 = datetime.fromisoformat(started)
                                dt2 = datetime.fromisoformat(last_ev)
                                duration_min = max(round((dt2 - dt1).total_seconds() / 60.0, 1), 0.0)
                            except Exception:
                                duration_min = 0.0

                        proj_name = sanitize_project_name(p_dir)

                        session_entry = {
                            "sessionId": s_id,
                            "projectDir": p_dir,
                            "projectName": proj_name,
                            "startedAt": started,
                            "lastEventAt": last_ev,
                            "durationMin": duration_min,
                            "eventCount": ev_cnt,
                            "compactCount": cp_cnt,
                        }
                        all_sessions.append(session_entry)

                        # Agrega por data
                        if started:
                            dt_key = started.split("T")[0] if "T" in started else started.split(" ")[0]
                            if dt_key not in date_sessions_map:
                                date_sessions_map[dt_key] = {"date": dt_key, "count": 0, "events": 0, "compacts": 0}
                            date_sessions_map[dt_key]["count"] += 1
                            date_sessions_map[dt_key]["events"] += ev_cnt
                            date_sessions_map[dt_key]["compacts"] += cp_cnt

                        # Agrega por projeto
                        if p_dir not in project_agg:
                            project_agg[p_dir] = {
                                "projectDir": p_dir,
                                "projectName": proj_name,
                                "sessions": 0,
                                "events": 0,
                                "compacts": 0,
                            }
                        project_agg[p_dir]["sessions"] += 1
                        project_agg[p_dir]["events"] += ev_cnt
                        project_agg[p_dir]["compacts"] += cp_cnt

                # 3. Leitura de session_events
                if "session_events" in tables:
                    event_cols = [c[1] for c in cur.execute("PRAGMA table_info(session_events)").fetchall()]
                    q_events = "SELECT id, type, category, priority, data, created_at, session_id FROM session_events ORDER BY id DESC"
                    for ev_id, ev_type, ev_cat, ev_prio, ev_data, ev_created, ev_sid in cur.execute(q_events).fetchall():
                        total_events_count += 1

                        # Decisões de arquitetura/técnicas
                        if ev_type == "decision":
                            decisions_list.append({
                                "id": ev_id,
                                "sessionId": ev_sid,
                                "text": str(ev_data or "").strip(),
                                "createdAt": ev_created or "",
                                "projectName": sanitize_project_name(session_proj_map.get(ev_sid, ""))
                            })

                        # Eventos detalhados recentes (para timeline e busca)
                        if len(detailed_events) < 500:
                            detailed_events.append({
                                "id": ev_id,
                                "sessionId": ev_sid,
                                "type": ev_type or "unknown",
                                "priority": ev_prio or 1,
                                "data": str(ev_data or "")[:200],
                                "createdAt": ev_created or ""
                            })

                        # Contagem horária (00..23) e buffer para correlação
                        if ev_created:
                            try:
                                h_int = int(ev_created[11:13]) if len(ev_created) >= 13 else None
                                if h_int is not None and 0 <= h_int <= 23:
                                    hourly_counts[h_int] = hourly_counts.get(h_int, 0) + 1
                                dt_corr = datetime.fromisoformat(ev_created.replace(" ", "T").rstrip("Z"))
                                all_events_for_correlation.append((dt_corr, ev_type or "", str(ev_data or "")))
                            except Exception:
                                pass

                        # Categorização de ferramenta / tipo
                        if ev_type in ("file_read", "read_file"):
                            total_reads_count += 1
                            tool_counts["Read"] = tool_counts.get("Read", 0) + 1
                        elif ev_type in ("file_write", "write_file", "file_edit", "edit_file"):
                            total_writes_count += 1
                            tool_counts["Write"] = tool_counts.get("Write", 0) + 1
                        elif ev_type in ("file_search", "grep_search"):
                            tool_counts["Search"] = tool_counts.get("Search", 0) + 1
                        elif ev_type in ("file_glob", "find_files"):
                            tool_counts["Glob"] = tool_counts.get("Glob", 0) + 1
                        elif ev_type in ("error_tool", "error"):
                            total_errors_count += 1
                            tool_counts["Error"] = tool_counts.get("Error", 0) + 1
                        elif ev_type == "user_prompt":
                            total_prompts_count += 1
                        elif ev_type == "subagent":
                            tool_counts["Subagent"] = tool_counts.get("Subagent", 0) + 1
                            subagent_events.append({"task": ev_data, "createdAt": ev_created, "sessionId": ev_sid})
                        elif ev_type in ("mcp", "mcp_tool_call", "sandbox-execute"):
                            tool_counts["context-mode"] = tool_counts.get("context-mode", 0) + 1
                            # Identifica o método específico do context-mode
                            d_str = str(ev_data or "")
                            mcp_name = "other"
                            for prefix in ["batch_execute", "execute_file", "execute", "search", "index", "fetch_and_index", "fetch", "stats", "doctor", "purge"]:
                                if prefix in d_str:
                                    mcp_name = f"ctx_{prefix}" if not prefix.startswith("ctx_") else prefix
                                    break
                            if mcp_name not in mcp_tool_counts:
                                mcp_tool_counts[mcp_name] = {"tool": mcp_name, "count": 0, "bytes": 0}
                            mcp_tool_counts[mcp_name]["count"] += 1
                        else:
                            norm_type = ev_type or "other"
                            tool_counts[norm_type] = tool_counts.get(norm_type, 0) + 1

                        # Rastreamento de Invocação de Agentes e Subagentes
                        d_str = str(ev_data or "")
                        seen_sub_in_event = set()
                        if ev_type == "subagent" or ev_cat == "subagent":
                            found_sub = False
                            for sp in SUBAGENT_PATTERNS:
                                for m in sp.finditer(d_str):
                                    ag = m.group(1).lower()
                                    if ag in known_agents:
                                        if ag not in agent_stats:
                                            agent_stats[ag] = {"direct": 0, "subagent": 0, "total": 0}
                                        agent_stats[ag]["subagent"] += 1
                                        seen_sub_in_event.add(ag)
                                        found_sub = True
                            if not found_sub:
                                try:
                                    j = json.loads(d_str)
                                    ag = (j.get("agent") or j.get("agentName") or j.get("name") or "").lower()
                                    if ag in known_agents:
                                        if ag not in agent_stats:
                                            agent_stats[ag] = {"direct": 0, "subagent": 0, "total": 0}
                                        agent_stats[ag]["subagent"] += 1
                                        seen_sub_in_event.add(ag)
                                        found_sub = True
                                except Exception:
                                    pass
                            if not found_sub:
                                for ag in known_agents:
                                    if ag in d_str.lower():
                                        if ag not in agent_stats:
                                            agent_stats[ag] = {"direct": 0, "subagent": 0, "total": 0}
                                        agent_stats[ag]["subagent"] += 1
                                        seen_sub_in_event.add(ag)
                                        break
                        else:
                            for sp in SUBAGENT_PATTERNS:
                                for m in sp.finditer(d_str):
                                    ag = m.group(1).lower()
                                    if ag in known_agents and ag not in seen_sub_in_event:
                                        if ag not in agent_stats:
                                            agent_stats[ag] = {"direct": 0, "subagent": 0, "total": 0}
                                        agent_stats[ag]["subagent"] += 1
                                        seen_sub_in_event.add(ag)

                        # Invocações diretas de agentes (prompts, roles, decisões, intenções)
                        if ev_type in ("user_prompt", "role", "decision", "intent"):
                            seen_dir_in_event = set()
                            for dp in DIRECT_PATTERNS:
                                for m in dp.finditer(d_str):
                                    ag = m.group(1).lower()
                                    if ag in known_agents and ag not in seen_sub_in_event and ag not in seen_dir_in_event:
                                        if ag not in agent_stats:
                                            agent_stats[ag] = {"direct": 0, "subagent": 0, "total": 0}
                                        agent_stats[ag]["direct"] += 1
                                        seen_dir_in_event.add(ag)

                # 4. Leitura da tabela tool_calls (se existir)
                if "tool_calls" in tables:
                    tc_cols = [c[1] for c in cur.execute("PRAGMA table_info(tool_calls)").fetchall()]
                    if "tool" in tc_cols and "calls" in tc_cols:
                        b_col = "bytes_returned" if "bytes_returned" in tc_cols else "0"
                        for t_name, c_cnt, b_cnt in cur.execute(f"SELECT tool, SUM(calls), SUM({b_col}) FROM tool_calls GROUP BY tool").fetchall():
                            if t_name not in mcp_tool_counts:
                                mcp_tool_counts[t_name] = {"tool": t_name, "count": 0, "bytes": 0}
                            mcp_tool_counts[t_name]["count"] += (c_cnt or 0)
                            mcp_tool_counts[t_name]["bytes"] += (b_cnt or 0)

                conn.close()

            except Exception as ex:
                self.warnings.append(f"Erro ao processar banco SQLite {db_file.name}: {str(ex)}")

        # 5. Processamento da telemetria declarativa nativa de subagentes (JSONL)
        telemetry_jsonl_candidates = [
            Path(__file__).resolve().parent.parent / "logs" / "subagent-telemetry.jsonl",
            Path.cwd() / "tools" / "context-insight-visualizer" / "logs" / "subagent-telemetry.jsonl",
            Path.home() / ".context-mode" / "subagent-telemetry.jsonl",
        ]
        seen_telemetry_timestamps = set()
        for jf in telemetry_jsonl_candidates:
            if jf.exists():
                try:
                    with open(jf, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            l_str = line.strip()
                            if not l_str:
                                continue
                            try:
                                entry = json.loads(l_str)
                                ag = (entry.get("agent") or "search").lower().strip()
                                ts = entry.get("timestamp") or ""
                                seen_telemetry_timestamps.add(ts[:19])
                                if ag in known_agents or True:
                                    if ag not in agent_stats:
                                        agent_stats[ag] = {"direct": 0, "subagent": 0, "total": 0}
                                    agent_stats[ag]["subagent"] += 1
                                    tool_counts["Subagent"] = tool_counts.get("Subagent", 0) + 1
                                    subagent_events.append({
                                        "task": f"Invocação de subagente ({ag}): {entry.get('task', '')}",
                                        "createdAt": ts,
                                        "sessionId": entry.get("sessionId", "hook")
                                    })
                            except Exception:
                                pass
                except Exception as ex:
                    self.warnings.append(f"Aviso ao ler telemetria de subagentes {jf}: {str(ex)}")

        # 6. Processamento dos logs de debug (fallback histórico de chamadas run_subagent)
        subagent_log_calls: List[Tuple[str, Optional[str]]] = []
        for log_file in self.debug_logs:
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        m = re.match(r'\[([^\]]+)\]\s+CALL:\s+run_subagent(?:\s+\[agent:([a-zA-Z0-9_\-]+)\])?', line)
                        if m:
                            subagent_log_calls.append((m.group(1), m.group(2)))
            except Exception as ex:
                self.warnings.append(f"Aviso ao ler log de subagentes {log_file.name}: {str(ex)}")

        if subagent_log_calls:
            all_events_for_correlation.sort(key=lambda x: x[0])
            for sc_ts, explicit_ag in subagent_log_calls:
                # Evita duplicar se já capturado pelo hook nativo
                if sc_ts[:19] in seen_telemetry_timestamps:
                    continue
                chosen_agent = None
                if explicit_ag and explicit_ag.lower() in known_agents:
                    chosen_agent = explicit_ag.lower()
                else:
                    try:
                        sc_dt = datetime.fromisoformat(sc_ts[:19].replace(" ", "T"))
                        candidates = [
                            ev for dt, *ev in all_events_for_correlation
                            if -600 <= (sc_dt - dt).total_seconds() <= 120
                        ]
                        for ev_type, d_str in reversed(candidates):
                            for p in SUBAGENT_PATTERNS:
                                for m in p.finditer(d_str):
                                    ag = m.group(1).lower()
                                    if ag in known_agents:
                                        chosen_agent = ag
                                        break
                                if chosen_agent:
                                    break
                            if chosen_agent:
                                break
                        if not chosen_agent:
                            for ev_type, d_str in reversed(candidates):
                                for ag in known_agents:
                                    pat = r'(?:@|agentName["\']?\s*[:=]\s*["\']|agent\s+|subagent[:\s]+)' + re.escape(ag)
                                    if re.search(pat, d_str, re.IGNORECASE):
                                        chosen_agent = ag
                                        break
                                if chosen_agent:
                                    break
                        if not chosen_agent:
                            for ev_type, d_str in reversed(candidates):
                                if ev_type in ("user_prompt", "role", "decision"):
                                    d_lower = d_str.lower()
                                    for ag in known_agents:
                                        if ag in d_lower:
                                            chosen_agent = ag
                                            break
                                    if chosen_agent:
                                        break
                    except Exception:
                        pass

                chosen_agent = chosen_agent or "search"
                if chosen_agent not in agent_stats:
                    agent_stats[chosen_agent] = {"direct": 0, "subagent": 0, "total": 0}
                agent_stats[chosen_agent]["subagent"] += 1
                tool_counts["Subagent"] = tool_counts.get("Subagent", 0) + 1
                subagent_events.append({"task": f"Invocação via run_subagent ({chosen_agent})", "createdAt": sc_ts, "sessionId": "subagent-log"})

        # Ordenação das sessões por data desc
        all_sessions.sort(key=lambda s: s.get("startedAt") or "", reverse=True)

        # Ordenação da atividade diária por data asc
        sessions_by_date = sorted(list(date_sessions_map.values()), key=lambda d: d["date"])

        # Tool usage formatado
        tool_usage_list = [{"tool": k, "count": v} for k, v in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)]

        # MCP tools formatado
        mcp_tools_list = list(mcp_tool_counts.values())
        mcp_tools_list.sort(key=lambda x: x["count"], reverse=True)

        # Projects formatado
        projects_list = list(project_agg.values())
        projects_list.sort(key=lambda p: p["events"], reverse=True)

        # Subagent burst analysis
        subagent_analysis = self._analyze_subagent_bursts(subagent_events)

        # Agregação e ordenação de agentInvocations
        agent_invocations_list: List[Dict[str, Any]] = []
        max_agent_total = max([v["direct"] + v["subagent"] for v in agent_stats.values()], default=0)
        for ag_name, stats in agent_stats.items():
            tot = stats["direct"] + stats["subagent"]
            pct = round((tot / max_agent_total) * 100.0, 1) if max_agent_total > 0 else 0.0
            agent_invocations_list.append({
                "agent": ag_name,
                "total": tot,
                "direct": stats["direct"],
                "subagent": stats["subagent"],
                "percentage": pct
            })
        agent_invocations_list.sort(key=lambda a: a["total"], reverse=True)

        return {
            "dbsCount": len(db_files),
            "sessions": all_sessions,
            "eventsSummary": {
                "totalEvents": total_events_count,
                "totalErrors": total_errors_count,
                "totalPrompts": total_prompts_count,
                "totalReads": total_reads_count,
                "totalWrites": total_writes_count,
                "hourlyPattern": [{"hour": h, "count": hourly_counts[h]} for h in range(24)],
                "sessionsByDate": sessions_by_date,
                "toolUsage": tool_usage_list,
                "mcpTools": mcp_tools_list,
                "projects": projects_list,
                "subagents": subagent_analysis,
                "agentInvocations": agent_invocations_list,
                "decisions": decisions_list,
                "detailedEvents": detailed_events,
            }
        }

    def _analyze_subagent_bursts(self, subagents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas de paralelismo e tempo economizado por subagentes."""
        if not subagents:
            return {
                "total": 0,
                "bursts": 0,
                "maxConcurrent": 0,
                "parallelCount": 0,
                "sequentialCount": 0,
                "timeSavedMin": 0,
            }

        valid_events = []
        for s in subagents:
            created = s.get("createdAt")
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace(" ", "T"))
                    valid_events.append((dt, s))
                except Exception:
                    pass

        valid_events.sort(key=lambda x: x[0])

        bursts: List[List[Any]] = []
        current_burst: List[Any] = []

        for dt, item in valid_events:
            if not current_burst:
                current_burst.append((dt, item))
                continue
            last_dt = current_burst[-1][0]
            gap_seconds = (dt - last_dt).total_seconds()
            if gap_seconds <= 30:
                current_burst.append((dt, item))
            else:
                bursts.append(current_burst)
                current_burst = [(dt, item)]

        if current_burst:
            bursts.append(current_burst)

        parallel_bursts = [b for b in bursts if len(b) >= 2]
        parallel_count = sum(len(b) for b in parallel_bursts)
        max_concurrent = max((len(b) for b in bursts), default=0)
        time_saved_min = sum((len(b) - 1) * 2 for b in parallel_bursts)

        return {
            "total": len(subagents),
            "bursts": len(parallel_bursts),
            "maxConcurrent": max_concurrent,
            "parallelCount": parallel_count,
            "sequentialCount": len(subagents) - parallel_count,
            "timeSavedMin": time_saved_min,
        }

    def _read_otel_spans(self) -> Dict[str, Any]:
        """Lê spans OTel GenAI exportados nativamente pelo Copilot/Claude Code (best-effort,
        sem assumir schema fixo — atributos ausentes são ignorados silenciosamente)."""
        candidates = [
            Path(__file__).resolve().parent.parent / "logs" / "otel-spans.jsonl",
            Path.cwd() / "tools" / "context-insight-visualizer" / "logs" / "otel-spans.jsonl",
        ]
        path = next((p for p in candidates if p.exists()), None)
        empty = {
            "spansCount": 0, "byService": {}, "operationBreakdown": {},
            "tokenUsage": {"inputTokens": 0, "outputTokens": 0, "cacheReadTokens": 0, "cacheCreationTokens": 0},
            "modelBreakdown": [], "agentBreakdown": [],
        }
        if not path:
            return empty

        by_service: Dict[str, int] = {}
        op_breakdown: Dict[str, int] = {}
        model_agg: Dict[str, Dict[str, int]] = {}
        agent_agg: Dict[str, int] = {}
        input_tok = output_tok = cache_read_tok = cache_creation_tok = 0
        spans_count = 0

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue

                    spans_count += 1
                    attrs = rec.get("attributes", {}) or {}
                    resource = rec.get("resource", {}) or {}

                    service = str(resource.get("service.name", "unknown"))
                    by_service[service] = by_service.get(service, 0) + 1

                    op = str(attrs.get("gen_ai.operation.name", "unknown"))
                    op_breakdown[op] = op_breakdown.get(op, 0) + 1

                    agent_name = attrs.get("gen_ai.agent.name")
                    if agent_name:
                        agent_agg[str(agent_name)] = agent_agg.get(str(agent_name), 0) + 1

                    in_tok = attrs.get("gen_ai.usage.input_tokens") or 0
                    out_tok = attrs.get("gen_ai.usage.output_tokens") or 0
                    cr_tok = attrs.get("gen_ai.usage.cache_read.input_tokens") or 0
                    cc_tok = attrs.get("gen_ai.usage.cache_creation.input_tokens") or 0
                    input_tok += int(in_tok) if str(in_tok).isdigit() else 0
                    output_tok += int(out_tok) if str(out_tok).isdigit() else 0
                    cache_read_tok += int(cr_tok) if str(cr_tok).isdigit() else 0
                    cache_creation_tok += int(cc_tok) if str(cc_tok).isdigit() else 0

                    model = attrs.get("gen_ai.response.model") or attrs.get("gen_ai.request.model")
                    if model:
                        m_key = str(model)
                        if m_key not in model_agg:
                            model_agg[m_key] = {"model": m_key, "calls": 0, "inputTokens": 0, "outputTokens": 0}
                        model_agg[m_key]["calls"] += 1
                        model_agg[m_key]["inputTokens"] += int(in_tok) if str(in_tok).isdigit() else 0
                        model_agg[m_key]["outputTokens"] += int(out_tok) if str(out_tok).isdigit() else 0
        except Exception as ex:
            self.warnings.append(f"Aviso ao ler otel-spans.jsonl: {str(ex)}")
            return empty

        return {
            "spansCount": spans_count,
            "byService": by_service,
            "operationBreakdown": op_breakdown,
            "tokenUsage": {
                "inputTokens": input_tok, "outputTokens": output_tok,
                "cacheReadTokens": cache_read_tok, "cacheCreationTokens": cache_creation_tok,
            },
            "modelBreakdown": sorted(model_agg.values(), key=lambda m: m["calls"], reverse=True),
            "agentBreakdown": [{"agent": k, "count": v} for k, v in sorted(agent_agg.items(), key=lambda x: x[1], reverse=True)],
        }

    def _read_stats_pid_files(self) -> Dict[str, Any]:
        """Lê e agrega os arquivos stats-pid-*.json do context-mode."""
        if not self.sessions_dirs:
            return {"filesCount": 0, "totalCalls": 0, "tokensSaved": 0, "dollarsSaved": 0.0, "byTool": {}}

        json_files: List[Path] = []
        for s_dir in self.sessions_dirs:
            if s_dir.exists():
                for jf in s_dir.glob("stats-pid-*.json"):
                    if "node_modules" not in str(jf) and jf not in json_files:
                        json_files.append(jf)

        total_calls = 0
        total_bytes_returned = 0
        tokens_saved_lifetime = 0
        dollars_saved_lifetime = 0.0
        by_tool_aggregated: Dict[str, Dict[str, int]] = {}

        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                total_calls += data.get("total_calls", 0)
                total_bytes_returned += data.get("bytes_returned", 0)
                
                # O maior lifetime entre todos os arquivos representa o acumulado real
                ts_lt = data.get("tokens_saved_lifetime", 0)
                ds_lt = data.get("dollars_saved_lifetime", 0.0)
                if ts_lt > tokens_saved_lifetime:
                    tokens_saved_lifetime = ts_lt
                if ds_lt > dollars_saved_lifetime:
                    dollars_saved_lifetime = ds_lt

                for tool, stats in data.get("by_tool", {}).items():
                    if tool not in by_tool_aggregated:
                        by_tool_aggregated[tool] = {"calls": 0, "bytes": 0}
                    by_tool_aggregated[tool]["calls"] += stats.get("calls", 0)
                    by_tool_aggregated[tool]["bytes"] += stats.get("bytes", 0)

            except Exception as ex:
                self.warnings.append(f"Aviso ao ler {jf.name}: {str(ex)}")

        return {
            "filesCount": len(json_files),
            "totalCalls": total_calls,
            "bytesReturned": total_bytes_returned,
            "tokensSavedLifetime": tokens_saved_lifetime,
            "dollarsSavedLifetime": round(dollars_saved_lifetime, 2),
            "byTool": by_tool_aggregated,
        }

    def _read_content_databases(self) -> Dict[str, Any]:
        """Lê metadados agregados das bases content/*.db (chunks indexados, tamanho, fontes)."""
        if not self.content_dirs:
            return {"dbsCount": 0, "totalSources": 0, "totalChunks": 0, "totalSizeBytes": 0, "sources": [], "chunksBySource": {}}

        db_files: List[Path] = []
        for c_dir in self.content_dirs:
            if c_dir.exists():
                for db in c_dir.glob("*.db"):
                    if "node_modules" not in str(db) and ".cache" not in str(db) and db not in db_files:
                        db_files.append(db)

        total_sources = 0
        total_chunks = 0
        total_size_bytes = 0
        sources_list: List[Dict[str, Any]] = []
        chunks_by_source: Dict[int, List[Dict[str, Any]]] = {}

        for db_file in db_files:
            try:
                total_size_bytes += db_file.stat().st_size
                conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                cur = conn.cursor()
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

                if "sources" in tables:
                    cnt = cur.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
                    total_sources += cnt
                    s_rows = cur.execute("SELECT id, label, chunk_count, code_chunk_count, indexed_at, file_path FROM sources ORDER BY indexed_at DESC LIMIT 250").fetchall()
                    for sid, slabel, c_cnt, cc_cnt, idx_at, fpath in s_rows:
                        sanitized_path = (fpath or "").replace("\\", "/")
                        if "/" in sanitized_path:
                            sanitized_path = ".../" + "/".join(sanitized_path.split("/")[-3:])
                        sources_list.append({
                            "id": sid,
                            "dbHash": db_file.stem,
                            "label": slabel or "Untitled",
                            "chunkCount": c_cnt or 0,
                            "codeChunkCount": cc_cnt or 0,
                            "indexedAt": idx_at or "",
                            "filePath": sanitized_path or slabel or "Sem caminho",
                        })

                if "chunks" in tables:
                    cnt = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
                    total_chunks += cnt
                    chunk_rows = cur.execute("SELECT source_id, title, content_type, length(content), substr(content, 1, 280) FROM chunks LIMIT 800").fetchall()
                    for ch_sid, ch_title, ch_type, ch_len, ch_prev in chunk_rows:
                        s_key = int(ch_sid) if ch_sid is not None else 0
                        if s_key not in chunks_by_source:
                            chunks_by_source[s_key] = []
                        if len(chunks_by_source[s_key]) < 10:
                            chunks_by_source[s_key].append({
                                "title": ch_title or "(Sem título)",
                                "contentType": ch_type or "text",
                                "charLen": ch_len or 0,
                                "preview": (ch_prev or "").strip(),
                            })
                conn.close()
            except Exception as ex:
                self.warnings.append(f"Aviso ao ler content DB {db_file.name}: {str(ex)}")

        return {
            "dbsCount": len(db_files),
            "totalSources": total_sources,
            "totalChunks": total_chunks,
            "totalSizeBytes": total_size_bytes,
            "sources": sources_list,
            "chunksBySource": chunks_by_source,
        }


if __name__ == "__main__":
    extractor = ContextDataExtractor()
    result = extractor.extract_all()
    print(f"Extracao concluida:")
    print(f"  Sessions DBs: {result['meta']['sessionDbsCount']}")
    print(f"  Total Sessions: {len(result['sessions'])}")
    print(f"  Stats PID files: {result['meta']['statsPidCount']}")
    print(f"  Warnings: {len(result['meta']['warnings'])}")
