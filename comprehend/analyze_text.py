import json

from rag_system.analyzer import analyze_text


def lambda_handler(event, context):
    text = event.get("text")
    if not text:
        return {"statusCode": 400, "body": json.dumps("text is required")}

    analysis = analyze_text(text)

    return {
        "statusCode": 200,
        "body": json.dumps(analysis),
    }
