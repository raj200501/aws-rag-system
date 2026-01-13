# AWS Integrated RAG System (Local, Deterministic Edition)

This repository provides a **local, deterministic** Retrieval-Augmented Generation (RAG)
system that mirrors an AWS-centric architecture. It includes:

- Document storage (local filesystem, modeled after S3)
- Document indexing and search (SQLite FTS5, modeled after OpenSearch/Elasticsearch)
- Response generation (deterministic local generator)
- Text analysis (simple Comprehend-style output)
- Lambda-style wrappers (Python functions that call the local pipeline)

> The AWS deployment templates are included for reference, but the verified
> workflow in this repository runs fully locally so it is reproducible in CI.

## Features

- Deterministic local RAG pipeline with no external dependencies
- HTTP API for upload, search, analysis, and generation
- CLI for fast local workflows
- Automated verification script used by CI
- Sample documents for reproducible results

## Prerequisites

- Python 3.11+

No third-party packages are required. Everything runs on the Python standard
library.

## Quickstart (Verified)

The following commands are verified and reproduce the expected behavior locally.

```bash
# From the repo root
./scripts/run.sh
```

This will:

1. Initialize the local database.
2. Seed the sample documents in `examples/documents/`.
3. Start the HTTP server at `http://127.0.0.1:8000`.

### Example API Usage

```bash
curl -s http://127.0.0.1:8000/healthz

curl -s -X POST http://127.0.0.1:8000/documents \
  -H 'Content-Type: application/json' \
  -d '{"id":"doc-77","content":"CloudWatch collects metrics."}'

curl -s "http://127.0.0.1:8000/search?query=Lambda"

curl -s -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"query":"What does S3 do?"}'
```

## CLI Workflow

```bash
python -m rag_system.cli init
python -m rag_system.cli seed examples/documents
python -m rag_system.cli search "Lambda"
python -m rag_system.cli generate "What does S3 do?"
```

## Configuration

Copy `.env.example` to `.env` to override defaults. The key settings are:

- `RAG_HOST`: Bind address for the HTTP server.
- `RAG_PORT`: Port for the HTTP server.
- `RAG_DB_PATH`: SQLite database path.
- `RAG_TOP_K`: Number of results returned for search/generate.

## Verification (Verified)

The canonical verification command is:

```bash
./scripts/verify.sh
```

It runs unit tests and a smoke test that:

1. Seeds sample documents.
2. Starts the HTTP server.
3. Uploads a document.
4. Performs a search.
5. Generates a response with retrieved context.

## AWS Deployment Notes (Reference Only)

The `infrastructure/serverless.yml` file and lambda handlers in
`lambda_functions/` are included as reference templates. They are not part of the
verified local workflow. For production deployments, you would adapt these
resources to your AWS account and security requirements.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [HTTP API Reference](docs/api.md)
- [Development Guide](docs/development.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

This project is licensed under the MIT License.
