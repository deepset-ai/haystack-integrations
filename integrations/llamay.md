---
layout: integration
name: llamay
description: Run open-weight models locally with llamay and use them in Haystack
authors:
    - name: Kosa8 Labs
      socials:
        github: AzmxAI
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/AzmxAI/llamay-releases
type: Model Provider
report_issue: https://github.com/AzmxAI/llamay-releases/issues
logo: /logos/llamay.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Using `OpenAIChatGenerator`](#using-openaichatgenerator)
  - [Use with a Haystack Agent](#use-with-a-haystack-agent)
  - [Embeddings and RAG](#embeddings-and-rag)

## Overview

[llamay](https://llamay.com) is a local inference server for GGUF models. It is free to use, but not open source.
`llamay serve` exposes an OpenAI-compatible API (chat completions with streaming and tool calling, embeddings, and models)
on `http://127.0.0.1:11435/v1`, so it works with Haystack's OpenAI components:
[OpenAIChatGenerator](https://docs.haystack.deepset.ai/docs/openaichatgenerator),
[OpenAITextEmbedder](https://docs.haystack.deepset.ai/docs/openaitextembedder) and
[OpenAIDocumentEmbedder](https://docs.haystack.deepset.ai/docs/openaidocumentembedder).

Models are named the way Ollama names them (`qwen2.5:7b`) or by a Hugging Face reference
(`hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M`).

## Installation

Install llamay from [llamay.com/download](https://llamay.com/download/), for example on macOS or Linux:

```bash
curl -fsSL https://llamay.com/install.sh | sh
```

Pull a chat model and an embedding model, then start the server:

```bash
llamay pull qwen2.5:7b
llamay pull all-minilm
llamay serve -m qwen2.5:7b -embed all-minilm
```

Install Haystack:

```bash
pip install haystack-ai
```

The server needs no API key by default. The OpenAI client still expects one, so pass any placeholder.
If you start the server with `-api-key <key>` (recommended when binding beyond loopback with `-addr 0.0.0.0:11435`),
pass that key instead, for example with `Secret.from_env_var("LLAMAY_API_KEY")`.

## Usage

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_token("unused"),  # llamay needs no key unless started with -api-key
    api_base_url="http://localhost:11435/v1",
    model="qwen2.5:7b",
)

response = generator.run(messages=[ChatMessage.from_user("Say hello in one short sentence.")])
print(response["replies"][0].text)
```

Streaming works through `streaming_callback` as with OpenAI.

### Use with a Haystack Agent

llamay supports tool calling, so `OpenAIChatGenerator` can drive an `Agent`:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def weather(city: str) -> str:
    """Return the weather for a city."""
    return f"The weather in {city} is sunny and 22 degrees"


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_token("unused"),
        api_base_url="http://localhost:11435/v1",
        model="qwen2.5:7b",
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Lisbon?")])
print(result["last_message"].text)
```

### Embeddings and RAG

With the server started with `-embed all-minilm`, the OpenAI embedders work against the same base URL:

```python
from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

base_url = "http://localhost:11435/v1"
api_key = Secret.from_token("unused")

document_store = InMemoryDocumentStore()
documents = [
    Document(content="The best food in the world is pizza"),
    Document(content="I saw a black horse running"),
    Document(content="The capital of Sweden is Stockholm"),
]

indexing = Pipeline()
indexing.add_component("embedder", OpenAIDocumentEmbedder(api_key=api_key, api_base_url=base_url, model="all-minilm"))
indexing.add_component("writer", DocumentWriter(document_store=document_store))
indexing.connect("embedder", "writer")
indexing.run({"embedder": {"documents": documents}})

template = [
    ChatMessage.from_user(
        """Answer the question from these documents.
{% for doc in documents %}{{ doc.content }}
{% endfor %}
Question: {{ question }}"""
    )
]

rag = Pipeline()
rag.add_component("text_embedder", OpenAITextEmbedder(api_key=api_key, api_base_url=base_url, model="all-minilm"))
rag.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store, top_k=1))
rag.add_component("prompt_builder", ChatPromptBuilder(template=template, required_variables=["documents", "question"]))
rag.add_component("llm", OpenAIChatGenerator(api_key=api_key, api_base_url=base_url, model="qwen2.5:7b"))
rag.connect("text_embedder.embedding", "retriever.query_embedding")
rag.connect("retriever.documents", "prompt_builder.documents")
rag.connect("prompt_builder.prompt", "llm.messages")

question = "What is the capital of Sweden?"
result = rag.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
print(result["llm"]["replies"][0].text)
```
