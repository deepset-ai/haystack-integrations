---
layout: integration
name: AstraDB
description: A Document Store for storing and retrieval from AstraDB - built for Haystack 2.0.
authors:
  - name: Nicholas Brackley
    socials:
      github: hc33brackles
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: https://pypi.org/project/astra-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/astra
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/astradb.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Note](#note)
- [License](#license)

## Overview


DataStax Astra DB is a serverless vector database built on Apache Cassandra, and it supports vector-based search and auto-scaling. You can deploy it on AWS, GCP, or Azure and easily expand to one or more regions within those clouds for multi-region availability, low latency data access, data sovereignty, and to avoid cloud vendor lock-in. For more information, see the [DataStax documentation](https://docs.datastax.com/en/astra-serverless/docs/).


This integration allows you to use AstraDB for document storage and retrieval in your Haystack 2.0 pipelines. This page provides instructions on how to initialize an AstraDB instance and connect with Haystack.

## Components

- [`AstraDocumentStore`](https://docs.haystack.deepset.ai/v2.0/docs/astradocumentstore). This component serves as a persistent data store for your Haystack documents, and supports a number of embedding models and vector dimensions.
- [`AstraEmbeddingRetriever`](https://docs.haystack.deepset.ai/v2.0/docs/astraretriever) This is an embedding-based Retriever compatible with the Astra Document Store.


## Initialization

First you need to [sign up for a free DataStax account](https://astra.datastax.com/signup). Follow these instructions for [creating an AstraDB Database](https://docs.datastax.com/en/astra/astra-db-vector/databases/create-database.html#create-a-serverless-non-vector-database) in the Datastax console. Make sure you create a collection, a keyspace name, and an access token since you'll need those later.

## Installation

```console
pip install astra-haystack
```
## Usage

This package includes Astra Document Store and Astra Retriever classes that integrate with Haystack 2.0, allowing you to easily perform document retrieval or RAG with AstraDB, and include those functions in Haystack pipelines.

In order to connect AstraDB with Haystack, you'll need these pieces of information from your Datastax console:
- API Endpoint
- Token
- Astra collection name (otherwise `documents` will be used)
- Astra keyspace name (otherwise `default_keyspace` will be used)

### how to use the `AstraDocumentStore`:

```python
from haystack import Document
from haystack_integrations.document_stores.astra import AstraDocumentStore

# Make sure ASTRA_API_ENDPOINT and ASTRA_TOKEN environment variables are set
document_store = AstraDocumentStore()

document_store.write_documents([
    Document(content="This is first"),
    Document(content="This is second")
    ])
print(document_store.count_documents())
```

### How to use the `AstraEmbeddingRetriever`

```python
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack_integrations.components.retrievers.astra import AstraEmbeddingRetriever
from haystack_integrations.document_stores.astra import AstraDocumentStore


# Make sure ASTRA_API_ENDPOINT and ASTRA_TOKEN environment variables are set
document_store = AstraDocumentStore()

model = "sentence-transformers/all-mpnet-base-v2"

documents = [Document(content="There are over 7,000 languages spoken around the world today."),
						Document(content="Elephants have been observed to behave in a way that indicates a high level of self-awareness, such as recognizing themselves in mirrors."),
						Document(content="In certain parts of the world, like the Maldives, Puerto Rico, and San Diego, you can witness the phenomenon of bioluminescent waves.")]

document_embedder = SentenceTransformersDocumentEmbedder(model=model_name_or_path)  
document_embedder.warm_up()
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))
query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model=model_name_or_path))
query_pipeline.add_component("retriever", AstraEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

query = "How many languages are there?"

result = query_pipeline.run({"text_embedder": {"text": query}})

print(result['retriever']['documents'][0])
```

### Note:
Please note that the current version of Astra JSON API does not support the following operators:
$lt, $lte, $gt, $gte, $nin, $not, $neq 
As well as filtering with none values (these won't be inserted as the result is stored as json document, and it doesn't store nones)

### License

`astra-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
