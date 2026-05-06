---
layout: integration
name: AlloyDB
description: A Document Store for storing and retrieval from Google Cloud AlloyDB with pgvector
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Gary Badwal
      socials:
        website: garybadwal.com
        github: garybadwal
        twitter: garybadwal_
        linkedin: https://www.linkedin.com/in/garybadwal/
pypi: https://pypi.org/project/alloydb-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/alloydb
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/alloydb.png
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/alloydb-haystack.svg)](https://pypi.org/project/alloydb-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/alloydb-haystack.svg)](https://pypi.org/project/alloydb-haystack/)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Writing Documents to AlloyDBDocumentStore](#writing-documents-to-alloydbdocumentstore)
  - [Vector Similarity Search](#vector-similarity-search)
  - [Keyword Search](#keyword-search)
  - [HNSW Index](#hnsw-index)
- [Examples](#examples)
- [License](#license)

## Overview

[AlloyDB](https://cloud.google.com/alloydb) is a fully managed, PostgreSQL-compatible database service on Google Cloud, optimised for demanding transactional and analytical workloads.

This integration provides a Haystack `DocumentStore` backed by AlloyDB with the [pgvector extension](https://cloud.google.com/alloydb/docs/ai/work-with-embeddings), enabling both dense vector similarity search and full-text keyword search.

Connections are established through the [AlloyDB Python Connector](https://github.com/GoogleCloudPlatform/alloydb-python-connector), which handles IAM-based authentication and TLS encryption without requiring manual firewall rules or IP allowlisting.

## Installation

```bash
pip install alloydb-haystack
```

## Usage

Set the following environment variables to point at your AlloyDB instance:

| Variable | Description |
|---|---|
| `ALLOYDB_INSTANCE_URI` | AlloyDB instance URI: `projects/P/locations/R/clusters/C/instances/I` |
| `ALLOYDB_USER` | Database user (or IAM principal for IAM auth) |
| `ALLOYDB_PASSWORD` | Database password (not required when `enable_iam_auth=True`) |

Once installed, initialize `AlloyDBDocumentStore`:

```python
from haystack_integrations.document_stores.alloydb import AlloyDBDocumentStore

document_store = AlloyDBDocumentStore(
    db="my-database",
    embedding_dimension=768,
    recreate_table=True,
)
```

### Authentication

The integration supports both password-based authentication (default) and IAM-based authentication via a Google Cloud service account.

#### Password Authentication

```python
from haystack_integrations.document_stores.alloydb import AlloyDBDocumentStore

# Reads ALLOYDB_INSTANCE_URI, ALLOYDB_USER, and ALLOYDB_PASSWORD from the environment
document_store = AlloyDBDocumentStore(
    db="my-database",
    embedding_dimension=768,
)
```

#### IAM Authentication

When using a service account for database access, set `enable_iam_auth=True`:

```python
from haystack.utils import Secret
from haystack_integrations.document_stores.alloydb import AlloyDBDocumentStore

document_store = AlloyDBDocumentStore(
    db="my-database",
    user=Secret.from_env_var("ALLOYDB_IAM_USER"),  # e.g. "my-sa@my-project.iam"
    enable_iam_auth=True,
    embedding_dimension=768,
)
```

You can also choose the IP type used by the connector (`PRIVATE`, `PUBLIC`, or `PSC`) depending on your network configuration.

### Writing Documents to AlloyDBDocumentStore

To write documents to `AlloyDBDocumentStore`, create an indexing pipeline.

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

### Vector Similarity Search

You can retrieve semantically similar documents to a given query using a pipeline that includes the `AlloyDBEmbeddingRetriever`.

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.alloydb import AlloyDBEmbeddingRetriever

querying = Pipeline()
querying.add_component("embedder", SentenceTransformersTextEmbedder())
querying.add_component("retriever", AlloyDBEmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("embedder", "retriever")

results = querying.run({"embedder": {"text": "my query"}})
```

### Keyword Search

You can also retrieve documents based on full-text keyword matching with the `AlloyDBKeywordRetriever`, which uses PostgreSQL's `tsvector`/`tsquery`.

```python
from haystack_integrations.components.retrievers.alloydb import AlloyDBKeywordRetriever

retriever = AlloyDBKeywordRetriever(document_store=document_store, top_k=3)
results = retriever.run(query="capital France")
```

### HNSW Index

For large datasets, the HNSW index provides approximate nearest-neighbour search with significantly better query throughput:

```python
document_store = AlloyDBDocumentStore(
    db="my-database",
    embedding_dimension=768,
    search_strategy="hnsw",
    hnsw_index_creation_kwargs={"m": 16, "ef_construction": 64},
    hnsw_ef_search=40,
)
```

## Examples

You can find code examples showing how to use the Document Store and the Retrievers under the `examples/` folder of [this repo](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/alloydb).

## License

`alloydb-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
