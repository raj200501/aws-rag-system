from pathlib import Path

from rag_system.config import load_config


def create_bucket() -> Path:
    config = load_config()
    config.data_dir.mkdir(parents=True, exist_ok=True)
    return config.data_dir


if __name__ == "__main__":
    bucket_path = create_bucket()
    print(f"Local storage directory ready at {bucket_path}")
