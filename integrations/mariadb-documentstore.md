---
layout: integration
name: MariaDB
description: A Document Store for storing and retrieval from MariaDB 11.7+ using native VECTOR support
logo: /logos/mariadb.svg
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

MariaDB 11.7+ introduced a native `VECTOR` datatype with HNSW-based indexing, enabling efficient vector similarity search directly in the database.

To quickly set up a MariaDB instance, you can use Docker:

```bash
docker run -d -p 3306:3306 \
  -e MARIADB_ROOT_PASSWORD=secret \
  -e MARIADB_DATABASE=haystack \
  -e MARIADB_USER=haystack \
  -e MARIADB_PASSWORD=secret \
  mariadb:11.7
```

The `mariadb` connector is a C extension built from source, so it needs the MariaDB Connector/C system library (`mariadb_config`):

```bash
# Ubuntu / Debian
sudo apt-get install -y libmariadb-dev

# macOS
brew install mariadb-connector-c
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
from haystack_integrations.components.retrievers.mariadb import MariaDBKeywordRetriever

retriever = MariaDBKeywordRetriever(document_store=document_store, top_k=3)
results = retriever.run(query="vector search")
```

## License

`mariadb-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
