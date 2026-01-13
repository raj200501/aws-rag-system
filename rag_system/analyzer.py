"""Simple text analysis mimicking Comprehend-style outputs."""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']+")


def _tokenize(text: str) -> List[str]:
    return [match.group(0) for match in _WORD_RE.finditer(text)]


def analyze_text(text: str) -> Dict[str, List[Dict[str, object]]]:
    if not text:
        raise ValueError("text must be provided")

    tokens = _tokenize(text)
    lower_tokens = [token.lower() for token in tokens]

    entity_candidates = []
    for token in tokens:
        if token[0].isupper() and len(token) > 2:
            entity_candidates.append(token)

    entity_counts = Counter(entity_candidates)
    entities = [
        {"Text": token, "Score": round(count / len(tokens), 3)}
        for token, count in entity_counts.most_common(10)
    ]

    phrase_counts = Counter()
    for idx in range(len(lower_tokens) - 1):
        phrase = f"{lower_tokens[idx]} {lower_tokens[idx + 1]}"
        phrase_counts[phrase] += 1

    key_phrases = [
        {"Text": phrase, "Score": round(count / len(lower_tokens), 3)}
        for phrase, count in phrase_counts.most_common(10)
    ]

    return {
        "entities": entities,
        "key_phrases": key_phrases,
    }
