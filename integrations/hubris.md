---
layout: integration
name: Hubris
description: Use 500+ models from OpenAI, Anthropic, Google, DeepSeek, Qwen and others through Hubris, an OpenAI-compatible LLM gateway billed in Russian rubles
authors:
    - name: Hubris
      socials:
        github: Aimagine-life
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/hubris.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Hubris](https://hubris.pw) is an OpenAI-compatible LLM gateway: one API key and one balance (billed in Russian rubles) for models from OpenAI, Anthropic, Google, DeepSeek, Qwen, Z.ai, Moonshot, xAI, MiniMax and others. The full catalog with prices is at [hubris.pw/models](https://hubris.pw/models); model ids always use the `vendor/model` form (for example `anthropic/claude-sonnet-5`).

## Usage

The Hubris API is OpenAI compatible, so it works with Haystack's OpenAI components out of the box. Create an API key at [hubris.pw/keys](https://hubris.pw/keys) and set it as the `HUBRIS_API_KEY` environment variable.

### Using `ChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("HUBRIS_API_KEY"),
    api_base_url="https://api.hubris.pw/v1",
    model="anthropic/claude-sonnet-5",
)

messages = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user("What is the capital of France?"),
]
response = generator.run(messages=messages)
print(response["replies"][0].text)
```

### In a pipeline

Here's a question-answering pipeline over a web page. Any model from the [catalog](https://hubris.pw/models) can be used; `google/gemini-3.7-flash` is a good fit for long pages.

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

template = [
    ChatMessage.from_user(
        """According to the contents of this website:
{% for document in documents %}
  {{document.content}}
{% endfor %}
Answer the given question: {{query}}
Answer:"""
    )
]

pipeline = Pipeline()
pipeline.add_component("fetcher", LinkContentFetcher())
pipeline.add_component("converter", HTMLToDocument())
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["documents", "query"]))
pipeline.add_component(
    "llm",
    OpenAIChatGenerator(
        api_key=Secret.from_env_var("HUBRIS_API_KEY"),
        api_base_url="https://api.hubris.pw/v1",
        model="google/gemini-3.7-flash",
    ),
)

pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.messages")

result = pipeline.run(
    {
        "fetcher": {"urls": ["https://hubris.pw/docs"]},
        "prompt": {"query": "How do I authenticate requests to Hubris?"},
    }
)
print(result["llm"]["replies"][0].text)
```

### Embeddings

Embedding models from the catalog work through the OpenAI embedders the same way:

```python
from haystack.components.embedders import OpenAITextEmbedder
from haystack.utils import Secret

embedder = OpenAITextEmbedder(
    api_key=Secret.from_env_var("HUBRIS_API_KEY"),
    api_base_url="https://api.hubris.pw/v1",
    model="openai/text-embedding-3-small",
)
print(embedder.run(text="Haystack pipelines with Hubris")["embedding"][:5])
```

Streaming (`streaming_callback`), tool calling (`tools`) and structured output (`response_format`) work exactly as with the stock OpenAI components; the `supported_parameters` field of `GET https://api.hubris.pw/v1/models` lists what each model accepts.
