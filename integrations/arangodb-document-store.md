---
layout: integration
name: ArangoDB
description: Use the ArangoDB database as a Document Store with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/arangodb-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/arangodb
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/arangodb.png
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/arangodb-haystack.svg)](https://pypi.org/project/arangodb-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/arangodb-haystack.svg)](https://pypi.org/project/arangodb-haystack/)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/arangodb.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/arangodb.yml)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[ArangoDB](https://arango.ai/) is an open-source, multi-model database that combines documents, graphs, and key/values with native vector search. This integration lets you use ArangoDB as a [Document Store](https://docs.haystack.deepset.ai/docs/document-store) in Haystack and retrieve documents with vector similarity search, which makes it a good fit for RAG and GraphRAG pipelines.

The integration provides two components:

- `ArangoDocumentStore`: a Document Store that stores documents (including their embeddings) in an ArangoDB collection and implements the [DocumentStore protocol](https://docs.haystack.deepset.ai/docs/document-store#documentstore-protocol).
- `ArangoEmbeddingRetriever`: a [retriever](https://docs.haystack.deepset.ai/docs/retrievers) that fetches the most relevant documents from an `ArangoDocumentStore` using vector similarity on embeddings.

## Installation

Vector search requires ArangoDB 3.12 or later with the vector index enabled. You can quickly start a local instance with Docker:

```bash
docker run -e ARANGO_ROOT_PASSWORD=test-password -p 8529:8529 arangodb:3.12 arangod --vector-index
```

Install the integration with `pip`:

```bash
pip install arangodb-haystack
```

## Usage

By default, the `ArangoDocumentStore` reads its credentials from the `ARANGO_USERNAME` (optional, falls back to the `root` user) and `ARANGO_PASSWORD` environment variables:

```bash
export ARANGO_PASSWORD="test-password"
```

Then initialize the Document Store:

```python
from haystack_integrations.document_stores.arangodb import ArangoDocumentStore

document_store = ArangoDocumentStore(
    host="http://localhost:8529",
    database="haystack",
    collection_name="haystack_documents",
    embedding_dimension=768,
    similarity_function="cosine",
    recreate_collection=True,
)
```

### Writing Documents to ArangoDocumentStore

To write documents to the `ArangoDocumentStore`, create an indexing pipeline that embeds and writes documents:

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

### Retrieval from ArangoDocumentStore

You can retrieve documents that are semantically similar to a query with a pipeline that uses the `ArangoEmbeddingRetriever`:

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.arangodb import ArangoEmbeddingRetriever

querying = Pipeline()
querying.add_component("embedder", SentenceTransformersTextEmbedder())
querying.add_component("retriever", ArangoEmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("embedder", "retriever")

results = querying.run({"embedder": {"text": "my query"}})
```

The retriever also supports [metadata filtering](https://docs.haystack.deepset.ai/docs/metadata-filtering), which you can pass either at initialization or at query time.

## License

`arangodb-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
