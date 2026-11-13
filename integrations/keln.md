---
layout: integration
name: Keln
description: Use open models from Keln in Haystack through its OpenAI-compatible API
authors:
    - name: Keln
      socials:
        github: kris-holy
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/keln.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)
  - [Chat](#chat)
  - [Streaming](#streaming)
  - [Tool calling with an Agent](#tool-calling-with-an-agent)

## Overview

[Keln](https://keln.ai/) is an inference platform for open models. Keln serves models such as GLM 5.3 and Kimi K3 through one OpenAI-compatible API at `https://api.keln.ai/v1`. The API supports streaming, tool calling, structured outputs and reasoning controls.

Keln keeps request metadata such as token counts, cost and latency. Keln does not store prompts or completions and does not train on them. See [Privacy](https://docs.keln.ai/capabilities/privacy/) for details.

The model list is public at [https://api.keln.ai/v1/models](https://api.keln.ai/v1/models) and on the [models page](https://keln.ai/models), with prices. For the full API reference, see the [Keln docs](https://docs.keln.ai/).

## Usage

The Keln API is OpenAI compatible, so it works in Haystack through `OpenAIChatGenerator`. Set `api_base_url` to the Keln endpoint and pass your Keln API key.

Install Haystack:

```bash
pip install haystack-ai
```

To get a key, sign up at [app.keln.ai/signup](https://app.keln.ai/signup), then go to **Keys** → **Create key**. Set the key as an environment variable:

```bash
export KELN_API_KEY="your-api-key"
```

### Chat

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("KELN_API_KEY"),
    api_base_url="https://api.keln.ai/v1",
    model="zai-org/glm-5.3",
    generation_kwargs={"max_tokens": 2048, "reasoning_effort": "low"},
)

messages = [
    ChatMessage.from_system("Answer in 2 sentences."),
    ChatMessage.from_user("What is retrieval-augmented generation?"),
]
response = generator.run(messages=messages)
print(response["replies"][0].text)
```

`generation_kwargs` goes to the API as request fields. `max_tokens` caps the output, reasoning and answer together. `reasoning_effort` sets how much the model thinks, for example `"low"`, `"high"` or `"max"`. Each model lists the levels it accepts in [`/v1/models`](https://api.keln.ai/v1/models). Without it, each model uses its default level. See [Reasoning](https://docs.keln.ai/capabilities/reasoning/).

To use another model, change `model`, for example to `moonshotai/kimi-k3`.

### Streaming

Pass a `streaming_callback` to receive tokens as the model writes them:

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("KELN_API_KEY"),
    api_base_url="https://api.keln.ai/v1",
    model="zai-org/glm-5.3",
    streaming_callback=print_streaming_chunk,
)

generator.run(messages=[ChatMessage.from_user("Write a short poem about open models.")])
```

### Tool calling with an Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its ID."""
    return f"Order {order_id} shipped on 3 November and arrives on 7 November."


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_env_var("KELN_API_KEY"),
        api_base_url="https://api.keln.ai/v1",
        model="zai-org/glm-5.3",
    ),
    tools=[get_order_status],
    system_prompt="You are a support assistant. Use the tools to answer.",
)

result = agent.run(messages=[ChatMessage.from_user("Where is my order A-1042?")])
print(result["last_message"].text)
```

The Agent sends the tool definitions to Keln, runs the tool the model calls, and returns the model's final answer.
