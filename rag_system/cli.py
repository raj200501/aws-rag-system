"""Command-line interface for the local RAG system."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .config import load_config
from .storage import (
    DocumentRecord,
    add_document,
    add_documents,
    ensure_sample_data,
    initialize_database,
    list_documents,
    search_documents,
)
from .generator import generate_response
from .analyzer import analyze_text


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cmd_init(_: argparse.Namespace) -> int:
    config = load_config()
    initialize_database(config.db_path)
    print(f"Initialized database at {config.db_path}")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    config = load_config()
    initialize_database(config.db_path)

    records = []
    for file_path in args.paths:
        path = Path(file_path)
        content = _load_text(path)
        records.append(
            DocumentRecord(
                doc_id=path.stem,
                content=content,
                source=str(path),
                metadata={"filename": path.name},
            )
        )

    inserted = add_documents(config.db_path, records)
    print(json.dumps({"inserted": len(inserted)}, indent=2))
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    config = load_config()
    inserted = ensure_sample_data(config.db_path, Path(args.sample_dir))
    print(json.dumps({"seeded": len(inserted)}, indent=2))
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    config = load_config()
    docs = list_documents(config.db_path)
    print(json.dumps([doc.__dict__ for doc in docs], indent=2))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    config = load_config()
    results = search_documents(config.db_path, args.query, limit=config.top_k)
    print(json.dumps([result.__dict__ for result in results], indent=2))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    config = load_config()
    results = search_documents(config.db_path, args.query, limit=config.top_k)
    response = generate_response(args.query, results)
    print(json.dumps(response, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    analysis = analyze_text(args.text)
    print(json.dumps(analysis, indent=2))
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    config = load_config()
    initialize_database(config.db_path)
    record = add_document(
        config.db_path,
        doc_id=args.doc_id,
        content=args.content,
        source=args.source,
        metadata=json.loads(args.metadata) if args.metadata else {},
    )
    print(json.dumps(record.__dict__, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local RAG system CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the local database").set_defaults(
        func=cmd_init
    )

    ingest_parser = subparsers.add_parser("ingest", help="Ingest text files")
    ingest_parser.add_argument("paths", nargs="+", help="Paths to .txt files")
    ingest_parser.set_defaults(func=cmd_ingest)

    seed_parser = subparsers.add_parser("seed", help="Seed from sample documents")
    seed_parser.add_argument("sample_dir", help="Directory with sample .txt files")
    seed_parser.set_defaults(func=cmd_seed)

    subparsers.add_parser("list", help="List indexed documents").set_defaults(
        func=cmd_list
    )

    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_search)

    generate_parser = subparsers.add_parser("generate", help="Generate response")
    generate_parser.add_argument("query", help="User query")
    generate_parser.set_defaults(func=cmd_generate)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze text")
    analyze_parser.add_argument("text", help="Text to analyze")
    analyze_parser.set_defaults(func=cmd_analyze)

    add_parser = subparsers.add_parser("add", help="Add a single document")
    add_parser.add_argument("doc_id", help="Document id")
    add_parser.add_argument("content", help="Document content")
    add_parser.add_argument("--source", default="manual", help="Source label")
    add_parser.add_argument(
        "--metadata",
        default="",
        help="JSON metadata string (optional)",
    )
    add_parser.set_defaults(func=cmd_add)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
