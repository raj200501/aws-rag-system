import os
from pathlib import Path
import tempfile
import unittest

from rag_system.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_config_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path.cwd()
            os.chdir(temp_dir)
            try:
                config = load_config()
            finally:
                os.chdir(cwd)

        self.assertTrue(str(config.db_path).endswith(".rag_data/rag.db"))
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.top_k, 5)

    def test_load_config_from_env_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "RAG_PORT=9000\nRAG_TOP_K=3\nRAG_DATA_DIR=.data\n",
                encoding="utf-8",
            )
            cwd = Path.cwd()
            os.chdir(temp_dir)
            try:
                config = load_config(env_path)
            finally:
                os.chdir(cwd)

        self.assertEqual(config.port, 9000)
        self.assertEqual(config.top_k, 3)
        self.assertTrue(str(config.data_dir).endswith(".data"))


if __name__ == "__main__":
    unittest.main()
