---
layout: integration
name: MariaDB
description: A Document Store for storing and retrieval from MariaDB 11.7+ using native VECTOR support
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/mariadb-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mariadb
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/mariadb-haystack.svg)](https://pypi.org/project/mariadb-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mariadb-haystack.svg)](https://pypi.org/project/mariadb-haystack/)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/mariadb.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/mariadb.yml)

-----

**Table of Contents**

- MariaDB Document Store for Haystack
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)

## Installation

MariaDB 11.7+ introduced a native `VECTOR` datatype with MHNSW indexing, enabling efficient vector similarity search directly in the database.

To quickly set up a MariaDB instance, you can use Docker:

```bash
docker run -d -p 3306:3306 \
  -e MARIADB_ROOT_PASSWORD=secret \
  -e MARIADB_DATABASE=haystack \
  -e MARIADB_USER=haystack \
  -e MARIADB_PASSWORD=secret \
  mariadb:11.7
```

Use `pip` to install `mariadb-haystack`:

```bash
pip install mariadb-haystack
```

## Usage

Set the connection credentials as environment variables:

```bash
export MARIADB_USER=haystack
export MARIADB_PASSWORD=secret
```

Then initialize `MariaDBDocumentStore`:

```python
from haystack_integrations.document_stores.mariadb import MariaDBDocumentStore

document_store = MariaDBDocumentStore(
    host="localhost",
    port=3306,
    database="haystack",
    embedding_dimension=768,
    distance="cosine",
)
```

### Writing Documents

```python
from haystack import Document

docs = [
    Document(content="MariaDB supports native VECTOR type since 11.7"),
    Document(content="Haystack makes building LLM pipelines easy"),
]
document_store.write_documents(docs)
print(document_store.count_documents())
```

### Embedding Retrieval

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.retrievers.mariadb import MariaDBEmbeddingRetriever

# Indexing
indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("embedder", "writer")
indexing.run({"embedder": {"documents": docs}})

# Querying
querying = Pipeline()
querying.add_component("embedder", SentenceTransformersTextEmbedder())
querying.add_component("retriever", MariaDBEmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("embedder", "retriever")
results = querying.run({"embedder": {"text": "vector similarity search"}})
```

### Keyword Retrieval

```python
from haystack_integrations.components.retrievers.mariadb import MariaDBBM25Retriever

retriever = MariaDBBM25Retriever(document_store=document_store, top_k=3)
results = retriever.run(query="vector search")
```

## License

`mariadb-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
