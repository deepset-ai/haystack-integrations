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
repo: https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations
type: Memory Store
report_issue: https://github.com/maximem-ai/maximem_synap/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [SynapRetriever](#synapretriever)
  - [SynapMemoryWriter](#synapmemorywriter)
  - [Full Pipeline Example](#full-pipeline-example)

## Overview

[Synap](https://maximem.ai) is a managed memory layer for AI agents. The Haystack integration provides two native Haystack `@component` classes:

- **`SynapRetriever`** — retrieves facts, preferences, episodes, and past context relevant to a query from the user's Synap memory and returns them as Haystack `Document` objects
- **`SynapMemoryWriter`** — records conversation turns to Synap so they are available for retrieval in future sessions

Memory is scoped to the `user_id` and `customer_id` you provide, ensuring strict isolation in multi-tenant applications.

## Installation

```bash
pip install maximem-synap-haystack
```

Get an API key at [synap.maximem.ai](https://synap.maximem.ai).

## Usage

### SynapRetriever

`SynapRetriever` is a standard Haystack component that takes a `query` string and returns a list of `Document` objects populated from the user's Synap memory. Plug it into any pipeline that needs long-term context before calling an LLM.

```python
import os

from haystack import Pipeline
from maximem_synap import MaximemSynapSDK
from synap_haystack import SynapRetriever

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])

retriever = SynapRetriever(
    sdk=sdk,
    user_id="user_123",
    customer_id="acme_corp",
)

pipeline = Pipeline()
pipeline.add_component("memory", retriever)
```

Each returned `Document` has a `content` field with the memory text and a `meta` dict that includes:

| Key | Description |
|---|---|
| `type` | `"fact"`, `"preference"`, `"episode"`, `"emotion"`, `"temporal_event"` |
| `id` | Synap memory item ID |
| `confidence` / `strength` / `significance` | Relevance signal, type-dependent |

### SynapMemoryWriter

`SynapMemoryWriter` accepts a list of `Document` objects where `content` is the message text and `meta["role"]` is `"user"` or `"assistant"`. It records each turn to Synap so future retrieval requests can surface them.

```python
from synap_haystack import SynapMemoryWriter

writer = SynapMemoryWriter(
    sdk=sdk,
    conversation_id="conv_abc",
    user_id="user_123",
    customer_id="acme_corp",
)

pipeline.add_component("memory_writer", writer)
```

The component returns `written_count`, `failed_count`, `skipped_count`, and `first_error` outputs so downstream components can branch on partial failures. If every document fails, it raises `SynapIntegrationError` — a 100% failure rate indicates a broken pipeline and should not be silenced.

### Full Pipeline Example

A complete retrieval-augmented pipeline that loads Synap context before the LLM and records turns afterward:

```python
import os

from haystack import Pipeline
from haystack.components.generators.chat import OpenAIChatGenerator
from maximem_synap import MaximemSynapSDK
from synap_haystack import SynapMemoryWriter, SynapRetriever

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])

retriever = SynapRetriever(sdk=sdk, user_id="user_123", customer_id="acme_corp")
writer = SynapMemoryWriter(
    sdk=sdk, conversation_id="session_1", user_id="user_123", customer_id="acme_corp"
)

pipeline = Pipeline()
pipeline.add_component("memory", retriever)
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o"))
pipeline.add_component("memory_writer", writer)

result = pipeline.run({"memory": {"query": "What are my dietary restrictions?"}})
```

## More Resources

- [Synap Documentation](https://docs.maximem.ai)
- [Haystack Integration Guide](https://docs.maximem.ai/integrations/haystack)
- [Dashboard](https://synap.maximem.ai)
- [PyPI: maximem-synap-haystack](https://pypi.org/project/maximem-synap-haystack/)
- [Open source integration package](https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations)
