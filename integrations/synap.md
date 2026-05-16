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
  - [SynapRetriever](#synapretriever)
  - [SynapMemoryWriter](#synapmemorywriter)
  - [Full Pipeline Example](#full-pipeline-example)
- [License](#license)

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

A retrieval pipeline that surfaces relevant Synap memories as Haystack `Document` objects, ready to inject into any downstream component:

```python
import os

from haystack import Pipeline
from maximem_synap import MaximemSynapSDK
from synap_haystack import SynapRetriever

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])

pipeline = Pipeline()
pipeline.add_component(
    "memory",
    SynapRetriever(sdk=sdk, user_id="user_123", customer_id="acme_corp"),
)

result = pipeline.run({"memory": {"query": "What are my dietary restrictions?"}})
for doc in result["memory"]["documents"]:
    print(doc.content)
```

To record conversation turns, add `SynapMemoryWriter` as a separate pipeline step and supply it with `Document` objects whose `meta["role"]` is `"user"` or `"assistant"`. Wire components together with `pipeline.connect()` to match your application's prompt-building and LLM architecture.

## More Resources

- [Synap Documentation](https://docs.maximem.ai)
- [Haystack Integration Guide](https://docs.maximem.ai/integrations/haystack)
- [Dashboard](https://synap.maximem.ai)
- [PyPI: maximem-synap-haystack](https://pypi.org/project/maximem-synap-haystack/)
- [Open source integration package](https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations/synap-haystack)

## License

`maximem-synap-haystack` is released under the [Apache License 2.0](https://github.com/maximem-ai/maximem_synap_sdk/blob/main/LICENSE).
