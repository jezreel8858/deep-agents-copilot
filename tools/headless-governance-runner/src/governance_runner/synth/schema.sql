-- Schema DDL SQLite do historico de geracao, avaliacao e diagnostico sintetico de roteamento (v2)
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS schema_meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT OR IGNORE INTO schema_meta (key, value) VALUES ('schema_version', '2');

CREATE TABLE IF NOT EXISTS synth_runs (
  run_id                 TEXT PRIMARY KEY,
  kind                   TEXT NOT NULL CHECK (kind IN ('generate','eval','export','promote')),
  parent_run_id          TEXT REFERENCES synth_runs(run_id),
  started_at             TEXT NOT NULL,
  finished_at            TEXT,
  status                 TEXT NOT NULL CHECK (status IN ('running','completed','neutral','failed')),
  motivo                 TEXT,
  generator              TEXT CHECK (generator IN ('sdk','template')),
  model                  TEXT,
  rng_seed               INTEGER,
  params_json            TEXT NOT NULL DEFAULT '{}',
  router_agent_sha256    TEXT,
  golden_set_sha256      TEXT,
  routing_graph_sha256   TEXT,
  premium_requests_used  INTEGER NOT NULL DEFAULT 0,
  n_candidates           INTEGER NOT NULL DEFAULT 0,
  n_rejected_hash        INTEGER NOT NULL DEFAULT 0,
  n_rejected_similarity  INTEGER NOT NULL DEFAULT 0,
  n_rejected_override    INTEGER NOT NULL DEFAULT 0,
  n_accepted             INTEGER NOT NULL DEFAULT 0,
  trace_id               TEXT
);

CREATE TABLE IF NOT EXISTS synth_prompts (
  prompt_id              TEXT PRIMARY KEY,
  run_id                 TEXT NOT NULL REFERENCES synth_runs(run_id),
  text                   TEXT NOT NULL,
  text_norm              TEXT NOT NULL,
  sha256                 TEXT NOT NULL UNIQUE,
  expected_route         TEXT NOT NULL,
  agente_alvo            TEXT NOT NULL,
  dimensao_perturbacao   TEXT NOT NULL,
  seed_case_id           TEXT,
  seed_source            TEXT NOT NULL DEFAULT 'manual',
  graph_edge_id          TEXT NULL,
  graph_edge_resolution  TEXT NULL,
  max_similarity         REAL NOT NULL,
  nearest_ref            TEXT,
  created_at             TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_prompts_stratum
  ON synth_prompts(agente_alvo, dimensao_perturbacao);

CREATE INDEX IF NOT EXISTS ix_prompts_graph_edge
  ON synth_prompts(graph_edge_id);

CREATE TABLE IF NOT EXISTS synth_evaluations (
  eval_id                TEXT PRIMARY KEY,
  run_id                 TEXT NOT NULL REFERENCES synth_runs(run_id),
  prompt_id              TEXT NOT NULL REFERENCES synth_prompts(prompt_id),
  observed_route         TEXT,
  route_source           TEXT CHECK (verdict = 'unparseable' OR route_source IN ('tool_hook', 'text_banner')),
  verdict                TEXT NOT NULL CHECK (verdict IN ('matched','mismatched','unparseable','error')),
  passed                 INTEGER NOT NULL CHECK (passed IN (0,1)),
  response_excerpt       TEXT,
  latency_ms             INTEGER,
  premium_requests       INTEGER NOT NULL DEFAULT 0,
  error                  TEXT,
  created_at             TEXT NOT NULL,
  UNIQUE (run_id, prompt_id)
);

CREATE INDEX IF NOT EXISTS ix_eval_failed
  ON synth_evaluations(passed, run_id);

CREATE TABLE IF NOT EXISTS synth_exports (
  export_id              TEXT PRIMARY KEY,
  prompt_id              TEXT NOT NULL REFERENCES synth_prompts(prompt_id),
  eval_id                TEXT REFERENCES synth_evaluations(eval_id),
  silver_path            TEXT NOT NULL,
  silver_case_id         TEXT NOT NULL UNIQUE,
  promoted_path          TEXT,
  status                 TEXT NOT NULL CHECK (status IN ('silver','promoted','discarded')),
  exported_at            TEXT NOT NULL,
  decided_at             TEXT
);

CREATE TABLE IF NOT EXISTS routing_graph_edges (
  snapshot_sha256        TEXT NOT NULL,
  edge_id                TEXT NOT NULL,
  de                     TEXT NOT NULL,
  para                   TEXT NOT NULL,
  tipo                   TEXT NOT NULL,
  regra                  TEXT,
  prioridade             REAL,
  threshold_score        REAL,
  nivel_routing          TEXT,
  keywords_json          TEXT NOT NULL DEFAULT '[]',
  valida                 INTEGER NOT NULL CHECK (valida IN (0,1)),
  PRIMARY KEY (snapshot_sha256, edge_id)
);

CREATE TABLE IF NOT EXISTS synth_diagnostics (
  diagnostic_id          TEXT PRIMARY KEY,
  eval_run_id            TEXT NOT NULL REFERENCES synth_runs(run_id),
  routing_graph_sha256   TEXT NOT NULL,
  router_agent_sha256    TEXT,
  golden_set_sha256      TEXT,
  created_at             TEXT NOT NULL,
  yaml_path              TEXT,
  md_path                TEXT,
  metrics_json           TEXT NOT NULL,
  n_suggestions          INTEGER NOT NULL DEFAULT 0
);

PRAGMA user_version = 2;
