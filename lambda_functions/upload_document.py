import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    es = Elasticsearch(
        hosts=[{'host': 'your-es-domain', 'port': 443}],
        http_auth=AWS4Auth('your-access-key', 'your-secret-key', 'us-east-1', 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    document = s3.get_object(Bucket=bucket, Key=key)
    content = document['Body'].read().decode('utf-8')

    es.index(index='documents', doc_type='_doc', id=key, body={'content': content})

    return {
        'statusCode': 200,
        'body': json.dumps('Document uploaded and indexed successfully')
    }
