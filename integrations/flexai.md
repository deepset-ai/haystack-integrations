---
layout: integration
name: FlexAI
description: Use open-weight language and embedding models served by FlexAI
authors:
    - name: FlexAI
      socials:
        github: flexaihq
        twitter: FlexAI
        linkedin: https://www.linkedin.com/company/flexai
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/flexai.png
version: Haystack 3.3
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[FlexAI](https://flex.ai) serves open-weight models — chat, embedding, vision, image, speech and
transcription — on a single inference API.

To start using FlexAI, sign up for an API key at [flex.ai](https://flex.ai). The
[documentation](https://docs.flex.ai) covers the API in full, and the `/v1/models` endpoint returns
the models that are currently served along with their context length and supported features.

## Usage

FlexAI is OpenAI compatible, making it easy to use in Haystack via OpenAI Generators and Embedders.

Set the environment variable `FLEXAI_API_KEY`, point `api_base_url` at `https://api.flex.ai/v1`, and
choose a model from the [model list](https://docs.flex.ai).

### Using `ChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FLEXAI_API_KEY"),
    api_base_url="https://api.flex.ai/v1",
    model="DeepSeek-V4-Flash-0731",
    generation_kwargs={"max_tokens": 512},
)

response = generator.run(
    messages=[ChatMessage.from_user("What is an open-weight model? Answer in one sentence.")]
)
print(response["replies"][0].text)
```

```
An open-weight model is an AI model whose trained parameters — the numerical weights and biases
that define its behavior — are publicly released, but its training data, code, and usage
restrictions may still be proprietary.
```

### Using `ChatGenerator` in a Pipeline

Here is a retrieval-augmented generation pipeline that answers a question from a small document
store.

```python
from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

document_store = InMemoryDocumentStore()
document_store.write_documents([
    Document(content="FlexAI serves open-weight models behind an OpenAI-compatible API."),
    Document(content="The FlexAI API base URL is https://api.flex.ai/v1."),
    Document(content="Haystack is an open source framework for building LLM applications."),
])

template = [
    ChatMessage.from_user(
        "Given these documents, answer the question.\n"
        "{% for document in documents %}{{ document.content }}\n{% endfor %}\n"
        "Question: {{ query }}\nAnswer:"
    )
]

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipeline.add_component(
    "prompt_builder", ChatPromptBuilder(template=template, required_variables="*")
)
pipeline.add_component("llm", OpenAIChatGenerator(
    api_key=Secret.from_env_var("FLEXAI_API_KEY"),
    api_base_url="https://api.flex.ai/v1",
    model="DeepSeek-V4-Flash-0731",
    generation_kwargs={"max_tokens": 512},
))
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.messages")

query = "What is the FlexAI API base URL?"
result = pipeline.run({"retriever": {"query": query}, "prompt_builder": {"query": query}})
print(result["llm"]["replies"][0].text)
```

```
The FlexAI API base URL is https://api.flex.ai/v1.
```

### Tool calling

Models that support tool calling are marked with the `tools` feature in the `/v1/models` response.

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import Tool
from haystack.utils import Secret


def multiply(a: int, b: int) -> int:
    return a * b


multiply_tool = Tool(
    name="multiply",
    description="Multiply two integers and return the product.",
    parameters={
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    },
    function=multiply,
)

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FLEXAI_API_KEY"),
    api_base_url="https://api.flex.ai/v1",
    model="DeepSeek-V4-Flash-0731",
    tools=[multiply_tool],
)

response = generator.run(messages=[ChatMessage.from_user("What is 1234 * 5678? Use the tool.")])
print(response["replies"][0].tool_calls)
```

```
[ToolCall(tool_name='multiply', arguments={'a': 1234, 'b': 5678}, id='chatcmpl-tool-9bc1d7b333a00c76', extra=None)]
```

### Using Embedders

FlexAI serves embedding models on the same base URL, so `OpenAITextEmbedder` and
`OpenAIDocumentEmbedder` work against it as well.

```python
from haystack import Document
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.utils import Secret

text_embedder = OpenAITextEmbedder(
    api_key=Secret.from_env_var("FLEXAI_API_KEY"),
    api_base_url="https://api.flex.ai/v1",
    model="bge-m3",
)
result = text_embedder.run("Open-weight models on a shared API.")
print(len(result["embedding"]))

document_embedder = OpenAIDocumentEmbedder(
    api_key=Secret.from_env_var("FLEXAI_API_KEY"),
    api_base_url="https://api.flex.ai/v1",
    model="bge-m3",
)
documents = document_embedder.run([Document(content="FlexAI serves open-weight models.")])
print(len(documents["documents"][0].embedding))
```

```
1024
1024
```
