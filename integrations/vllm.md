---
layout: integration
name: vLLM
description: Use the vLLM inference engine with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/vllm-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/vllm
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/vllm.png
version: Haystack 2.0
toc: true
---
### Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Components](#components)
- [Usage](#usage)
  - [Serving a model with vLLM](#serving-a-model-with-vllm)
  - [VLLMChatGenerator](#vllmchatgenerator)
  - [VLLMTextEmbedder and VLLMDocumentEmbedder](#vllmtextembedder-and-vllmdocumentembedder)
  - [VLLMRanker](#vllmranker)
- [End-to-end example](#end-to-end-example)
- [License](#license)

## Overview

[vLLM](https://github.com/vllm-project/vllm) is a high-throughput and memory-efficient inference and serving engine for LLMs.
It is an open-source project that allows serving open models in production, when you have GPU resources available.

vLLM serves models behind an OpenAI-compatible HTTP server and supports generative, embedding, and ranking models. The `vllm-haystack` integration provides dedicated Haystack components that connect to a running vLLM server.

## Installation

Install vLLM following the [official instructions](https://docs.vllm.ai/en/latest/getting_started/installation.html). For production use cases, there are other options, including [Docker](https://docs.vllm.ai/en/latest/deployment/docker).

Then install the Haystack integration:

```bash
pip install vllm-haystack
```

## Components

This integration introduces the following components:

- [**VLLMChatGenerator**](https://docs.haystack.deepset.ai/docs/vllmchatgenerator): A component for chat completion using generative models served by vLLM. Supports streaming, tool calling, reasoning, and structured outputs.

- [**VLLMTextEmbedder**](https://docs.haystack.deepset.ai/docs/vllmtextembedder): A component for embedding a single string (e.g., a query) using an embedding model served by vLLM.

- [**VLLMDocumentEmbedder**](https://docs.haystack.deepset.ai/docs/vllmdocumentembedder): A component for embedding a list of `Document` objects using an embedding model served by vLLM.

- [**VLLMRanker**](https://docs.haystack.deepset.ai/docs/vllmranker): A component for reranking documents using a ranking model (cross-encoder or late interaction) served by vLLM.

## Usage

### Serving a model with vLLM

`vllm serve` launches an OpenAI-compatible server. For example, to serve a small generative model with reasoning and tool-calling enabled:

```bash
vllm serve "Qwen/Qwen3-0.6B" --port 8000 \
    --reasoning-parser qwen3 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes
```

Embedding and ranking models are served the same way. Just point `vllm serve` at the relevant model (e.g., `sentence-transformers/all-MiniLM-L6-v2` or `BAAI/bge-reranker-base`).

### VLLMChatGenerator

```python
from haystack_integrations.components.generators.vllm import VLLMChatGenerator
from haystack.dataclasses import ChatMessage

llm = VLLMChatGenerator(
    model="Qwen/Qwen3-0.6B",
    api_base_url="http://localhost:8000/v1",
    generation_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": True}}},
)

response = llm.run(messages=[ChatMessage.from_user("Write Python code to reverse a string.")])
print(response["replies"][0].text)

# When reasoning is enabled, the reasoning trace is available separately:
print(response["replies"][0].reasoning)
```

`VLLMChatGenerator` also supports structured outputs via `response_format` and tool calling, making it a drop-in chat generator for Haystack `Agent` pipelines.

### VLLMTextEmbedder and VLLMDocumentEmbedder

Use the two embedders together to build a simple semantic retrieval pipeline:

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.vllm import (
    VLLMDocumentEmbedder,
    VLLMTextEmbedder,
)

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

docs = [
    Document(content="My name is Wolfgang and I live in Berlin"),
    Document(content="My name is Luca and I live in Milan"),
    Document(content="Germany has many big cities"),
    Document(content="Italy is a country in Europe"),
]

document_embedder = VLLMDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2",
    api_base_url="http://localhost:8000/v1",
)
document_store.write_documents(document_embedder.run(docs)["documents"])

query_pipeline = Pipeline()
query_pipeline.add_component(
    "text_embedder",
    VLLMTextEmbedder(
        model="sentence-transformers/all-MiniLM-L6-v2",
        api_base_url="http://localhost:8000/v1",
    ),
)
query_pipeline.add_component(
    "retriever",
    InMemoryEmbeddingRetriever(document_store=document_store, top_k=2),
)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"text_embedder": {"text": "Who lives in Berlin?"}})
for doc in result["retriever"]["documents"]:
    print(doc.score, doc.content)
# 0.668... My name is Wolfgang and I live in Berlin
# 0.602... Germany has many big cities
```

### VLLMRanker

Pair `VLLMRanker` with a fast first-stage retriever (e.g., BM25) to rerank candidates by relevance to the query:

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.rankers.vllm import VLLMRanker

docs = [
    Document(content="Paris is the capital city of France"),
    Document(content="Lyon is a major city in France known for cuisine"),
    Document(content="Toulouse is a large city in France known for aerospace"),
    Document(content="Marseille is a port city in southern France"),
    Document(content="France has a rich history and culture"),
    Document(content="Berlin is the capital of Germany"),
    Document(content="Madrid is the capital city of Spain"),
]
document_store = InMemoryDocumentStore()
document_store.write_documents(docs)

retriever = InMemoryBM25Retriever(document_store=document_store, top_k=10)
ranker = VLLMRanker(
    model="BAAI/bge-reranker-base",
    api_base_url="http://localhost:8000/v1",
    top_k=3,
)

pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
pipeline.add_component("ranker", ranker)
pipeline.connect("retriever.documents", "ranker.documents")

query = "france cities"
result = pipeline.run({"retriever": {"query": query}, "ranker": {"query": query}})
for doc in result["ranker"]["documents"]:
    print(doc.score, doc.content)
# 0.986... Paris is the capital city of France
# 0.914... Lyon is a major city in France known for cuisine
# 0.858... Toulouse is a large city in France known for aerospace
```

## End-to-end example

For a complete walkthrough covering generative, embedding, and ranking models — including a tool-calling agent and a retrieval + reranking pipeline — see the [vLLM + Haystack cookbook notebook](https://haystack.deepset.ai/cookbook/vllm_inference_engine).

## License

`vllm-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
