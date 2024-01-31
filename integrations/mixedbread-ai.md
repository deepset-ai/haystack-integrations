---
layout: integration
name: mixedbread ai
description: Use mixedbread's models as well as top open-source models in seconds
authors:
    - name: mixedbread ai
      socials:
        github: mixedbread-ai
        website: mixedbread.ai
pypi: https://pypi.org/project/mixedbread-ai-haystack/
repo: https://github.com/mixedbread-ai/mixedbread-ai-haystack
type: Model Provider
report_issue: https://github.com/mixedbread-ai/mixedbread-ai-haystack/issues
logo: /logos/mixedbread-ai.png
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[mixedbread ai](https://www.mixedbread.ai) is an ai start-up that provides open-source, as well as, in-house embedding models. You can choose from various foundation models to find the one best suited for your use case. More information can be found on the [documentation page](https://www.mixedbread.ai/api-reference/integrations#haystack).

## Installation

Install the mixedbread ai integration with a simple pip command:

```bash
pip install mixedbread-ai-haystack
```

## Usage

This integration comes with 2 components:
- [`MixedbreadAiTextEmbedder`](https://github.com/mixedbread-ai/mixedbread-ai-haystack/blob/main/mixedbread_ai_haystack/embedders/text_embedder.py)
- [`MixedbreadAiDocumentEmbedder`](https://github.com/mixedbread-ai/mixedbread-ai-haystack/blob/main/mixedbread_ai_haystack/embedders/document_embedder.py).

For documents you can use `MixedbreadAiDocumentEmbedder` and for queries you can use `MixedbreadAiTextEmbedder`. Once you've selected the component for your specific use case, initialize the component with the `model` and the [`api_key`](https://www.mixedbread.ai/dashboard?next=api-keys). You can also set the environment variable `MIXEDBREAD_API_KEY` instead of passing the api key as an argument.



### In a Pipeline

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore, InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from mixedbread_ai_haystack.embedders import MixedbreadAiDocumentEmbedder, MixedbreadAiTextEmbedder

# -------------------------------------
# Indexing Pipeline
# -------------------------------------
document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
documents = [Document(content="china is the most populous country in the world."), Document(content="india is the second most populous country in the world."), Document(content="united states is the third most populous country in the world.")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("doc_embedder", MixedbreadAiDocumentEmbedder(api_key="MIXEDBREAD_API_KEY", model="UAE-Large-V1"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("doc_embedder", "writer")

indexing_pipeline.run({"doc_embedder": {"documents": documents}})

# -------------------------------------
# Query Pipeline
# -------------------------------------
text_embedder = MixedbreadAiTextEmbedder(model="UAE-Large-V1", api_key="MIXEDBREAD_API_KEY")

# Query Pipeline
query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", text_embedder)
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

results = query_pipeline.run({"text_embedder": {"text": "Which country has the biggest population?"}})
top_document = results["retriever"]["documents"][0].content
print(top_document)
```
