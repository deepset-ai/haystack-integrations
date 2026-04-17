---
layout: integration
name: Superlinked
description: Use Superlinked (SIE) embeddings, reranking, and extraction in Haystack pipelines.
authors:
    - name: Superlinked
      socials:
        github: superlinked
        linkedin: superlinked
pypi: https://pypi.org/project/sie-haystack/
repo: https://github.com/superlinked/sie/tree/main/integrations/sie_haystack
type: Model Provider
report_issue: https://github.com/superlinked/sie/issues
logo: /logos/superlinked.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Dense Embeddings](#dense-embeddings)
  - [Sparse Embeddings](#sparse-embeddings)
  - [Multivector (ColBERT) Embeddings](#multivector-colbert-embeddings)
  - [Image Embeddings](#image-embeddings)
  - [Reranking](#reranking)
  - [Extraction](#extraction)
  - [End-to-End RAG Pipeline](#end-to-end-rag-pipeline)
- [Resources](#resources)
- [License](#license)

## Overview

[Superlinked's](https://superlinked.com) Search Inference Engine (SIE) is a self-hosted inference server for embeddings, reranking, and extraction. The `sie-haystack` package provides Haystack 2.0 components that route requests through a single SIE endpoint for 85+ embedding models (dense, sparse, multivector/ColBERT, multimodal), cross-encoder reranking, and zero-shot entity, relation, classification, and object-detection extraction.

All components live under the standard Haystack integrations namespace: `haystack_integrations.components.{embedders,rankers,extractors}.sie`.

Start a local SIE server with Docker before running any of the examples below:

```bash
docker run -p 8080:8080 ghcr.io/superlinked/sie-server:latest
```

## Installation

```bash
pip install sie-haystack
```

This installs `sie-sdk` and `haystack-ai` as dependencies. Every component accepts `base_url` and a `model` identifier from the [Superlinked model catalog](https://superlinked.com/models). Swapping models is a parameter change, not a new deployment.

## Usage

### Dense Embeddings

Use `SIEDocumentEmbedder` in an indexing pipeline and `SIETextEmbedder` at query time.

Indexing:

```python
from haystack import Document, Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.sie import SIEDocumentEmbedder

document_store = InMemoryDocumentStore()
documents = [
    Document(content="Python is a high-level programming language."),
    Document(content="France is a country in Western Europe."),
    Document(content="Berlin is the capital of Germany."),
]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(
    "embedder",
    SIEDocumentEmbedder(base_url="http://localhost:8080", model="BAAI/bge-m3"),
)
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

Query-side:

```python
from haystack_integrations.components.embedders.sie import SIETextEmbedder

embedder = SIETextEmbedder(base_url="http://localhost:8080", model="BAAI/bge-m3")
result = embedder.run(text="What is Python?")
query_vector = result["embedding"]  # list[float]
```

### Sparse Embeddings

For hybrid search with SPLADE-style or BGE-M3 sparse vectors:

```python
from haystack_integrations.components.embedders.sie import SIESparseTextEmbedder

embedder = SIESparseTextEmbedder(base_url="http://localhost:8080", model="BAAI/bge-m3")
result = embedder.run(text="What is machine learning?")
print(result["sparse_embedding"].keys())  # dict_keys(['indices', 'values'])
```

Use `SIESparseDocumentEmbedder` on the indexing side with the same model.

### Multivector (ColBERT) Embeddings

For late-interaction retrieval (ColBERT, Jina-ColBERT, ModernColBERT):

```python
from haystack_integrations.components.embedders.sie import SIEMultivectorTextEmbedder

embedder = SIEMultivectorTextEmbedder(
    base_url="http://localhost:8080",
    model="jinaai/jina-colbert-v2",
)
result = embedder.run(text="What is machine learning?")
multivector = result["multivector_embedding"]  # list[list[float]], one vector per token
```

`SIEMultivectorDocumentEmbedder` provides the document-side equivalent for indexing.

### Image Embeddings

Multimodal retrieval through CLIP, SigLIP, or ColPali:

```python
from haystack_integrations.components.embedders.sie import SIEImageEmbedder

embedder = SIEImageEmbedder(
    base_url="http://localhost:8080",
    model="openai/clip-vit-large-patch14",
)
with open("photo.jpg", "rb") as f:
    result = embedder.run(images=[f.read()])
embeddings = result["embeddings"]  # list[list[float]]
```

### Reranking

Rerank retrieved documents with a cross-encoder or late-interaction reranker:

```python
from haystack import Document
from haystack_integrations.components.rankers.sie import SIERanker

ranker = SIERanker(
    base_url="http://localhost:8080",
    model="BAAI/bge-reranker-v2-m3",
    top_k=3,
)
result = ranker.run(
    query="What is Python?",
    documents=[
        Document(content="Python is a high-level programming language."),
        Document(content="France is a country in Western Europe."),
        Document(content="Python snakes live in tropical climates."),
    ],
)
for doc in result["documents"]:
    print(doc.score, doc.content)
```

### Extraction

Zero-shot entities (GLiNER), relations (GLiREL), classifications (GLiClass), and object detection (GroundingDINO, OWL-v2) all use `SIEExtractor`. The output shape depends on the model family.

Named entity recognition:

```python
from haystack_integrations.components.extractors.sie import SIEExtractor

extractor = SIEExtractor(
    base_url="http://localhost:8080",
    model="urchade/gliner_multi-v2.1",
    labels=["person", "organization", "location"],
)
result = extractor.run(text="Tim Cook is the CEO of Apple in Cupertino.")
for entity in result["entities"]:
    print(f"{entity.text} ({entity.label}): {entity.score:.2f}")
```

Relation extraction:

```python
extractor = SIEExtractor(
    base_url="http://localhost:8080",
    model="jackboyla/glirel-large-v0",
    labels=["works_at", "located_in"],
)
result = extractor.run(text="Tim Cook works at Apple in Cupertino.")
for relation in result["relations"]:
    print(f"{relation.head} ({relation.relation}) {relation.tail}")
```

Classification and object detection follow the same pattern; see `result["classifications"]` and `result["objects"]` in the [full integration guide](https://superlinked.com/docs/integrations/haystack#extraction).

### End-to-End RAG Pipeline

Combine embedder, retriever, and ranker into one query pipeline:

```python
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack_integrations.components.embedders.sie import SIETextEmbedder
from haystack_integrations.components.rankers.sie import SIERanker

# Assumes documents were indexed with SIEDocumentEmbedder into document_store above.
query_pipeline = Pipeline()
query_pipeline.add_component(
    "text_embedder",
    SIETextEmbedder(base_url="http://localhost:8080", model="BAAI/bge-m3"),
)
query_pipeline.add_component(
    "retriever",
    InMemoryEmbeddingRetriever(document_store=document_store, top_k=10),
)
query_pipeline.add_component(
    "ranker",
    SIERanker(base_url="http://localhost:8080", model="BAAI/bge-reranker-v2-m3", top_k=3),
)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "ranker.documents")

result = query_pipeline.run({
    "text_embedder": {"text": "What is Python?"},
    "ranker": {"query": "What is Python?"},
})
for doc in result["ranker"]["documents"]:
    print(doc.score, doc.content)
```

One SIE server backs the full pipeline through the shared `base_url`. Swapping retrieval or reranking models is a configuration change, not a new deployment.

## Resources

- [`sie-haystack` source](https://github.com/superlinked/sie/tree/main/integrations/sie_haystack)
- [`sie-haystack` on PyPI](https://pypi.org/project/sie-haystack/)
- [Superlinked Haystack integration guide](https://superlinked.com/docs/integrations/haystack)
- [Superlinked model catalog](https://superlinked.com/models)

## License

`sie-haystack` is released under the Apache 2.0 license.
