---
layout: integration
name: FalkorDB
description: Use FalkorDB as a document store with native vector search for GraphRAG workloads in Haystack
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/falkordb-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/falkordb
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/falkordb.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Writing documents](#writing-documents)
  - [Retrieving documents](#retrieving-documents)
  - [Graph queries with Cypher](#graph-queries-with-cypher)
- [License](#license)

## Overview

An integration of [FalkorDB](https://www.falkordb.com/) with [Haystack](https://docs.haystack.deepset.ai/docs/intro) by [deepset](https://www.deepset.ai).

FalkorDB is a high-performance graph database optimized for GraphRAG workloads. It stores documents as graph nodes and supports native vector search — no APOC is required. All bulk writes use `UNWIND` + `MERGE` for safe, idiomatic OpenCypher upserts.

The library provides a `FalkorDBDocumentStore` that implements the Haystack [DocumentStore protocol](https://docs.haystack.deepset.ai/docs/document-store#documentstore-protocol), plus two pipeline-ready retriever components:

- **FalkorDBDocumentStore** — stores Documents as labeled graph nodes in a named FalkorDB graph, with `meta` fields stored flat alongside `id` and `content`. Embeddings are indexed using FalkorDB's native vector index.
- **FalkorDBEmbeddingRetriever** — a [retriever component](https://docs.haystack.deepset.ai/docs/retrievers) that queries the native vector index to find Documents by dense similarity, with support for metadata filtering.
- **FalkorDBCypherRetriever** — a power-user retriever for executing arbitrary [OpenCypher](https://opencypher.org/) queries, enabling graph traversal and multi-hop queries in GraphRAG pipelines.

```text
                                   +-----------------------------+
                                   |      FalkorDB Database      |
                                   +-----------------------------+
                                   |                             |
                                   |      +----------------+     |
                                   |      |    Document    |     |
                write_documents    |      +----------------+     |
          +------------------------+----->|   properties   |     |
          |                        |      |                |     |
+---------+----------+             |      |   embedding    |     |
|                    |             |      +--------+-------+     |
| FalkorDBDocument   |             |               |             |
|       Store        |             |               |index/query  |
+---------+----------+             |               |             |
          |                        |     +---------+---------+   |
          |                        |     | Native Vector Idx |   |
          +----------------------->|     |                   |   |
              _embedding_retrieval |     |  (vecf32 index)   |   |
                                   |     +-------------------+   |
                                   |                             |
                                   +-----------------------------+
```

In the above diagram:

- `Document` is a FalkorDB node with a configurable label (default: `"Document"`)
- `properties` are Document [attributes](https://docs.haystack.deepset.ai/docs/data-classes#document) and `meta` fields stored flat on the node
- `embedding` is stored as a `vecf32` vector property indexed by FalkorDB's native vector index
- The native vector index enables approximate nearest neighbor search via `db.idx.vector.queryNodes`

## Installation

`falkordb-haystack` can be installed using pip:

```bash
pip install falkordb-haystack
```

You will need a running FalkorDB instance. The simplest way is with Docker:

```bash
docker run -d -p 6379:6379 falkordb/falkordb:latest
```

## Usage

```python
from haystack_integrations.document_stores.falkordb import FalkorDBDocumentStore

document_store = FalkorDBDocumentStore(
    host="localhost",
    port=6379,
    embedding_dim=384,
    similarity="cosine",
)
```

### Writing documents

```python
from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

documents = [
    Document(
        content="FalkorDB is a high-performance graph database for GraphRAG.",
        meta={"source": "docs", "category": "database"},
    )
]
document_store.write_documents(documents, policy=DuplicatePolicy.OVERWRITE)
```

### Retrieving documents

`FalkorDBEmbeddingRetriever` can be used in a pipeline to retrieve documents by querying the native vector index with an embedded query, with optional metadata filtering:

```python
from haystack import Document, Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack_integrations.document_stores.falkordb import FalkorDBDocumentStore
from haystack_integrations.components.retrievers.falkordb import FalkorDBEmbeddingRetriever

document_store = FalkorDBDocumentStore(
    host="localhost",
    port=6379,
    embedding_dim=384,
    recreate_graph=True,
)

documents = [
    Document(
        content="My name is Morgan and I live in Paris.",
        meta={"release_date": "2018-12-09"},
    )
]

document_embedder = SentenceTransformersDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)
document_embedder.warm_up()
documents_with_embeddings = document_embedder.run(documents)
document_store.write_documents(documents_with_embeddings["documents"])

pipeline = Pipeline()
pipeline.add_component(
    "text_embedder",
    SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"),
)
pipeline.add_component(
    "retriever",
    FalkorDBEmbeddingRetriever(document_store=document_store),
)
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = pipeline.run(
    data={
        "text_embedder": {"text": "What cities do people live in?"},
        "retriever": {
            "top_k": 5,
            "filters": {"field": "release_date", "operator": "==", "value": "2018-12-09"},
        },
    }
)

documents = result["retriever"]["documents"]
```

### Graph queries with Cypher

`FalkorDBCypherRetriever` allows you to run arbitrary OpenCypher queries against the graph, which is useful for multi-hop traversals and custom GraphRAG patterns. Use parameterized queries to avoid injection vulnerabilities:

```python
from haystack_integrations.document_stores.falkordb import FalkorDBDocumentStore
from haystack_integrations.components.retrievers.falkordb import FalkorDBCypherRetriever

document_store = FalkorDBDocumentStore(host="localhost", port=6379)

retriever = FalkorDBCypherRetriever(
    document_store=document_store,
    custom_cypher_query="MATCH (d:Document {topic: $topic}) RETURN d",
)

result = retriever.run(parameters={"topic": "GraphRAG"})
documents = result["documents"]
```

## License

`falkordb-haystack` is distributed under the terms of the [Apache 2.0](https://spdx.org/licenses/Apache-2.0.html) license.
