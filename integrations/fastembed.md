---
layout: integration
name: FastEmbed
description: Use the FastEmbed embedding models
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
    - name: Nicola Procopio
      socials:
        github: nickprock
        linkedin: https://www.linkedin.com/in/nicolaprocopio
pypi: https://pypi.org/project/fastembed-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/fastembed
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
[FastEmbed](https://qdrant.github.io/fastembed/) is a lightweight, fast, Python library built for embedding generation.

- Light and fast: quantized model weights; ONNX Runtime for inference via Optimum.
- Performant embedding models: list of [supported models](https://qdrant.github.io/fastembed/examples/Supported_Models/) - including multilingual models.
- Support for sparse embedding models.


## Installation

```bash
pip install fastembed-haystack
```

## Usage
### Components
The `fastembed-haystack` integrations provides the following components:
- `FastembedTextEmbedder`: creates a dense embedding for text (used in query/RAG pipelines).
- `FastembedDocumentEmbedder`: enriches documents with dense embeddings (used in indexing pipelines).
- `FastembedSparseTextEmbedder`: creates a sparse embedding for text (used in query/RAG pipelines).
- `FastembedSparseDocumentEmbedder`: enriches documents with sparse embeddings (used in indexing pipelines).
  
### Example with dense embeddings

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder, FastembedTextEmbedder

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [
    Document(content="My name is Wolfgang and I live in Berlin"),
    Document(content="I saw a black horse running"),
    Document(content="Germany has many big cities"),
    Document(content="fastembed is supported by and maintained by Qdrant."),
]

document_embedder = FastembedDocumentEmbedder()
document_embedder.warm_up()
documents_with_embeddings = document_embedder.run(documents)["documents"]
document_store.write_documents(documents_with_embeddings)

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", FastembedTextEmbedder())
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

query = "Who supports fastembed?"

result = query_pipeline.run({"text_embedder": {"text": query}})
```

### Example with sparse embeddings
Currently, Sparse Embedding retrieval is only supported by `QdrantDocumentStore`.
You can install the package as follows: 
```bash
pip install qdrant-haystack
```

```python
from haystack import Document, Pipeline
from haystack_integrations.components.retrievers.qdrant import QdrantSparseEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder, FastembedTextEmbedder

document_store = QdrantDocumentStore(
    ":memory:",
    recreate_index=True,
    use_sparse_embeddings=True
)

documents = [
    Document(content="My name is Wolfgang and I live in Berlin"),
    Document(content="I saw a black horse running"),
    Document(content="Germany has many big cities"),
    Document(content="fastembed is supported by and maintained by Qdrant."),
]

sparse_document_embedder = FastembedSparseDocumentEmbedder()
sparse_document_embedder.warm_up()
documents_with_sparse_embeddings = sparse_document_embedder.run(documents)["documents"]
document_store.write_documents(documents_with_sparse_embeddings)

query_pipeline = Pipeline()
query_pipeline.add_component("sparse_text_embedder", FastembedSparseTextEmbedder())
query_pipeline.add_component("sparse_retriever", QdrantSparseEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("sparse_text_embedder.sparse_embedding", "retriever.query_sparse_embedding")

query = "Who supports fastembed?"

result = query_pipeline.run({"sparse_text_embedder": {"text": query}})
```

### License

`fastembed-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
