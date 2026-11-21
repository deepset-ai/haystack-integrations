---
layout: integration
name: Powerspring
description: Use open-weight models on EU infrastructure owned by EU companies, through an OpenAI-compatible API
authors:
    - name: Powerspring
      socials:
        github: poolside-ventures
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/powerspring.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Powerspring](https://powerspring.eu/) serves popular open-weight models through one OpenAI-compatible API: gpt-oss-120b and gpt-oss-20b, DeepSeek V4.1 Flash, GLM 5.3 Flash, Qwen3.8-27B, Gemma 4 31B and Gemma 4 26B A4B. Every request runs on EU infrastructure owned by EU companies, and Powerspring does not store prompts or outputs.

All current models support tool calling and JSON schema output. You pay from prepaid credits in euros, with no subscription. [`GET /v1/models`](https://api.powerspring.eu/v1/models) lists the model IDs, context lengths, capabilities and prices; the [models page](https://powerspring.eu/models) shows the same list with independent benchmark scores.

## Usage

The [Powerspring API](https://powerspring.eu/docs) is OpenAI compatible, so it works in Haystack through the OpenAI generators pointed at the Powerspring endpoint.

Create an API key in the [Powerspring console](https://app.powerspring.eu/signup) and set it as an environment variable:

```bash
export POWERSPRING_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("POWERSPRING_API_KEY"),
    api_base_url="https://api.powerspring.eu/v1",
    model="gpt-oss-120b",
)

messages = [ChatMessage.from_user("Summarise this clause in two sentences: ...")]
response = generator.run(messages=messages)
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
    template=[ChatMessage.from_user("Answer using only this context: {{context}}\n\nQuestion: {{question}}")],
    required_variables=["context", "question"],
))
pipe.add_component("llm", OpenAIChatGenerator(
    api_key=Secret.from_env_var("POWERSPRING_API_KEY"),
    api_base_url="https://api.powerspring.eu/v1",
    model="qwen3.8-27b",
))
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {"context": "...", "question": "..."}})
print(result["llm"]["replies"][0].text)
```

### Streaming

Pass a callback to print tokens as they arrive:

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("POWERSPRING_API_KEY"),
    api_base_url="https://api.powerspring.eu/v1",
    model="glm-5.3-flash",
    streaming_callback=print_streaming_chunk,
)

generator.run(messages=[ChatMessage.from_user("Count from 1 to 5.")])
```
