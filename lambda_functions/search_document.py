import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    es = Elasticsearch(
        hosts=[{'host': 'your-es-domain', 'port': 443}],
        http_auth=AWS4Auth('your-access-key', 'your-secret-key', 'us-east-1', 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    query = event['query']
    response = es.search(index='documents', body={'query': {'match': {'content': query}}})

    return {
        'statusCode': 200,
        'body': json.dumps(response['hits']['hits'])
    }
