# AWS Integrated RAG System

This repository contains the code for a Retrieval-Augmented Generation (RAG) system built using AWS services. The system includes document indexing, searching, and response generation using AWS Lambda, Elasticsearch, and Amazon Comprehend.

## Features

- Document Storage (Amazon S3)
- Document Indexing and Search (AWS Lambda, Amazon Elasticsearch Service)
- Response Generation (AWS Lambda, LLM)
- Text Analysis (Amazon Comprehend)
- Infrastructure as Code (Serverless Framework)

## Getting Started

### Prerequisites

- Node.js
- Serverless Framework
- AWS CLI

### Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/aws-rag-system.git
    cd aws-rag-system
    ```

2. Install dependencies:
    ```bash
    npm install
    ```

3. Deploy the infrastructure:
    ```bash
    serverless deploy
    ```

4. Set up Elasticsearch index and S3 buckets:
    ```bash
    python backend/elasticsearch/setup_index.py
    python backend/s3/setup_buckets.py
    ```

## License

This project is licensed under the MIT License.
