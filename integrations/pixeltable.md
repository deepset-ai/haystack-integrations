---
layout: integration
name: Pixeltable
description: Document Store and Retriever backed by Pixeltable — persistent, versioned, multimodal data infrastructure for AI applications.
authors:
    - name: Pixeltable
      socials:
        github: pixeltable
        twitter: pixeltable
        linkedin: https://www.linkedin.com/company/pixeltable/
pypi: https://pypi.org/project/haystack-pixeltable/
repo: https://github.com/pixeltable/haystack-pixeltable
type: Document Store
report_issue: https://github.com/pixeltable/haystack-pixeltable/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/haystack-pixeltable.svg)](https://pypi.org/project/haystack-pixeltable/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/haystack-pixeltable.svg)](https://pypi.org/project/haystack-pixeltable/)
[![CI](https://github.com/pixeltable/haystack-pixeltable/actions/workflows/ci.yml/badge.svg)](https://github.com/pixeltable/haystack-pixeltable/actions/workflows/ci.yml)

---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Document Store](#document-store)
  - [Retriever](#retriever)
  - [In a Haystack Pipeline](#in-a-haystack-pipeline)
  - [Filtering](#filtering)
  - [Pixeltable Escape Hatch](#pixeltable-escape-hatch)
- [License](#license)

## Overview

[Pixeltable](https://pixeltable.com/) is open-source Python data infrastructure for multimodal AI. It provides persistent, versioned tables that store text, images, video, audio, and documents alongside embeddings and metadata — with automatic incremental computation via computed columns.

This integration provides two components:

- **`PixeltableDocumentStore`** — a Haystack `DocumentStore` backed by a Pixeltable table with a built-in embedding index.
- **`PixeltableRetriever`** — a Haystack `Retriever` component that performs vector similarity search.

### Why Pixeltable as a Document Store?

| Feature | Pixeltable | Typical vector DBs |
|---------|-----------|-------------------|
| Persistent storage | Built-in (embedded PostgreSQL) | Varies |
| Computed columns | Native — auto-run transforms on insert | No |
| Version history | Built-in — time-travel queries | No |
| Multimodal types | Image, Video, Audio, Document | Text only |
| Metadata filtering | JSON + SQL predicates | Limited |
| Embedding auto-compute | Via computed columns | Manual |

The `.table` escape hatch lets you break out of the Haystack interface to use the full Pixeltable API — add computed columns, run LLM inference on insert, query version history, and work with multimodal data.

## Installation

```bash
pip install haystack-pixeltable
```

## Usage

### Document Store

```python
from haystack import Document
from haystack_pixeltable import PixeltableDocumentStore

store = PixeltableDocumentStore(
    table_name="myproject.docs",
    embedding_dimension=1536,
)

store.write_documents([
    Document(
        content="Pixeltable is multimodal data infrastructure.",
        embedding=[0.1] * 1536,
        meta={"category": "infra"},
    ),
    Document(
        content="Haystack is a framework for building RAG pipelines.",
        embedding=[0.2] * 1536,
        meta={"category": "frameworks"},
    ),
])

print(store.count_documents())  # 2
```

### Retriever

```python
from haystack_pixeltable import PixeltableDocumentStore, PixeltableRetriever

store = PixeltableDocumentStore(
    table_name="myproject.docs",
    embedding_dimension=1536,
)
retriever = PixeltableRetriever(document_store=store, top_k=5)

result = retriever.run(query_embedding=[0.1] * 1536)
for doc in result["documents"]:
    print(f"{doc.content} (score: {doc.score:.3f})")
```

### In a Haystack Pipeline

```python
from haystack import Pipeline
from haystack.components.embedders import (
    SentenceTransformersTextEmbedder,
    SentenceTransformersDocumentEmbedder,
)
from haystack.components.writers import DocumentWriter
from haystack_pixeltable import PixeltableDocumentStore, PixeltableRetriever

store = PixeltableDocumentStore(
    table_name="rag.knowledge",
    embedding_dimension=384,
)

# Indexing pipeline
indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.connect("embedder", "writer")

# Query pipeline
query = Pipeline()
query.add_component("embedder", SentenceTransformersTextEmbedder())
query.add_component("retriever", PixeltableRetriever(document_store=store, top_k=5))
query.connect("embedder.embedding", "retriever.query_embedding")

result = query.run({"embedder": {"text": "What is multimodal AI?"}})
```

### Filtering

The Document Store supports the [Haystack filter specification](https://docs.haystack.deepset.ai/docs/metadata-filtering):

```python
# Simple comparison
store.filter_documents(
    filters={"field": "meta.category", "operator": "==", "value": "science"}
)

# Compound AND
store.filter_documents(filters={
    "operator": "AND",
    "conditions": [
        {"field": "meta.category", "operator": "==", "value": "science"},
        {"field": "meta.score", "operator": ">", "value": 0.5},
    ],
})

# Compound OR
store.filter_documents(filters={
    "operator": "OR",
    "conditions": [
        {"field": "meta.source", "operator": "==", "value": "arxiv"},
        {"field": "meta.source", "operator": "==", "value": "pubmed"},
    ],
})
```

### Pixeltable Escape Hatch

Access the underlying Pixeltable table for operations beyond the Haystack interface:

```python
store = PixeltableDocumentStore(
    table_name="myproject.docs", embedding_dimension=1536
)
t = store.table

# Add a computed column that auto-summarizes every document on insert
import pixeltable.functions.openai as openai

t.add_computed_column(
    summary=openai.chat_completions(
        messages=[{"role": "user", "content": t.content}],
        model="gpt-4o-mini",
    )
)

# Query with Pixeltable's full API
results = t.select(t.content, t.summary).collect()
```

## License

[Apache 2.0](https://github.com/pixeltable/haystack-pixeltable/blob/main/LICENSE)
