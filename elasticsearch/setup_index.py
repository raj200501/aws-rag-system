from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def setup_index():
    es = Elasticsearch(
        hosts=[{'host': 'your-es-domain', 'port': 443}],
        http_auth=AWS4Auth('your-access-key', 'your-secret-key', 'us-east-1', 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    es.indices.create(index='documents', body={
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0
        },
        'mappings': {
            '_doc': {
                'properties': {
                    'content': {
                        'type': 'text'
                    }
                }
            }
        }
    })

if __name__ == '__main__':
    setup_index()
    print("Elasticsearch index created successfully")
