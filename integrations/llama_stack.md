---
layout: integration
name: Llama Stack
description: Use the Llama Stack generation models.
authors:
    - name: deepset 
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/llama-stack-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/llama_stack
type: Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/meta.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`LlamaStackChatGenerator` lets you use any available LLMs provided by inference providers running on a Llama Stack server. For more information on the providers supported by Llama Stack, see the [Llama Stack docs](https://llama-stack.readthedocs.io/en/latest/providers/inference/index.html). You can use the same client-side code with different inference providers on the Llama Stack server.

To follow this guide, you need a running Llama Stack server (remote or local) and a `model` name for `LlamaStackChatGenerator`, which varies by provider. Below are examples for the Llama-3.2-3B model:

Ollama as the inference provider:

```chat_generator = LlamaStackChatGenerator(model="llama3.2:3b")```

vLLM as the inference provider:
```chat_generator = LlamaStackChatGenerator(model="meta-llama/Llama-3.2-3B")```

## Installation

```bash
pip install llama-stack-haystack
```

## Usage
### Standalone with vLLM inference

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.llama-stack import LlamaStackChatGenerator

client = LlamaStackChatGenerator(model="meta-llama/Llama-3.2-3B")
response = client.run(
    [ChatMessage.from_user("What are Agentic Pipelines? Be brief.")]
)
print(response["replies"])

```
```bash
{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='The capital of Vietnam is Hanoi.')], _name=None, _meta={'model': 'openai/gpt-4o-mini', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 8, 'prompt_tokens': 13, 'total_tokens': 21, 'completion_tokens_details': CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=0, rejected_prediction_tokens=None), 'prompt_tokens_details': PromptTokensDetails(audio_tokens=None, cached_tokens=0)}})]}
```
`LlamaStackChatGenerator` also support streaming responses if you pass a streaming callback:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.llama-stack import LlamaStackChatGenerator


def show(chunk):                              # simple streaming callback
    print(chunk.content, end="", flush=True)

client = LlamaStackChatGenerator(
    model="meta-llama/Llama-3.2-3B",
    streaming_callback=show,
)

response = client.run([ChatMessage.from_user("Summarize RAG in two lines.")])

print (response)

```

### License

`llama-stack-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
