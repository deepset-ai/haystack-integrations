---
layout: integration
name: Sentence Transformers
description: Use Sentence Transformers embedding and ranking models in your Haystack pipelines
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/sentence-transformers.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Sentence Transformers](https://www.sbert.net/) is a library for state-of-the-art embedding and reranking models. With this integration, you can run Sentence Transformers compatible models from the [Hugging Face Hub](https://huggingface.co/models?library=sentence-transformers) **locally**, on your own machine, in your Haystack pipelines.

Haystack supports Hugging Face models in other ways too:
- [Hugging Face Transformers](https://haystack.deepset.ai/integrations/huggingface) for other local models (LLMs, extractive QA, classification, NER)
- [Hugging Face API](https://haystack.deepset.ai/integrations/huggingface-api) to call models via Inference Providers, Inference Endpoints, or self-hosted TGI/TEI
- [Optimum](https://haystack.deepset.ai/integrations/optimum) for high-performance inference with ONNX Runtime

## Installation

```bash
pip install haystack-ai "sentence-transformers>=5.0.0"
```

## Usage

### Components

Haystack provides several components based on Sentence Transformers:
- Embedders:
    - [`SentenceTransformersTextEmbedder`](https://docs.haystack.deepset.ai/docs/sentencetransformerstextembedder): creates a dense embedding for text (used in query/RAG pipelines).
    - [`SentenceTransformersDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/sentencetransformersdocumentembedder): enriches documents with dense embeddings (used in indexing pipelines).
    - [`SentenceTransformersSparseTextEmbedder`](https://docs.haystack.deepset.ai/docs/sentencetransformerssparsetextembedder): creates a sparse embedding for text (used in query/RAG pipelines).
    - [`SentenceTransformersSparseDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/sentencetransformerssparsedocumentembedder): enriches documents with sparse embeddings (used in indexing pipelines).
    - [`SentenceTransformersDocumentImageEmbedder`](https://docs.haystack.deepset.ai/docs/sentencetransformersdocumentimageembedder): enriches documents with embeddings computed from their images.
- Rankers:
    - [`SentenceTransformersSimilarityRanker`](https://docs.haystack.deepset.ai/docs/sentencetransformerssimilarityranker): ranks documents based on their similarity to the query, using cross-encoder models.
    - [`SentenceTransformersDiversityRanker`](https://docs.haystack.deepset.ai/docs/sentencetransformersdiversityranker): ranks documents to maximize their overall diversity.

### Embedding Models

To create semantic embeddings for documents, use `SentenceTransformersDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `SentenceTransformersTextEmbedder`.

Below is an example of a document retrieval pipeline, after the documents have been indexed with their embeddings:

```python
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
documents_with_embeddings = document_embedder.run(documents)["documents"]
document_store.write_documents(documents_with_embeddings)

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"text_embedder": {"text": "Who lives in Berlin?"}})
```

### Sparse Embedding Models

Sparse embedding models like SPLADE produce interpretable embeddings and can perform better than dense models in out-of-domain settings. Currently, sparse embedding retrieval is supported by the [Qdrant Document Store](https://haystack.deepset.ai/integrations/qdrant-document-store).

```python
from haystack.components.embedders import SentenceTransformersSparseTextEmbedder

text_embedder = SentenceTransformersSparseTextEmbedder()

print(text_embedder.run("I love pizza!"))
# {'sparse_embedding': SparseEmbedding(indices=[999, 1045, ...], values=[0.918, 0.867, ...])}
```

### Ranking Models

To rank documents based on their relevance to the query, use `SentenceTransformersSimilarityRanker` with a cross-encoder model:

```python
from haystack import Document
from haystack.components.rankers import SentenceTransformersSimilarityRanker

ranker = SentenceTransformersSimilarityRanker(model="cross-encoder/ms-marco-MiniLM-L-6-v2")

docs = [Document(content="Paris"), Document(content="Berlin")]
result = ranker.run(query="City in Germany", documents=docs)
print(result["documents"][0].content)
# Berlin
```
