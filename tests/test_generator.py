import unittest

from rag_system.generator import generate_response
from rag_system.storage import SearchResult


class GeneratorTests(unittest.TestCase):
    def test_generate_response_includes_query(self):
        results = [
            SearchResult(
                doc_id="doc-1",
                content="Lambda is a serverless compute service.",
                source="seed",
                score=0.1,
                metadata={},
            )
        ]
        response = generate_response("What is Lambda?", results)
        self.assertIn("What is Lambda?", response["answer"])
        self.assertIn("doc-1", response["context"])

    def test_generate_response_requires_query(self):
        with self.assertRaises(ValueError):
            generate_response("", [])


if __name__ == "__main__":
    unittest.main()
