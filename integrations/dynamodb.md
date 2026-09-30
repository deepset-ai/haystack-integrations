---
layout: integration
name: Amazon DynamoDB
description: A Document Store for storing documents and running vector search with Amazon DynamoDB's native vector indexes
logo: /logos/aws.png
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/dynamodb-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/dynamodb
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/dynamodb-haystack.svg)](https://pypi.org/project/dynamodb-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dynamodb-haystack.svg)](https://pypi.org/project/dynamodb-haystack/)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/dynamodb.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/dynamodb.yml)

-----

**Table of Contents**

- Amazon DynamoDB Document Store for Haystack
  - [Overview](#overview)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Limitations](#limitations)
  - [License](#license)

## Overview

[Amazon DynamoDB](https://aws.amazon.com/dynamodb/) is a serverless NoSQL database. Its native vector search stores embeddings in a vector index directly on a table and queries them with the `SearchVectors` API, so your documents and their embeddings live next to your operational data without a separate vector database or synchronisation pipeline.

`DynamoDBDocumentStore` stores each Haystack `Document` as an item in a DynamoDB table with a vector index and retrieves documents by cosine similarity. `DynamoDBEmbeddingRetriever` wraps that retrieval as a pipeline component.

## Installation

Use `pip` to install `dynamodb-haystack`:

```bash
pip install dynamodb-haystack
```

DynamoDB's vector search requires `boto3 >= 1.43.66`, which the package installs for you. There is no local DynamoDB emulator with vector index support, so you need an AWS account.

## Usage

The Document Store uses the standard AWS credential chain. Set your credentials and region as environment variables, or rely on any other boto3 credential source such as an IAM role:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

Then initialize `DynamoDBDocumentStore`. With `create_table_if_not_exists=True` (the default), the table and its vector index are created on first use:

```python
from haystack_integrations.document_stores.dynamodb import DynamoDBDocumentStore

document_store = DynamoDBDocumentStore(
    table_name="haystack_documents",
    index_name="haystack_vector_index",
    embedding_dimension=768,
    region_name="us-east-1",
)
```

If you point the store at an existing table, it must have a single partition key named `id` and a cosine vector index on the `embedding` attribute with matching `index_name` and `embedding_dimension`.

### Writing Documents

```python
from haystack import Document

docs = [
    Document(content="DynamoDB stores embeddings in native vector indexes"),
    Document(content="Haystack makes building LLM pipelines easy"),
]
document_store.write_documents(docs)
print(document_store.count_documents())
```

Note: the documents above have no embeddings. To store documents with embeddings for vector similarity search, use the indexing pipeline in the [Embedding Retrieval](#embedding-retrieval) section below.

### Embedding Retrieval

Install the `sentence-transformers-haystack` integration to use the embedders:

```bash
pip install sentence-transformers-haystack
```

```python
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.sentence_transformers import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack_integrations.components.retrievers.dynamodb import DynamoDBEmbeddingRetriever

# Indexing
indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("embedder", "writer")
indexing.run({"embedder": {"documents": docs}})

# Querying
querying = Pipeline()
querying.add_component("embedder", SentenceTransformersTextEmbedder())
querying.add_component("retriever", DynamoDBEmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("embedder", "retriever")
results = querying.run({"embedder": {"text": "vector similarity search"}})
```

Scores follow Haystack's higher-is-better convention: an identical vector scores `1.0`, an opposite one `0.0`.

## Limitations

- `filter_documents`, `count_documents` and the filter-based bulk operations run a consistent full-table `Scan` and evaluate metadata filters client-side, so their cost grows with the table size.
- `SearchVectors` returns at most 100 candidates per request, so `top_k` cannot exceed 100. Metadata filters are applied to those candidates, so a selective filter can return fewer than `top_k` documents.
- Only cosine similarity is supported for now.
- A DynamoDB item is limited to 400 KB, which bounds a document's content, metadata and embedding together.

## License

`dynamodb-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
