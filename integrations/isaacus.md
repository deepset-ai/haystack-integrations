---
layout: integration
name: Isaacus
description: Use the latest foundational legal AI models from Isaacus in Haystack.
authors:
  - name: Isaacus
    socials:
      github: isaacus-dev
      linkedin: https://www.linkedin.com/company/isaacus/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/isaacus
type: Model Provider
logo: /logos/isaacus.png
version: Haystack 2.0
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Components](#components)
- [Quick Example](#quick-example)
- [Docs](#docs)
- [License](#license)

## Overview
Isaacus currently supports the following models in Haystack:
- **Kanon 2 embedder** – the best performing model on the [Massive Legal Embedding Benchmark (MLEB)](https://isaacus.com/blog/introducing-kanon-2-embedder). It is a legal domain-specific embedding model that can be used for semantic search, question answering, and other NLP tasks.

## Installation
```bash
pip install isaacus-haystack
```

## Components
- `Kanon2TextEmbedder` – embeds query text into a vector.
- `Kanon2DocumentEmbedder` – embeds Haystack `Document`s and writes to `document.embedding`.

## Quick Example
```python
from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.utils.auth import Secret
from isaacus_haystack.kanon2_embedder import Kanon2TextEmbedder, Kanon2DocumentEmbedder

store = InMemoryDocumentStore(embedding_similarity_function="dot_product")
embedder = Kanon2DocumentEmbedder(api_key=Secret.from_env_var("ISAACUS_API_KEY"))

raw_docs = [Document(content="Isaacus built Kanon 2: the best performing model on the Massive Legal Embedding Benchmark (MLEB).")]
store.write_documents(embedder.run(raw_docs)["documents"])

pipe = Pipeline()
pipe.add_component("q", Kanon2TextEmbedder(api_key=Secret.from_env_var("ISAACUS_API_KEY")))
pipe.add_component("ret", InMemoryEmbeddingRetriever(document_store=store))
pipe.connect("q.embedding", "ret.query_embedding")

print(pipe.run({"q": {"text": "Who builds Kanon 2?"}}))
```

## Docs
- Isaacus Embeddings API: https://docs.isaacus.com/capabilities/embedding
- Haystack: https://haystack.deepset.ai/

## License
MIT
