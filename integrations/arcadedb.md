---
layout: integration
name: ArcadeDB
description: Use ArcadeDB as a document store with native HNSW vector search for Haystack
authors:
  - name: ArcadeData Ltd
    socials:
      github: ArcadeData
      twitter: arcade_db
pypi: https://pypi.org/project/arcadedb-haystack/
repo: https://github.com/ArcadeData/arcadedb-haystack
type: Document Store
report_issue: https://github.com/ArcadeData/arcadedb-haystack/issues
logo: /logos/arcadedb.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Writing documents](#writing-documents)
  - [Retrieving documents](#retrieving-documents)
  - [More examples](#more-examples)
- [License](#license)

## Overview

An integration of [ArcadeDB](https://arcadedb.com) with [Haystack](https://docs.haystack.deepset.ai/docs/intro) by [ArcadeData](https://arcadedata.com).

ArcadeDB is a multi-model database that combines document storage, HNSW vector search, and SQL-based metadata filtering:

- **Document storage** — vertex-based records with flexible MAP metadata
- **HNSW vector search** — native approximate nearest neighbor index via `vectorNeighbors()` (cosine, euclidean, dot product)
- **SQL filtering** — full SQL WHERE clauses on metadata fields
- **No special drivers** — pure HTTP/JSON API, no binary protocol or custom driver required

The library provides an `ArcadeDBDocumentStore` that implements the Haystack [DocumentStore protocol](https://docs.haystack.deepset.ai/docs/document-store#documentstore-protocol), plus pipeline-ready retriever components:

- **ArcadeDBDocumentStore** — stores Documents as ArcadeDB vertices with embeddings indexed by a dedicated HNSW Vector Index for dense retrieval.
- **ArcadeDBEmbeddingRetriever** — a [retriever component](https://docs.haystack.deepset.ai/docs/retrievers) that queries the vector index to find related Documents, with support for metadata filtering and runtime parameter overrides.

```text
                                   +-----------------------------+
                                   |      ArcadeDB Database      |
                                   +-----------------------------+
                                   |                             |
                                   |      +----------------+     |
                                   |      |    Document    |     |
                write_documents    |      +----------------+     |
          +------------------------+----->|   properties   |     |
          |                        |      |                |     |
+---------+----------+             |      |   embedding    |     |
|                    |             |      +--------+-------+     |
| ArcadeDBDocument   |             |               |             |
|       Store        |             |               |index/query  |
+---------+----------+             |               |             |
          |                        |     +---------+---------+   |
          |                        |     | HNSW Vector Index |   |
          +----------------------->|     |                   |   |
              _embedding_retrieval |     | (for embedding)   |   |
                                   |     +-------------------+   |
                                   |                             |
                                   +-----------------------------+
```

In the above diagram:

- `Document` is an ArcadeDB vertex type
- `properties` are Document [attributes](https://docs.haystack.deepset.ai/docs/data-classes#document) stored as vertex properties
- `embedding` is a vector property of type `LIST[FLOAT]`, indexed by ArcadeDB's native HNSW index
- `HNSW Vector Index` provides approximate nearest neighbor search via `vectorNeighbors()`

## Installation

`arcadedb-haystack` can be installed using pip:

```bash
pip install arcadedb-haystack
```

## Usage

Once installed, you can start using `ArcadeDBDocumentStore` as any other document store that supports embeddings.

```python
from haystack_integrations.document_stores.arcadedb import ArcadeDBDocumentStore

document_store = ArcadeDBDocumentStore(
    url="http://localhost:2480",
    database="haystack",
    embedding_dimension=384,
    similarity_function="cosine",
)
```

You will need a running ArcadeDB instance. The simplest way is with Docker:

```bash
docker run -d -p 2480:2480 \
    -e JAVA_OPTS="-Darcadedb.server.rootPassword=arcadedb" \
    arcadedata/arcadedb:latest
```

Set credentials via environment variables:

```bash
export ARCADEDB_USERNAME=root
export ARCADEDB_PASSWORD=arcadedb
```

### Writing documents

```python
from haystack import Document
from haystack.document_stores.types import DuplicatePolicy

documents = [
    Document(
        content="ArcadeDB supports graphs, documents, and vectors.",
        meta={"source": "docs", "category": "database"},
    )
]
document_store.write_documents(documents, policy=DuplicatePolicy.OVERWRITE)
```

### Retrieving documents

`ArcadeDBEmbeddingRetriever` can be used in a pipeline to retrieve documents by querying the HNSW vector index with an embedded query, including metadata filtering:

```python
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack_integrations.components.retrievers.arcadedb import ArcadeDBEmbeddingRetriever
from haystack_integrations.document_stores.arcadedb import ArcadeDBDocumentStore

document_store = ArcadeDBDocumentStore(
    url="http://localhost:2480",
    database="haystack",
    embedding_dimension=384,
)

# Index documents with embeddings
documents = [
    Document(content="My name is Morgan and I live in Paris.", meta={"release_date": "2018-12-09"})
]

document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
documents_with_embeddings = document_embedder.run(documents)
document_store.write_documents(documents_with_embeddings.get("documents"))

# Build retrieval pipeline
pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
pipeline.add_component("retriever", ArcadeDBEmbeddingRetriever(document_store=document_store))
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

### More examples

You can find more examples in the [repository](https://github.com/ArcadeData/arcadedb-haystack/tree/main/examples):

- [embedding_retrieval.py](https://github.com/ArcadeData/arcadedb-haystack/blob/main/examples/embedding_retrieval.py) — Full workflow demonstrating document indexing and vector similarity retrieval with ArcadeDB.

## License

`arcadedb-haystack` is distributed under the terms of the [Apache 2.0](https://spdx.org/licenses/Apache-2.0.html) license.
