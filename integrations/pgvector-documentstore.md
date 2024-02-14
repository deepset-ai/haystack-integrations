---
layout: integration
name: pgvector
description: A Document Store for storing and retrieval from pgvector
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/pgvector-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/pgvector
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/pgvector-haystack.svg)](https://pypi.org/project/pgvector-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pgvector-haystack.svg)](https://pypi.org/project/pgvector-haystack/)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/pgvector.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/pgvector.yml)

-----

**Table of Contents**

- Pgvector Document Store for Haystack
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
  - [License](#license)

## Installation
`pgvector` is an extension for PostgreSQL that adds support for vector similarity search.

To quickly set up a PostgreSQL database with pgvector, you can use Docker:
```bash
docker run -d -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres ankane/pgvector
```

For more information on how to install pgvector, visit the [pgvector GitHub repository](https://github.com/pgvector/pgvector).

Use `pip` to install `pgvector-haystack`:
```bash
pip install pgvector-haystack
```
## Usage

Define the connection string to your PostgreSQL database in the `PG_CONN_STR` environment variable. For example:
```bash
export PG_CONN_STR="postgresql://postgres:postgres@localhost:5432/postgres"
````

Once installed, initialize PgvectorDocumentStore:

```python
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

document_store = PgvectorDocumentStore(
    table_name="haystack_docs",
    embedding_dimension=768,
    vector_function="cosine_similarity",
    recreate_table=True,
    search_strategy="hnsw",
)
```

### Writing Documents to PgvectorDocumentStore
To write documents to `PgvectorDocumentStore`, create an indexing Pipeline.

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "embedder")
indexing.connect("embedder", "writer")
indexing.run({"converter": {"sources": file_paths}})
```

### Retrieval from PgvectorDocumentStore
You can retrieve Documents similar to a given query using a simple Pipeline.

```python
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
from haystack.pipeline import Pipeline

querying = Pipeline()
querying.add_component("embedder", SentenceTransformersTextEmbedder())
querying.add_component("retriever", PgvectorEmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("embedder", "retriever")

results = querying.run({"embedder": {"text": "my query"}})
```

## Examples
You can find a code example showing how to use the Document Store and the Retriever under the `examples/` folder of [this repo](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/pgvector).

## License

`pgvector-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
