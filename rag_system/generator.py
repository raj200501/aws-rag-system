"""Response generation logic for the local RAG pipeline."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from .analyzer import analyze_text
from .storage import SearchResult


def _build_context(results: List[SearchResult]) -> str:
    snippets = []
    for result in results:
        snippet = result.content.strip().replace("\n", " ")
        if len(snippet) > 240:
            snippet = snippet[:237] + "..."
        snippets.append(f"[{result.doc_id}] {snippet}")
    return "\n".join(snippets)


def generate_response(query: str, results: List[SearchResult]) -> Dict[str, object]:
    if not query:
        raise ValueError("query must be provided")

    context = _build_context(results)
    analysis = analyze_text(query)

    answer_lines = [
        "Answer (deterministic demo response)",
        f"Query: {query}",
        "",
        "Most relevant snippets:",
        context or "No matching documents found.",
        "",
        "Observed entities:",
    ]
    for entity in analysis["entities"]:
        answer_lines.append(f"- {entity['Text']} (score {entity['Score']})")

    answer_lines.append("")
    answer_lines.append("Key phrases:")
    for phrase in analysis["key_phrases"]:
        answer_lines.append(f"- {phrase['Text']} (score {phrase['Score']})")

    return {
        "answer": "\n".join(answer_lines),
        "context": context,
        "results": [asdict(result) for result in results],
        "analysis": analysis,
    }
