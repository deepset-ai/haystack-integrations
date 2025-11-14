---
layout: integration
name: Voyage AI
description: Use text embeddings and rerankers from Voyage AI
authors:
  - name: Ashwin Mathur
    socials:
      github: awinml
      twitter: awinml
      linkedin: https://www.linkedin.com/in/ashwin-mathur-ds
pypi: https://pypi.org/project/voyage-embedders-haystack/
repo: https://github.com/awinml/voyage-embedders-haystack/tree/main
type: Model Provider
report_issue: https://github.com/awinml/voyage-embedders-haystack/issues
logo: /logos/voyage_ai.jpg
version: Haystack 2.0
toc: true
---

[![PyPI](https://img.shields.io/pypi/v/voyage-embedders-haystack)](https://pypi.org/project/voyage-embedders-haystack/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/voyage-embedders-haystack?logo=python&logoColor=gold)

### **Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Contextualized Embeddings Example](#contextualized-embeddings-example)

[Voyage AI](https://voyageai.com/)'s embedding and ranking models are state-of-the-art in retrieval accuracy. The integration supports the following models:
- **`voyage-3.5`** and **`voyage-3.5-lite`** - Latest general-purpose embedding models with superior performance
- **`voyage-3-large`** and **`voyage-3`** - High-performance general-purpose embedding models
- **`voyage-context-3`** - Contextualized chunk embedding model that preserves document context for improved retrieval accuracy
- **`voyage-2`** and **`voyage-large-2`** - Proven models that outperform `intfloat/e5-mistral-7b-instruct` and `OpenAI/text-embedding-3-large` on the [MTEB Benchmark](https://github.com/embeddings-benchmark/mteb)

For the complete list of available models, see the [Embeddings Documentation](https://docs.voyageai.com/embeddings/) and [Contextualized Chunk Embeddings](https://docs.voyageai.com/docs/contextualized-chunk-embeddings).

## Installation

```bash
pip install voyage-embedders-haystack
```

## Usage

You can use Voyage models with four components:
- [VoyageTextEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/haystack_integrations/components/embedders/voyage_embedders/voyage_text_embedder.py) - For embedding query text
- [VoyageDocumentEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/haystack_integrations/components/embedders/voyage_embedders/voyage_document_embedder.py) - For embedding documents
- [VoyageContextualizedDocumentEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/voyage_context-3_model/src/haystack_integrations/components/embedders/voyage_embedders/voyage_contextualized_document_embedder.py) - For contextualized chunk embeddings with `voyage-context-3`
- [VoyageRanker](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/haystack_integrations/components/rankers/voyage/ranker.py) - For reranking documents

### Standard Embeddings

To create semantic embeddings for documents, use `VoyageDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `VoyageTextEmbedder`. For reranking, use `VoyageRanker` with [Voyage Rerankers](https://docs.voyageai.com/docs/reranker).

### Contextualized Embeddings

For improved retrieval quality, use `VoyageContextualizedDocumentEmbedder` with the `voyage-context-3` model. This component preserves context between related document chunks by grouping them together during embedding, reducing context loss that occurs when chunks are embedded independently

**Important:** You must explicitly specify the `model` parameter when initializing any component. Choose from the available models listed in the [Embeddings Documentation](https://docs.voyageai.com/embeddings/). Recommended choices include:
- `voyage-3.5` - Latest general-purpose model for best performance
- `voyage-3.5-lite` - Efficient model with lower latency
- `voyage-3-large` - High-capacity model for complex tasks
- `voyage-context-3` - Contextualized embeddings for improved retrieval (use with `VoyageContextualizedDocumentEmbedder`)
- `voyage-2` - Proven general-purpose model

You can set the environment variable `VOYAGE_API_KEY` instead of passing the API key as an argument. To get an API key, please see the [Voyage AI website.](https://www.voyageai.com/)

> **Note (v1.7.0+):** The `model` parameter is required and must be explicitly specified. Earlier versions defaulted to `voyage-3` for embedders and `rerank-2` for the ranker.

## Example

Below is the example Semantic Search pipeline that uses the [Simple Wikipedia](https://huggingface.co/datasets/pszemraj/simple_wikipedia) Dataset from HuggingFace. You can find more examples in the [`examples`](https://github.com/awinml/voyage-embedders-haystack/tree/main/examples) folder.

Load the dataset:

```python
# Install HuggingFace Datasets using "pip install datasets"
from datasets import load_dataset
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore

# Import Voyage Embedders
from haystack_integrations.components.embedders.voyage_embedders import VoyageDocumentEmbedder, VoyageTextEmbedder

# Load first 100 rows of the Simple Wikipedia Dataset from HuggingFace
dataset = load_dataset("pszemraj/simple_wikipedia", split="validation[:100]")

docs = [
    Document(
        content=doc["text"],
        meta={
            "title": doc["title"],
            "url": doc["url"],
        },
    )
    for doc in dataset
]
```

Index the documents to the `InMemoryDocumentStore` using the `VoyageDocumentEmbedder` and `DocumentWriter`:

```python
doc_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
retriever = InMemoryEmbeddingRetriever(document_store=doc_store)
doc_writer = DocumentWriter(document_store=doc_store)

doc_embedder = VoyageDocumentEmbedder(
    model="voyage-3.5",
    input_type="document",
)
text_embedder = VoyageTextEmbedder(model="voyage-3.5", input_type="query")

# Indexing Pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=doc_embedder, name="DocEmbedder")
indexing_pipeline.add_component(instance=doc_writer, name="DocWriter")
indexing_pipeline.connect("DocEmbedder", "DocWriter")

indexing_pipeline.run({"DocEmbedder": {"documents": docs}})

print(f"Number of documents in Document Store: {len(doc_store.filter_documents())}")
print(f"First Document: {doc_store.filter_documents()[0]}")
print(f"Embedding of first Document: {doc_store.filter_documents()[0].embedding}")
```

Query the Semantic Search Pipeline using the `InMemoryEmbeddingRetriever` and `VoyageTextEmbedder`:

```python
text_embedder = VoyageTextEmbedder(model="voyage-3.5", input_type="query")

# Query Pipeline
query_pipeline = Pipeline()
query_pipeline.add_component(instance=text_embedder, name="TextEmbedder")
query_pipeline.add_component(instance=retriever, name="Retriever")
query_pipeline.connect("TextEmbedder.embedding", "Retriever.query_embedding")

# Search
results = query_pipeline.run({"TextEmbedder": {"text": "Which year did the Joker movie release?"}})

# Print text from top result
top_result = results["Retriever"]["documents"][0].content
print("The top search result is:")
print(top_result)
```

## Contextualized Embeddings Example

The `voyage-context-3` model enables contextualized chunk embeddings, which preserve relationships between document chunks for better retrieval accuracy. Documents with the same `source_id` are embedded together in context:

```python
from haystack import Document
from haystack_integrations.components.embedders.voyage_embedders import VoyageContextualizedDocumentEmbedder

# Create documents with source_id to group related chunks
docs = [
    # Chunks from the same document (source_id: "doc1")
    Document(
        content="Apple Inc. released their Q1 earnings report.",
        meta={"source_id": "doc1", "title": "Apple News"}
    ),
    Document(
        content="Revenue increased by 12% year over year.",
        meta={"source_id": "doc1", "title": "Apple News"}
    ),
    # Chunks from another document (source_id: "doc2")
    Document(
        content="Tesla announced new vehicle production targets.",
        meta={"source_id": "doc2", "title": "Tesla Update"}
    ),
]

# Use VoyageContextualizedDocumentEmbedder for voyage-context-3
embedder = VoyageContextualizedDocumentEmbedder(
    model="voyage-context-3",
    input_type="document",
)

result = embedder.run(documents=docs)

# Chunks with the same source_id are embedded together, preserving context
# This improves retrieval - e.g., searching "Apple revenue growth" will better match
# the second chunk because it maintains its connection to "Apple Inc."
```

For more examples, see the [contextualized embedder example](https://github.com/awinml/voyage-embedders-haystack/blob/voyage_context-3_model/examples/contextualized_embedder_example.py).

## License

`voyage-embedders-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/awinml/voyage-embedders-haystack/blob/main/LICENSE).
