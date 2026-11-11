---
layout: integration
name: MemorySync
description: Connect a Haystack agent to MemorySync's hosted MCP memory server to search and store durable facts, preferences and decisions
authors:
    - name: MemorySync
      socials:
        github: memorysyncio
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/memorysyncio/memorysync-plugins
type: Tool Integration
report_issue: https://github.com/memorysyncio/memorysync-plugins/issues
logo: /logos/memorysync.png
version: Haystack 2.0
toc: true
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[MemorySync](https://memorysync.io) provides API and SDK infrastructure for storing, retrieving, updating, deleting, governing, and inspecting memory used by AI applications.

MemorySync runs two hosted Model Context Protocol servers. The memory server at `https://mcp.memorysync.io/mcp` exposes 15 tools, 4 resources and 2 prompts; the documentation server at `https://docs.memorysync.io/mcp` gives a coding agent the current documentation. Both are hosted and speak Streamable HTTP, so there is no local process to install, keep running or upgrade.

Memory tools include:

| Tool | What it does |
| --- | --- |
| `search_memory` | Ranked memories with a relevance score for a query. |
| `list_memories` | Memories newest first. |
| `get_related_memories` | Connected memories with the edge type, direction and confidence. |
| `add_memory` | Stores text through the same extraction pipeline as the REST API; returns the new memory ids, or skipped when nothing was worth keeping. |
| `delete_memory` | Deletes memories by id, up to 100 per call. |
| `whoami` | How this client authenticated, its granted scopes and whether it may write or delete. |

See [Memory tools](https://docs.memorysync.io/mcp/tools) for the full list. This integration does not ship its own package: it uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the MemorySync memory server.

## Prerequisites

Browser sign-in needs a browser, so for a server-side Haystack agent use an API key: the MemorySync memory server accepts a MemorySync API key as a bearer token or in the `X-API-Key` header. Get an API key from the [dashboard](https://app.memorysync.io/dashboard) and keep it server-side.

API-key calls are scoped to one end user: send a stable, opaque end-user ID (not an email address) in the `X-End-User-ID` header, resolved from your own authenticated session. Two agents that use the same key and end-user ID read and write the same memories. See [Authentication](https://docs.memorysync.io/api/authentication).

```bash
export MEMORYSYNC_API_KEY="your-memorysync-api-key"
```

## Installation

```bash
pip install mcp-haystack
```

## Usage

### Connect and discover the memory tools

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://mcp.memorysync.io/mcp",
    headers={
        "X-API-Key": Secret.from_env_var("MEMORYSYNC_API_KEY"),
        "X-End-User-ID": "usr_7f3a9c2e",  # stable opaque ID for the end user whose memory this agent uses
    },
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

### Use MemorySync memory in a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.memorysync.io/mcp",
        headers={
            "X-API-Key": Secret.from_env_var("MEMORYSYNC_API_KEY"),
            "X-End-User-ID": "usr_7f3a9c2e",
        },
    ),
    tool_names=["search_memory", "add_memory"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=toolset,
    system_prompt=(
        "Call search_memory before answering. "
        "Call add_memory when the user states a lasting preference, fact or decision."
    ),
)

agent.run(messages=[ChatMessage.from_user("Remember that I prefer concise answers.")])
result = agent.run(messages=[ChatMessage.from_user("How should you format answers for me?")])
print(result["messages"][-1].text)
```

## License

`mcp-haystack` is licensed under Apache-2.0. The MemorySync client plugins in [memorysyncio/memorysync-plugins](https://github.com/memorysyncio/memorysync-plugins) are MIT licensed. MemorySync itself is a hosted, closed-source service.
