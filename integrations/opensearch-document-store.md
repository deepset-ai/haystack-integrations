---
layout: integration
name: OpenSearch
description: A Document Store for storing and retrieval from OpenSearch
authors:
    - name: Thomas Stadelmann
      socials:
        github: tstadel
    - name: Julian Risch
      socials:
        github: julian-risch
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/opensearch-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opensearch
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/opensearch.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml)

-----

## Installation
Use `pip` to install OpenSearch:

```console
pip install opensearch-haystack
```
## Usage
Once installed, initialize your OpenSearch database to use it with Haystack:

```python
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore

document_store = OpenSearchDocumentStore()
```

### Writing Documents to OpenSearchDocumentStore
To write documents to `OpenSearchDocumentStore`, create an indexing pipeline.

```python
from haystack.components.file_converters import TextFileToDocument
from haystack.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"paths": file_paths}})
```

### Hybrid Retriever

This integration also provides a hybrid retriever. The `OpenSearchHybridRetriever` combines the capabilities of a vector search and a keyword search. It uses the OpenSearch document store to retrieve documents based on both semantic and keyword-based queries.

You can use the `OpenSearchHybridRetriever` together with the `OpenSearchDocumentStore` to perform hybrid retrieval.

See the example below on how to index documents and use the hybrid retriever:

```python
from haystack import Document
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack_integrations.components.retrievers.opensearch import OpenSearchHybridRetriever
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore

# Initialize the document store
doc_store = OpenSearchDocumentStore(
    hosts=["http://localhost:9200"],
    index="document_store",
    embedding_dim=384,
)

# Create some sample documents
docs = [
    Document(content="Machine learning is a subset of artificial intelligence."),
    Document(content="Deep learning is a subset of machine learning."),
    Document(content="Natural language processing is a field of AI."),
    Document(content="Reinforcement learning is a type of machine learning."),
    Document(content="Supervised learning is a type of machine learning."),
]

# Embed the documents and add them to the document store
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
doc_embedder.warm_up()
docs = doc_embedder.run(docs)

# Write the documents to the OpenSearch document store
doc_store.write_documents(docs['documents'])

# Initialize some haystack text embedder, in this case the SentenceTransformersTextEmbedder
embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

# Initialize the hybrid retriever
retriever = OpenSearchHybridRetriever(
    document_store=doc_store,
    embedder=embedder,
    top_k_bm25=3,
    top_k_embedding=3,
    join_mode="reciprocal_rank_fusion"
)

# Run the retriever
results = retriever.run(query="What is reinforcement learning?", filters_bm25=None, filters_embedding=None)

>> results['documents']
{'documents': [Document(id=..., content: 'Reinforcement learning is a type of machine learning.', score: 1.0),
  Document(id=..., content: 'Supervised learning is a type of machine learning.', score: 0.9760624679979518),
  Document(id=..., content: 'Deep learning is a subset of machine learning.', score: 0.4919354838709677),
  Document(id=..., content: 'Machine learning is a subset of artificial intelligence.', score: 0.4841269841269841)]}
```

You can learn more about the `OpenSearchHybridRetriever` in the [documentation](https://docs.haystack.deepset.ai/docs/opensearchhybridretriever).

### License

`opensearch-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
