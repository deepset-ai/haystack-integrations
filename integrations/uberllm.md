---
layout: integration
name: UberLLM
description: Use text models from many providers through UberLLM's OpenAI-compatible API in Haystack
authors:
    - name: UberLLM team
      socials:
        github: PSA-Team-source
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/uberllm.png
version: Haystack 3.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[UberLLM](https://uberllm.dev) is a pay-as-you-go API that gives one key for text models such as GPT, Claude, Gemini, DeepSeek, Qwen, Llama, Mistral and Kimi, served by third-party providers. Its API is OpenAI compatible, so it works in Haystack through `OpenAIChatGenerator` with the base URL `https://api.uberllm.dev/v1`.

Model IDs use the `provider/model` form, for example `deepseek/deepseek-v4-flash` or `openai/gpt-5-mini`. The live list is returned by `GET https://api.uberllm.dev/v1/models`.

## Usage

Create an API key at [uberllm.dev](https://uberllm.dev) and set it as an environment variable:

```bash
export UBERLLM_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("UBERLLM_API_KEY"),
    api_base_url="https://api.uberllm.dev/v1",
    model="deepseek/deepseek-v4-flash",
)

response = generator.run(messages=[ChatMessage.from_user("What is the capital of France?")])
print(response["replies"][0].text)
```

### Streaming

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("UBERLLM_API_KEY"),
    api_base_url="https://api.uberllm.dev/v1",
    model="deepseek/deepseek-v4-flash",
    streaming_callback=print_streaming_chunk,
)

generator.run(messages=[ChatMessage.from_user("Count from 1 to 5.")])
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
    api_key=Secret.from_env_var("UBERLLM_API_KEY"),
    api_base_url="https://api.uberllm.dev/v1",
    model="deepseek/deepseek-v4-flash",
))
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {
    "context": "The Eiffel Tower is 330 metres tall.",
    "question": "How tall is the Eiffel Tower?",
}})
print(result["llm"]["replies"][0].text)
```

Tool calling works the same way as with OpenAI: pass `tools=[...]` to `OpenAIChatGenerator` and use a model that supports tools.
