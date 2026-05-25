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
pypi: https://pypi.org/project/mem0-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mem0
type: Memory Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/mem0.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Classes](#available-classes)
  - [Use with a Haystack Agent](#use-with-a-haystack-agent)
  - [Use in a Pipeline](#use-in-a-pipeline)
- [License](#license)

## Overview

[Mem0](https://mem0.ai) provides a memory layer for AI agents and assistants. It helps Haystack applications store user-specific facts, preferences, and project context, then retrieve relevant memories in later conversations.

The `mem0-haystack` package is part of [Haystack Core Integrations](https://github.com/deepset-ai/haystack-core-integrations) and provides:

- `Mem0MemoryStore`: A persistent memory store backed by the Mem0 Cloud API.
- `Mem0MemoryRetriever` and `Mem0MemoryWriter`: Pipeline components for retrieving and writing `ChatMessage` memories.
- `Mem0MemoryRetrieverTool` and `Mem0MemoryWriterTool`: Ready-made tools for memory-augmented Haystack Agents.

More information:

- [Mem0 website](https://mem0.ai)
- [Mem0 documentation](https://docs.mem0.ai)
- [Mem0 platform](https://app.mem0.ai)
- [Mem0 GitHub repository](https://github.com/mem0ai/mem0)

## Installation

Install the integration:

```bash
pip install mem0-haystack
```

Set your Mem0 API key:

```bash
export MEM0_API_KEY="your-mem0-api-key"
```

You can obtain an API key by signing up at [app.mem0.ai](https://app.mem0.ai).

## Usage

### Available Classes

- [`Mem0MemoryRetrieverTool`](https://docs.haystack.deepset.ai/docs/mem0memorytools) and [`Mem0MemoryWriterTool`](https://docs.haystack.deepset.ai/docs/mem0memorytools): Ready-made Agent tools for long-term memory.
- [`Mem0MemoryRetriever`](https://docs.haystack.deepset.ai/docs/mem0memoryretriever): Retrieves memories from Mem0 as system `ChatMessage` objects.
- [`Mem0MemoryWriter`](https://docs.haystack.deepset.ai/docs/mem0memorywriter): Writes `ChatMessage` objects to Mem0.
- [`Mem0MemoryStore`](https://docs.haystack.deepset.ai/reference/integrations-mem0#mem0memorystore): Lower-level store used by the tools and components.

### Use with a Haystack Agent

Use the ready-made tools when you want an Agent to decide when to retrieve and store memories:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage

from haystack_integrations.memory_stores.mem0 import Mem0MemoryStore
from haystack_integrations.tools.mem0 import (
    Mem0MemoryRetrieverTool,
    Mem0MemoryWriterTool,
)

store = Mem0MemoryStore()

retrieve_memories = Mem0MemoryRetrieverTool(memory_store=store, top_k=10)
store_memory = Mem0MemoryWriterTool(memory_store=store)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-5.4"),
    tools=[retrieve_memories, store_memory],
    system_prompt="""You are a helpful assistant with long-term memory.

At the beginning of each turn, call retrieve_memories without a query to inspect known memories.
Use store_memory only for new durable user-specific facts, preferences, or project context.
Before storing, compare the proposed memory with retrieved memories and avoid duplicates.
""",
    streaming_callback=print_streaming_chunk,
    state_schema={"user_id": {"type": str}},
)

agent.run(
    messages=[
        ChatMessage.from_user(
            "My name is Alice. Please remember that I prefer concise Python examples.",
        ),
    ],
    user_id="alice",
)
```

### Use in a Pipeline

Use the components when you want explicit pipeline control over memory retrieval and writing:

```python
from haystack import Pipeline
from haystack.components.agents import Agent
from haystack.components.converters import OutputAdapter
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.retrievers.mem0 import Mem0MemoryRetriever
from haystack_integrations.components.writers.mem0 import Mem0MemoryWriter
from haystack_integrations.memory_stores.mem0 import Mem0MemoryStore

store = Mem0MemoryStore()

pipeline = Pipeline()
pipeline.add_component("retriever", Mem0MemoryRetriever(memory_store=store, top_k=5))
pipeline.add_component(
    "memory_context",
    OutputAdapter(
        template="{{ memories + user_messages }}",
        output_type=list[ChatMessage],
        unsafe=True,
    ),
)
pipeline.add_component(
    "agent",
    Agent(
        chat_generator=OpenAIChatGenerator(model="gpt-5.4"),
        system_prompt="Use system messages at the start of the conversation as long-term memory.",
        streaming_callback=print_streaming_chunk,
    ),
)
pipeline.add_component("writer", Mem0MemoryWriter(memory_store=store, infer=True))

pipeline.connect("retriever.memories", "memory_context.memories")
pipeline.connect("memory_context.output", "agent.messages")
pipeline.connect("agent.messages", "writer.messages")

query = "Give me a short implementation tip."

pipeline.run(
    {
        "retriever": {
            "query": query,
            "user_id": "alice",
        },
        "memory_context": {
            "user_messages": [ChatMessage.from_user(query)],
        },
        "writer": {
            "user_id": "alice",
        },
    }
)
```

For more examples, see the [Mem0 integration source](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mem0).

## License

`mem0-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
