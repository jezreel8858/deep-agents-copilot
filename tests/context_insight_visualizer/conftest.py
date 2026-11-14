import sqlite3
from pathlib import Path
import pytest


def create_v2_db(db_path: Path, with_fts: bool = True) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    cur.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '6')")

    cur.execute(
        """
        CREATE TABLE events (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            worktree TEXT NOT NULL,
            agent TEXT NOT NULL,
            kind TEXT NOT NULL,
            tool TEXT,
            key TEXT,
            path TEXT,
            ok INTEGER NOT NULL DEFAULT 1,
            exit_code INTEGER,
            bytes INTEGER NOT NULL DEFAULT 0,
            body TEXT NOT NULL DEFAULT '',
            turn INTEGER NOT NULL DEFAULT 0,
            sandbox_bytes INTEGER NOT NULL DEFAULT 0,
            returned_bytes INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            worktree TEXT NOT NULL,
            agent TEXT,
            label TEXT NOT NULL,
            path TEXT,
            kind TEXT NOT NULL DEFAULT 'text',
            chunk_count INTEGER NOT NULL DEFAULT 0,
            bytes_total INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL
        )
        """
    )

    if with_fts:
        cur.execute(
            """
            CREATE VIRTUAL TABLE chunks USING fts5(
                source_id UNINDEXED,
                session_id UNINDEXED,
                worktree UNINDEXED,
                agent UNINDEXED,
                ord UNINDEXED,
                body,
                title
            )
            """
        )

    base_ts = 1794600000000  # epoch ms
    wt = "D:/workspace/public/deep-agents-copilot"

    # Real user session events
    events_rows = [
        ("sess-real-001", wt, "copilot-cli", "prompt", "user_prompt", None, None, 1, 0, 120, "Auditar context-insight-visualizer", 1, 0, 0, base_ts),
        ("sess-real-001", wt, "copilot-cli", "cmd", "ctx_execute", "ctx_execute:javascript", None, 1, 0, 48000, "output inspect", 1, 48000, 1200, base_ts + 5000),
        ("sess-real-001", wt, "copilot-cli", "file", "ctx_search", "ctx_search:schema", "src/schema.ts", 1, 0, 1500, "schema v6", 1, 8000, 800, base_ts + 15000),
        ("sess-real-001", wt, "copilot-cli", "edit", "replace_string_in_file", None, "generator/extractor.py", 1, 0, 900, "updated extractor", 2, 0, 0, base_ts + 30000),
        ("sess-real-001", wt, "copilot-cli", "decision", "ask_questions", "gate2", None, 1, 0, 200, "Aprovar e Executar (Recomendado)", 2, 0, 0, base_ts + 45000),
        ("sess-real-001", wt, "copilot-cli", "toolerr", "ctx_execute", None, None, 0, 1, 300, "Error: ENOENT", 3, 0, 0, base_ts + 60000),
        # Doctor synthetic session (must be filtered out)
        ("context-mode-doctor-hook-runs", "C:/Temp/cm-doctor-runs-abc123/proj", "copilot-cli", "cmd", "Bash", "Bash:cat big.log", None, 1, 0, 65564, "context-mode doctor sample line 0", 0, 65564, 140, base_ts + 90000),
    ]
    cur.executemany(
        """
        INSERT INTO events (
            session_id, worktree, agent, kind, tool, key, path, ok, exit_code,
            bytes, body, turn, sandbox_bytes, returned_bytes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        events_rows,
    )

    cur.execute(
        """
        INSERT INTO sources (session_id, worktree, agent, label, path, kind, chunk_count, bytes_total, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("sess-real-001", wt, "copilot-cli", "docs/architecture.md", "docs/architecture.md", "file", 2, 4096, base_ts + 10000),
    )
    src_id = cur.lastrowid

    if with_fts:
        cur.execute(
            "INSERT INTO chunks (source_id, session_id, worktree, agent, ord, body, title) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (src_id, "sess-real-001", wt, "copilot-cli", 0, "Context Mode v2.1.10 unified SQLite FTS5 store", "Architecture Overview"),
        )

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def v2_data_root(tmp_path: Path) -> Path:
    root = tmp_path / "context-mode-v2"
    db_path = root / "projects" / "a1b2c3d4e5f60718" / "context.db"
    create_v2_db(db_path, with_fts=True)
    # Also create a backup db inside backups/ that MUST be ignored
    backup_db = root / "backups" / "v1-aside-2026" / "projects" / "deadbeef" / "context.db"
    create_v2_db(backup_db, with_fts=True)
    return root
