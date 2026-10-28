---
layout: integration
name: Obscurify.ai
description: Use 200+ open and frontier models through Obscurify.ai's private, OpenAI-compatible API
authors:
    - name: Tony Davis
      socials:
        github: tonydavis629
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/obscurify.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Obscurify.ai](https://obscurify.ai/?utm_source=haystack) is a privacy-focused
AI provider with an OpenAI-compatible API. Accounts are a random 16-digit
account number with no email, prompts and responses are not stored on the
server, and requests only use zero-data-retention routes. It can be paid with
Monero, Bitcoin, Lightning or a card.

The API serves 200+ models, including open models such as
`deepseek/deepseek-v4-flash`, `z-ai/glm-5.3`, `moonshotai/kimi-k2-0905` and
`qwen/qwen3-coder`, and frontier models such as `openai/gpt-5.5` and
`anthropic/claude-sonnet-5.5` on the Casual and Pro plans. Streaming and tool
calling are supported. The model list with context lengths and prices is public
at `https://obscurify.ai/v1/models` (no key needed) and on the
[model cards page](https://obscurify.ai/model_cards).

## Usage

The [Obscurify.ai API](https://obscurify.ai/api-docs) is OpenAI compatible, so
it works in Haystack through `OpenAIChatGenerator` by pointing it at the
Obscurify.ai endpoint. Get your key from the
[account page](https://obscurify.ai/account) ("Show API Key") and set it as an
environment variable:

```bash
pip install haystack-ai
export OBSCURIFY_API_KEY="sk-obs1_..."
```

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("OBSCURIFY_API_KEY"),
    api_base_url="https://obscurify.ai/v1",
    model="deepseek/deepseek-v4-flash",
)

response = generator.run(messages=[ChatMessage.from_user("In one sentence, what is Haystack?")])
print(response["replies"][0].text)
```

### Streaming

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("OBSCURIFY_API_KEY"),
    api_base_url="https://obscurify.ai/v1",
    model="deepseek/deepseek-v4-flash",
    streaming_callback=print_streaming_chunk,
)

generator.run(messages=[ChatMessage.from_user("Count from 1 to 5, comma separated.")])
```

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def weather(city: str) -> str:
    """Return the weather for a city."""
    return f"The weather in {city} is sunny and 22 degrees"


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_env_var("OBSCURIFY_API_KEY"),
        api_base_url="https://obscurify.ai/v1",
        model="deepseek/deepseek-v4-flash",
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Lisbon?")])
print(result["last_message"].text)
```
