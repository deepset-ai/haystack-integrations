---
layout: integration
name: HopBase
description: Call GPT, Gemini, DeepSeek, GLM, Qwen and other models from Haystack through one OpenAI-compatible base URL
authors:
    - name: HopBase
      socials:
        github: HopBase-AI
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/hopbase.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)
  - [Using `OpenAIChatGenerator`](#using-openaichatgenerator)
  - [Using `OpenAIResponsesChatGenerator`](#using-openairesponseschatgenerator)
  - [Streaming](#streaming)
  - [Use with a Haystack Agent](#use-with-a-haystack-agent)

## Overview

[HopBase](https://hop-base.com/) is an API gateway that serves models from several
vendors behind one OpenAI-compatible base URL: OpenAI GPT, Google Gemini, DeepSeek,
Zhipu GLM, Alibaba Qwen, Moonshot Kimi, xAI Grok and others. In Haystack you use the
built-in OpenAI generators and point them at the HopBase endpoint, so switching
vendors in a pipeline is a change of the `model` string.

Two things are worth knowing when you wire it into Haystack:

- The same base URL exposes both **Chat Completions** and the **Responses API**, so
  `OpenAIChatGenerator` and `OpenAIResponsesChatGenerator` both work without extra
  configuration.
- An API key can call the models of the groups it includes. `GET /v1/models` returns
  exactly the model IDs your key can use, so read the IDs from there instead of
  hard-coding them.

Model IDs, context sizes and parameters are documented in the
[HopBase docs](https://hop-base.com/en/docs), and the list of models is on the
[models page](https://hop-base.com/models).

## Usage

Install Haystack:

```bash
pip install haystack-ai
```

Create an API key in the [HopBase console](https://api.hop-base.com/login) and set it
as an environment variable:

```bash
export HOPBASE_API_KEY="your-api-key"
```

To see which model IDs your key can call:

```bash
curl https://api.hop-base.com/v1/models -H "Authorization: Bearer $HOPBASE_API_KEY"
```

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("HOPBASE_API_KEY"),
    api_base_url="https://api.hop-base.com/v1",
    model="glm-5.3",
)

messages = [ChatMessage.from_user("Explain retrieval-augmented generation in two sentences.")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
```

To use a model from another vendor, change `model` (for example `gpt-6.1-sol`) and
keep everything else.

### Using `OpenAIResponsesChatGenerator`

Models served over the Responses API can be used with `OpenAIResponsesChatGenerator`
on the same base URL:

```python
from haystack.components.generators.chat import OpenAIResponsesChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIResponsesChatGenerator(
    api_key=Secret.from_env_var("HOPBASE_API_KEY"),
    api_base_url="https://api.hop-base.com/v1",
    model="gpt-6.1-sol",
)

response = generator.run(messages=[ChatMessage.from_user("Summarise what a document store does.")])
print(response["replies"][0].text)
```

### Streaming

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("HOPBASE_API_KEY"),
    api_base_url="https://api.hop-base.com/v1",
    model="gpt-6.1-sol",
    streaming_callback=print_streaming_chunk,
)

generator.run(messages=[ChatMessage.from_user("Count from 1 to 5.")])
```

### Use with a Haystack Agent

Tool calling goes through the standard `tools` interface, so the same agent code runs
on models from different vendors:

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
        api_key=Secret.from_env_var("HOPBASE_API_KEY"),
        api_base_url="https://api.hop-base.com/v1",
        model="glm-5.3",
    ),
    tools=[weather],
)

result = agent.run(messages=[ChatMessage.from_user("What's the weather in Munich?")])
print(result["last_message"].text)
```
