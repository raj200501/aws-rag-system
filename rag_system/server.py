"""HTTP server exposing the local RAG API."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse

from .config import load_config
from .storage import (
    add_document,
    initialize_database,
    list_documents,
    search_documents,
)
from .generator import generate_response
from .analyzer import analyze_text


class RagRequestHandler(BaseHTTPRequestHandler):
    server_version = "RAGServer/1.0"

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            return json.loads(raw or "{}")
        except json.JSONDecodeError as exc:  # noqa: BLE001
            raise ValueError("Invalid JSON payload") from exc

    def _handle_exception(self, exc: Exception) -> None:
        print(f"Server error: {exc}", flush=True)
        self._send_json({"error": str(exc)}, status=500)

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/healthz":
                self._send_json({"status": "ok"})
                return

            if parsed.path == "/documents":
                config = load_config()
                docs = list_documents(config.db_path)
                self._send_json({"documents": [doc.__dict__ for doc in docs]})
                return

            if parsed.path == "/search":
                params = parse_qs(parsed.query)
                query = params.get("query", [""])[0]
                if not query:
                    self._send_json({"error": "query parameter is required"}, status=400)
                    return
                config = load_config()
                results = search_documents(config.db_path, query, limit=config.top_k)
                self._send_json({"results": [result.__dict__ for result in results]})
                return

            self._send_json({"error": "not found"}, status=404)
        except Exception as exc:  # noqa: BLE001
            self._handle_exception(exc)

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            payload = self._read_json()

            if parsed.path == "/documents":
                doc_id = payload.get("id")
                content = payload.get("content")
                source = payload.get("source", "manual")
                metadata = payload.get("metadata", {})
                if not doc_id or not content:
                    self._send_json({"error": "id and content are required"}, status=400)
                    return
                config = load_config()
                initialize_database(config.db_path)
                record = add_document(config.db_path, doc_id, content, source, metadata)
                self._send_json({"document": record.__dict__}, status=201)
                return

            if parsed.path == "/generate":
                query = payload.get("query")
                if not query:
                    self._send_json({"error": "query is required"}, status=400)
                    return
                config = load_config()
                results = search_documents(config.db_path, query, limit=config.top_k)
                response = generate_response(query, results)
                self._send_json(response)
                return

            if parsed.path == "/analyze":
                text = payload.get("text")
                if not text:
                    self._send_json({"error": "text is required"}, status=400)
                    return
                analysis = analyze_text(text)
                self._send_json(analysis)
                return

            self._send_json({"error": "not found"}, status=404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # noqa: BLE001
            self._handle_exception(exc)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def run_server() -> None:
    config = load_config()
    initialize_database(config.db_path)
    server = HTTPServer((config.host, config.port), RagRequestHandler)
    print(f"RAG server running at http://{config.host}:{config.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
