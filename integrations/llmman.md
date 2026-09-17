---
layout: integration
name: llmman
description: Run models locally with llmman, a local model runner that serves the Ollama API (alongside OpenAI- and Anthropic-compatible ones) on port 17434.
authors:
    - name: Eric Curtin
      socials:
        github: ericcurtin
repo: https://github.com/llmmanorg/llmman
type: Model Provider
report_issue: https://github.com/llmmanorg/llmman/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Chat Generation](#chat-generation)
  - [Tool Calling](#tool-calling)
  - [Embedders](#embedders)
  - [Using the OpenAI-compatible API](#using-the-openai-compatible-api)

## Introduction

[llmman](https://github.com/llmmanorg/llmman) is a local model runner that serves the Ollama API (alongside OpenAI- and Anthropic-compatible ones) on port `17434`.

Models are pulled as OCI artifacts from any registry (Docker Hub, GHCR, quay, ...) or straight from Hugging Face (`hf.co/org/model`), and are served by upstream `llama.cpp` (`llama-server`), `vllm`, or `mlx-lm`.

Because llmman speaks the Ollama API, you do not need a dedicated Haystack package: the existing [`OllamaChatGenerator`](https://docs.haystack.deepset.ai/docs/ollamachatgenerator), [`OllamaTextEmbedder`](https://docs.haystack.deepset.ai/docs/ollamatextembedder) and [`OllamaDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/ollamadocumentembedder) from `ollama-haystack` work unchanged once pointed at `http://localhost:17434`.

## Installation

Install llmman:

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/llmmanorg/llmman/main/install.sh | sh

# Windows (PowerShell)
irm https://raw.githubusercontent.com/llmmanorg/llmman/main/install.ps1 | iex
```

Start the server and pull a model:

```bash
llmman serve
llmman pull gemma4
```

By default llmman binds to `127.0.0.1:17434`. Override the address with the `LLMMAN_HOST` environment variable (`[host][:port]`).

Then install the Ollama Haystack integration:

```bash
pip install ollama-haystack
```

## Usage

llmman serves the Ollama endpoints `/api/generate`, `/api/chat`, `/api/embed`, `/api/embeddings`, `/api/tags`, `/api/show`, `/api/ps`, `/api/pull`, `/api/push`, `/api/create`, `/api/copy`, `/api/delete` and `/api/version`. `/api/chat` supports `tools`, `images`, `format` (JSON / JSON schema) and `keep_alive`.

The only difference from a stock Ollama setup is the port, so pass `url="http://localhost:17434"` to the Ollama components.

### Chat Generation

```python
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.generators.ollama import OllamaChatGenerator

messages = [
    ChatMessage.from_user("What's Natural Language Processing?"),
    ChatMessage.from_system(
        "Natural Language Processing (NLP) is a field of computer science and artificial "
        "intelligence concerned with the interaction between computers and human language"
    ),
    ChatMessage.from_user("How do I get started?"),
]
client = OllamaChatGenerator(model="gemma4", timeout=45, url="http://localhost:17434")

response = client.run(messages, generation_kwargs={"temperature": 0.2})

print(response["replies"][0].text)
```

Any model you have pulled works here, e.g. `qwen3.8` or a Hugging Face reference such as `hf.co/unsloth/Qwen3.5-0.8B-GGUF`.

### Tool Calling

llmman's `/api/chat` endpoint supports `tools`, so `OllamaChatGenerator` tool calling works as it does with Ollama:

```python
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack_integrations.components.generators.ollama import OllamaChatGenerator


@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 22°C in {city}"


generator = OllamaChatGenerator(
    model="gemma4",
    url="http://localhost:17434",
    generation_kwargs={"temperature": 0.0},
    tools=[get_weather],
)

response = generator.run(
    messages=[ChatMessage.from_user(
        "What's the weather in Berlin? Use the get_weather tool."
    )]
)
print(response["replies"][0].tool_calls)
```

### Embedders

[`OllamaTextEmbedder`](https://docs.haystack.deepset.ai/docs/ollamatextembedder) and [`OllamaDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/ollamadocumentembedder) work against llmman's `/api/embed` endpoint once pointed at `http://localhost:17434`.

First pull an embedding model, for example straight from Hugging Face:

```bash
llmman pull hf.co/nomic-ai/nomic-embed-text-v1.5-GGUF
```

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder, OllamaTextEmbedder

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [
    Document(content="I saw a black horse running"),
    Document(content="Germany has many big cities"),
    Document(content="My name is Wolfgang and I live in Berlin"),
]

document_embedder = OllamaDocumentEmbedder(
    model="hf.co/nomic-ai/nomic-embed-text-v1.5-GGUF", url="http://localhost:17434"
)
documents_with_embeddings = document_embedder.run(documents)["documents"]
document_store.write_documents(documents_with_embeddings)

query_pipeline = Pipeline()
query_pipeline.add_component(
    "text_embedder",
    OllamaTextEmbedder(model="hf.co/nomic-ai/nomic-embed-text-v1.5-GGUF", url="http://localhost:17434"),
)
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

query = "Who lives in Berlin?"

result = query_pipeline.run({"text_embedder": {"text": query}})

print(result["retriever"]["documents"][0])
```

### Using the OpenAI-compatible API

llmman also exposes `/v1/chat/completions`, `/v1/completions`, `/v1/models` and `/v1/responses`, so you can use [`OpenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/openaichatgenerator) instead of `OllamaChatGenerator` if you prefer to depend only on `haystack-ai`:

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_token("sk-no-key-required"),  # llmman needs no key
    model="gemma4",
    api_base_url="http://localhost:17434/v1",
)

response = generator.run([ChatMessage.from_user("What's Natural Language Processing?")])
print(response["replies"][0].text)
```
