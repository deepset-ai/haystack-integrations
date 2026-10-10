---
layout: integration
name: Mnemoverse
description: Hosted long-term memory for Haystack agents over MCP. Agents recall by natural-language query, report whether a recalled memory helped, and share memory through rooms.
authors:
    - name: Mnemoverse
      socials:
        github: mnemoverse
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/mnemoverse/mcp-memory-server
type: Tool Integration
report_issue: https://github.com/mnemoverse/mcp-memory-server/issues
logo: /logos/mnemoverse.png
version: Haystack 2.0
toc: true
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

[Mnemoverse](https://mnemoverse.com) is hosted persistent memory for AI agents. An agent stores memories, recalls them with a natural-language query, and reports whether a recalled memory helped or misled; that feedback re-ranks what comes back next. Shared rooms let several agents, or several people's assistants, read and write one memory.

This integration doesn't ship its own package. It uses the `MCPToolset` from `mcp-haystack` to start the open-source [`@mnemoverse/mcp-memory-server`](https://github.com/mnemoverse/mcp-memory-server) (MIT) over stdio, which gives a Haystack `Agent` these tools:

| Tool | What it does |
|------|--------------|
| `memory_write` | Store a memory that should persist across sessions: a preference, decision, lesson or project fact |
| `memory_read` | Search memory with a natural-language query before answering or starting a task |
| `memory_list_recent` | List the newest memories first, filtered by domain and time window, without a query |
| `memory_feedback` | Report whether a recalled memory helped, so useful memories rank higher next time |
| `memory_stats` | Show how many memories are stored and which domains exist |
| `memory_graph` | Read the association graph the memory has formed around given concepts |
| `memory_create_room` | Create a shared memory room (beta) |
| `memory_invite_to_room` | Create an invite code for a room you own (beta) |
| `memory_join_room` | Join a shared room with an invite code (beta) |
| `memory_list_rooms` | List the rooms you own or have joined (beta) |
| `vault_list` | List stored secrets by alias and purpose; values are never returned |

The server runs locally through `npx` and calls the hosted Mnemoverse API over HTTPS, so memories persist across runs, processes and machines that use the same account.

## Installation

```bash
pip install mcp-haystack
```

You also need:

- Node.js 18 or newer, because the server is started with `npx`.
- A Mnemoverse API key (it starts with `mk_live_`). The free tier needs no credit card: sign up at [console.mnemoverse.com](https://console.mnemoverse.com/sign-up).

## Usage

Pass the key to the server process through `env`. The MCP Python SDK starts a stdio server with only a short list of inherited variables such as `PATH`, so a key that is set only in your shell does not reach the server.

```python
import os

from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

os.environ["MNEMOVERSE_API_KEY"] = "mk_live_YOUR_KEY"

server_info = StdioServerInfo(
    command="npx",
    args=["-y", "@mnemoverse/mcp-memory-server@latest"],
    env={"MNEMOVERSE_API_KEY": Secret.from_env_var("MNEMOVERSE_API_KEY")},
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

## Examples

The agent below is told to save a team convention in the first run and to search memory for it in the next. Because the memory is stored by the hosted service, the second run can be a new process, or a different machine with the same key.

```python
import os

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

os.environ["MNEMOVERSE_API_KEY"] = "mk_live_YOUR_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

toolset = MCPToolset(
    server_info=StdioServerInfo(
        command="npx",
        args=["-y", "@mnemoverse/mcp-memory-server@latest"],
        env={"MNEMOVERSE_API_KEY": Secret.from_env_var("MNEMOVERSE_API_KEY")},
    ),
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt=(
        "You have long-term memory. Before answering, search it with memory_read. "
        "When the user states a durable fact, preference or decision, save it with memory_write. "
        "After you use a recalled memory, call memory_feedback to say whether it helped."
    ),
)

agent.run(messages=[ChatMessage.from_user(
    "Remember: staging deploys go through make deploy-staging, never through the hosting dashboard."
)])

result = agent.run(messages=[ChatMessage.from_user("How do we deploy to staging?")])
print(result["last_message"].text)
```

More on the server and its tools: [Mnemoverse MCP server docs](https://mnemoverse.com/docs/api/mcp-server).

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

The `@mnemoverse/mcp-memory-server` package is MIT licensed. The Mnemoverse memory service it connects to is a hosted service governed by the [Mnemoverse terms of service](https://mnemoverse.com/terms), separate from the licenses of both client packages. Pricing, including the free tier, is at [mnemoverse.com/pricing](https://mnemoverse.com/pricing).

