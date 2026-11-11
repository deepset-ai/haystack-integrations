---
layout: integration
name: CoworkingView
description: Search coworking spaces and query flexible-office market rates through the hosted CoworkingView MCP server
authors:
    - name: CoworkingView
      socials:
        github: coworkingview
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/coworkingview/coworkingview-mcp/issues
logo: /logos/coworkingview.png
version: Haystack 2.0
toc: true
mcp: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

[CoworkingView](https://coworkingview.com) is a directory and price index for coworking spaces, flex desks and private offices, currently covering cities in Germany, Spain, the United Kingdom, the Netherlands and the United Arab Emirates. The [CoworkingView MCP server](https://coworkingview.com/en/mcp) is a hosted, read-only [Model Context Protocol](https://modelcontextprotocol.io) server at `https://mcp.coworkingview.com/mcp` (Streamable HTTP). It needs no API key.

With the `mcp-haystack` integration you can load its tools into a Haystack `Agent` or `ToolInvoker`:

| Tool | What it does |
|------|--------------|
| `search_coworking_spaces` | Search spaces by city, zone, country, operator, workspace type, amenities, price or coordinates |
| `get_coworking_space` | Details for one space by slug |
| `compare_coworking_spaces` | Side-by-side comparison of several spaces |
| `get_coworking_market_rates` | Median, quartile and min/max monthly prices for flex desks, fixed desks and private offices, plus day pass and meeting room rates |
| `resolve_coworking_query` | Turn a free-text query into a city, zone or operator |
| `list_coworking_locations` | Countries and cities that are covered, with their slugs |
| `get_coworking_filter_options` | Available filter values for a location |
| `get_coworking_operator` | Operator profile and locations |
| `get_coworking_place_guide` | City or zone guide |
| `get_coworking_public_holidays` | Public holidays for a country or region |

The server source and snippets for other clients are in the [coworkingview-mcp](https://github.com/coworkingview/coworkingview-mcp) repository.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Connect to the server and list its tools:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://mcp.coworkingview.com/mcp")
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(tool.name)
```

Call a single tool directly with `MCPTool`:

```python
from haystack_integrations.tools.mcp import MCPTool, StreamableHttpServerInfo

rates = MCPTool(
    name="get_coworking_market_rates",
    server_info=StreamableHttpServerInfo(url="https://mcp.coworkingview.com/mcp"),
)
print(rates.invoke(city="berlin", locale="en"))
```

To expose only some tools to an LLM, pass `tool_names`:

```python
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["search_coworking_spaces", "get_coworking_market_rates"],
)
```

## Examples

An `Agent` that answers questions about coworking prices and spaces. This example uses `OpenAIChatGenerator`, so set `OPENAI_API_KEY`; any chat generator with tool calling support works.

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://mcp.coworkingview.com/mcp"),
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=toolset,
    system_prompt="You help people find coworking spaces. Use the tools and always state prices with their currency.",
)

result = agent.run(
    messages=[ChatMessage.from_user("What does a flex desk cost per month in Berlin, and which spaces are under 250 EUR?")]
)
print(result["messages"][-1].text)
```

## License

`mcp-haystack` is distributed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The CoworkingView MCP server is a free hosted service; aggregated market rate data is published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) with attribution to CoworkingView.
