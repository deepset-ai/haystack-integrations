---
layout: integration
name: looot
description: "Use looot's hosted MCP server from a Haystack agent: work email, phone, company and people enrichment, Google SERP and web page reading from one key and prepaid balance"
authors:
    - name: looot
      socials:
        github: loootai
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/loootai/looot-mcp
type: Tool Integration
report_issue: https://github.com/loootai/looot-mcp/issues
logo: /logos/looot.png
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

**[looot](https://looot.ai)** is a data API with a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://api.looot.ai/mcp`. One API key and one prepaid balance cover about 2,500 data endpoints from 90+ providers: work email lookup and verification, phone, company and people enrichment, company search, tech stack, Google SERP, web search, news, web page reading, LinkedIn profiles and local business search. The agent sees the price before a call, and a failed call costs nothing.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the looot MCP server over Streamable HTTP. looot is paid: you top up a prepaid balance from $5, with no subscription and no free tier. Docs are at [docs.looot.ai](https://docs.looot.ai).

## Installation

```bash
pip install mcp-haystack
```

## Usage

The looot MCP server accepts browser-based OAuth for clients that support it, and an API key sent as `Authorization: Bearer <key>` for headless frameworks like Haystack. Create a key in the looot dashboard and pass it through `StreamableHttpServerInfo`'s `token` parameter:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret
import os

os.environ["LOOOT_API_KEY"] = "YOUR_LOOOT_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://api.looot.ai/mcp",
    token=Secret.from_env_var("LOOOT_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

The toolset lists the tools the server exposes when you connect, so the list stays current as looot adds endpoints.

## Examples

The snippet below gives a Haystack `Agent` the looot toolset and asks it a lookup question:

```python
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret
import os

os.environ["LOOOT_API_KEY"] = "YOUR_LOOOT_API_KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR_ANTHROPIC_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://api.looot.ai/mcp",
    token=Secret.from_env_var("LOOOT_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

agent = Agent(
    chat_generator=AnthropicChatGenerator(model="claude-opus-4-6"),
    tools=toolset,
    system_prompt="You are a research assistant. Use the looot tools to look up companies, people and web pages, and say what each lookup cost.",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Find the tech stack of deepset.ai and the top Google results for 'Haystack framework'."
        )
    ]
)

print(result["last_message"].text)
```

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

The [looot MCP bridge](https://github.com/loootai/looot-mcp) is MIT licensed. looot itself is a hosted service governed by looot's terms of service, separate from the license of the `mcp-haystack` client used to connect to it.
