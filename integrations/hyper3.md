---
layout: integration
name: Hyper3
description: Native Lorentz image-text embeddings with Hyper3-CLIP
authors:
    - name: hyper³labs
      socials:
        github: Hyper3Labs
pypi: https://pypi.org/project/hyper-models/
repo: https://github.com/Hyper3Labs/hyper-models
type: Model Provider
report_issue: https://github.com/Hyper3Labs/hyper-models/issues
version: Haystack 3.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The Hyper3 integration ships inside [hyper-models](https://github.com/Hyper3Labs/hyper-models) and provides native image and text embedders for [Hyper3-CLIP v1](https://huggingface.co/hyper3labs/hyper3-clip-v1). The components produce 513-coordinate Lorentz embeddings and preserve the model's radial information.

The integration reuses Haystack's existing `OutputAdapter`, `InMemoryDocumentStore`, and embedding retriever. It does not introduce a custom retriever or document store.

## Installation

The integration requires Haystack 3.2 or newer and uses the SDK's Transformers 5 runtime. Hyper3-CLIP v1 is gated, so request access on the model page and authenticate with `hf auth login`, `HF_TOKEN`, or `HF_API_TOKEN`. Install with:

```bash
pip install "hyper-models[ml,haystack]>=0.4.0"
```

## Usage

### Components

- `Hyper3DocumentImageEmbedder` embeds image paths stored in Haystack document metadata.
- `Hyper3TextEmbedder` embeds text queries in the same native Lorentz space.

Store native image points unchanged. Negate only the first coordinate of each native query before dot-product retrieval:

```python
from haystack import Document, Pipeline
from haystack.components.converters import OutputAdapter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from hyper_models.integrations.haystack import (
    Hyper3DocumentImageEmbedder,
    Hyper3TextEmbedder,
)

documents = [
    # Replace these paths with your own image files.
    Document(id="sofa", meta={"file_path": "sofa.jpg"}),
    Document(id="chair", meta={"file_path": "chair.jpg"}),
]

store = InMemoryDocumentStore(embedding_similarity_function="dot_product")

indexing = Pipeline()
indexing.add_component("embedder", Hyper3DocumentImageEmbedder())
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.connect("embedder.documents", "writer.documents")
indexing.run({"embedder": {"documents": documents}})

query = Pipeline()
query.add_component("embedder", Hyper3TextEmbedder())
query.add_component(
    "lorentz_query",
    OutputAdapter(
        template="{{ [-embedding[0]] + embedding[1:] }}",
        output_type=list[float],
    ),
)
query.add_component(
    "retriever",
    InMemoryEmbeddingRetriever(document_store=store, top_k=2, scale_score=False),
)
query.connect("embedder.embedding", "lorentz_query.embedding")
query.connect("lorentz_query.output", "retriever.query_embedding")

result = query.run({"embedder": {"text": "a grey sofa"}})
for document in result["retriever"]["documents"]:
    print(document.id, document.score)
```

For native Lorentz points `q = (q0, q1, ...)` and `x = (x0, x1, ...)`, the inner product is `-q0*x0 + q1*x1 + ...`. Negating the query's first coordinate makes an ordinary dot product compute that value. `scale_score=False` keeps these raw scores unchanged, so higher scores return nearer points first. Query and document embeddings must come from the same model revision.

The components use the SDK's model loader and pin the released model revision by default.

To deserialize a trusted saved pipeline containing these components, use `Pipeline.loads(yaml_text, allowed_modules=["hyper_models.integrations.haystack"])`.

This route scores every stored image exactly with `InMemoryDocumentStore`. Vector stores that normalize embeddings or use approximate indexes require separate numerical and recall validation.

## License

The hyper-models SDK uses the MIT license; its optional Haystack integration retains the Apache-2.0 license. Hyper3-CLIP v1 has its own model license on the Hugging Face model page.
