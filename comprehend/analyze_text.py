import boto3
import json

def lambda_handler(event, context):
    comprehend = boto3.client('comprehend')
    text = event['text']

    entities = comprehend.detect_entities(Text=text, LanguageCode='en')
    key_phrases = comprehend.detect_key_phrases(Text=text, LanguageCode='en')

    return {
        'statusCode': 200,
        'body': json.dumps({
            'entities': entities['Entities'],
            'key_phrases': key_phrases['KeyPhrases']
        })
    }
