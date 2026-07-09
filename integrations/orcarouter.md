---
layout: integration
name: OrcaRouter
description: Use OrcaRouter's OpenAI-compatible API gateway for chat generation in Haystack.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Jinhao Song
      socials:
        github: jinhaosong-source
pypi: https://pypi.org/project/orcarouter-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/orcarouter
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/orcarouter.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[`OrcaRouterChatGenerator`](https://docs.haystack.deepset.ai/reference/integrations-orcarouter) lets you call chat models through [OrcaRouter](https://www.orcarouter.ai), an OpenAI-compatible API gateway.

OrcaRouter routes requests to provider-prefixed models from upstream providers such as OpenAI, Anthropic, Google Gemini, DeepSeek, xAI Grok, Alibaba Qwen, Moonshot Kimi, and MiniMax. Use the live [OrcaRouter model catalog](https://www.orcarouter.ai/models) or the `/v1/models` endpoint to see which models your account can access.

This integration provides:

- **OpenAI-compatible chat generation** through the OrcaRouter API at `https://api.orcarouter.ai/v1`.
- **Provider-prefixed model IDs** such as `openai/gpt-4o-mini`, `google/gemini-2.5-flash`, and `deepseek/deepseek-chat`.
- **Automatic routing** with `orcarouter/auto`, which lets OrcaRouter choose a live model for the request.
- **Fallback chains and routing preferences** by forwarding OrcaRouter-specific options through `generation_kwargs`.
- **Streaming, tool calling, and structured outputs** inherited from Haystack's `OpenAIChatGenerator`.

To follow along with the examples below, create an OrcaRouter API key and set it as the `ORCAROUTER_API_KEY` environment variable.

## Installation

```bash
pip install orcarouter-haystack
```

## Usage

You can use `OrcaRouterChatGenerator` on its own, in a [pipeline](https://docs.haystack.deepset.ai/docs/pipelines), or with the [Agent component](https://docs.haystack.deepset.ai/docs/agent).

### Basic Chat Generation

```python
import os

from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.orcarouter import OrcaRouterChatGenerator

os.environ["ORCAROUTER_API_KEY"] = "YOUR_ORCAROUTER_API_KEY"

generator = OrcaRouterChatGenerator(model="openai/gpt-4o-mini")

result = generator.run(
    messages=[
        ChatMessage.from_system("You are a concise assistant."),
        ChatMessage.from_user("Briefly explain what OrcaRouter offers."),
    ]
)

print(result["replies"][0].text)
```

### Automatic Routing and Fallbacks

Use `orcarouter/auto` when you want OrcaRouter to choose a live model for the request:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.orcarouter import OrcaRouterChatGenerator

generator = OrcaRouterChatGenerator(model="orcarouter/auto")

result = generator.run(
    messages=[ChatMessage.from_user("Summarize retrieval augmented generation in two sentences.")]
)
```

You can also pass OrcaRouter routing options through `generation_kwargs`. For example, this creates an explicit fallback chain:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.orcarouter import OrcaRouterChatGenerator

generator = OrcaRouterChatGenerator(
    model="openai/gpt-4o-mini",
    generation_kwargs={
        "extra_body": {
            "route": "fallback",
            "models": [
                "openai/gpt-4o-mini",
                "anthropic/claude-haiku-4.5",
                "google/gemini-2.5-flash",
            ],
        }
    },
)

result = generator.run(messages=[ChatMessage.from_user("What is Haystack?")])
```

### Streaming

Pass a streaming callback to receive chunks as the response is generated:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.orcarouter import OrcaRouterChatGenerator


def show(chunk):
    print(chunk.content, end="", flush=True)


generator = OrcaRouterChatGenerator(
    model="openai/gpt-4o-mini",
    streaming_callback=show,
)

generator.run(messages=[ChatMessage.from_user("Explain model routing in one paragraph.")])
```

### Tool Calling with an Agent

Because `OrcaRouterChatGenerator` supports Haystack tools, you can use it as the chat generator for an Agent:

```python
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack.tools import Tool
from haystack_integrations.components.generators.orcarouter import OrcaRouterChatGenerator


def weather(city: str) -> str:
    return f"The weather in {city} is sunny."


weather_tool = Tool(
    name="weather",
    description="Useful for getting the weather in a specific city",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
    function=weather,
)

agent = Agent(
    chat_generator=OrcaRouterChatGenerator(model="openai/gpt-4o-mini"),
    tools=[weather_tool],
    system_prompt="You help users by calling the provided tools when they are relevant.",
)

result = agent.run(messages=[ChatMessage.from_user("What's the weather in Tokyo?")])

print(result["last_message"].text)
```

## License

`orcarouter-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
