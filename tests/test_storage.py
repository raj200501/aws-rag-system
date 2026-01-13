import tempfile
import unittest
from pathlib import Path

from rag_system.storage import (
    DocumentRecord,
    add_document,
    add_documents,
    get_document,
    initialize_database,
    list_documents,
    search_documents,
)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "rag.db"
        initialize_database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_get_document(self):
        record = add_document(self.db_path, "doc-1", "hello world", "unit", {"tag": "a"})
        fetched = get_document(self.db_path, "doc-1")
        self.assertEqual(record.doc_id, fetched.doc_id)
        self.assertEqual(fetched.metadata["tag"], "a")

    def test_add_documents_and_list(self):
        records = [
            DocumentRecord("doc-1", "alpha beta", "seed", {}),
            DocumentRecord("doc-2", "beta gamma", "seed", {"team": "ops"}),
        ]
        add_documents(self.db_path, records)
        listed = list_documents(self.db_path)
        self.assertEqual(len(listed), 2)
        self.assertEqual(listed[1].metadata["team"], "ops")

    def test_search_documents(self):
        add_document(self.db_path, "doc-1", "AWS Lambda scales automatically", "seed")
        add_document(self.db_path, "doc-2", "Amazon S3 stores objects", "seed")
        results = search_documents(self.db_path, "Lambda", limit=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].doc_id, "doc-1")

    def test_search_documents_strips_punctuation(self):
        add_document(self.db_path, "doc-3", "Step Functions coordinates workflows", "seed")
        results = search_documents(self.db_path, "What does Step Functions do?", limit=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].doc_id, "doc-3")


if __name__ == "__main__":
    unittest.main()
