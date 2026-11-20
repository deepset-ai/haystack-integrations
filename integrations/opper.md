---
layout: integration
name: Opper
description: Use 700+ models from 50+ providers in Haystack through Opper's EU-hosted, OpenAI-compatible gateway
authors:
    - name: Opper
      socials:
        github: opper-ai
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/opper.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Opper](https://opper.ai/llm-gateway) is an AI gateway hosted in the EU (AWS Stockholm). One OpenAI-compatible API and one key reach 700+ models from 50+ providers, at the providers' token rates with no markup. Requests can be pinned to EU-hosted regions, and audit logs and traces stay in EU storage.

Model ids are pool names such as `claude-sonnet-4-6` or `gpt-5.4-mini`, where Opper picks the route per request. A `provider/model` id such as `anthropic/claude-sonnet-4-6` pins one route. The full list is in the [model catalogue](https://opper.ai/models).

## Usage

The [Opper API](https://docs.opper.ai/build/gateway/drop-in-sdks) is OpenAI compatible, so it works in Haystack through the OpenAI components by pointing them at `https://api.opper.ai/v3/compat`.

Create a key at [platform.opper.ai](https://platform.opper.ai) and set it as an environment variable:

```bash
export OPPER_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("OPPER_API_KEY"),
    api_base_url="https://api.opper.ai/v3/compat",
    model="claude-sonnet-4-6",
)

messages = [ChatMessage.from_user("Summarise the following contract clause: ...")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
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
        api_key=Secret.from_env_var("OPPER_API_KEY"),
        api_base_url="https://api.opper.ai/v3/compat",
        model="gpt-5.4-mini",
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Stockholm?")])
print(result["last_message"].text)
```

### Embeddings

```python
from haystack.components.embedders import OpenAITextEmbedder
from haystack.utils import Secret

embedder = OpenAITextEmbedder(
    api_key=Secret.from_env_var("OPPER_API_KEY"),
    api_base_url="https://api.opper.ai/v3/compat",
    model="text-embedding-3-small",
)

result = embedder.run(text="Opper routes requests to many model providers")
print(len(result["embedding"]))
```
