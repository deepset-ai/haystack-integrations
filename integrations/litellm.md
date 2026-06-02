---
layout: integration
name: LiteLLM
description: Use any of 100+ LLM providers with Haystack through LiteLLM
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/litellm-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/litellm
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/litellm.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[LiteLLM](https://docs.litellm.ai/) provides a single, unified interface to over 100 LLM providers, including OpenAI, Anthropic, Google, AWS Bedrock, Azure, Cohere, Mistral, and Groq. This integration brings that unified interface to Haystack through the `LiteLLMChatGenerator`, so you can switch between providers by changing only the model string, without rewriting your pipeline.

Model names use the LiteLLM `provider/model-name` format, for example `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`, or `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0`. For the full list of supported providers and their model identifiers, see the [LiteLLM providers documentation](https://docs.litellm.ai/docs/providers).

The `LiteLLMChatGenerator` supports streaming, tool/function calling, and asynchronous execution.

## Installation

```bash
pip install litellm-haystack
```

## Usage

`LiteLLMChatGenerator` needs an API key for the selected provider. LiteLLM reads it from the provider's standard environment variable (for example, `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`), so make sure the relevant variable is set before running. You can also pass the key explicitly through the `api_key` init parameter using Haystack's `Secret` API.

### Using `LiteLLMChatGenerator`

Here is a simple example that calls a model directly. Switch providers by changing only the `model` string.

```python
# Set the relevant provider key, e.g. OPENAI_API_KEY or ANTHROPIC_API_KEY, in your environment.

from haystack_integrations.components.generators.litellm import LiteLLMChatGenerator
from haystack.dataclasses import ChatMessage

generator = LiteLLMChatGenerator(
    model="anthropic/claude-sonnet-4-20250514",
    generation_kwargs={"max_tokens": 1024, "temperature": 0.7},
)

messages = [
    ChatMessage.from_system("You are a helpful assistant"),
    ChatMessage.from_user("What's Natural Language Processing? Be brief."),
]
result = generator.run(messages=messages)
print(result["replies"][0].text)
```

### In a pipeline

Below is an example RAG pipeline that answers a question using the contents of a URL. We fetch the URL, convert it to a document, build the prompt, and generate the answer with the `LiteLLMChatGenerator`.

```python
# Set the relevant provider key, e.g. OPENAI_API_KEY, in your environment.
# !pip install trafilatura

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.fetchers import LinkContentFetcher
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.generators.litellm import LiteLLMChatGenerator

messages = [
    ChatMessage.from_system("You answer questions based on the given documents."),
    ChatMessage.from_user(
        "Here are the documents:\n"
        "{% for d in documents %} \n"
        "    {{d.content}} \n"
        "{% endfor %}"
        "\nAnswer: {{query}}"
    ),
]

rag_pipeline = Pipeline()
rag_pipeline.add_component("fetcher", LinkContentFetcher())
rag_pipeline.add_component("converter", HTMLToDocument())
rag_pipeline.add_component("prompt_builder", ChatPromptBuilder(variables=["documents"]))
rag_pipeline.add_component("llm", LiteLLMChatGenerator(model="openai/gpt-4o"))

rag_pipeline.connect("fetcher", "converter")
rag_pipeline.connect("converter", "prompt_builder")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "What is Haystack?"
result = rag_pipeline.run(
    data={
        "fetcher": {"urls": ["https://haystack.deepset.ai/overview/intro"]},
        "prompt_builder": {"template_variables": {"query": question}, "template": messages},
    }
)
print(result["llm"]["replies"][0].text)
```

### Streaming

Pass a callback to `streaming_callback` to stream the response as it is generated. Use the built-in `print_streaming_chunk` to print text tokens and tool events.

```python
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.litellm import LiteLLMChatGenerator

generator = LiteLLMChatGenerator(model="openai/gpt-4o", streaming_callback=print_streaming_chunk)
generator.run([ChatMessage.from_user("Tell me about Natural Language Processing in two sentences.")])
```
