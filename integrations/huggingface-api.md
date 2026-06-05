---
layout: integration
name: Hugging Face API
description: Use models through Hugging Face APIs - Inference Providers, Inference Endpoints, TGI and TEI
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/huggingface-api-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/huggingface_api
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/huggingface.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

With this integration, you can use models through Hugging Face APIs:
- [Serverless Inference API (Inference Providers)](https://huggingface.co/docs/inference-providers): access many models from different providers through a unified API.
- [Inference Endpoints](https://huggingface.co/inference-endpoints): deploy models on dedicated, fully managed infrastructure.
- Self-hosted [Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference) and [Text Embeddings Inference (TEI)](https://github.com/huggingface/text-embeddings-inference) servers.

Haystack supports Hugging Face models in other ways too:
- [Hugging Face Transformers](https://haystack.deepset.ai/integrations/huggingface) for local models (LLMs, extractive QA, classification, NER)
- [Sentence Transformers](https://haystack.deepset.ai/integrations/sentence-transformers) for local embedding and ranking models
- [Optimum](https://haystack.deepset.ai/integrations/optimum) for high-performance inference with ONNX Runtime

## Installation

```bash
pip install huggingface-api-haystack
```

## Usage

Unless you are using a self-hosted TGI/TEI server, set your Hugging Face token as the `HF_API_TOKEN` or `HF_TOKEN` environment variable.

### Components

This integration provides several components to interact with Hugging Face APIs:
- [`HuggingFaceAPIChatGenerator`](https://docs.haystack.deepset.ai/docs/huggingfaceapichatgenerator): chat generation with LLMs.
- [`HuggingFaceAPITextEmbedder`](https://docs.haystack.deepset.ai/docs/huggingfaceapitextembedder): creates an embedding for text (used in query/RAG pipelines).
- [`HuggingFaceAPIDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/huggingfaceapidocumentembedder): enriches documents with embeddings (used in indexing pipelines).
- [`HuggingFaceTEIRanker`](https://docs.haystack.deepset.ai/docs/huggingfaceteiranker): ranks documents based on their similarity to the query, using a TEI endpoint.

### Chat Generation

Use [`HuggingFaceAPIChatGenerator`](https://docs.haystack.deepset.ai/docs/huggingfaceapichatgenerator) with the Serverless Inference API (Inference Providers):

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.huggingface_api import HuggingFaceAPIChatGenerator

generator = HuggingFaceAPIChatGenerator(
    api_type="serverless_inference_api",
    api_params={"model": "Qwen/Qwen2.5-7B-Instruct", "provider": "together"},
)

messages = [ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
result = generator.run(messages)
print(result)
```

To use a dedicated Inference Endpoint or a self-hosted TGI server, pass its URL instead:

```python
generator = HuggingFaceAPIChatGenerator(
    api_type="inference_endpoints",  # or "text_generation_inference" for self-hosted TGI
    api_params={"url": "<your-endpoint-url>"},
)
```

### Embedding Models

To create semantic embeddings for documents, use [`HuggingFaceAPIDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/huggingfaceapidocumentembedder) in your indexing pipeline. For generating embeddings for queries, use [`HuggingFaceAPITextEmbedder`](https://docs.haystack.deepset.ai/docs/huggingfaceapitextembedder).

```python
from haystack_integrations.components.embedders.huggingface_api import HuggingFaceAPITextEmbedder

text_embedder = HuggingFaceAPITextEmbedder(
    api_type="serverless_inference_api",
    api_params={"model": "BAAI/bge-small-en-v1.5"},
)

print(text_embedder.run("I love pizza!"))
# {'embedding': [0.017020374536514282, -0.023255806416273117, ...]}
```

Both embedders also work with a self-hosted TEI server:

```python
text_embedder = HuggingFaceAPITextEmbedder(
    api_type="text_embeddings_inference",
    api_params={"url": "http://localhost:8080"},
)
```

### Ranking Models

Use [`HuggingFaceTEIRanker`](https://docs.haystack.deepset.ai/docs/huggingfaceteiranker) to rank documents with a reranking model served by a TEI endpoint:

```python
from haystack import Document
from haystack_integrations.components.rankers.huggingface_api import HuggingFaceTEIRanker

ranker = HuggingFaceTEIRanker(url="http://localhost:8080", top_k=2)

docs = [Document(content="The capital of France is Paris"),
        Document(content="The capital of Germany is Berlin")]

result = ranker.run(query="What is the capital of France?", documents=docs)
print(result["documents"][0].content)
# The capital of France is Paris
```
