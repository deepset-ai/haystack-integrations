---
layout: integration
name: Wiro AI
description: Use LLMs from several providers through one OpenAI-compatible Wiro AI API
authors:
    - name: Wiro AI
      socials:
        github: wiroai
        twitter: wiroai
        linkedin: https://www.linkedin.com/company/wiroai/
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/wiro-ai.png
version: Haystack 3.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Wiro AI](https://wiro.ai) serves large language models from several providers,
including Anthropic Claude, OpenAI GPT, DeepSeek and Qwen, through one
OpenAI-compatible API at `https://llm.wiro.ai/v1`. A single project credential
works for every model, and usage is billed per token to a prepaid Wiro wallet.

The [model list](https://llm.wiro.ai/v1/models) needs no key. Each entry shows
the model's context length, token prices and supported parameters, such as tool
calling.

## Usage

The [Wiro AI LLM gateway](https://wiro.ai/docs/completions-api) is OpenAI
compatible, so it works in Haystack through `OpenAIChatGenerator` pointed at the
Wiro endpoint.

Create a project at [wiro.ai/panel/project/new](https://wiro.ai/panel/project/new)
and set its credential as an environment variable:

```bash
export WIRO_API_KEY="your-api-key"
```

For a project that uses signature authentication, set the key and the secret
joined by a colon: `your-api-key:your-api-secret`.

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("WIRO_API_KEY"),
    api_base_url="https://llm.wiro.ai/v1",
    model="claude/sonnet-5",
)

messages = [ChatMessage.from_user("Explain retrieval-augmented generation in two sentences.")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
```

To use another model, set `model` to any ID from the model list, for example
`deepseek/v4-1-flash`.

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def get_current_time(city: str) -> str:
    """Return the current time in a city."""
    return f"It is 10:30 AM in {city}."


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_env_var("WIRO_API_KEY"),
        api_base_url="https://llm.wiro.ai/v1",
        model="claude/sonnet-5",
    ),
    tools=[get_current_time],
)
result = agent.run(messages=[ChatMessage.from_user("What time is it in Tokyo?")])
print(result["last_message"].text)
```
