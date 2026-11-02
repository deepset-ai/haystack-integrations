---
# SPDX-License-Identifier: CC0-1.0
layout: integration
name: Wally
description: Use open-weight models served by Wally in Haystack
authors:
    - name: RunAnywhere
      socials:
        github: RunanywhereAI
        twitter: RunAnywhereAI
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/wally.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Wally](https://www.runwally.com) is RunAnywhere's hosted inference API for
open-weight models, including DeepSeek V4.1 Flash, GLM-5.3 Flash, Kimi K3 and
MiniMax M3. The API is OpenAI compatible and supports streaming, tool calling,
JSON mode, structured outputs and automatic prompt caching. DeepSeek V4.1 Flash
and Kimi K3 also accept image input.

For the current models and prices, see the [pricing page](https://www.runwally.com/pricing).

## Usage

The [Wally API](https://docs.runanywhere.ai/wally-cloud/api) is OpenAI compatible, so it works in Haystack through the OpenAI generators by pointing them at the Wally endpoint.

Create an API key in the [RunAnywhere console](https://console.runanywhere.ai) and set it as an environment variable:

```bash
export WALLY_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("WALLY_API_KEY"),
    api_base_url="https://inference.runanywhere.ai/v1",
    model="deepseek-v4.1-flash",
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
        api_key=Secret.from_env_var("WALLY_API_KEY"),
        api_base_url="https://inference.runanywhere.ai/v1",
        model="deepseek-v4.1-flash",
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Munich?")])
print(result["last_message"].text)
```
