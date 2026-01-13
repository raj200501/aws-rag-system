import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(f"http://127.0.0.1:{port}/healthz") as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("status") == "ok":
                return
        except Exception:  # noqa: BLE001
            time.sleep(0.1)
    raise RuntimeError("Server did not become healthy in time")


def _request_json(request: Request) -> dict:
    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sample_dir = root / "examples" / "documents"
    port = _free_port()

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "rag.db"
        env = os.environ.copy()
        env["RAG_DB_PATH"] = str(db_path)
        env["RAG_PORT"] = str(port)

        subprocess.run(
            ["python", "-m", "rag_system.cli", "seed", str(sample_dir)],
            check=True,
            env=env,
        )

        server = subprocess.Popen(
            ["python", "-m", "rag_system.server"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            _wait_for_health(port)

            doc_payload = json.dumps(
                {
                    "id": "smoke-doc",
                    "content": "AWS Step Functions coordinates workflows.",
                }
            ).encode("utf-8")
            request = Request(
                f"http://127.0.0.1:{port}/documents",
                data=doc_payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            payload = _request_json(request)
            assert payload["document"]["doc_id"] == "smoke-doc"

            request = Request(f"http://127.0.0.1:{port}/search?query=Lambda")
            search_payload = _request_json(request)
            assert search_payload["results"], "Expected search results"

            generate_payload = json.dumps({"query": "What does S3 do?"}).encode(
                "utf-8"
            )
            request = Request(
                f"http://127.0.0.1:{port}/generate",
                data=generate_payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            gen_payload = _request_json(request)
            assert "Answer" in gen_payload["answer"], "Expected generated response"
        except Exception as exc:  # noqa: BLE001
            server.terminate()
            try:
                stdout, _ = server.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                stdout, _ = server.communicate(timeout=3)
            if stdout:
                raise RuntimeError(
                    f"Smoke test failed. Server output:\\n{stdout}"
                ) from exc
            raise
        else:
            server.terminate()
            try:
                server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=3)


if __name__ == "__main__":
    main()
