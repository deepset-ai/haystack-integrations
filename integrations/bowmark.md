---
layout: integration
name: Bowmark
description: "Give a Haystack agent typed functions for live websites through Bowmark's MCP server: search, check prices and availability, get quotes, and read pages, with structured data back and no browser to drive"
authors:
    - name: Bowmark AI
      socials:
        github: bowmark-ai
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/bowmark-ai/skill
type: Tool Integration
report_issue: mailto:support@bowmark.ai
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

**[Bowmark](https://bowmark.ai)** turns websites into typed functions an AI agent can call. The agent asks Bowmark's library what functions exist for a task (flights, product prices, a site's search, a quote form), writes a short JavaScript script against them, and Bowmark runs that script on the live sites and returns structured data. The agent never drives a browser itself.

Bowmark is a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://api.bowmark.ai/mcp`. Two tools do the work:

- `get_library`: read-only. Pass what you want to do, or a site name, and get back the matching functions with their TypeScript types and examples.
- `run`: execute a script written against those functions and get back `{ ok, result, logs, error }`.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the Bowmark MCP server over Streamable HTTP.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Create an API key in the [Bowmark dashboard](https://bowmark.ai), then pass it as a bearer token through `StreamableHttpServerInfo`'s `token` parameter:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
import os

os.environ["BOWMARK_API_KEY"] = "YOUR_BOWMARK_API_KEY"

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.bowmark.ai/mcp",
        token=Secret.from_env_var("BOWMARK_API_KEY"),
    ),
    tool_names=["get_library", "run"],
    eager_connect=True,
)

for tool in toolset.tools:
    print(tool.name)
```

## Examples

An agent that looks up the functions it needs, writes a script, and answers from the live result:

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
    system_prompt=(
        "You can act on live websites through Bowmark. Call get_library with what the user "
        "wants to do, then write a short script against the functions it returns and execute "
        "it with run. Answer from the run's result."
    ),
)

result = agent.run(
    messages=[ChatMessage.from_user("What is the current top story on Hacker News? Give its title and points.")]
)
print(result["last_message"].text)
```

## License

The Bowmark client and skill are MIT licensed: [bowmark-ai/skill](https://github.com/bowmark-ai/skill). `mcp-haystack` is Apache 2.0.
