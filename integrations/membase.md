---
layout: integration
name: Membase
description: Add persistent, cross-session long-term memory to Haystack agents and pipelines with Membase
authors:
    - name: Unibase
      socials:
        github: unibaseio
        twitter: Unibase_AI
pypi: https://pypi.org/project/membase-haystack/
repo: https://github.com/unibaseio/membase/tree/main/integrations/haystack
type: Memory Store
report_issue: https://github.com/unibaseio/membase/issues
logo: /logos/membase.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [Use with a Haystack Agent](#use-with-a-haystack-agent)
  - [Use in a Pipeline](#use-in-a-pipeline)
- [License](#license)

## Overview

[Membase](https://membase.com) is a long-term memory layer that a user keeps across the AI tools they use. Memory lives in named Memories, and every search result names the Memory it came from, so the model can cite where a fact was learned.

The `membase-haystack` package brings that memory to Haystack agents and pipelines. Saving is deliberate: the model saves a note in the user's own words when the user asks, and there is no delete tool.

More information:

- [Membase website](https://membase.com)
- [Membase documentation](https://docs.membase.com)
- [membase-haystack source](https://github.com/unibaseio/membase/tree/main/integrations/haystack)

## Installation

```bash
pip install membase-haystack
```

Create a developer key in the [Membase app](https://app.membase.com) under **Connect › Developer keys** and export it:

```bash
export MEMBASE_API_KEY="your-membase-developer-key"
```

A Read key can search and, with Profile ticked, read the profile. Saving needs a Read & write key that reaches a single Memory.

## Usage

### Components

This integration introduces:

- `MembaseMemoryStore`: the memory store. It owns the Membase client and offers `search_memories` (system `ChatMessage`s, each prefixed with its Memory in brackets), `add_memories` (saves the user messages' text as one note) and `profile`. The key is a Haystack `Secret`, so the store serializes with a pipeline.
- `MembaseMemoryRetriever`: a pipeline component that returns the relevant memories as system `ChatMessage`s. Its search is time-boxed (8 seconds by default): when the budget runs out it returns no memories and the pipeline goes on.
- `membase_tools(store)`: `membase_search`, `membase_save` and `membase_profile` as Haystack `Tool`s for an `Agent`.

### Use with a Haystack Agent

Use the tools when the Agent should decide when to search and save:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from membase_haystack import MembaseMemoryStore, membase_tools

store = MembaseMemoryStore()  # reads MEMBASE_API_KEY

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=membase_tools(store),
    system_prompt=(
        "You are a helpful assistant with long-term memory. Search Membase before answering anything that "
        "may depend on what the user told you before, and cite the Memory in brackets. Save to Membase only "
        "when the user asks you to remember something."
    ),
)

result = agent.run(messages=[ChatMessage.from_user("Which database did we pick for the ledger?")])
print(result["last_message"].text)
```

### Use in a Pipeline

Use `MembaseMemoryRetriever` to put the relevant memories in front of the model on every run:

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from membase_haystack import MembaseMemoryRetriever, MembaseMemoryStore

template = [
    ChatMessage.from_system(
        "Memory from Membase (cite the Memory in brackets):\n{% for m in memories %}{{ m.text }}\n{% endfor %}"
    ),
    ChatMessage.from_user("{{ question }}"),
]

pipeline = Pipeline()
pipeline.add_component("memory", MembaseMemoryRetriever(memory_store=MembaseMemoryStore(), top_k=5))
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["question"]))
pipeline.add_component("llm", OpenAIChatGenerator())
pipeline.connect("memory.memories", "prompt.memories")
pipeline.connect("prompt.prompt", "llm.messages")

question = "Which database did we pick for the ledger?"
result = pipeline.run({"memory": {"query": question}, "prompt": {"question": question}})
print(result["llm"]["replies"][0].text)
```

A Membase key belongs to one person's account, so one `MembaseMemoryStore` serves one person. In a multi-user app, build the store per user from that user's own key, for example `MembaseMemoryStore(api_key=Secret.from_token(user_key))`.

For local mode, more options and the full API, see the [package README](https://github.com/unibaseio/membase/tree/main/integrations/haystack#readme).

## License

`membase-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
