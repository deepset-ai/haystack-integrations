---
layout: integration
name: DXMT
description: Use DXMT, the open-source memory database for personal agents, as a Haystack document store with embedding, BM25 and hybrid retrievers
authors:
    - name: DXMT
      socials:
        github: dxmt
pypi: https://pypi.org/project/dxmt-haystack/
repo: https://github.com/dxmt/dxmt/tree/main/vectordb/clients/dxmt-haystack
type: Document Store
report_issue: https://github.com/dxmt/dxmt/issues
logo: /logos/dxmt.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Filters](#filters)
- [License](#license)

## Overview

[DXMT](https://github.com/dxmt/dxmt) is an open-source memory database for personal agents with
a vector database underneath: one Rust binary with HNSW and HNSW-PQ vector search, BM25
full-text search (with Chinese word segmentation), hybrid fusion, metadata filters, a
write-ahead log, server-side embedding and an MCP server.

`dxmt-haystack` makes a DXMT table a Haystack `DocumentStore` and adds three retrievers:
`DXMTEmbeddingRetriever`, `DXMTBM25Retriever` and `DXMTHybridRetriever`. It passes Haystack's
own `DocumentStoreBaseTests` (count, every duplicate policy, delete and the 39 filter cases)
against a live server.

## Installation

```bash
pip install dxmt-haystack
```

A DXMT server has to be running: a [release binary](https://github.com/dxmt/dxmt/releases)
(`vectordb serve`) or Docker (`docker run -p 9999:9999 -v dxmt:/data dxmtai/dxmt`).

## Usage

```python
from haystack import Document, Pipeline
from haystack_integrations.document_stores.dxmt import DXMTDocumentStore
from haystack_integrations.components.retrievers.dxmt import (
    DXMTBM25Retriever,
    DXMTEmbeddingRetriever,
    DXMTHybridRetriever,
)

document_store = DXMTDocumentStore(
    table_name="docs",
    embedding_dim=768,
    host="localhost",
    port=9999,
    enable_full_text_search=True,   # BM25 over `content`, for the BM25 and hybrid retrievers
)

document_store.write_documents([
    Document(content="rust borrows memory instead of collecting it", meta={"lang": "rust"}, embedding=[...]),
    Document(content="go collects garbage instead of borrowing", meta={"lang": "go"}, embedding=[...]),
])

retriever = DXMTEmbeddingRetriever(document_store=document_store, top_k=5)
retriever.run(query_embedding=[...])

DXMTBM25Retriever(document_store=document_store, top_k=5).run(query="garbage")
DXMTHybridRetriever(document_store=document_store, top_k=5).run(query="garbage", query_embedding=[...])
```

In a pipeline, with a text embedder in front:

```python
from haystack.components.embedders import SentenceTransformersTextEmbedder

pipeline = Pipeline()
pipeline.add_component("embedder", SentenceTransformersTextEmbedder(model="BAAI/bge-m3"))
pipeline.add_component("retriever", DXMTEmbeddingRetriever(document_store=document_store, top_k=5))
pipeline.connect("embedder.embedding", "retriever.query_embedding")
pipeline.run({"embedder": {"text": "how does rust manage memory"}})
```

The server can embed for you instead: construct the store with
`server_embedding={"model": "text-embedding-3-small"}` (or any OpenAI-compatible `/embeddings`
endpoint via `base_url`), write documents without an `embedding`, and call the embedding
retriever with `query_text=` rather than `query_embedding=`.

A document without an embedding is kept, as in every Haystack store, and is returned by
`filter_documents`; the embedding retriever never ranks it.

## Filters

`filter_documents` supports the whole Haystack filter language. A filter the server has a flat
form for (`==`, `!=`, numeric `>` `>=` `<` `<=`, `in`, `not in`, `AND`, `OR`, `NOT` of one
condition) runs on the server; anything else (comparisons against dates, strings or `None`,
`AND` nested inside `OR`, `NOT` over several conditions) is evaluated with Haystack's own
`document_matches_filter` over the table, which is correct and slower. The retrievers take
filters with a server form and refuse the rest by name.

```python
document_store.filter_documents({
    "operator": "AND",
    "conditions": [
        {"field": "meta.lang", "operator": "in", "value": ["rust", "go"]},
        {"field": "meta.year", "operator": ">=", "value": 2010},
    ],
})
```

## License

`dxmt-haystack` is distributed under the Apache-2.0 license.
