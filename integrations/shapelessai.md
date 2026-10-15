---
layout: integration
name: ShapelessAI
description: "Give a Haystack agent a social media team: list connected accounts, draft, schedule and publish posts to LinkedIn, X, Instagram, TikTok, YouTube, Facebook, Threads and Bluesky, and generate the images and video for them, through the ShapelessAI MCP server"
authors:
    - name: ShapelessAI
      socials:
        github: FirstClassTree
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/FirstClassTree/shapelessai
type: Tool Integration
report_issue: https://github.com/FirstClassTree/shapelessai/issues
logo: /logos/shapelessai.png
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

**[ShapelessAI](https://shapelessai.com)** is an agentic social media team with a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://shapelessai.com/mcp`. Connected to a Haystack agent, it lets the agent read the social accounts you connected, draft posts for your approval, schedule them into each account's next free queue slot or publish them now, and make the media that goes with them (images, carousels, narrated short video, thumbnails). It publishes to LinkedIn (profiles and Pages), X, Instagram, TikTok, YouTube, Facebook, Threads and Bluesky, and checks each network's limits before a post leaves.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the ShapelessAI MCP server over Streamable HTTP. The server describes its tools at connect time, so the snippets below discover them instead of hardcoding a list. The API, CLI and MCP server are on the Free plan (no card); see the [API docs](https://shapelessai.com/docs/api) and [MCP docs](https://shapelessai.com/docs/mcp).

## Installation

```bash
pip install mcp-haystack
```

## Usage

The server takes an interactive OAuth sign-in for clients that speak remote MCP natively, and a ShapelessAI API key passed as an `Authorization: Bearer` header for headless frameworks like Haystack. Create a key at [shapelessai.com/studio/api-keys](https://shapelessai.com/studio/api-keys) after signing in, and pass it through `StreamableHttpServerInfo`'s `token` parameter:

```python
import os

from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["SHAPELESSAI_API_KEY"] = "YOUR_SHAPELESSAI_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://shapelessai.com/mcp",
    token=Secret.from_env_var("SHAPELESSAI_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description[:80]}")
```

To give the agent only part of the server, pass `tool_names`, for example `tool_names=["connections_list", "posts_list", "posts_create"]`.

## Examples

The snippet below connects the toolset to a Haystack `Agent` and asks it what is connected and what is already scheduled, which only reads the account:

```python
import os

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["SHAPELESSAI_API_KEY"] = "YOUR_SHAPELESSAI_API_KEY"

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://shapelessai.com/mcp",
        token=Secret.from_env_var("SHAPELESSAI_API_KEY"),
    ),
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="You manage the user's social media through the ShapelessAI tools. "
    "Draft posts for approval unless the user asks you to publish now.",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Which social accounts are connected, and what is scheduled to go out this week?"
        )
    ]
)
print(result["last_message"].text)
```

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

ShapelessAI is a hosted service governed by [ShapelessAI's terms](https://shapelessai.com/terms), separate from the license of the `mcp-haystack` client used to connect to it.
