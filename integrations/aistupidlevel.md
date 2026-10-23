---
layout: integration
name: AI Stupid Level
description: Let benchmark scores pick the model for each Haystack call, using your own provider keys
authors:
    - name: AI Stupid Level
      socials:
        github: StudioPlatforms
        twitter: AIStupidlevel
        linkedin: https://www.linkedin.com/company/asl-aistupidlevel-info
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/aistupidlevel.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

Stop choosing AI models manually. Let live benchmarks choose the best model for coding, reasoning, or agent tasks—using your own provider keys, with zero token markup.

[AI Stupid Level](https://aistupidlevel.info) benchmarks models from OpenAI, Anthropic, Google, DeepSeek, Moonshot (Kimi) and Z.ai (GLM) on coding, reasoning and tool use. Its Smart Router is an OpenAI-compatible endpoint, `https://aistupidlevel.info/v1`, that uses the measured scores to choose the model for each request.

- **Your own provider keys.** You add your provider keys to your AI Stupid Level account. The router calls the chosen model with your key, so the provider bills you directly and AI Stupid Level adds zero token markup.
- **Routing from benchmark scores.** Instead of a model name, you pass a routing mode such as `auto-coding` or `auto-tooling`. You can still pin a specific model when you want one.
- **You can see which model answered.** Every response carries an `X-AISM-Model` header with the model that answered and an `X-AISM-Reasoning` header that explains the choice.

The router supports chat completions, streaming, tool calling and JSON output. It is text only, with no image, audio or file input.

Create a router key (it starts with `aism_`) at [aistupidlevel.info/router/keys](https://aistupidlevel.info/router/keys). The [router docs](https://aistupidlevel.info/router/docs) cover the rest.

## Usage

The Smart Router is OpenAI compatible, so it works with Haystack's [`OpenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/openaichatgenerator) pointed at `https://aistupidlevel.info/v1`. You only need `haystack-ai`; there is no extra package to install.

Set your router key as an environment variable:

```bash
export AISTUPIDLEVEL_API_KEY="aism_..."
```

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("AISTUPIDLEVEL_API_KEY"),
    api_base_url="https://aistupidlevel.info/v1",
    model="auto-coding",
)

messages = [ChatMessage.from_user("Write a Python function that checks whether a string is a palindrome.")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
print(response["replies"][0].meta["model"])  # the model the router chose
```

### Routing modes

Pass one of these as `model`:

| Mode | What it picks |
| --- | --- |
| `auto-coding`, `auto-reasoning`, `auto-tooling`, `auto-best` | The best measured score on the coding, reasoning, tool-use or combined benchmarks |
| `auto-value`, `auto-value-coding`, `auto-value-reasoning`, `auto-value-tooling` | The most benchmark points per measured dollar, among models within 5 points of the best |
| `auto-fastest-quality` | The fastest model within 5 points of the best |
| `auto-cheapest`, `auto-fastest`, `auto-consistent` | The cheapest, fastest or steadiest model |
| `auto-task` | A strategy chosen from the request's content |
| `auto` | The strategy saved in your account preferences |
| `auto-split` | A custom split |

When the leading models are statistically tied, the router picks the cheapest one by default; you can choose the fastest or the highest-scoring one instead. To pin a model, pass its id instead, for example `claude-sonnet-5`. `GET https://aistupidlevel.info/v1/models` lists every routing mode and model id, and the router docs describe the [routing modes](https://aistupidlevel.info/router/docs#strategies) in detail.

### Use with a Haystack Agent

For an agent that calls tools, `auto-tooling` picks the model with the best measured tool-use score:

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
        api_key=Secret.from_env_var("AISTUPIDLEVEL_API_KEY"),
        api_base_url="https://aistupidlevel.info/v1",
        model="auto-tooling",
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Munich?")])
print(result["last_message"].text)
```
