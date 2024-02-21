---
layout: integration
name: FastEmbed
description: Use the Fastembed embedding models
authors:
    - name: Nicola Procopio
      socials:
        github: nickprock
        linkedin: https://www.linkedin.com/in/nicolaprocopio
pypi: https://pypi.org/project/fastembed-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/fastembed
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
# logo: /logos/your-logo.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
[Fastembed](https://qdrant.github.io/fastembed/) is a lightweight, fast, Python library built for embedding generation.

1. Light & Fast
  * Quantized model weights
  * ONNX Runtime for inference via Optimum

2. Accuracy/Recall
  * Better than OpenAI Ada-002
  * Default is Flag Embedding, which is top of the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
  * List of [supported models](https://qdrant.github.io/fastembed/examples/Supported_Models/) - including multilingual models


## Installation

```bash
pip install fastembed-haystack
```

## Usage
### Components

You can use Fastembed models with two components: [FastembedTextEmbedder](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/fastembed/src/haystack_integrations/components/embedders/fastembed/fastembed_text_embedder.py) and [FastembedDocumentEmbedder](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/fastembed/src/haystack_integrations/components/embedders/fastembed/fastembed_document_embedder.py).

To create semantic embeddings for documents, use `FastembedDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `FastembedTextEmbedder`.
  
### Example

Below is the example indexing pipeline with `InMemoryDocumentStore`, `InMemoryEmbeddingRetriever`, `FastembedTextEmbedder` and  `FastembedDocumentEmbedder`:

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

### License

`fastembed-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
