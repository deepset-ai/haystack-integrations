---
layout: integration
name: Bowmark
description: "Give a Haystack agent typed functions for live websites through Bowmark's hosted MCP server: search stores, read listings, compare fares, pull profiles and posts"
authors:
    - name: Bowmark AI
      socials:
        github: bowmark-ai
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/bowmark.svg
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

**[Bowmark](https://bowmark.ai)** gives agents a library of typed functions for live websites: search a store, read a listing, compare fares, pull a profile or a video's details. It is exposed as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://api.bowmark.ai/mcp`.

The agent looks up the functions it needs with the `get_library` tool, then calls them from a short JavaScript script with the `run` tool. One `run` can call several sites at once and return one combined result. Results come back as structured data, and each function is tested against the live site on a schedule. Sites that need a login work through a connection the user saves once in Bowmark.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect any Haystack agent to the Bowmark MCP server over Streamable HTTP.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Create an API key at [bowmark.ai](https://bowmark.ai) and pass it as a Bearer token through `StreamableHttpServerInfo`'s `token` parameter:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://api.bowmark.ai/mcp",
    token=Secret.from_env_var("BOWMARK_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description[:80]}")
```

To give the agent only the two core tools, pass `tool_names=["get_library", "run"]`.

## Examples

Connect the toolset to a Haystack `Agent` and ask about a live site:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.bowmark.ai/mcp",
        token=Secret.from_env_var("BOWMARK_API_KEY"),
    ),
    tool_names=["get_library", "run"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="Use Bowmark's tools: call get_library to find functions for the site, then run a short script.",
)

result = agent.run(messages=[ChatMessage.from_user("What are the top 3 stories on Hacker News right now?")])
print(result["messages"][-1].text)

toolset.close()
```

The agent calls `get_library` to find the Hacker News functions, then `run` to read the front page, and answers with the current titles, points and comment links.

## License

`mcp-haystack` is licensed under Apache 2.0. Bowmark is a hosted service; see [bowmark.ai](https://bowmark.ai) for its terms.
