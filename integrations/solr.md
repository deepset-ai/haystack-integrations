---
layout: integration
name: Apache Solr
description: Use an Apache Solr search server as a Document Store with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/solr-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/solr
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/solr.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/solr-haystack.svg)](https://pypi.org/project/solr-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/solr-haystack.svg)](https://pypi.org/project/solr-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/solr.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/solr.yml)

[Apache Solr](https://solr.apache.org/) is a widely used open source search server built on Apache Lucene. Since Solr 9, it ships a `DenseVectorField` and the `{!knn}` query parser, so it can serve both keyword (BM25) and dense vector retrieval — everything a RAG pipeline needs from a Document Store.

The integration provides:

- `SolrDocumentStore`, with sync and async support for all operations
- `SolrBM25Retriever`, `SolrEmbeddingRetriever`, and `SolrHybridRetriever`
- Full metadata filtering support, including exact round-trips of Python metadata types
- Extended methods such as `delete_by_filter`, `update_by_filter`, `count_documents_by_filter`, and metadata field introspection

The Document Store requires Solr 9.6 or newer and talks to Solr over its JSON HTTP API via `httpx`, so no Solr client library is needed.

## Installation

```console
pip install solr-haystack
```

## Usage

Start a Solr instance, for example with Docker:

```console
docker run -d -p 8983:8983 solr:10 solr-precreate haystack
```

Then initialize a `SolrDocumentStore` connected to the instance and write documents to it. By default, the store manages the schema itself: it creates the fields it needs and disables Solr's schemaless field guessing.

```python
from haystack import Document
from haystack_integrations.document_stores.solr import SolrDocumentStore

document_store = SolrDocumentStore(
    url="http://localhost:8983/solr",
    core="haystack",
    embedding_dim=768,
)

document_store.write_documents(
    [Document(content="This is first"), Document(content="This is second")]
)
print(document_store.count_documents())
```

The store reads the `SOLR_URL`, `SOLR_USERNAME`, and `SOLR_PASSWORD` environment variables by default, so credentials never need to appear in code or serialized pipelines.

### Retrieval

The integration supports different retrieval types through different retriever components:

- [`SolrBM25Retriever`](https://docs.haystack.deepset.ai/docs/solrbm25retriever): A keyword-based retriever that fetches documents matching a query using Solr's BM25 similarity.
- [`SolrEmbeddingRetriever`](https://docs.haystack.deepset.ai/docs/solrembeddingretriever): Compares the query and document embeddings using Solr's `{!knn}` dense vector search and fetches the documents most relevant to the query.
- [`SolrHybridRetriever`](https://docs.haystack.deepset.ai/docs/solrhybridretriever): A SuperComponent that embeds the query, runs BM25 and embedding retrieval over the same core, and fuses the results with reciprocal rank fusion.

Here is a hybrid retrieval example — one component embeds the query, retrieves with both methods, and merges the result lists:

```python
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.solr import SolrHybridRetriever
from haystack_integrations.document_stores.solr import SolrDocumentStore

document_store = SolrDocumentStore(core="haystack", embedding_dim=384)
retriever = SolrHybridRetriever(
    document_store=document_store,
    embedder=SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"),
)
retriever.warm_up()
result = retriever.run(query="Apache Solr")
print(result["documents"])
```

### Metadata

Metadata values keep their Python types across the round-trip: the integer `1`, the string `"1"`, the float `1.0`, and `True` stay four distinct values. Filters work on all metadata fields, and extended methods let you delete or update documents by filter, count documents and unique metadata values, and inspect metadata fields — each with an async twin.

## License

`solr-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/solr/LICENSE.txt).
