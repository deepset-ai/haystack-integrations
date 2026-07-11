---
layout: integration
name: IBM Db2
description: A Document Store for storing and retrieving documents from IBM Db2
authors:
    - name: Geetika Chugh
      socials:
        github: https://github.com/GeetikaChughIBM
        linkedin: https://in.linkedin.com/in/geetika-chugh-085251252
pypi: https://pypi.org/project/ibm-db-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ibm_db
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/ibm-db-haystack.svg)](https://pypi.org/project/ibm-db-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ibm-db-haystack.svg)](https://pypi.org/project/ibm-db-haystack/)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/ibm_db.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/ibm_db.yml)

-----

**Table of Contents**

- IBM Db2 Document Store for Haystack
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)

## Installation
IBM Db2 (version 12.1.2 and later) provides a native `VECTOR` data type that adds support for vector similarity search directly inside the database, allowing Db2 to act as a fully featured vector store while keeping documents, embeddings, and metadata within your existing enterprise database.

For more information on Db2 vector capabilities, visit the [IBM Db2 product page](https://www.ibm.com/products/db2).

Use `pip` to install `ibm-db-haystack`:

```bash
pip install ibm-db-haystack
```

## Usage
Set your IBM Db2 credentials as environment variables:

```bash
export DB2_USERNAME="db2inst1"
export DB2_PASSWORD="your_password"
```

Once installed, initialize IBMDb2DocumentStore.

```python
from haystack.utils import Secret
from haystack_integrations.document_stores.ibm_db import IBMDb2DocumentStore

document_store = IBMDb2DocumentStore(
    database="BLUDB",
    hostname="your-db2-host",
    port=50000,
    username=Secret.from_env_var("DB2_USERNAME"),
    password=Secret.from_env_var("DB2_PASSWORD"),
    table_name="haystack_docs",
    embedding_dim=768,
    distance_metric="COSINE",
)
```

Supported distance metrics are `COSINE`, `EUCLIDEAN`, and `MANHATTAN`.

### Writing Documents to IBMDb2DocumentStore
To write documents to `IBMDb2DocumentStore`, create an indexing pipeline.

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

### Retrieval from IBMDb2DocumentStore
You can retrieve semantically similar documents to a given query using a simple pipeline that includes the `IBMDb2EmbeddingRetriever`.

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.ibm_db import IBMDb2EmbeddingRetriever

querying = Pipeline()
querying.add_component("embedder", SentenceTransformersTextEmbedder())
querying.add_component("retriever", IBMDb2EmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("embedder.embedding", "retriever.query_embedding")

results = querying.run({"embedder": {"text": "my query"}})
```

You can also combine vector similarity search with metadata filtering, including compound AND/OR conditions, executed in the same query as the vector search.

```python
from haystack_integrations.components.retrievers.ibm_db import IBMDb2EmbeddingRetriever

retriever = IBMDb2EmbeddingRetriever(document_store=document_store, top_k=3)

results = retriever.run(
    query_embedding=query_embedding,
    filters={
        "operator": "AND",
        "conditions": [
            {"field": "meta.category", "operator": "==", "value": "security"},
            {"field": "meta.priority", "operator": "==", "value": "high"},
        ],
    },
)
```

## License
`ibm-db-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
