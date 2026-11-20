---
layout: integration
name: Fortytwo
description: Use Fortytwo's OpenAI-compatible API with Haystack chat generators and agents
authors:
    - name: Fortytwo
      socials:
        github: Fortytwo-Network
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/fortytwo.svg
version: Haystack 3.4.1
toc: true
---

## Overview

[Fortytwo](https://fortytwo.network/) provides an OpenAI-compatible inference API.
You can use it with Haystack's built-in `OpenAIChatGenerator` by setting the API
base URL and supplying your own Fortytwo API key. No additional integration
package is needed.

The [models page](https://docs.fortytwo.network/docs/models) describes the current
model and its support for tool calling, structured output and image input.
The examples below demonstrate text generation, a local tool and text streaming.
They do not expose the model's reasoning content.

## Usage

These examples use Python 3.11 or later and Haystack 3.4.1:

```bash
pip install haystack-ai==3.4.1
export FORTYTWO_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FORTYTWO_API_KEY"),
    api_base_url="https://api.fortytwo.network/v1",
    model="qwen/qwen3.8-27b",
    timeout=30.0,
    max_retries=0,
    generation_kwargs={"max_completion_tokens": 512},
)
messages = [ChatMessage.from_user("Summarise RAG in one sentence.")]
result = generator.run(messages=messages)
print(result["replies"][0].text)
```

To stream the same request, import Haystack's callback and replace the `run` call
above with:

```python
from haystack.components.generators.utils import print_streaming_chunk

result = generator.run(
    messages=messages,
    streaming_callback=print_streaming_chunk,
)
```

### Using a Haystack Agent with a tool

Haystack executes the local Python tool when the model requests it. This example
uses a deterministic multiplication tool, strict tool schemas and a limit of
three agent steps. The model can return a final answer after using the tool.

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def multiply(a: int, b: int) -> str:
    """Multiply two integers and return their product."""
    return str(a * b)


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_env_var("FORTYTWO_API_KEY"),
        api_base_url="https://api.fortytwo.network/v1",
        model="qwen/qwen3.8-27b",
        timeout=30.0,
        max_retries=0,
        tools_strict=True,
        generation_kwargs={"max_completion_tokens": 512},
    ),
    tools=[multiply],
    max_agent_steps=3,
    exit_conditions=["text"],
)
result = agent.run(
    messages=[ChatMessage.from_user("Use multiply to calculate 17 times 23, then report the result.")]
)
print(result["last_message"].text)
```
