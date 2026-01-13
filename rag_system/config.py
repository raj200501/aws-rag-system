"""Configuration loader for the local RAG system."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Dict, Optional


@dataclass(frozen=True)
class Config:
    data_dir: Path
    db_path: Path
    host: str
    port: int
    top_k: int
    environment: str


_ENV_PREFIX = "RAG_"


def _parse_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("\"")
    return values


def _env(name: str, env_values: Dict[str, str], default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name) or env_values.get(name) or default


def load_config(env_path: Optional[Path] = None) -> Config:
    root = Path.cwd()
    env_file = env_path or root / ".env"
    env_values = _parse_env_file(env_file)

    data_dir_str = _env(f"{_ENV_PREFIX}DATA_DIR", env_values, str(root / ".rag_data"))
    data_dir = Path(data_dir_str).expanduser().resolve()
    db_path_str = _env(f"{_ENV_PREFIX}DB_PATH", env_values, str(data_dir / "rag.db"))
    db_path = Path(db_path_str).expanduser().resolve()

    host = _env(f"{_ENV_PREFIX}HOST", env_values, "127.0.0.1")
    port_raw = _env(f"{_ENV_PREFIX}PORT", env_values, "8000")
    top_k_raw = _env(f"{_ENV_PREFIX}TOP_K", env_values, "5")
    environment = _env(f"{_ENV_PREFIX}ENV", env_values, "development")

    return Config(
        data_dir=data_dir,
        db_path=db_path,
        host=host or "127.0.0.1",
        port=int(port_raw or 8000),
        top_k=int(top_k_raw or 5),
        environment=environment or "development",
    )
