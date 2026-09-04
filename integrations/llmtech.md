---
layout: integration
name: LLM Tech
description: Use open-weight models served from EU hardware with zero data retention
authors:
    - name: Artem Burei
      socials:
        github: Pessimist228
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[LLM Tech](https://llmtech.eu/) serves open-weight models from dedicated GPUs
inside the European Union. Inference runs on an RTX PRO 6000 Blackwell in
Helsinki with the edge in Nuremberg, with no US cloud at any hop. Prompts and
completions are never written to disk, and an Art. 28 GDPR data processing
agreement naming both sub-processors is available on request.

The currently served model is Qwen3.8-27B in NVFP4 with a 262,144-token
context, image input, tool calling and prompt caching. Measured latency and
throughput are published at [llmtech.eu/status](https://llmtech.eu/status).

## Usage

The [LLM Tech API](https://llmtech.eu/docs/) is OpenAI compatible, so it works
in Haystack through the OpenAI generators by pointing them at the LLM Tech
endpoint.

Set your API key as an environment variable:

```bash
export LLMTECH_API_KEY="your-api-key"
```

### Using `OpenAIGenerator`

```python
import os
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

generator = OpenAIGenerator(
    api_key=Secret.from_env_var("LLMTECH_API_KEY"),
    api_base_url="https://api.llmtech.eu/v1",
    model="unsloth/Qwen3.8-27B-NVFP4",
)

response = generator.run("What is the capital of Finland?")
print(response["replies"][0])
```

### Using `OpenAIChatGenerator`

```python
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("LLMTECH_API_KEY"),
    api_base_url="https://api.llmtech.eu/v1",
    model="unsloth/Qwen3.8-27B-NVFP4",
)

messages = [ChatMessage.from_user("Summarise the following contract clause: ...")]
response = generator.run(messages)
print(response["replies"][0].text)
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder(
    template=[ChatMessage.from_user("Answer using only this context: {{context}}\n\nQuestion: {{question}}")]
))
pipe.add_component("llm", OpenAIChatGenerator(
    api_key=Secret.from_env_var("LLMTECH_API_KEY"),
    api_base_url="https://api.llmtech.eu/v1",
    model="unsloth/Qwen3.8-27B-NVFP4",
))
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {"context": "...", "question": "..."}})
print(result["llm"]["replies"][0].text)
```

### Prompt caching

Repeated prefixes are cached automatically. Agents that resend the same system
prompt and tool definitions on every step pay the cached rate for that portion,
which in production is where most of an agentic workload lands. Keep the system
prompt and tool definitions stable and in a fixed order, and put anything that
varies after them.
