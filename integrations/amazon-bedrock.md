---
layout: integration
name: Amazon Bedrock
description: Use Models from AI21 Labs, Anthropic, Cohere, Meta, and Amazon via Amazon Bedrock with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/amazon-bedrock-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/amazon_bedrock
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aws.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Amazon Bedrock](https://aws.amazon.com/bedrock/) is a fully managed service that makes high-performing foundation models from leading AI startups and Amazon available for your use through a unified API. You can choose from various foundation models to find the one best suited for your use case. More information can be found on the [Amazon Bedrock documentation page](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html).

## Installation

Install the Amazon Bedrock integration:
```bash
pip install amazon-bedrock-haystack
```

## Usage

Once installed, you will have access to [AmazonBedrockChatGenerator](https://docs.haystack.deepset.ai/docs/amazonbedrockchatgenerator) and [AmazonBedrockGenerator](https://docs.haystack.deepset.ai/docs/amazonbedrockgenerator) components that support generative language models on Amazon Bedrock. 
You will also have access to the [AmazonBedrockTextEmbedder](https://docs.haystack.deepset.ai/docs/amazonbedrocktextembedder) and [AmazonBedrockDocumentEmbedder](https://docs.haystack.deepset.ai/docs/amazonbedrockdocumentembedder), which can be used to compute embeddings.
The integration also includes [S3Downloader](https://docs.haystack.deepset.ai/docs/s3downloader) that allows downloading files from AWS S3 buckets to the local filesystem. 

To use this integration, set the AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`) as environment variables or passed as [Secret](https://docs.haystack.deepset.ai/docs/secret-management) arguments. 

> Note: Make sure the region you set supports Amazon Bedrock.
For using `S3Downloader`, you also need to set `FILE_ROOT_PATH` (path where files will be downloaded).

### AmazonBedrockChatGenerator

To use this integration for chat models, initialize an `AmazonBedrockChatGenerator` with the model name:

Some supported models are: 
- **AI21 Labs'** Jamba 1.5 Large, Jamba 1.5 Mini
- **Amazon's** Nova Canvas, Nova Lite, Nova Pro
- **Amazon's** Titan Text G1 - Express, Titan Text G1 - Lite
- **Anthropic's** Claude chat models
- **Cohere's** Command, Command Light and other Command models
- **DeepSeek's** DeepSeek-R1
- **Meta's** Llama models
- **Mistral AI's** 

Get the complete list of models in [Supported foundation models in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)

```python
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator
from haystack.dataclasses import ChatMessage
    
generator = AmazonBedrockChatGenerator(model="amazon.nova-pro-v1:0")
messages = [ChatMessage.from_system("You are a helpful assistant that answers question in Spanish only"), 
            ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
    
response = generator.run(messages)
print(response)

```
Output: 
```js
{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='El procesamiento del lenguaje natural (PLN) es una rama de la inteligencia artificial que permite a las computadoras comprender, interpretar y generar lenguaje humano.')], _name=None, _meta={'model': 'amazon.nova-pro-v1:0', 'index': 0, 'finish_reason': 'end_turn', 'usage': {'prompt_tokens': 21, 'completion_tokens': 31, 'total_tokens': 52}})]}
```

### AmazonBedrockGenerator 

Most [supported models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) can be used with `AmazonBedrockGenerator`, but we highly recommend using the `AmazonBedrockChatGenerator` instead.

```python
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockGenerator

generator = AmazonBedrockGenerator(model="mistral.mixtral-8x7b-instruct-v0:1")
result = generator.run("Who is the best American actor?")
print(result)
```
Output: 
```shell
{'replies': ['It\'s subjective to determine the "best" American actor as it depends on personal preferences, critical acclaim, and the impact of their work. However, some of the most renowned and influential American actors include:\n\n1. Daniel Day-Lewis - Known for his versatility and commitment to his roles, Day-Lewis is a three-time Academy Award winner for Best Actor.\n2. Meryl Streep - With a record 21 Academy Award nominations and three wins, Streep is widely regarded as one of the greatest actresses in American film history.\n3. Jack Nicholson - A three-time Academy Award winner and 12-time nominee, Nicholson is known for his iconic roles in films like "One Flew Over the Cuckoo\'s Nest," "Terms of Endearment," and "As Good as It Gets."\n4. Robert De Niro - A two-time Academy Award winner, De Niro is known for his collaborations with Martin Scorsese and his memorable roles in films like "Taxi Driver," "Raging Bull," and "The Godfather: Part II."\n5. Leonardo DiCaprio - A four-time Academy Award nominee and one-time winner, DiCaprio has had a successful career in both blockbusters and independent films.\n\nThese are just a few examples of highly acclaimed American actors, and there are many other talented actors who could be considered for this title.'], 'meta': {'RequestId': 'ed9c8566-0b13-4c08-ba72-c88be1aecd02', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Mon, 28 Apr 2025 11:00:15 GMT', 'content-type': 'application/json', 'content-length': '1322', 'connection': 'keep-alive', 'x-amzn-requestid': 'ed9c8566-0b13-4c08-ba72-c88be1aecd02', 'x-amzn-bedrock-invocation-latency': '7065', 'x-amzn-bedrock-output-token-count': '323', 'x-amzn-bedrock-input-token-count': '16'}, 'RetryAttempts': 0}}
```

### Embedders

Three components are available for using embedding models with Amazon Bedrock: [`AmazonBedrockTextEmbedder`](https://docs.haystack.deepset.ai/docs/amazonbedrocktextembedder), [`AmazonBedrockDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/amazonbedrockdocumentembedder) and [`AmazonBedrockDocumentImageEmbedder`](https://docs.haystack.deepset.ai/docs/amazonbedrockdocumentimageembedder).

The supported models are "amazon.titan-embed-text-v1", "amazon.titan-embed-text-v2:0", "cohere.embed-english-v3," and "cohere.embed-multilingual-v3."

To create embeddings for textual documents, use `AmazonBedrockDocumentEmbedder` in your indexing pipeline. To create embeddings for image-based documents, use `AmazonBedrockDocumentImageEmbedder`. For generating embeddings for queries, use `AmazonBedrockTextEmbedder`. 

An example using `AmazonBedrockDocumentEmbedder` and `AmazonBedrockTextEmbedder`:

```python
from haystack import Pipeline
from haystack.dataclasses import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.amazon_bedrock import (
    AmazonBedrockDocumentEmbedder,
    AmazonBedrockTextEmbedder,
)
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", AmazonBedrockDocumentEmbedder(model="cohere.embed-english-v3"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})


query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", AmazonBedrockTextEmbedder(model="cohere.embed-english-v3"))
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

query = "Who lives in Berlin?"

result = query_pipeline.run({"text_embedder":{"text": query}})

print(result['retriever']['documents'][0])

# Document(id=..., content: 'My name is Wolfgang and I live in Berlin')
```

An example using `AmazonBedrockDocumentImageEmbedder` and `AmazonBedrockTextEmbedder`:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack_integrations.components.embedders.amazon_bedrock import (
    AmazonBedrockDocumentImageEmbedder,
    AmazonBedrockTextEmbedder,
)

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")


documents = [
    Document(content="A hyena", meta={"file_path": "hyena.png"}),
    Document(content="A dog", meta={"file_path": "dog.jpg"}),
]

indexing = Pipeline()
indexing.add_component("image_embedder", AmazonBedrockDocumentImageEmbedder(model="cohere.embed-english-v3"))
indexing.add_component("writer", DocumentWriter(document_store=document_store))
indexing.connect("image_embedder", "writer")
indexing.run({"image_embedder": {"documents": documents}})


query = Pipeline()
query.add_component("text_embedder", AmazonBedrockTextEmbedder(model="cohere.embed-english-v3"))
query.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query.connect("text_embedder.embedding", "retriever.query_embedding")

res = query.run({"text_embedder": {"text": "man's best friend"}})
```

### S3Downloader

Before using this component, you need to set `S3_DOWNLOADER_BUCKET` environment variable that specifies which S3 bucket to download files from. 

Here is an example of how to use the downloader in a pipeline.

```python
from haystack import Pipeline
from haystack.components.converters import PDFMinerToDocument
from haystack.components.routers import DocumentTypeRouter
from haystack.dataclasses import Document

from haystack_integrations.components.downloaders.s3 import S3Downloader

# Create a pipeline
pipe = Pipeline()

# Add S3Downloader to download files from S3
pipe.add_component(
    "downloader", 
    S3Downloader(
        file_root_path="/tmp/s3_downloads",
        file_extensions=[".pdf", ".txt"]
    )
)

# Route documents by file type
pipe.add_component(
    "router", 
    DocumentTypeRouter(
        file_path_meta_field="file_path",
        mime_types=["application/pdf", "text/plain"]
    )
)

# Convert PDFs to documents
pipe.add_component("pdf_converter", PDFMinerToDocument())

# Connect components
pipe.connect("downloader.documents", "router.documents")
pipe.connect("router.application/pdf", "pdf_converter.documents")

# Create documents with S3 file names
documents = [
    Document(meta={"file_name": "report.pdf"}),
    Document(meta={"file_name": "summary.txt"}),
]

# Run the pipeline
result = pipe.run({"downloader": {"documents": documents}})
```