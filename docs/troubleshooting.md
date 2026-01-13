# Troubleshooting

## Database initialization errors

**Symptom:** You see an error similar to `no such table: documents`.

**Cause:** The database schema was not initialized before attempting to query.

**Fix:** Run one of the following commands to initialize the database:

```bash
python -m rag_system.cli init
# or
python -m rag_system.cli seed examples/documents
```

The server will also initialize the database automatically when it starts.

## Search returns no results

**Symptom:** `GET /search?query=...` returns an empty list.

**Cause:** The index is empty, or the query terms do not match any documents.

**Fix:** Seed or add documents, and try a query that matches the sample data:

```bash
python -m rag_system.cli seed examples/documents
python -m rag_system.cli search "Lambda"
```

## Server won't start

**Symptom:** `OSError: [Errno 98] Address already in use`.

**Cause:** Another process is using the configured port.

**Fix:** Choose a new port or stop the existing process:

```bash
export RAG_PORT=8080
./scripts/run.sh
```

## Smoke test failures

**Symptom:** `scripts/smoke_test.py` raises `Server did not become healthy in time`.

**Cause:** The server failed to start, often due to invalid configuration.

**Fix:** Check that the environment variables are valid and that the database
path is writable. Re-run the verification script with debugging:

```bash
RAG_ENV=development ./scripts/verify.sh
```

## Lambda wrapper errors

**Symptom:** Lambda handlers return `text is required` or `query is required`.

**Cause:** The lambda wrapper expects a JSON payload with specific keys.

**Fix:** Pass the correct keys (`text`, `query`, `id`, `content`) when invoking
lambda handlers, or use the HTTP server which validates the payload for you.

## SQLite FTS5 errors

**Symptom:** `OperationalError: no such module: fts5`.

**Cause:** The Python build does not include the SQLite FTS5 extension.

**Fix:** Use a Python distribution that includes FTS5 (the default in
python.org builds and GitHub Actions). If needed, install Python 3.11 from
python.org or use `pyenv` with a build that enables FTS5.

## Cleaning state

To reset the data directory, delete `.rag_data`:

```bash
rm -rf .rag_data
```

Then re-seed data:

```bash
python -m rag_system.cli seed examples/documents
```
