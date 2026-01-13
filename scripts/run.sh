#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export RAG_ENV="${RAG_ENV:-development}"

if [[ -z "${RAG_DB_PATH:-}" ]]; then
  export RAG_DB_PATH="$ROOT_DIR/.rag_data/rag.db"
fi

python -m rag_system.cli seed "$ROOT_DIR/examples/documents" >/dev/null
python -m rag_system.server
