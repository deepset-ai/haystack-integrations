---
layout: integration
name: TopK
description: Use the TopK database with Haystack
authors:
    - name: TopK
      socials:
        github: topk-io
        twitter: topk_io
        linkedin: https://www.linkedin.com/company/topkio/
pypi: https://pypi.org/project/topk-haystack/
repo: https://github.com/topk-io/topk-haystack
type: Document Store
report_issue: https://github.com/topk-io/topk-haystack/issues
logo: /logos/topk.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [RAG pipeline](#rag-pipeline)
- [Retrievers](#retrievers)
- [Multi-tenant workloads](#multi-tenant-workloads)
- [Resources](#resources)
- [License](#license)

## Overview

[TopK](https://topk.io) is a hosted database powering fast vector search, keyword search (BM25), hybrid search and multi-vector search.

This integration ships with TopK Document Store and five retrievers you can use to best fit your use case:

- [`TopKSemanticRetriever`](#semantic-retriever) — semantic search with server-side embedding, no embedder component needed
- [`TopKBM25Retriever`](#bm25-keyword-retriever) — keyword search using BM25 scoring
- [`TopKEmbeddingRetriever`](#dense-vector-retriever) — dense vector search with your own embedding model
- [`TopKHybridRetriever`](#hybrid-retriever) — combines vector and BM25 scores in a single query
- [`TopKMetadataRetriever`](#metadata-filtering-retriever) — filter documents by metadata fields

## Installation

```bash
pip install topk-haystack
```

## Prerequisites

Before you set up TopK Document Store in Haystack, you'll need:

- TopK API key — get one from the [TopK console](https://console.topk.io/api-key)
- Region identifier — see the list of [available regions](https://docs.topk.io/regions)

## Quick start

The fastest way to build a RAG pipeline with TopK is the `TopKSemanticRetriever`. TopK handles embedding server-side — no embedder component needed:

```python
import os
from haystack import Document, Pipeline
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret

from haystack_integrations.components.topk import TopKSemanticRetriever
from haystack_integrations.document_stores.topk import TopKDocumentStore

store = TopKDocumentStore(
    api_key=Secret.from_env_var("TOPK_API_KEY"),
    region="aws-us-east-1-elastica",
    collection_name="my-docs",
)

# Index
indexing = Pipeline()
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.run({"writer": {"documents": [
    Document(content="Rust guarantees memory safety without a garbage collector."),
    Document(content="Python is known for readable syntax and scientific libraries."),
]}})

# Query — no embedder needed
retriever = TopKSemanticRetriever(document_store=store, top_k=3)
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
result = pipeline.run({"retriever": {"query": "memory safe systems programming"}})

for doc in result["retriever"]["documents"]:
    print(f"[{doc.score:.3f}] {doc.content}")
```

## RAG pipeline

```python
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

from haystack_integrations.components.topk import TopKSemanticRetriever
from haystack_integrations.document_stores.topk import TopKDocumentStore

store = TopKDocumentStore(
    api_key=Secret.from_env_var("TOPK_API_KEY"),
    region="aws-us-east-1-elastica",
    collection_name="my-docs",
)

template = [
    ChatMessage.from_system("Answer using only the context below.\n{% for doc in documents %}{{ doc.content }}\n{% endfor %}"),
    ChatMessage.from_user("{{ question }}"),
]

rag = Pipeline()
rag.add_component("retriever", TopKSemanticRetriever(document_store=store, top_k=5))
rag.add_component("prompt", ChatPromptBuilder(template=template))
rag.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
rag.connect("retriever.documents", "prompt.documents")
rag.connect("prompt.prompt", "llm.messages")

result = rag.run({
    "retriever": {"query": "What makes Rust memory safe?"},
    "prompt": {"question": "What makes Rust memory safe?"},
})
print(result["llm"]["replies"][0].text)
```

## Retrievers

### Semantic Retriever

TopK handles embedding server-side — no embedder component needed. Pass a plain text query and TopK returns semantically relevant documents:

```python
from haystack_integrations.components.topk import TopKSemanticRetriever

retriever = TopKSemanticRetriever(document_store=store, top_k=5)
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
result = pipeline.run({"retriever": {"query": "memory safe systems programming"}})
```

### BM25 Keyword Retriever

```python
from haystack_integrations.components.topk import TopKBM25Retriever

retriever = TopKBM25Retriever(document_store=store, top_k=5)
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
result = pipeline.run({"retriever": {"query": "garbage collector memory"}})
```

### Dense Vector Retriever

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret

from haystack_integrations.components.topk import TopKEmbeddingRetriever
from haystack_integrations.document_stores.topk import TopKDocumentStore

MODEL = "sentence-transformers/all-MiniLM-L6-v2"

store = TopKDocumentStore(
    api_key=Secret.from_env_var("TOPK_API_KEY"),
    region="aws-us-east-1-elastica",
    collection_name="my-docs",
    embedding_dim=384,  # must match the model
)

# Indexing
indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(model=MODEL))
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.connect("embedder.documents", "writer.documents")

# Querying
query_pipeline = Pipeline()
query_pipeline.add_component("embedder", SentenceTransformersTextEmbedder(model=MODEL))
query_pipeline.add_component("retriever", TopKEmbeddingRetriever(document_store=store, top_k=5))
query_pipeline.connect("embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"embedder": {"text": "type safe programming"}})
```

### Hybrid Retriever

Combines dense vector similarity and BM25 keyword scoring in a single query, ranked by the sum of both scores.

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.topk import TopKHybridRetriever

MODEL = "sentence-transformers/all-MiniLM-L6-v2"

retriever = TopKHybridRetriever(document_store=store, top_k=5)
query_pipeline = Pipeline()
query_pipeline.add_component("embedder", SentenceTransformersTextEmbedder(model=MODEL))
query_pipeline.add_component("retriever", retriever)
query_pipeline.connect("embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({
    "embedder": {"text": "concurrent network services"},
    "retriever": {"query": "goroutines channels"},
})
```

### Metadata Filtering Retriever

```python
from haystack_integrations.components.topk import TopKMetadataRetriever

retriever = TopKMetadataRetriever(document_store=store, top_k=5)
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)

result = pipeline.run({"retriever": {"filters": {
    "operator": "AND",
    "conditions": [
        {"field": "meta.language", "operator": "==", "value": "en"},
        {"field": "meta.year", "operator": ">=", "value": 2020},
    ],
}}})
```

Supported filter operators: `==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `not in`, `AND`, `OR`, `NOT`.

## Multi-tenant workloads

Use the `partition` parameter to scope all reads and writes to a logical partition.
Different partitions in the same collection are fully isolated, enabling multi-tenant
workloads that scale to billions of documents.

```python
store_a = TopKDocumentStore(
    api_key=Secret.from_env_var("TOPK_API_KEY"),
    region="aws-us-east-1-elastica",
    collection_name="shared",
    partition="tenant-a",
)
store_b = TopKDocumentStore(
    api_key=Secret.from_env_var("TOPK_API_KEY"),
    region="aws-us-east-1-elastica",
    collection_name="shared",
    partition="tenant-b",
)
```

## Resources

- [Benchmarks](https://www.topk.io/benchmarks)
- [Pricing](https://www.topk.io/pricing)

## License

`topk-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.