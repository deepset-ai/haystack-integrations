---
layout: integration
name: Cognee
description: Add persistent, knowledge-graph-backed memory to your Haystack agents and pipelines with Cognee
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Cognee
      socials:
        github: topoteretes
        twitter: cognee_ai
        linkedin: https://www.linkedin.com/company/cognee-ai/
pypi: https://pypi.org/project/cognee-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/cognee
type: Memory Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/cognee.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Classes](#available-classes)
  - [Use in a Pipeline](#use-in-a-pipeline)
- [License](#license)

## Overview

[Cognee](https://www.cognee.ai/) provides open-source, knowledge-graph-backed memory for AI agents and assistants. It helps Haystack applications store facts, conversation history, and contextual knowledge as a semantic graph, then retrieve the most relevant memories using graph-completion or other search strategies.

The `cognee-haystack` package is part of [Haystack Core Integrations](https://github.com/deepset-ai/haystack-core-integrations) and provides:

- `CogneeMemoryStore`: A persistent memory store backed by Cognee's knowledge graph API.
- `CogneeRetriever`: A pipeline component for retrieving memories from Cognee as system `ChatMessage` objects.
- `CogneeWriter`: A pipeline component for writing `ChatMessage` memories to Cognee.

Cognee supports two memory tiers:

- **Permanent knowledge graph** — rich semantic storage backed by an LLM extraction step; supports graph-completion queries and cross-session recall.
- **Session cache** — fast, LLM-free writes scoped to a single session; can be promoted to the permanent graph later via `CogneeMemoryStore.improve()`.

More information:

- [Cognee website](https://www.cognee.ai)
- [Cognee documentation](https://docs.cognee.ai)
- [Cognee GitHub repository](https://github.com/topoteretes/cognee)

## Installation

Install the integration:

```bash
pip install cognee-haystack
```

Set your LLM API key (used by Cognee for knowledge graph extraction and queries):

```bash
export LLM_API_KEY="your-llm-api-key"
```

Optionally, set a separate embedding API key (defaults to `LLM_API_KEY` when unset):

```bash
export EMBEDDING_API_KEY="your-embedding-api-key"
```

Cognee reads LLM provider, database, and vector-store settings from environment variables. See the [Cognee documentation](https://docs.cognee.ai) for the full list of configuration options.

## Usage

### Available Classes

- [`CogneeRetriever`](https://docs.haystack.deepset.ai/docs/cogneeretriever): Retrieves memories from Cognee as system `ChatMessage` objects.
- [`CogneeWriter`](https://docs.haystack.deepset.ai/docs/cogneewriter): Writes `ChatMessage` objects to Cognee.
- [`CogneeMemoryStore`](https://docs.haystack.deepset.ai/reference/integrations-cognee#cogneememorystore): The underlying store that wraps Cognee's V2 memory API (`remember`, `recall`, `improve`, `forget`).

### Use in a Pipeline

Use `CogneeRetriever` and `CogneeWriter` for explicit pipeline control over when memories are stored and retrieved.

The example below seeds long-lived facts into the permanent knowledge graph, then runs an agent pipeline that retrieves relevant context before each response. `cognee.recall` auto-captures each turn as a session QA entry, so no `CogneeWriter` is needed inside the agent pipeline for session memory.

```python
from haystack import Pipeline
from haystack.components.agents import Agent
from haystack.components.converters import OutputAdapter
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.retrievers.cognee import CogneeRetriever
from haystack_integrations.components.writers.cognee import CogneeWriter
from haystack_integrations.memory_stores.cognee import CogneeMemoryStore

# Seed long-lived facts into the permanent knowledge graph (no session_id).
seed_store = CogneeMemoryStore(dataset_name="my_agent_memory", self_improvement=False)
persistent_writer = CogneeWriter(memory_store=seed_store)
persistent_writer.run(
    messages=[
        ChatMessage.from_user("Alice is a senior data scientist specialising in NLP."),
        ChatMessage.from_user("Alice's current project is a documentation search system built with Haystack."),
        ChatMessage.from_user("Alice prefers concise answers with Python code examples."),
    ]
)

# Build the agent pipeline with a session-scoped store.
SESSION = "alice_session_1"
chat_store = CogneeMemoryStore(dataset_name="my_agent_memory", session_id=SESSION)

pipeline = Pipeline()
pipeline.add_component("retriever", CogneeRetriever(memory_store=chat_store))
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
        chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
        system_prompt=(
            "You are a helpful assistant with long-term memory. "
            "System messages at the start of the conversation contain relevant memories. "
            "Be concise; prefer short answers and Python code examples."
        ),
    ),
)

pipeline.connect("retriever.messages", "memory_context.memories")
pipeline.connect("memory_context.output", "agent.messages")

query = "What project is Alice currently working on?"
result = pipeline.run(
    {
        "retriever": {"query": query},
        "memory_context": {"user_messages": [ChatMessage.from_user(query)]},
    }
)
print(result["agent"]["last_message"].text)

# After the session, promote the session cache into the permanent graph.
chat_store.improve()
```

For a full four-phase demo (persistent seeding → session seeding → agent chat → graph promotion), see the [example script](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/cognee/examples/demo_memory_agent.py).

## License

`cognee-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
