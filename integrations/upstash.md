---
layout: integration
name: Upstash Vector
description: Use Upstash Vector as a serverless document store in Haystack pipelines — zero infrastructure, pay-as-you-go, with native hybrid search via Reciprocal Rank Fusion.
authors:
    - name: Avish Sinha
      socials:
        github: avish006
        linkedin: https://www.linkedin.com/in/avish-sinha
pypi: https://pypi.org/project/upstash-haystack
repo: https://github.com/avish006/upstash_haystack
report_issue: https://github.com/avish006/upstash_haystack/issues
type: Document Store
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Upstash Vector](https://upstash.com/vector) is a serverless, pay-as-you-go vector database that you can use in Haystack pipelines with the `UpstashDocumentStore`. It requires zero infrastructure — no Docker containers, no servers, no clusters to manage.

This integration provides three components:

| Component | Description |
|---|---|
| `UpstashDocumentStore` | Full-featured document store backed by Upstash Vector |
| `UpstashEmbeddingRetriever` | Dense retrieval using cosine/dot-product similarity |
| `UpstashHybridRetriever` | Dense + sparse hybrid search via native Reciprocal Rank Fusion (RRF) |

## Installation

```bash
pip install upstash-haystack
```

## Usage

To use Upstash Vector as your data storage for Haystack LLM pipelines, you must have an [Upstash account](https://console.upstash.com/) and a Vector index. Once you have those, set your credentials as environment variables:

```bash
export UPSTASH_VECTOR_REST_URL="https://your-endpoint.upstash.io"
export UPSTASH_VECTOR_REST_TOKEN="your-token"
```

Then initialize an `UpstashDocumentStore`:

```python
from haystack_integrations.document_stores.upstash import UpstashDocumentStore

# Reads UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN from env
document_store = UpstashDocumentStore()
```

### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.converters import MarkdownToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.upstash import UpstashDocumentStore

document_store = UpstashDocumentStore()

indexing = Pipeline()
indexing.add_component("converter", MarkdownToDocument())
indexing.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=2))
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "splitter")
indexing.connect("splitter", "embedder")
indexing.connect("embedder", "writer")

indexing.run({"converter": {"sources": ["filename.md"]}})
```

### RAG Query Pipeline

Once documents are indexed, use `UpstashEmbeddingRetriever` to retrieve them in a RAG pipeline:

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret
from haystack_integrations.document_stores.upstash import UpstashDocumentStore
from haystack_integrations.components.retrievers.upstash import UpstashEmbeddingRetriever

document_store = UpstashDocumentStore()

prompt_template = """Answer the following query based on the provided context. If the context does
                     not include an answer, reply with 'I don't know'.
                     Query: {{query}}
                     Documents:
                     {% for doc in documents %}
                        {{ doc.content }}
                     {% endfor %}
                     Answer:
                  """

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
query_pipeline.add_component("retriever", UpstashEmbeddingRetriever(document_store=document_store))
query_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
query_pipeline.add_component("generator", OpenAIGenerator(model="gpt-4o-mini"))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "prompt_builder.documents")
query_pipeline.connect("prompt_builder", "generator")

query = "What is Upstash Vector?"
results = query_pipeline.run(
    {
        "text_embedder": {"text": query},
        "prompt_builder": {"query": query},
    }
)
```

### Hybrid Retrieval (Dense + Sparse)

`UpstashHybridRetriever` uses Upstash Vector's native Reciprocal Rank Fusion (RRF) to combine dense and sparse signals without any custom fusion logic:

```python
from haystack.dataclasses import SparseEmbedding
from haystack_integrations.document_stores.upstash import UpstashDocumentStore
from haystack_integrations.components.retrievers.upstash import UpstashHybridRetriever

document_store = UpstashDocumentStore()
retriever = UpstashHybridRetriever(document_store=document_store)

result = retriever.run(
    query_embedding=[0.1, 0.2, 0.3],
    query_sparse_embedding=SparseEmbedding(indices=[0, 5, 12], values=[0.9, 0.4, 0.2]),
    top_k=5,
)
print(result["documents"])
```

### Filtering

```python
# Equality filter
docs = document_store.filter_documents(
    filters={"field": "meta.category", "operator": "==", "value": "science"}
)

# Compound AND filter
docs = document_store.filter_documents(
    filters={
        "operator": "AND",
        "conditions": [
            {"field": "meta.category", "operator": "==", "value": "science"},
            {"field": "meta.year", "operator": ">", "value": 2020},
        ],
    }
)
```