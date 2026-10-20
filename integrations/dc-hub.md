---
layout: integration
name: DC Hub
description: "DC Hub is the live data layer for data-center site selection. Its Data Center Power Index (DCPI) is a daily score of where data centers can get grid power, across 300+ markets."
authors:
    - name: DC Hub
      socials:
        github: azmartone67
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/azmartone67/dchub-mcp-server
type: Tool Integration
report_issue: https://github.com/azmartone67/dchub-mcp-server/issues
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

**[DC Hub](https://dchub.cloud)** is the live data layer for data-center site selection. Its Data Center Power Index (DCPI) is a daily score of where data centers can get grid power, across 300+ markets. It also carries live grid feeds from the seven US ISOs (PJM, ERCOT, CAISO, MISO, SPP, NYISO, ISO-NE), interconnection queues, electricity and gas prices, fiber and site-level risk. Every answer carries an as-of date and a citation line, so an agent can quote it.

DC Hub is a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://dchub.cloud/mcp` (Streamable HTTP), listed in the official MCP Registry as `cloud.dchub/mcp-server`. This integration doesn't ship its own package: it uses `mcp-haystack`'s `MCPToolset` to connect any Haystack agent to the server. The free tier needs no key.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Connect keyless and list the live tools. DC Hub adds tools as it ships them, so discover them at connect time rather than hardcoding a list:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://dchub.cloud/mcp")
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description[:80]}")
```

If you have a DC Hub key, pass it as a header:

```python
from haystack.utils import Secret

server_info = StreamableHttpServerInfo(
    url="https://dchub.cloud/mcp",
    headers={"X-API-Key": Secret.from_env_var("DCHUB_API_KEY")},
)
```

## Examples

Give an agent a small set of read-only siting tools and ask a power-availability question:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://dchub.cloud/mcp"),
    tool_names=["rank_markets", "get_market_dcpi_rank", "get_grid_intelligence", "analyze_site"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=toolset,
    system_prompt=(
        "You answer data-center siting questions with DC Hub tools. "
        "Call a tool before answering and cite figures with the as-of date DC Hub returns."
    ),
)

result = agent.run(
    messages=[ChatMessage.from_user("Where can a 100 MW data center get grid power fastest in the US? Give the top 3 markets.")]
)
print(result["last_message"].text)
```

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The DC Hub MCP server repository is MIT-licensed; DC Hub data is CC-BY-4.0 (cite as "DC Hub, dchub.cloud").
