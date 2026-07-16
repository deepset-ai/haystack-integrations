---
layout: integration
name: Perseus Vault
description: Local-first, encrypted, persistent memory for Haystack 2.x pipelines and agents — no cloud, no API keys.
authors:
    - name: Perseus Computing LLC
      socials:
        github: Perseus-Computing-LLC
pypi: https://pypi.org/project/perseus-vault-haystack/
repo: https://github.com/Perseus-Computing-LLC/perseus-vault-haystack
type: Memory Store
report_issue: https://github.com/Perseus-Computing-LLC/perseus-vault-haystack/issues
logo: /logos/perseus-vault.svg
version: Haystack 2.0
toc: true
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Classes](#available-classes)
  - [Use with a Haystack Agent](#use-with-a-haystack-agent)
  - [Automatic Memory](#automatic-memory)
  - [Use in a Pipeline](#use-in-a-pipeline)
- [License](#license)

## Overview

[Perseus Vault](https://github.com/Perseus-Computing-LLC/perseus-vault) is a local-first,
single-binary memory engine for AI agents. It stores data in an encrypted (AES-256-GCM)
SQLite database with FTS5 full-text and vector search, runs fully offline, and requires
**no external vector database, no cloud service, and no API keys**. Your data never leaves
the machine — which makes it a fit for privacy-sensitive, air-gapped, and cost-constrained
deployments.

The `perseus-vault-haystack` package brings that persistent memory into Haystack 2.x as
both pipeline components and ready-made Agent tools:

- **`PerseusVaultMemoryStore`** — the encrypted document/memory store (`Document` and
  `ChatMessage` APIs).
- **`PerseusVaultMemoryWriter`** / **`PerseusVaultMemoryRetriever`** — pipeline components
  that persist and retrieve documents.
- **`create_perseus_vault_tools(...)`** — `retain_memory` / `recall_memory` /
  `reflect_memory` tools so a Haystack `Agent` decides when to store and recall memory.
- **`PerseusVaultMemoryWrapper`** — automatic recall-before / retain-after memory for an
  agent, without relying on tool-calling.

More information:

- [Perseus Vault GitHub repository](https://github.com/Perseus-Computing-LLC/perseus-vault)
- [perseus-vault-haystack package](https://github.com/Perseus-Computing-LLC/perseus-vault-haystack)

## Installation

Install the Python components from PyPI:

```bash
pip install perseus-vault-haystack
```

The components talk to a local `perseus-vault` executable over stdio, so the binary is a
separate, language-agnostic dependency. Download a pre-built binary from the
[Perseus Vault releases page](https://github.com/Perseus-Computing-LLC/perseus-vault/releases)
(or build from source) and either put it on your `$PATH` (so `perseus-vault` resolves) or
pass its absolute path via `perseus_vault_binary=`. No API key or account is required.

## Usage

### Available Classes

- [`PerseusVaultMemoryStore`](https://github.com/Perseus-Computing-LLC/perseus-vault-haystack):
  the encrypted store. `add_memories` / `search_memories` / `delete_all_memories` for
  `Document`s, plus `write_messages` / `recall_messages` for `ChatMessage`s.
- `create_perseus_vault_tools(memory_store, ...)`: returns `retain_memory`,
  `recall_memory`, and `reflect_memory` `Tool` instances for a Haystack `Agent`. Any tool
  can be excluded (e.g. `include_reflect=False`).
- `PerseusVaultMemoryWrapper`: wraps an agent with automatic `auto_recall` / `auto_retain`.
- `PerseusVaultMemoryWriter` / `PerseusVaultMemoryRetriever`: pipeline components over the
  store.

### Use with a Haystack Agent

Use the ready-made tools when you want an Agent to decide when to retrieve and store
memories. Everything runs against a local, encrypted database — no API key for memory:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from perseus_vault_haystack import PerseusVaultMemoryStore, create_perseus_vault_tools

store = PerseusVaultMemoryStore(db_path="~/.perseus-vault/agent.db", category="agent-memory")
tools = create_perseus_vault_tools(store)  # retain_memory, recall_memory, reflect_memory

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=tools,
    system_prompt=(
        "You are a helpful assistant with long-term memory. "
        "Use recall_memory before answering, and retain_memory to store durable "
        "user-specific facts, preferences, or project context."
    ),
)

agent.run(messages=[ChatMessage.from_user("Remember that I prefer concise Python examples.")])
```

### Automatic Memory

Use `PerseusVaultMemoryWrapper` when you want memory to work automatically — injecting
relevant memories into the conversation before each turn and storing the exchange after —
without relying on the model to call tools:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from perseus_vault_haystack import PerseusVaultMemoryStore, PerseusVaultMemoryWrapper

store = PerseusVaultMemoryStore(db_path="~/.perseus-vault/agent.db")
memory = PerseusVaultMemoryWrapper(store, auto_recall=True, auto_retain=True)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    system_prompt="You are a helpful assistant with long-term memory.",
)

result = memory.run(agent, messages=[ChatMessage.from_user("I prefer dark mode.")])
print(result["last_message"].text)
```

### Use in a Pipeline

Use the components when you want explicit pipeline control over when memories are stored
and retrieved. Because Perseus Vault persists to an encrypted SQLite file, documents
written in one run are available in any future run pointed at the same `db_path`:

```python
from pathlib import Path

from haystack import Pipeline, Document
from perseus_vault_haystack import (
    PerseusVaultMemoryStore,
    PerseusVaultMemoryWriter,
    PerseusVaultMemoryRetriever,
)

db_path = Path("~/.perseus-vault/haystack.db").expanduser()
db_path.parent.mkdir(parents=True, exist_ok=True)
store = PerseusVaultMemoryStore(db_path=str(db_path))

write_pipe = Pipeline()
write_pipe.add_component("writer", PerseusVaultMemoryWriter(memory_store=store))
write_pipe.run(
    {"writer": {"documents": [
        Document(content="Perseus Vault stores encrypted memory for Haystack agents."),
    ]}}
)

read_pipe = Pipeline()
read_pipe.add_component("retriever", PerseusVaultMemoryRetriever(memory_store=store))
result = read_pipe.run({"retriever": {"query": "encrypted memory"}})
print(result["retriever"]["documents"])
```

## License

`perseus-vault-haystack` is distributed under the terms of the MIT license.
