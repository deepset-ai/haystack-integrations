---
layout: integration
name: Mem0
description: Add persistent, user-specific memory to your Haystack agents and pipelines with Mem0
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Mem0
      socials:
        github: mem0ai
        twitter: mem0ai
        linkedin: https://www.linkedin.com/company/mem0ai/
pypi: https://pypi.org/project/haystack-experimental/
repo: https://github.com/deepset-ai/haystack-experimental
type: Memory Store
report_issue: https://github.com/deepset-ai/haystack-experimental/issues
logo: /logos/mem0.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Standalone Memory Operations](#standalone-memory-operations)
  - [Using Mem0 with a Haystack Agent](#using-mem0-with-a-haystack-agent)
- [License](#license)

## Overview

[Mem0](https://mem0.ai) (pronounced "mem-zero") provides a universal memory layer for AI agents and assistants. It enables your Haystack applications to remember user preferences, adapt to individual needs, and continuously learn from past interactions — making AI conversations truly personalized.

This integration is part of the [`haystack-experimental`](https://github.com/deepset-ai/haystack-experimental) package and provides the `Mem0MemoryStore`, which acts as a persistent memory backend for [Haystack Agents](https://docs.haystack.deepset.ai/docs/agent). Instead of relying solely on conversation history or static document stores, agents can use Mem0 to store and retrieve user-specific memories across sessions.

### Key Features

- **Persistent Memory**: Store and retrieve user-specific memories that persist across sessions
- **Multi-Level Scoping**: Organize memories by User, Session, or Agent scope
- **Intelligent Extraction**: Automatically extracts relevant facts from conversations — no need to store entire transcripts
- **Seamless Agent Integration**: Works natively with Haystack's Agent component for context-aware responses
- **Flexible Deployment**: Use the managed [Mem0 Platform](https://app.mem0.ai) or self-host with your own infrastructure

More info about Mem0:

- [Mem0 Website](https://mem0.ai)
- [Mem0 Documentation](https://docs.mem0.ai)
- [Mem0 Platform (Managed)](https://app.mem0.ai)
- [Mem0 GitHub](https://github.com/mem0ai/mem0)

## Installation

```bash
pip install haystack-ai haystack-experimental mem0ai
```

### Environment Variables

Set the following environment variable to use the Mem0 Platform:

```bash
export MEM0_API_KEY="your-mem0-api-key"
```

You can obtain an API key by signing up at [app.mem0.ai](https://app.mem0.ai).

## Usage

### Components

This integration introduces one component:

- [`Mem0MemoryStore`](https://docs.haystack.deepset.ai/reference/experimental-mem0-memory-store-api#mem0memorystore): A memory store that uses Mem0 as the backend for storing and retrieving user-specific memories. It can be used standalone or plugged into a Haystack Agent.

### Standalone Memory Operations

You can use `Mem0MemoryStore` directly to add and search memories:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_experimental.memory_stores.mem0 import Mem0MemoryStore

os.environ["MEM0_API_KEY"] = "your-mem0-api-key"

# Initialize the memory store
memory = Mem0MemoryStore()

# Add memories from a conversation
messages = [
    ChatMessage.from_user("I'm a vegetarian and I love Italian food."),
]
memory.add_memories(messages=messages, user_id="alice")

# Later, retrieve relevant memories
query = "What kind of food do I like?"
memories = memory.search_memories(query=query, user_id="alice")

print(memories)
# Returns memories related to Alice's food preferences
```

### Using Mem0 with a Haystack Agent

The primary use case for `Mem0MemoryStore` is to provide personalized context to a Haystack Agent. The agent automatically retrieves relevant memories before generating a response, enabling context-aware conversations:

```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_experimental.components.agents import Agent
from haystack_experimental.memory_stores.mem0 import Mem0MemoryStore

os.environ["MEM0_API_KEY"] = "your-mem0-api-key"
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Initialize components
memory_store = Mem0MemoryStore()
generator = OpenAIChatGenerator(model="gpt-4o")

# Create an agent with memory
agent = Agent(
    generator=generator,
    memory_store=memory_store,
    system_prompt="You are a helpful assistant that remembers user preferences.",
)

# First interaction — the agent learns about the user
response = agent.run(
    query="I prefer dark mode and use vim keybindings.",
    memory_store_kwargs={"user_id": "user_123"},
)
print(response["replies"][0].content)

# Later interaction — the agent recalls the user's preferences
response = agent.run(
    query="Can you recommend an IDE setup for me?",
    memory_store_kwargs={"user_id": "user_123"},
)
print(response["replies"][0].content)
# The agent will reference the user's preference for dark mode and vim keybindings
```

> **Note:** The `Mem0MemoryStore` is currently part of the `haystack-experimental` package and is labeled as **experimental**. The API may change in future releases. Always refer to the [haystack-experimental repository](https://github.com/deepset-ai/haystack-experimental) for the latest updates.

### License

`haystack-experimental` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
