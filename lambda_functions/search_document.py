import json

from rag_system.config import load_config
from rag_system.storage import search_documents


def lambda_handler(event, context):
    query = event.get("query")
    if not query:
        return {"statusCode": 400, "body": json.dumps("query is required")}

    config = load_config()
    results = search_documents(config.db_path, query, limit=config.top_k)

    return {
        "statusCode": 200,
        "body": json.dumps([result.__dict__ for result in results]),
    }
