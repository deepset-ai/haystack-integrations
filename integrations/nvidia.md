---
layout: integration
name: NVIDIA
description: Use NVIDIA models with Haystack.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/nvidia-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/nvidia
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/nvidia.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Components](#components)
- [Usage](#usage)
  - [NvidiaTextEmbedder](#nvidiatextembedder)
  - [NvidiaDocumentEmbedder](#nvidiadocumentembedder)
  - [NvidiaGenerator](#nvidiagenerator)
  - [NvidiaChatGenerator](#nvidiachatgenerator)
  - [NvidiaRanker](#nvidiaranker)
- [Self-host with NVIDIA NIM](#self-host-with-nvidia-nim)
- [Use NVIDIA components in Haystack pipelines](#use-nvidia-components-in-haystack-pipelines)
  - [Indexing pipeline](#indexing-pipeline)
  - [RAG query pipeline](#rag-query-pipeline)
- [License](#license)

## Overview

The `nvidia-haystack` package contains Haystack integrations for chat models, embeddings, and reranking powered by [NVIDIA AI Foundation Models](https://www.nvidia.com/en-us/ai-data-science/foundation-models/) and hosted on the [NVIDIA API Catalog](https://build.nvidia.com/).

NVIDIA AI Foundation models are community- and NVIDIA-built models that are optimized to deliver the best performance on NVIDIA-accelerated infrastructure. You can use the API to query live endpoints that are available on the NVIDIA API Catalog to get quick results from a DGX-hosted cloud compute environment, or you can download models with [NVIDIA NIM](https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/), which is included with the NVIDIA AI Enterprise license. The ability to run models on-premises gives your enterprise ownership of your customizations and full control of your IP and AI application.

NIM microservices are packaged as container images on a per model or model family basis and are distributed as NGC container images through the [NVIDIA NGC Catalog](https://catalog.ngc.nvidia.com/).

## Prerequisites

To get access to the NVIDIA API Catalog, do the following:

1. Create a free account on the [NVIDIA API Catalog](https://build.nvidia.com/) and log in.
2. Click your profile icon, and then click **API Keys**.
3. Click **Generate API Key**, and then click **Generate Key**.
4. Copy and save your key.

Set the key as an environment variable:

```bash
export NVIDIA_API_KEY="nvapi-..."
```

## Installation

```bash
pip install nvidia-haystack
```

## Components

This integration introduces the following components:

- [**NvidiaTextEmbedder**](https://docs.haystack.deepset.ai/docs/nvidiatextembedder): A component for embedding text using NVIDIA embedding models. For models that differentiate between query and document inputs, this component embeds the input query.
  
- [**NvidiaDocumentEmbedder**](https://docs.haystack.deepset.ai/docs/nvidiadocumentembedder): A component for embedding documents using NVIDIA embedding models.

- [**NvidiaGenerator**](https://docs.haystack.deepset.ai/docs/nvidiagenerator): A component for generating text using generative models.

- [**NvidiaChatGenerator**](https://docs.haystack.deepset.ai/docs/nvidiachatgenerator): A component for chat completion using NVIDIA-hosted models. Takes a list of `ChatMessage` and returns `ChatMessage` replies.

- [**NvidiaRanker**](https://docs.haystack.deepset.ai/docs/nvidiaranker): A component for ranking documents using NVIDIA reranking models.

## Usage

### NvidiaTextEmbedder

```python
from haystack_integrations.components.embedders.nvidia import NvidiaTextEmbedder

text_to_embed = "I love pizza!"

text_embedder = NvidiaTextEmbedder(model="nvidia/llama-3.2-nv-embedqa-1b-v2")
text_embedder.warm_up()

print(text_embedder.run(text_to_embed))
# {'embedding': [-0.02264290489256382, -0.03457780182361603, ...}
```

### NvidiaDocumentEmbedder

```python
from haystack.dataclasses import Document
from haystack_integrations.components.embedders.nvidia import NvidiaDocumentEmbedder

documents = [
    Document(content="Pizza is made with dough and cheese"),
    Document(content="Cake is made with flour and sugar"),
    Document(content="Omelet is made with eggs"),
]

document_embedder = NvidiaDocumentEmbedder(model="nvidia/llama-3.2-nv-embedqa-1b-v2")
document_embedder.warm_up()
document_embedder.run(documents=documents)
# {'documents': [Document(id=..., content: 'Pizza is made with dough and cheese', embedding: vector of size 2048), ...], 'meta': {'usage': {'prompt_tokens': 36, 'total_tokens': 36}}}
```

### NvidiaGenerator

```python
from haystack_integrations.components.generators.nvidia import NvidiaGenerator

generator = NvidiaGenerator(
    model="meta/llama-3.1-70b-instruct",
    model_arguments={
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,
    },
)
generator.warm_up()

result = generator.run(prompt="When was the Golden Gate Bridge built?")
print(result["replies"])
print(result["meta"])
# ['The Golden Gate Bridge was built between 1933 and 1937...']
# [{'role': 'assistant', 'finish_reason': 'stop'}]
```

### NvidiaChatGenerator

```python
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.generators.nvidia import NvidiaChatGenerator

generator = NvidiaChatGenerator(
    model="meta/llama-3.1-8b-instruct",
    api_key=Secret.from_env_var("NVIDIA_API_KEY"),
)

messages = [ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
result = generator.run(messages)
print(result["replies"])
print(result["meta"])
```

### NvidiaRanker

```python
from haystack import Document
from haystack.utils import Secret
from haystack_integrations.components.rankers.nvidia import NvidiaRanker

ranker = NvidiaRanker(
    api_key=Secret.from_env_var("NVIDIA_API_KEY"),
)
ranker.warm_up()

query = "What is the capital of Germany?"
documents = [
    Document(content="Berlin is the capital of Germany."),
    Document(content="The capital of Germany is Berlin."),
    Document(content="Germany's capital is Berlin."),
]

result = ranker.run(query, documents, top_k=1)
print(result["documents"][0].content)
# The capital of Germany is Berlin.
```

## Self-host with NVIDIA NIM

When you are ready to deploy your AI application, you can self-host models with NVIDIA NIM. For more information, refer to [NVIDIA NIM Microservices](https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/).

The following code connects to locally hosted NIM microservices:

```python
from haystack_integrations.components.generators.nvidia import NvidiaChatGenerator

# Connect to a chat NIM running at localhost:8000
generator = NvidiaChatGenerator(
    base_url="http://localhost:8000/v1",
    model="meta/llama-3.1-8b-instruct",
)
```

## Use NVIDIA components in Haystack pipelines

### Indexing pipeline

```python
from haystack import Pipeline
from haystack.dataclasses import Document
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.nvidia import NvidiaDocumentEmbedder

documents = [
    Document(content="Tilde lives in San Francisco"),
    Document(content="Tuana lives in Amsterdam"),
    Document(content="Bilge lives in Istanbul"),
]

document_store = InMemoryDocumentStore()

document_embedder = NvidiaDocumentEmbedder(model="nvidia/llama-3.2-nv-embedqa-1b-v2")
writer = DocumentWriter(document_store=document_store)

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=document_embedder, name="document_embedder")
indexing_pipeline.add_component(instance=writer, name="writer")

indexing_pipeline.connect("document_embedder.documents", "writer.documents")
indexing_pipeline.run(data={"document_embedder": {"documents": documents}})

# Calling filter with no arguments prints the contents of the document store
document_store.filter_documents({})
```

### RAG query pipeline

```python
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.nvidia import NvidiaGenerator
from haystack_integrations.components.embedders.nvidia import NvidiaTextEmbedder

prompt = """Answer the query, based on the content in the documents.
If you can't answer based on the given documents, say so.

Documents:
{% for doc in documents %}
  {{doc.content}}
{% endfor %}

Query: {{query}}
"""

text_embedder = NvidiaTextEmbedder(model="nvidia/llama-3.2-nv-embedqa-1b-v2")
retriever = InMemoryEmbeddingRetriever(document_store=document_store)
prompt_builder = PromptBuilder(template=prompt)
generator = NvidiaGenerator(model="meta/llama-3.1-70b-instruct")
generator.warm_up()

rag_pipeline = Pipeline()

rag_pipeline.add_component(instance=text_embedder, name="text_embedder")
rag_pipeline.add_component(instance=retriever, name="retriever")
rag_pipeline.add_component(instance=prompt_builder, name="prompt_builder")
rag_pipeline.add_component(instance=generator, name="generator")

rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "generator")

question = "Who lives in San Francisco?"
result = rag_pipeline.run(
    data={
        "text_embedder": {"text": question},
        "prompt_builder": {"query": question},
    }
)
print(result)
# {'text_embedder': {'meta': {'usage': {'prompt_tokens': 10, 'total_tokens': 10}}}, 'generator': {'replies': ['Tilde'], 'meta': [{'role': 'assistant', 'finish_reason': 'stop'}], 'usage': {'completion_tokens': 3, 'prompt_tokens': 101, 'total_tokens': 104}}}
```

## License

`nvidia-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
