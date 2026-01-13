import json

from rag_system.config import load_config
from rag_system.storage import add_document, initialize_database


def lambda_handler(event, context):
    config = load_config()
    initialize_database(config.db_path)

    doc_id = event.get("id")
    content = event.get("content")
    source = event.get("source", "lambda")
    metadata = event.get("metadata", {})

    if not doc_id or not content:
        return {
            "statusCode": 400,
            "body": json.dumps("id and content are required"),
        }

    record = add_document(config.db_path, doc_id, content, source, metadata)

    return {
        "statusCode": 200,
        "body": json.dumps(record.__dict__),
    }
