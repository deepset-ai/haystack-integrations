---
layout: integration
name: OpenRouter
description: Use the OpenRouter API for text generation models.
authors:
    - name: deepset 
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/openrouter-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/openrouter
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/openrouter.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`OpenRouterChatGenerator` lets you call any LLMs available on [OpenRouter](https://openrouter.ai), including:

- OpenAI variants such as `openai/gpt-4o`
- Anthropic’s `claude-3.5-sonnet`
- Community-hosted open-source models (Llama 2, Mixtral, etc.)

For more information on models available via the OpenRouter API, see [the OpenRouter docs](https://openrouter.ai/models).

In addition to basic chat completion, the component exposes OpenRouter-specific features:

* **Provider / model routing** – choose fallback models or provider ordering with the `generation_kwargs` parameter.
* **Extra HTTP headers** – add attribution or tracing headers via `extra_headers`.


In order to follow along with this guide, you'll need a OpenRouter API key. Add it as an environment variable, `OPENROUTER_API_KEY`.

## Installation

```bash
pip install openrouter-haystack
```

## Usage
### Standalone

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.openrouter import OpenRouterChatGenerator

os.environ["OPENROUTER_API_KEY"] = "YOUR_OPENROUTER_API_KEY"
client = OpenRouterChatGenerator() # defaults to openai/gpt-4o-mini
response = client.run(
    [ChatMessage.from_user("What are Agentic Pipelines? Be brief.")]
)
print(response["replies"])

```
```bash
{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='The capital of Vietnam is Hanoi.')], _name=None, _meta={'model': 'openai/gpt-4o-mini', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 8, 'prompt_tokens': 13, 'total_tokens': 21, 'completion_tokens_details': CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=0, rejected_prediction_tokens=None), 'prompt_tokens_details': PromptTokensDetails(audio_tokens=None, cached_tokens=0)}})]}
```
`OpenRouterChatGenerator` also support streaming responses if you pass a streaming callback:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.openrouter import OpenRouterChatGenerator

os.environ["OPENROUTER_API_KEY"] = "YOUR_OPENROUTER_API_KEY"

def show(chunk):                              # simple streaming callback
    print(chunk.content, end="", flush=True)

client = OpenRouterChatGenerator(
    model="openrouter/auto",                  # let OpenRouter pick a model
    streaming_callback=show,
    generation_kwargs={
        "provider": {"sort": "throughput"},   # pick the fastest provider
    }
)

response = client.run([ChatMessage.from_user("Summarize RAG in two lines.")])

print (response)

```

### License

`openrouter-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
