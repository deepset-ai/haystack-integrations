---
layout: integration
name: Vespa
description: Use the Vespa search engine as a document store with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/vespa-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/vespa
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/vespa.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Vespa](https://vespa.ai/) is an open-source search engine and vector database that supports
vector search, lexical search, and search in structured data, all in the same query. This
integration lets you use Vespa as a `DocumentStore` in Haystack pipelines and provides
retrievers for both embedding-based and keyword-based search.

It is built on top of [pyvespa](https://pyvespa.readthedocs.io/) and expects a Vespa application
to be running and reachable (locally via Docker, on Vespa Cloud, or self-hosted). The Vespa
schema, including the fields and ranking profiles used by the retrievers, must be defined on
the Vespa application before you start indexing or querying.

When connecting to [Vespa Cloud](https://cloud.vespa.ai/), `VespaDocumentStore` supports either
token-based authentication via `vespa_cloud_secret_token` (or the `VESPA_CLOUD_SECRET_TOKEN`
environment variable) or mTLS authentication via the `cert` and `key` parameters pointing to
your data plane certificate and key files.

## Installation

```bash
pip install vespa-haystack
```

The integration requires Python 3.10+, `haystack-ai>=2.28.0` and `pyvespa>=0.58.0`.

## Usage

### Components

This integration introduces the following components:

- [`VespaDocumentStore`](https://docs.haystack.deepset.ai/reference/integrations-vespa#vespadocumentstore):
  a `DocumentStore` backed by a Vespa application. It connects to the Vespa endpoint
  (`VESPA_URL` by default) and reads/writes documents into the configured schema and namespace.
- [`VespaEmbeddingRetriever`](https://docs.haystack.deepset.ai/reference/integrations-vespa#vespaembeddingretriever):
  retrieves documents from a `VespaDocumentStore` using vector similarity (nearest-neighbor
  search on the configured embedding field).
- [`VespaKeywordRetriever`](https://docs.haystack.deepset.ai/reference/integrations-vespa#vespakeywordretriever):
  retrieves documents from a `VespaDocumentStore` using Vespa's lexical search (e.g. BM25 ranking).

### Indexing and embedding retrieval

```python
from haystack import Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import Document

from haystack_integrations.components.retrievers.vespa import VespaEmbeddingRetriever
from haystack_integrations.document_stores.vespa import VespaDocumentStore

document_store = VespaDocumentStore(
    schema="doc",
    namespace="doc",
    content_field="content",
    embedding_field="embedding",
    metadata_fields=["category"],
)

indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store=document_store))
indexing.connect("embedder", "writer")

indexing.run({"embedder": {"documents": [
    Document(id="1", content="Haystack integrates with Vespa for search.", meta={"category": "docs"}),
]}})

querying = Pipeline()
querying.add_component("text_embedder", SentenceTransformersTextEmbedder())
querying.add_component(
    "retriever",
    VespaEmbeddingRetriever(
        document_store=document_store,
        top_k=2,
        query_tensor_name="query_embedding",
    ),
)
querying.connect("text_embedder", "retriever")

results = querying.run({"text_embedder": {"text": "semantic vector search"}})
```

### Keyword retrieval

```python
from haystack import Pipeline

from haystack_integrations.components.retrievers.vespa import VespaKeywordRetriever
from haystack_integrations.document_stores.vespa import VespaDocumentStore

document_store = VespaDocumentStore(
    schema="doc",
    namespace="doc",
    content_field="content",
    metadata_fields=["category", "author"],
)

querying = Pipeline()
querying.add_component(
    "retriever",
    VespaKeywordRetriever(
        document_store=document_store,
        top_k=2,
        filters={"field": "meta.category", "operator": "==", "value": "docs"},
    ),
)

results = querying.run({"retriever": {"query": "vector retrieval"}})
```

### License

`vespa-haystack` is distributed under the terms of the [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
