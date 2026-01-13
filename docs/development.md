# Development Guide

This guide describes how to run the local RAG system, iterate on features, and
validate changes before submitting pull requests.

## Repository Layout

- `rag_system/`: Python package with storage, analysis, generation, and server.
- `lambda_functions/`: Lambda-style wrappers used for AWS deployments or demos.
- `scripts/`: Canonical run and verification scripts.
- `tests/`: Unit and integration tests.
- `examples/documents/`: Sample documents used for seeding and demos.

## Local Setup

1. Ensure Python 3.11+ is available.
2. Copy `.env.example` to `.env` if you want to customize settings.
3. Start the server:

```bash
./scripts/run.sh
```

The server binds to `RAG_HOST`/`RAG_PORT` and seeds the example documents so you
can immediately test search and generation.

## CLI Tips

The CLI is the fastest way to exercise the pipeline without HTTP:

```bash
python -m rag_system.cli init
python -m rag_system.cli seed examples/documents
python -m rag_system.cli search "Lambda"
python -m rag_system.cli generate "What does S3 do?"
```

## Adding Documents

Use either the CLI or the HTTP API:

```bash
python -m rag_system.cli add "doc-77" "CloudWatch collects metrics." --source manual
```

Or:

```bash
curl -s -X POST http://127.0.0.1:8000/documents \
  -H 'Content-Type: application/json' \
  -d '{"id":"doc-77","content":"CloudWatch collects metrics."}'
```

## Tests and Verification

Use the canonical verification script so you exercise the same behavior as CI:

```bash
./scripts/verify.sh
```

The verification script runs:

1. Unit tests (`python -m unittest`)
2. A smoke test that starts the HTTP server, seeds data, and issues real requests

## Extension Ideas

- Replace the analyzer with a real NLP library by updating `rag_system/analyzer.py`.
- Add streaming responses in `rag_system/server.py` if you want SSE support.
- Add caching to the storage layer using a `query_cache` table.
- Integrate a hosted LLM by editing `rag_system/generator.py`.

## Style Guidelines

- Prefer pure standard library dependencies to keep the verification flow fast.
- Keep responses deterministic so CI can validate outputs reliably.
- Add tests in `tests/` for every new module.
- Keep new scripts in `scripts/` and ensure they are executable.

## Debugging

If the server fails to start, check:

- The `RAG_DB_PATH` directory is writable.
- The port is not already in use.
- The `.env` file does not have malformed values.

Use `RAG_ENV=development` to keep default logging on.
