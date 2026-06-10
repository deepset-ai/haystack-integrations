---
layout: integration
name: Synap
description: Add persistent, cross-session user memory to your Haystack agents and pipelines with Synap
authors:
    - name: Maximem
      socials:
        github: maximem-ai
        linkedin: https://www.linkedin.com/company/maximem/
pypi: https://pypi.org/project/maximem-synap-haystack/
repo: https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations/synap-haystack
type: Memory Store
report_issue: https://github.com/maximem-ai/maximem_synap/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Classes](#available-classes)
  - [Standalone Memory Operations](#standalone-memory-operations)
  - [Use in a Pipeline](#use-in-a-pipeline)
- [More Resources](#more-resources)
- [License](#license)

## Overview

[Synap](https://maximem.ai) is a managed long-term memory layer for AI agents. It runs a full extraction pipeline on every conversation turn — automatically identifying facts, preferences, episodes, emotions, and temporal events — and retrieves only what is semantically relevant to the current query.

The `maximem-synap-haystack` package provides a Haystack-native memory store that follows the same shape as `mem0-haystack`:

- **`SynapMemoryStore`**: A persistent memory store backed by the Synap API. Owns all SDK interaction (`add_memories` / `search_memories` / `search_memories_as_single_message`).
- **`SynapMemoryRetriever`** and **`SynapMemoryWriter`**: Pipeline `@component` classes for retrieving memories as `ChatMessage` objects and writing conversation turns to the store.
- **`SynapRetriever`**: An additional `@component` that returns memories as `Document` objects for classic RAG-style pipelines.

Memory is scoped to the `user_id` and `customer_id` you provide, ensuring strict isolation in multi-tenant applications.

More information:

- [Synap website](https://maximem.ai)
- [Synap documentation](https://docs.maximem.ai)
- [Synap GitHub repository](https://github.com/maximem-ai/maximem_synap_sdk)

## Installation

```bash
pip install maximem-synap-haystack
```

Set your Synap API key:

```bash
export SYNAP_API_KEY="your-synap-api-key"
```

You can obtain an API key at [synap.maximem.ai](https://synap.maximem.ai).

## Usage

### Available Classes

- **`SynapMemoryStore`**: The memory store — a plain object (not a `@component`) that owns all Synap SDK interaction. Use it directly for standalone read/write, or pass it to the components below.
- **`SynapMemoryRetriever`**: Retrieves memories from Synap as system `ChatMessage` objects. Mem0-shaped chat read path.
- **`SynapMemoryWriter`**: Writes user / assistant `ChatMessage` objects to Synap. Returns per-message status so callers can branch on partial failures.
- **`SynapRetriever`**: Alternate retriever that returns Haystack `Document` objects (RAG-style read path).

### Standalone Memory Operations

You can use `SynapMemoryStore` directly to add and search memories:

```python
import os

from haystack.dataclasses import ChatMessage
from maximem_synap import MaximemSynapSDK
from synap_haystack import SynapMemoryStore

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])
store = SynapMemoryStore(sdk, user_id="alice", customer_id="acme_corp")

# Write — extracted server-side into long-term memory
store.add_memories(
    messages=[ChatMessage.from_user("I prefer window seats and aisle on red-eyes.")],
    conversation_id="conv_abc",
)

# Read — semantic, query-driven
memories = store.search_memories(query="seat preference")
for msg in memories:
    print(msg.text)

# Single-message variant — useful for prompt injection
context = store.search_memories_as_single_message(query="seat preference")
```

### Use in a Pipeline

`SynapMemoryRetriever` and `SynapMemoryWriter` are thin `@component` wrappers around the store. Construct the store once and share it across both:

```python
import os

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from maximem_synap import MaximemSynapSDK
from synap_haystack import SynapMemoryRetriever, SynapMemoryStore, SynapMemoryWriter

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])
store = SynapMemoryStore(sdk, user_id="alice", customer_id="acme_corp")

pipeline = Pipeline()
pipeline.add_component("memory_retriever", SynapMemoryRetriever(store=store))
pipeline.add_component("prompt_builder", ChatPromptBuilder())
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o"))
pipeline.add_component("memory_writer", SynapMemoryWriter(store=store))

pipeline.connect("memory_retriever.messages", "prompt_builder.template")
pipeline.connect("prompt_builder.prompt", "llm.messages")
```

For classic RAG pipelines that want `Document` objects rather than `ChatMessage` objects, use `SynapRetriever` instead of `SynapMemoryRetriever` — same store, different output shape.

## More Resources

- [Synap Documentation](https://docs.maximem.ai)
- [Haystack Integration Guide](https://docs.maximem.ai/integrations/haystack)
- [Dashboard](https://synap.maximem.ai)
- [PyPI: maximem-synap-haystack](https://pypi.org/project/maximem-synap-haystack/)
- [Open source integration package](https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations/synap-haystack)

## License

`maximem-synap-haystack` is released under the [Apache License 2.0](https://github.com/maximem-ai/maximem_synap_sdk/blob/main/LICENSE).
