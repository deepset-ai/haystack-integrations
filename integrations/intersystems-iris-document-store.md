---
layout: integration
name: InterSystems IRIS
description: Use the InterSystems IRIS database with Haystack
authors:
    - name: Scientificloud
      socials:
        github: s-c-ai
pypi: https://pypi.org/project/intersystems-iris-haystack/0.1.1/
repo: https://github.com/s-c-ai/iris-haystack
type: Document Store
report_issue: https://github.com/s-c-ai/iris-haystack/issues
logo: /logos/intersystems-iris.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
An integration of **InterSystems IRIS** database with [Haystack 2](https://haystack.deepset.ai/) by deepset. In IRIS, the native `VECTOR(DOUBLE, N)` type is used for storing document embeddings, and the `VECTOR_COSINE` function enables high-performance dense retrievals using SIMD operations.

The library allows using InterSystems IRIS as a DocumentStore, implementing the required Protocol methods. You can start working with the implementation by importing it from the package:

```python
from intersystems_iris_haystack import IRISDocumentStore
```

In addition to the IRISDocumentStore, the library includes the following Haystack components which can be used in a pipeline:

- IRISEmbeddingRetriever - A component used to query the vector store and find semantically related Documents. It uses VECTOR_COSINE natively in the database.

- IRISBm25Retriever - A keyword-based retriever that implements Okapi BM25 over the stored documents.

The `intersystems-iris-haystack` library uses the official intersystems-iris Python Driver to interact with the database and hides all SQL complexities under the hood.

```plaintext
                                   +-----------------------------+
                                   |   InterSystems IRIS         |
                                   +-----------------------------+
                                   |                             |
                                   |      +----------------+     |
                                   |      |  document_table|     |
                write_documents    |      +----------------+     |
          +------------------------+----->|  id (VARCHAR)  |     |
          |                        |      |  content (CLOB)|     |
+---------+----------+             |      |  meta (JSON)   |     |
|                    |             |      |  embedding     |     |
| IRISDocumentStore  |             |      +--------+-------+     |
|                    |             |               |             |
+---------+----------+             |               |             |
          |                        |               |             |
          |                        |      +--------+--------+    |
          |                        |      | VECTOR_COSINE   |    |
          +----------------------->|      | SIMD execution  |    |
               query_embeddings    |      +-----------------+    |
                                   |                             |
                                   +-----------------------------+

```
In the above diagram:

- Documents are stored as rows in a dedicated relational table.
- Meta properties are stored as natively queryable JSON.
- Embedding is stored as a VECTOR column type.
- Retrievals are executed by the database engine directly, eliminating the need for an external vector database.


## Installation

Install the integration via pip:

```bash
pip install intersystems-iris-haystack
```

Note: For the examples below, you will also need an embedder like sentence-transformers.

**Requires:** Python 3.10+ (Recommended/Tested on 3.12) and a running InterSystems IRIS instance.

## Usage

Once installed, you can start using ``IRISDocumentStore`` as any other document stores that support embeddings.

```python
from intersystems_iris_haystack import IRISDocumentStore

document_store = IRISDocumentStore(
    connection_string="localhost:1972/USER",
    username="_system",
    password="SYS",
    table_name="HaystackDocuments",
    embedding_dim=384,
)
```

The full list of parameters accepted by `IRISDocumentStore` can be found in
[API documentation](https://s-c-ai.github.io/iris-haystack/api/document-store/#intersystems_iris_haystack.IRISDocumentStore).

Please notice you will need to have a running instance of InterSystems IRIS. There are several options available:

- [Docker](https://hub.docker.com/r/intersystems/iris-community)

- [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-tdzm2pjb7opqs)

- [InterSystems IRIS Desktop](http://evaluation.intersystems.com/)

The simplest way to start database locally will be with Docker container:

### Running InterSystems IRIS

Start IRIS locally with Docker:

```bash
docker run -d --name iris -p 1972:1972 -p 52773:52773 \
  intersystemsdc/iris-community:latest
```

Start an interactive terminal with the following:

```bash
docker exec -it my-iris iris session IRIS
```

Or login to the Mangement Portal at http://localhost:52773/csp/sys/%25CSP.Portal.Home.zen

The default username is ```_SYSTEM``` and password is ```SYS```; you will be prompted to change this password after logging in.

Quick Start

Create a ```.env``` file using ```.env.example``` template and import the default config credentials for IntersystemsIris.


```bash
IRIS_CONNECTION_STRING="localhost:1972/USER"
IRIS_USERNAME="_system"
IRIS_PASSWORD="SYS"
```
### Example (RAG)

```python
from haystack import Document, Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy

from intersystems_iris_haystack import IRISDocumentStore
from intersystems_iris_haystack import (IRISEmbeddingRetriever, IRISBm25Retriever)

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
store = IRISDocumentStore(embedding_dim=384)

# Indexing
indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(model=MODEL))
indexing.add_component("writer", DocumentWriter(store, policy=DuplicatePolicy.OVERWRITE))
indexing.connect("embedder.documents", "writer.documents")
indexing.run({"embedder": {"documents": [
    Document(content="IRIS is a multimodel database.", meta={"category": "db"}),
    Document(content="Haystack builds LLM pipelines.",  meta={"category": "ai"}),
]}})

# Semantic search
query_pipeline = Pipeline()
query_pipeline.add_component("embedder", SentenceTransformersTextEmbedder(model=MODEL))
query_pipeline.add_component("retriever", IRISEmbeddingRetriever(store, top_k=3))
query_pipeline.connect("embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"embedder": {"text": "what is vector search?"}})

# BM25 keyword search
bm25 = IRISBm25Retriever(store, top_k=3)
result = bm25.run(query="multimodel database")
```


### Components
This integration introduces:

- `IRISDocumentStore` A DocumentStore backed by InterSystems IRIS
- `IRISEmbeddingRetriever`Retrieve documents from `IRISDocumentStore` by embedding similarity.

- `IRISBm25Retriever ` Retrieve documents from `IRISDocumentStore` using Okapi BM25.




## License

`intersystems-iris-haystack` is distributed under the terms of the [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) license.