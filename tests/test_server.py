import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from http.server import HTTPServer
from urllib.request import Request, urlopen

from rag_system.server import RagRequestHandler
from rag_system.storage import initialize_database


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "rag.db"
        initialize_database(self.db_path)

        self.port = _free_port()
        os.environ["RAG_DB_PATH"] = str(self.db_path)
        os.environ["RAG_PORT"] = str(self.port)

        self.httpd = HTTPServer(("127.0.0.1", self.port), RagRequestHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        time.sleep(0.1)

    def tearDown(self):
        self.httpd.shutdown()
        self.thread.join()
        self.httpd.server_close()
        self.temp_dir.cleanup()

    def test_healthz(self):
        with urlopen(f"http://127.0.0.1:{self.port}/healthz") as response:
            payload = json.loads(response.read().decode("utf-8"))
        self.assertEqual(payload["status"], "ok")

    def test_document_flow(self):
        body = json.dumps({"id": "doc-1", "content": "S3 stores objects"}).encode("utf-8")
        request = Request(
            f"http://127.0.0.1:{self.port}/documents",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
        self.assertEqual(payload["document"]["doc_id"], "doc-1")

        with urlopen(f"http://127.0.0.1:{self.port}/search?query=S3") as response:
            search_payload = json.loads(response.read().decode("utf-8"))
        self.assertEqual(len(search_payload["results"]), 1)


if __name__ == "__main__":
    unittest.main()
