---
layout: integration
name: Mistral
description: This page demonstrates how to use OpenAIGenerator within Haystack to make use of Mistral models.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/mistral.png
version: Haystack 2.0
toc: true
---

This page demonstrates how to use the [OpenAIChatGenerator](https://docs.haystack.deepset.ai/v2.0/docs/openaichatgenerator) and [OpenAITextEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/openaitextembedder) within Haystack to make use of Mistral models.

[Mistral AI](https://mistral.ai/) currently provides two types of access to Large Language Models:

- An API providing pay-as-you-go access to the latest models,
- Open source models available under the Apache 2.0 License, available on [Hugging Face](https://huggingface.co/mistralai) or directly from [the documentation](https://docs.mistral.ai/models/).

For more information see [the Mistal docs](https://docs.mistral.ai/).

In order to follow along with this guide, you'll need a [Mistal API key](https://console.mistral.ai/). Add it as an environment variable, `MISTRAL_API_KEY`.

### Installation

```bash
pip install haystack-ai
```

### Usage

To use a Mistral LLM:
```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-medium"

client = OpenAIChatGenerator(
    api_key=api_key, model=model, api_base_url="https://api.mistral.ai/v1"
)

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```
```bash
{'replies': [ChatMessage(content='The "best" French cheese is subjective and depends on personal taste...', role=<ChatRole.ASSISTANT: 'assistant'>, name=None, meta={'model': 'mistral-medium', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 231, 'prompt_tokens': 16, 'total_tokens': 247}})]}
```
Mistral LLMs also support streaming responses if you pass a callback in to the `OpenAIChatGenerator` like so:
```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-medium"

client = OpenAIChatGenerator(
    api_key=api_key,
    model=model,
    api_base_url="https://api.mistral.ai/v1",
    streaming_callback=lambda chunk: print(chunk.content, end="", flush=True)
)

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```

To use a Mistal embedding model:
```python
import os
from haystack.components.embedders import OpenAITextEmbedder

api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-embed"


embedder = OpenAITextEmbedder(api_key=api_key, model=model, api_base_url="https://api.mistral.ai/v1")

response = embedder.run(text="What is the best French cheese?")
print(response)
# {'embedding': [-0.0186004638671875, ...],
# 'meta': {'model': 'mistral-embed', 
#'usage': {'prompt_tokens': 9, 'total_tokens': 9, 'completion_tokens': 0}}}
```
