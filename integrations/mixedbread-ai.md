---
layout: integration
name: mixedbread ai
description: Use mixedbread's models as well as top open-source models in seconds
authors:
    - name: mixedbread ai
      socials:
        github: mixedbread-ai
        website: mixedbread.ai
pypi: https://pypi.org/project/mixedbread_ai_haystack/
repo: https://github.com/mixedbread-ai/mixedbread-ai-haystack
type: Model Provider
report_issue: https://github.com/mixedbread-ai/mixedbread-ai-haystack/issues
logo: /logos/mixedbread-ai.png
toc: true
---


mixedbread ai offers a seamless integration for users to employ both mixedbread's models and top open-source models effortlessly. Our platform stands out with its capability to re-rank, provide multi-modal embeddings, classifiers, and more. We're on a mission to make AI accessible to everyone, and we're excited to bring our state-of-the-art models to the Haystack community.

### **Table of Contents**

- [Installation](#installation)
- [Usage](#usage)


## Installation

Install the mixedbread ai integration with a simple pip command:

```bash
pip install mixedbread_ai_haystack
```

## Usage

This integration comes with 2 components:
- [`MixedbreadAiTextEmbedder`](https://github.com/mixedbread-ai/mixedbread-ai-haystack/blob/main/mixedbread_ai_haystack/embedders/text_embedder.py)
- [`MixedbreadAiDocumentEmbedder`](https://github.com/mixedbread-ai/mixedbread-ai-haystack/blob/main/mixedbread_ai_haystack/embedders/document_embedder.py).

For documents you can use `MixedbreadAiDocumentEmbedder` and for queries you can use MixedbreadAiTextEmbedder. Once you've selected the component for your specific use case, initialize the component with the model name and mixedbread ai API key. You can also set the environment variable `MIXEDBREAD_API_KEY` instead of passing the api key as an argument.

Here's a basic example:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from mixedbread_ai_haystack.embedders import MixedbreadAiDocumentEmbedder

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="Sample text for love"), Document(content="and not for hate"), Document(content="Sample text for mixedbread ai integration")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", MixedbreadAiDocumentEmbedder(api_key="MIXEDBREAD_API_KEY", model="UAE-Large-V1"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

Leverage the power of mixedbread ai to bring state-of-the-art ai capabilities to your applications effortlessly.
