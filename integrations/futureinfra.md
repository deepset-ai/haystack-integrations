---
layout: integration
name: FutureInfra
description: Use 300+ models from multiple providers through FutureInfra's OpenAI-compatible AI router
authors:
    - name: FutureInfra
      socials:
        github: uxidev
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/futureinfra.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

**FutureInfra** is a Korean cloud provider whose AI router serves 300+ models from OpenAI, Anthropic, and other providers behind one OpenAI-compatible API. Usage is billed per call from a prepaid wallet.

To start using FutureInfra, create an API key in the [FutureInfra console](https://futureinfra.ai/console/?screen=ai-router) under AI Router. Model IDs use the `vendor/model` format (for example `openai/gpt-4o-mini`), and the full catalog is available at `https://futureinfra.ai/v1/ai/models`. See the [FutureInfra docs](https://futureinfra.ai/docs/) for more details.

## Usage

The FutureInfra AI router is OpenAI compatible, so you can use it in Haystack through the `OpenAIChatGenerator`.

### Using `ChatGenerator`

Here's an example of chatting with a model through FutureInfra using the `OpenAIChatGenerator`.
You need to set the environment variable `FUTUREINFRA_API_KEY` and choose a model from the catalog.

```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

os.environ["FUTUREINFRA_API_KEY"] = "YOUR_FUTUREINFRA_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FUTUREINFRA_API_KEY"),
    api_base_url="https://futureinfra.ai/v1/ai",
    model="openai/gpt-4o-mini",
)
result = generator.run([ChatMessage.from_user("What are the main components of a RAG pipeline?")])
print(result["replies"][0].text)
```

### Streaming

```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

os.environ["FUTUREINFRA_API_KEY"] = "YOUR_FUTUREINFRA_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FUTUREINFRA_API_KEY"),
    api_base_url="https://futureinfra.ai/v1/ai",
    model="anthropic/claude-sonnet-4",
    streaming_callback=print_streaming_chunk,
)
generator.run([ChatMessage.from_user("Summarize what Haystack is in two sentences.")])
```
