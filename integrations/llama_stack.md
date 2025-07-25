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
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/llama.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Llama Stack](https://llama-stack.readthedocs.io/en/latest/index.html) is an open-source framework consisting of AI building blocks and unified APIs that standardizes building AI Apps across different environments.

The `LlamaStackChatGenerator` allows you to leverage any LLMs made available by inference providers hosted on a Llama Stack server. It abstracts away the specifics of the underlying provider, enabling you to use the same client-side code across different inference backends. For a list of supported providers and configuration details, refer to the [Llama Stack documentation](https://llama-stack.readthedocs.io/en/latest/providers/inference/index.html).

To use this chat generator, you’ll need:
- A running instance of a Llama Stack server (either local or remote)
- A valid model name supported by your chosen inference provider

Below are example configurations for using the Llama-3.2-3B model:

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
from haystack.components.generators.utils import print_streaming_chunk


client = LlamaStackChatGenerator(
    model="meta-llama/Llama-3.2-3B",
    streaming_callback=print_streaming_chunk,
)

response = client.run([ChatMessage.from_user("Summarize RAG in two lines.")])

print (response)

```

### License

`llama-stack-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
