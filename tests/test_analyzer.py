import unittest

from rag_system.analyzer import analyze_text


class AnalyzerTests(unittest.TestCase):
    def test_analyze_text_returns_entities(self):
        analysis = analyze_text("Amazon S3 stores objects and AWS Lambda runs code.")
        entities = {entity["Text"] for entity in analysis["entities"]}
        self.assertIn("Amazon", entities)
        self.assertIn("Lambda", entities)

    def test_analyze_text_raises_on_empty(self):
        with self.assertRaises(ValueError):
            analyze_text("")


if __name__ == "__main__":
    unittest.main()
