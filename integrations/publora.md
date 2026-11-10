---
layout: integration
name: Publora
description: "Let a Haystack agent draft, schedule and publish social media posts to LinkedIn, X, Instagram, Threads, TikTok, YouTube, Facebook, Bluesky, Mastodon and Telegram through Publora's hosted MCP server"
authors:
    - name: Publora
      socials:
        github: publora
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/publora.svg
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

**[Publora](https://publora.com)** publishes and schedules social media posts. It exposes its API as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://mcp.publora.com/mcp`, so a Haystack agent can write a post and send it to LinkedIn, X, Instagram, Threads, TikTok, YouTube, Facebook, Bluesky, Mastodon or Telegram at the time you pick.

The tools cover the connected social accounts, posts (create, schedule, list, update, delete), media uploads, post and profile stats for Bluesky and Mastodon, and LinkedIn comments, reactions and reshares. A post created without a scheduled time stays a draft and is never published, so the agent can write freely and a person can approve before anything goes out. Instagram, TikTok and YouTube need an image or video attached.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the Publora MCP server over Streamable HTTP. You need a Publora account with at least one social account connected in the Publora dashboard; the free Starter plan includes API and MCP access, 3 social accounts and 15 posts a month on every network except X.

## Installation

```bash
pip install mcp-haystack
```

## Usage

The Publora MCP server supports two ways to authenticate: interactive browser OAuth (for clients that speak remote MCP natively), and a Publora API key sent as an `Authorization: Bearer` header (for headless frameworks like Haystack). Create an API key in the Publora dashboard under **Settings → API Keys** and pass it through `StreamableHttpServerInfo`'s `token` parameter:

```python
import os
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["PUBLORA_API_KEY"] = "sk_..."

server_info = StreamableHttpServerInfo(
    url="https://mcp.publora.com/mcp",
    token=Secret.from_env_var("PUBLORA_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

To load only the personal publishing tools, pass `tool_names`:

```python
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["list_connections", "create_post", "list_posts", "get_post", "update_post"],
    eager_connect=True,
)
```

## Examples

The agent below drafts a LinkedIn post and keeps it as a draft, then lists what is already scheduled. Because the post is created without a time, nothing is published.

```python
import os
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["PUBLORA_API_KEY"] = "sk_..."
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.publora.com/mcp",
        token=Secret.from_env_var("PUBLORA_API_KEY"),
    ),
    tool_names=["list_connections", "create_post", "list_posts"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="""You manage social media posts through Publora.
Before creating a post, call list_connections and use the platformId values it returns exactly as given.
Create posts without a scheduled time unless the user asks for one, so they stay drafts for review.""",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Write a short LinkedIn post announcing our new pricing page and save it as a draft. "
            "Then tell me what is scheduled for next week."
        )
    ]
)

print(result["last_message"].text)
```

To schedule instead of drafting, ask for a time ("schedule it for Tuesday at 9:00 UTC"); the agent passes an ISO 8601 UTC timestamp to `create_post`.

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

Publora's MCP server is a hosted service provided by Publora and is governed by [Publora's terms of service](https://publora.com/terms), separate from the license of the `mcp-haystack` client used to connect to it.
