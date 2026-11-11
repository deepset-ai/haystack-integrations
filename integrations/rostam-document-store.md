---
layout: integration
name: Rostam
description: Use the Rostam vector database with Haystack
authors:
  - name: RostamLabs
    socials:
      github: rostamlabs
pypi: https://pypi.org/project/rostam-client/
repo: https://github.com/rostamlabs/rostam
type: Document Store
report_issue: https://github.com/rostamlabs/rostam/issues
version: Haystack 2.0
toc: true
---

An integration of [Rostam](https://rostamlabs.com) — a high-performance vector
database and sub-microsecond key-value store in a single Go engine — with
[Haystack](https://haystack.deepset.ai/).

`RostamDocumentStore` stores Haystack `Document`s in a Rostam collection and runs
dense similarity search over them; `RostamEmbeddingRetriever` is the matching
retriever component for Haystack pipelines. Rostam can be embedded as a library,
run standalone (REST / gRPC / TCP), or replicated across a Raft cluster, and adds
HNSW/IVF/Vamana indexes, quantization, hybrid dense+sparse and BM25 search, and
metadata filtering.

## Installation

```bash
pip install "rostam-client[haystack]"
```

Point it at a running Rostam server:

```bash
docker run -p 8080:8080 -e ROSTAM_API_KEY=secret ghcr.io/rostamlabs/rostam:latest
```

## Usage

```python
from haystack import Document
from rostam.haystack import RostamDocumentStore, RostamEmbeddingRetriever

store = RostamDocumentStore(url="http://localhost:8080", collection="docs")

# Write documents (each Document must carry an embedding)
store.write_documents([
    Document(content="Rostam is a vector database and KV store in one Go engine.",
             embedding=[0.1, 0.2, 0.3]),  # from your Haystack embedder
])

# Retrieve in a pipeline
retriever = RostamEmbeddingRetriever(document_store=store, top_k=5)
results = retriever.run(query_embedding=[0.1, 0.2, 0.3])
```

Pair `RostamEmbeddingRetriever` with any Haystack embedder (or Rostam's built-in
pure-Go local embeddings) in a retrieval or RAG pipeline. See the
[Rostam docs](https://docs.rostamlabs.com/) for server setup, indexes, hybrid
search, and filtering.

## License

`rostam-client` is available under the Apache-2.0 license.
