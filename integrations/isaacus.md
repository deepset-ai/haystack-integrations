---
layout: integration
name: Isaacus
description: Use the latest foundational legal AI models from Isaacus in Haystack.
authors:
  - name: Isaacus
    socials:
      github: isaacus-dev
      linkedin: https://www.linkedin.com/company/isaacus/
type: Model Provider
logo: /logos/isaacus.png
version: Haystack 2.0
repo: https://github.com/isaacus-dev/isaacus-haystack
pypi: https://pypi.org/project/isaacus-haystack
report_issue: https://github.com/isaacus-dev/isaacus-haystack/issues
---

### ***Table of Contents***
- [Overview](#overview)
- [Installation](#installation)
- [Components](#components)
- [Quick Example](#quick-example)
- [Docs](#docs)
- [License](#license)

## Overview
[Isaacus](https://isaacus.com/) is a foundational legal AI research company building AI models, apps, and tools for the legal tech ecosystem.

Isaacus offers first-class support for Haystack via the `isaacus-haystack` package, providing embedders optimized for legal retrieval—most notably **Kanon 2**, a high-performing legal embedding model (see the [Kanon 2 overview](https://isaacus.com/blog/introducing-kanon-2-embedder) and the [Massive Legal Embedding Benchmark](https://isaacus.com/blog/introducing-mleb)).

## Installation
```bash
pip install isaacus-haystack
```

## Components
- `IsaacusTextEmbedder` – embeds query text into a vector.
- `IsaacusDocumentEmbedder` – embeds Haystack `Document`s and writes to `document.embedding`.

## Quick Example
```python
from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.utils import Secret
from haystack_integrations.components.embedders.isaacus import (IsaacusTextEmbedder, IsaacusDocumentEmbedder)

store = InMemoryDocumentStore(embedding_similarity_function="dot_product")
embedder = IsaacusDocumentEmbedder(
    api_key=Secret.from_env_var("ISAACUS_API_KEY"),
    model="kanon-2-embedder",          # choose any supported Isaacus embedding model
    # dimensions=1792,                 # optionally set to match your vector DB
)

raw_docs = [Document(content="Isaacus releases Kanon 2 Embedder: the world's best legal embedding model."),
            Document(content="Isaacus also offers legal zero-shot classification and extractive question answering models.")]
store.write_documents(embedder.run(raw_docs)["documents"])

pipe = Pipeline()
pipe.add_component("q", IsaacusTextEmbedder(
    api_key=Secret.from_env_var("ISAACUS_API_KEY"),
    model="kanon-2-embedder",
))
pipe.add_component("ret", InMemoryEmbeddingRetriever(document_store=store))
pipe.connect("q.embedding", "ret.query_embedding")

print(pipe.run({"q": {"text": "Who built Kanon 2 Embedder?"}}))
```

## Docs
- Isaacus Embeddings API: https://docs.isaacus.com/capabilities/embedding
- Haystack: https://haystack.deepset.ai/

## License
Apache-2.0