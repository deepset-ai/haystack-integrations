---
layout: integration
name: Equibles
description: US stock research via MCP - search SEC filings and read financial statements, earnings call transcripts, insider trades and 13F holdings from a Haystack agent.
authors:
    - name: Equibles
      socials:
        github: daniel3303
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/daniel3303/stock-market-mcp-server
type: Tool Integration
report_issue: https://github.com/daniel3303/stock-market-mcp-server/issues
logo: /logos/equibles.png
version: Haystack 2.0
toc: true
mcp: true
---

**Table of Contents**

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Connecting to Equibles](#connecting-to-equibles)
  - [Researching a Stock with an Agent](#researching-a-stock-with-an-agent)
  - [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

[Equibles](https://equibles.com) serves US stock market data through a hosted [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server at `https://mcp.equibles.com/mcp`. Its tools search and read SEC filings and earnings call transcripts, return financial statements built from SEC XBRL data, and look up insider transactions, 13F institutional holdings, congressional trades, short interest and daily prices. Results name the filing or source each figure comes from.

The server exposes over 100 tools. Commonly used ones include:

| Tool | Description |
|------|-------------|
| `SearchDocuments` | Search SEC filings and earnings call transcripts across every company or for one ticker |
| `ReadDocumentLines` | Read numbered lines from one filing or transcript |
| `GetFinancialStatement` | Get an income statement, balance sheet or cash-flow statement from SEC XBRL data |
| `GetFinancialFact` | Get one financial concept, such as revenue or diluted EPS, over time |
| `GetEarningsCallTranscript` | Get a speaker-labelled earnings call transcript for a fiscal quarter |
| `GetInsiderTransactions` | Get insider transactions from SEC Forms 4 and 5 |
| `GetTopHolders` | Get the largest institutional holders of a stock from 13F filings |
| `GetCongressionalTrades` | Get securities transactions reported by members of Congress for a ticker |
| `GetStockPrices` | Get daily price history (open, high, low, close and volume) |

The [tools reference](https://equibles.com/docs/mcp/tools) lists every tool. Most tools only read data. The portfolio, watchlist and feedback tools (`CreateMyPortfolio`, `DeleteMyPortfolio`, `AddPortfolioLot`, `UpdatePortfolioLot`, `ClosePortfolioLot`, `RemovePortfolioLot`, `WatchInstrument`, `UnwatchInstrument`, `ReportProblem` and `SuggestToolImprovement`) write to the Equibles account that owns the API key, so leave them out of `tool_names` unless the agent should manage that account.

This integration does not require a separate Equibles Python package. It uses the existing `mcp-haystack` package to connect to the Equibles MCP server and discover its tools.

## Prerequisites

1. Create an Equibles account at [equibles.com](https://equibles.com) and generate an API key, as described in [Authentication](https://equibles.com/docs/authentication). The key starts with `eq_` and is shown once. The free plan allows 100 requests a day.
2. Set the required environment variable:

```bash
export EQUIBLES_API_KEY="eq_your_api_key"
```

## Installation

```bash
pip install mcp-haystack
```

## Usage

### Connecting to Equibles

Use `StreamableHttpServerInfo` to point to the Equibles MCP server and `MCPToolset` to connect and fetch the tools. The `token` is sent as an `Authorization: Bearer` header, and `tool_names` limits the toolset to the tools your agent needs, which keeps the tool definitions sent to the model short:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret

server_info = StreamableHttpServerInfo(
    url="https://mcp.equibles.com/mcp",
    token=Secret.from_env_var("EQUIBLES_API_KEY"),
)
toolset = MCPToolset(
    server_info=server_info,
    tool_names=[
        "SearchDocuments",
        "ReadDocumentLines",
        "GetFinancialStatement",
        "GetEarningsCallTranscript",
        "GetInsiderTransactions",
        "GetTopHolders",
    ],
    eager_connect=True,
)
```

`eager_connect=True` causes the toolset to immediately connect and fetch the tool definitions from the server. Leave out `tool_names` to load every tool.

### Researching a Stock with an Agent

The following example sets up a Haystack `Agent` that answers a question about institutional ownership. It uses `OpenAIChatGenerator`, so it also needs an `OPENAI_API_KEY` environment variable; any chat generator that supports tools works the same way.

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.equibles.com/mcp",
        token=Secret.from_env_var("EQUIBLES_API_KEY"),
    ),
    tool_names=[
        "SearchDocuments",
        "ReadDocumentLines",
        "GetFinancialStatement",
        "GetEarningsCallTranscript",
        "GetInsiderTransactions",
        "GetTopHolders",
    ],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(tools=toolset),
    tools=toolset,
    system_prompt=(
        "You are a stock research assistant. Use the Equibles tools to answer "
        "questions from SEC filings, financial statements, earnings calls and "
        "ownership data, and cite the source of each figure."
    ),
)

output = agent.run(messages=[
    ChatMessage.from_user(
        "Who are NVIDIA's three largest institutional holders, and as of which quarter?"
    )
])
print(output["last_message"].text)
```

For this question the agent calls `GetTopHolders`, which returns a table of holders with share counts, position values and the 13F report date. Questions about filings use `SearchDocuments` to find the relevant passage and `ReadDocumentLines` to read it in full.

### Troubleshooting

- **Tools load but every call raises `ToolInvocationError`**: listing tools works without a key, but calling one needs it. Check that `EQUIBLES_API_KEY` is set and not empty in the environment that runs the agent.
- **Connecting fails with a 401**: the server rejected the key. Check that the variable holds the full key you copied when you created it, not the shortened prefix the dashboard lists later, and that the key hasn't been deleted.

## License

The `mcp-haystack` package is distributed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The [client configuration repository](https://github.com/daniel3303/stock-market-mcp-server) is MIT. Use of the Equibles service is subject to the [Equibles terms of service](https://equibles.com/legal/terms).
