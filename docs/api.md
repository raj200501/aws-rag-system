# Local RAG HTTP API

The HTTP server exposes a minimal JSON API that mirrors the lambda-like
operations described in the README. All responses are JSON, and all request
bodies are UTF-8 encoded JSON objects.

## Base URL

```
http://127.0.0.1:8000
```

You can change the host and port using the `RAG_HOST` and `RAG_PORT`
configuration values.

## Health Check

**GET** `/healthz`

**Response**

```json
{
  "status": "ok"
}
```

Use this endpoint to confirm the service is accepting requests before running
integration tests or load tests.

## Create Document

**POST** `/documents`

**Request Body**

```json
{
  "id": "doc-001",
  "content": "Text to index",
  "source": "manual",
  "metadata": {
    "team": "platform",
    "priority": "high"
  }
}
```

- `id` is required and must be unique.
- `content` is required and becomes the searchable text.
- `source` is optional; use it to track ingestion origin.
- `metadata` is optional and is stored as JSON.

**Response**

```json
{
  "document": {
    "doc_id": "doc-001",
    "content": "Text to index",
    "source": "manual",
    "metadata": {
      "team": "platform",
      "priority": "high"
    }
  }
}
```

## List Documents

**GET** `/documents`

**Response**

```json
{
  "documents": [
    {
      "doc_id": "doc-001",
      "content": "Text to index",
      "source": "manual",
      "metadata": {
        "team": "platform"
      }
    }
  ]
}
```

## Search

**GET** `/search?query=...`

**Response**

```json
{
  "results": [
    {
      "doc_id": "doc-001",
      "content": "Text to index",
      "source": "manual",
      "score": -1.5,
      "metadata": {
        "team": "platform"
      }
    }
  ]
}
```

The `score` is the SQLite `bm25` ranking score, where lower numbers represent
higher relevance.

## Generate

**POST** `/generate`

**Request Body**

```json
{
  "query": "What does S3 do?"
}
```

**Response**

```json
{
  "answer": "Answer (deterministic demo response)\nQuery: What does S3 do?\n...",
  "context": "[doc-001] ...",
  "results": [
    {
      "doc_id": "doc-001",
      "content": "Text to index",
      "source": "manual",
      "score": -1.5,
      "metadata": {
        "team": "platform"
      }
    }
  ],
  "analysis": {
    "entities": [
      {
        "Text": "S3",
        "Score": 0.125
      }
    ],
    "key_phrases": [
      {
        "Text": "does s3",
        "Score": 0.125
      }
    ]
  }
}
```

## Analyze

**POST** `/analyze`

**Request Body**

```json
{
  "text": "AWS Lambda runs code without managing servers."
}
```

**Response**

```json
{
  "entities": [
    {
      "Text": "AWS",
      "Score": 0.2
    }
  ],
  "key_phrases": [
    {
      "Text": "lambda runs",
      "Score": 0.2
    }
  ]
}
```

## Error Handling

- Requests missing required fields return HTTP 400 with a short error message.
- Unknown paths return HTTP 404 with an error payload.
- Invalid JSON requests return HTTP 400.

## Curl Examples

```bash
curl -s http://127.0.0.1:8000/healthz

curl -s -X POST http://127.0.0.1:8000/documents \
  -H 'Content-Type: application/json' \
  -d '{"id":"doc-123","content":"AWS Step Functions coordinates workflows."}'

curl -s "http://127.0.0.1:8000/search?query=workflows"

curl -s -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"query":"What coordinates workflows?"}'
```
