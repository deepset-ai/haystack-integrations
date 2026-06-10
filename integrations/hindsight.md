---
layout: integration
name: Hindsight
description: Add open-source long-term memory to your Haystack agents with Hindsight's retain, recall, and reflect tools
authors:
    - name: Vectorize
      socials:
        github: vectorize-io
        twitter: vectorizeio
        linkedin: https://www.linkedin.com/company/vectorizeio/
pypi: https://pypi.org/project/hindsight-haystack/
repo: https://github.com/vectorize-io/hindsight/tree/main/hindsight-integrations/haystack
type: Memory Store
report_issue: https://github.com/vectorize-io/hindsight/issues
logo: /logos/hindsight.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Tools](#available-tools)
  - [Use with a Haystack Agent](#use-with-a-haystack-agent)
  - [Automatic Memory](#automatic-memory)
- [License](#license)

## Overview

[Hindsight](https://github.com/vectorize-io/hindsight) is an open-source long-term memory engine for AI agents. It stores facts, preferences, and project context across sessions, then retrieves what's relevant later — and can go a step further by *reflecting*: synthesizing a query-focused summary from many memories rather than returning raw snippets.

The `hindsight-haystack` package exposes Hindsight as ready-made Haystack `Tool` instances, so any Haystack `Agent` can read and write durable memory. It provides three tools:

- `retain_memory`: store new facts, preferences, or context.
- `recall_memory`: retrieve the raw memories relevant to a query.
- `reflect_on_memory`: get a synthesized, reasoned summary over the relevant memories.

Hindsight runs against [Hindsight Cloud](https://hindsight.vectorize.io) out of the box, or against a self-hosted Hindsight server.

More information:

- [Hindsight website](https://hindsight.vectorize.io)
- [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight)
- [hindsight-haystack package](https://github.com/vectorize-io/hindsight/tree/main/hindsight-integrations/haystack)

## Installation

Install the integration:

```bash
pip install hindsight-haystack
```

Set your Hindsight API key to use Hindsight Cloud:

```bash
export HINDSIGHT_API_KEY="your-hindsight-api-key"
```

You can get a free API key at [hindsight.vectorize.io](https://hindsight.vectorize.io), or run Hindsight [locally](https://github.com/vectorize-io/hindsight) and point the client at `http://localhost:8888`.

## Usage

### Available Tools

`create_hindsight_tools()` returns a list of Haystack `Tool` instances backed by a Hindsight memory bank:

- `retain_memory`: store durable user-specific facts, preferences, or project context.
- `recall_memory`: search memory and return the raw matching memories.
- `reflect_on_memory`: synthesize a focused summary over the relevant memories.

You can include or exclude any of them (e.g. `include_reflect=False`).

### Use with a Haystack Agent

Use the tools when you want the Agent to decide when to retrieve and store memory:

```python
from hindsight_client import Hindsight
from hindsight_haystack import create_hindsight_tools

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

# Hindsight Cloud (reads HINDSIGHT_API_KEY), or pass base_url="http://localhost:8888" for self-hosted
client = Hindsight(base_url="https://api.hindsight.vectorize.io")

tools = create_hindsight_tools(
    client=client,
    bank_id="user-123",
    mission="Track user preferences and project context",
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=tools,
    system_prompt=(
        "You are a helpful assistant with long-term memory. "
        "Use recall_memory to search memory before answering, "
        "and retain_memory to store important new facts."
    ),
)

result = agent.run(messages=[ChatMessage.from_user("Remember that I prefer dark mode and concise answers.")])
print(result["last_message"].text)
```

### Automatic Memory

Use `HindsightMemoryWrapper` when you want memory to work automatically — injecting relevant context before each turn and storing the exchange after — without relying on the model to call tools:

```python
from hindsight_client import Hindsight
from hindsight_haystack import HindsightMemoryWrapper

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

client = Hindsight(base_url="https://api.hindsight.vectorize.io")

memory = HindsightMemoryWrapper(
    client=client,
    bank_id="user-123",
    mission="Track user preferences and project context",
    auto_recall=True,   # inject relevant memories into the system prompt before each turn
    auto_retain=True,   # store the user + assistant messages after each turn
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=memory,
    system_prompt="You are a helpful assistant with long-term memory.",
)

# memory.run() drives the agent with automatic recall + retain
result = memory.run(agent, messages=[ChatMessage.from_user("I prefer dark mode.")])
print(result["last_message"].text)
```

For configuration options (budget, tags, recall/reflect tuning, self-hosting), see the [package README](https://github.com/vectorize-io/hindsight/tree/main/hindsight-integrations/haystack).

## License

`hindsight-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
