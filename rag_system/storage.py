"""SQLite-backed storage and search for documents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from typing import Iterable, List, Optional
import re


@dataclass(frozen=True)
class DocumentRecord:
    doc_id: str
    content: str
    source: str
    metadata: dict


@dataclass(frozen=True)
class SearchResult:
    doc_id: str
    content: str
    source: str
    score: float
    metadata: dict


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA foreign_keys=ON;")
    return connection


def initialize_database(db_path: Path) -> None:
    with _connect(db_path) as connection:
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(
                doc_id,
                content,
                source,
                metadata,
                tokenize='porter'
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_meta (
                doc_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.commit()


def add_document(
    db_path: Path,
    doc_id: str,
    content: str,
    source: str = "manual",
    metadata: Optional[dict] = None,
) -> DocumentRecord:
    if not doc_id:
        raise ValueError("doc_id must be provided")
    if not content:
        raise ValueError("content must be provided")

    metadata_payload = metadata or {}
    with _connect(db_path) as connection:
        connection.execute("DELETE FROM documents WHERE doc_id = ?;", (doc_id,))
        connection.execute("DELETE FROM document_meta WHERE doc_id = ?;", (doc_id,))
        connection.execute(
            "INSERT INTO documents (doc_id, content, source, metadata) VALUES (?, ?, ?, ?);",
            (doc_id, content, source, json.dumps(metadata_payload)),
        )
        connection.execute(
            "INSERT INTO document_meta (doc_id, created_at) VALUES (?, datetime('now'));",
            (doc_id,),
        )
        connection.commit()

    return DocumentRecord(
        doc_id=doc_id,
        content=content,
        source=source,
        metadata=metadata_payload,
    )


def add_documents(db_path: Path, records: Iterable[DocumentRecord]) -> List[DocumentRecord]:
    inserted: List[DocumentRecord] = []
    with _connect(db_path) as connection:
        for record in records:
            connection.execute("DELETE FROM documents WHERE doc_id = ?;", (record.doc_id,))
            connection.execute("DELETE FROM document_meta WHERE doc_id = ?;", (record.doc_id,))
            connection.execute(
                "INSERT INTO documents (doc_id, content, source, metadata) VALUES (?, ?, ?, ?);",
                (
                    record.doc_id,
                    record.content,
                    record.source,
                    json.dumps(record.metadata),
                ),
            )
            connection.execute(
                "INSERT INTO document_meta (doc_id, created_at) VALUES (?, datetime('now'));",
                (record.doc_id,),
            )
            inserted.append(record)
        connection.commit()
    return inserted


def list_documents(db_path: Path) -> List[DocumentRecord]:
    with _connect(db_path) as connection:
        rows = connection.execute(
            "SELECT doc_id, content, source, metadata FROM documents ORDER BY doc_id ASC;"
        ).fetchall()
    return [
        DocumentRecord(
            doc_id=row["doc_id"],
            content=row["content"],
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
        for row in rows
    ]


def get_document(db_path: Path, doc_id: str) -> Optional[DocumentRecord]:
    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT doc_id, content, source, metadata FROM documents WHERE doc_id = ?;",
            (doc_id,),
        ).fetchone()
    if not row:
        return None
    return DocumentRecord(
        doc_id=row["doc_id"],
        content=row["content"],
        source=row["source"],
        metadata=json.loads(row["metadata"] or "{}"),
    )


def search_documents(db_path: Path, query: str, limit: int = 5) -> List[SearchResult]:
    if not query:
        raise ValueError("query must be provided")
    if limit <= 0:
        raise ValueError("limit must be positive")

    normalized = re.sub(r"[^\w\s'-]", " ", query).strip()
    tokens = normalized.split()
    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "do",
        "does",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
    }
    tokens = [token for token in tokens if token.lower() not in stop_words]
    normalized = " ".join(tokens)
    if not normalized:
        raise ValueError("query must contain searchable terms")

    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT doc_id, content, source, metadata, bm25(documents) AS score
            FROM documents
            WHERE documents MATCH ?
            ORDER BY score
            LIMIT ?;
            """,
            (normalized, limit),
        ).fetchall()

    return [
        SearchResult(
            doc_id=row["doc_id"],
            content=row["content"],
            source=row["source"],
            score=float(row["score"]),
            metadata=json.loads(row["metadata"] or "{}"),
        )
        for row in rows
    ]


def ensure_sample_data(db_path: Path, sample_dir: Path) -> List[DocumentRecord]:
    initialize_database(db_path)
    if not sample_dir.exists():
        return []
    records = []
    for path in sorted(sample_dir.glob("*.txt")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        records.append(
            DocumentRecord(
                doc_id=path.stem,
                content=content,
                source=str(path),
                metadata={"filename": path.name},
            )
        )
    return add_documents(db_path, records)
