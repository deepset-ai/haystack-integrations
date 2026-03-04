---
layout: integration
name: FAISS
description: A Document Store for vector search using FAISS
authors:
  - name: Guna Palanivel
    socials:
      github: GunaPalanivel
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/faiss-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/faiss
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/meta.png
version: Haystack 2.0
toc: true
---

The integration provides `FAISSDocumentStore`, which uses [FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search) for vector search and a simple JSON file for metadata storage. It is suitable for small to medium-sized datasets where simplicity is preferred over scalability, and supports optional persistence by saving the FAISS index to a `.faiss` file and documents to a `.json` file. Use `FAISSEmbeddingRetriever` for semantic retrieval in your pipelines.

## Installation

Install the package with pip:

```bash
pip install faiss-haystack
```

For GPU-accelerated FAISS, install `faiss-gpu` separately and use it in place of the default `faiss-cpu` dependency where applicable.

The examples below use [Sentence Transformers](https://www.sbert.net/) for embeddings. Install with: `pip install "sentence-transformers>=5.0.0"`.

## Usage

### In-memory document store

Create an in-memory document store (no persistence):

```python
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

document_store = FAISSDocumentStore(embedding_dim=768)
```

### Persisted document store

To save and load the index and documents from disk, pass `index_path`:

```python
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

document_store = FAISSDocumentStore(
    index_path="./my_faiss_index",
    index_string="Flat",
    embedding_dim=768,
)
# After writing documents, persist with:
# document_store.save("./my_faiss_index")
# Later, create the store with the same index_path to load from disk.
```

### Writing documents

Use an indexing pipeline to write documents (with embeddings) to the store.
This example uses Sentence Transformers (768 dimensions).

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

document_store = FAISSDocumentStore(
    index_path="./my_faiss_index",
    index_string="Flat",
    embedding_dim=768,
)

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "embedder")
indexing.connect("embedder", "writer")
indexing.run({"converter": {"sources": file_paths}})

# If using persistence, save after indexing
# document_store.save("./my_faiss_index")
```

### Retrieval with FAISSEmbeddingRetriever

Build a query pipeline using `FAISSEmbeddingRetriever` for semantic search:

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.faiss import FAISSEmbeddingRetriever

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
query_pipeline.add_component(
    "retriever",
    FAISSEmbeddingRetriever(document_store=document_store, top_k=10),
)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

results = query_pipeline.run({"text_embedder": {"text": "your query"}})
documents = results["retriever"]["documents"]
```

## License

`faiss-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
