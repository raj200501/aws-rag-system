# Architecture Overview

This repository is a local, deterministic RAG system that mirrors the shape of an
AWS-backed pipeline. Instead of invoking managed services, each component has a
local implementation so the system can be executed and verified on any machine
with Python.

## Component Map

| AWS Concept | Local Component | Implementation |
| --- | --- | --- |
| Amazon S3 | Document storage | `.rag_data/` on disk |
| Amazon OpenSearch / Elasticsearch | Search index | SQLite FTS5 in `rag_system.storage` |
| Amazon Comprehend | Text analysis | `rag_system.analyzer` |
| Lambda handlers | API/CLI handlers | `rag_system.server` + `rag_system.cli` |

## Data Flow

1. **Ingestion**
   - A document is uploaded through the `/documents` endpoint or `rag_system.cli add`.
   - The `rag_system.storage.add_document` function normalizes the payload and stores
     it in the SQLite full-text index.

2. **Indexing**
   - The `initialize_database` routine creates an FTS5 virtual table named
     `documents` with Porter stemming enabled.
   - Each document is inserted with `doc_id`, `content`, `source`, and `metadata`
     columns. This mirrors the metadata stored alongside files in an S3 bucket.

3. **Search**
   - Queries are executed with the `MATCH` operator. Results are ranked using the
     built-in `bm25` scoring function.
   - Returned records are projected into `SearchResult` objects, which are used by
     both the HTTP API and the CLI.

4. **Analysis**
   - The local analyzer mimics the output shape of Comprehend by returning two
     payloads: `entities` and `key_phrases`.
   - Entities are detected using capitalization heuristics. Key phrases are a
     simple bigram frequency list. This keeps the implementation deterministic
     and dependency-free.

5. **Generation**
   - The response generator uses the search results as a context block and
     produces a deterministic, human-readable answer.
   - Each response includes the query, the ranked snippet context, and the
     analysis results so the output can be verified in automation.

## Persistence Model

The SQLite index is stored at `RAG_DB_PATH`. The CLI and server both call
`initialize_database` to create the schema on first use. Documents are stored in
an FTS5 table, while a `document_meta` table stores timestamps for operational
reporting.

## Configuration

Configuration is loaded from environment variables or `.env`:

- `RAG_HOST`: Bind address for the HTTP server.
- `RAG_PORT`: Port for the HTTP server.
- `RAG_DATA_DIR`: Local directory used for persisted assets.
- `RAG_DB_PATH`: SQLite database path (defaults to `<data_dir>/rag.db`).
- `RAG_TOP_K`: Number of search results to return.
- `RAG_ENV`: Environment label (development, test, production).

## Operational Behavior

- Starting the server does **not** seed data automatically, except in the helper
  script `scripts/run.sh` which seeds example documents for a first run.
- `scripts/verify.sh` always seeds the index before exercising the API. This
  guarantees deterministic smoke tests regardless of machine state.

## Local Service Boundaries

The local system can be thought of as four collaborating services, even though
it is implemented as a single Python package:

1. **Indexing Service**: Creates the database and inserts documents.
2. **Search Service**: Performs FTS5 queries and ranks results.
3. **Analysis Service**: Extracts entities and key phrases.
4. **Generation Service**: Produces the final response payload.

By keeping the data flow explicit, the same code paths can be used by the CLI,
HTTP server, lambda-style wrappers, and tests.

## Extension Points

If you need to extend the system, the recommended hooks are:

- Add richer analysis logic in `rag_system.analyzer`.
- Update `rag_system.generator` to include templated output or call a hosted LLM.
- Swap the storage implementation by replacing `rag_system.storage` functions.
- Add ingestion transforms in `rag_system.cli` or in a new `rag_system.pipeline`
  module.

## Files to Start With

- `rag_system/storage.py`: Storage and search implementation.
- `rag_system/server.py`: HTTP API definition.
- `rag_system/cli.py`: CLI commands and ingestion flows.
- `scripts/verify.sh`: Canonical verification path used in CI.
- `scripts/run.sh`: Developer-friendly server starter with data seeding.

