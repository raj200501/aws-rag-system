from rag_system.config import load_config
from rag_system.storage import initialize_database


def setup_index() -> None:
    config = load_config()
    initialize_database(config.db_path)


if __name__ == "__main__":
    setup_index()
    print("Local search index created successfully")
