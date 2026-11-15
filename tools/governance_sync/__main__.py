"""CLI entrypoint para execução via `python -m tools.governance_sync`."""

from __future__ import annotations

import sys

from tools.governance_sync.sync_docs_counts_and_mermaid import main

if __name__ == "__main__":
    sys.exit(main())
