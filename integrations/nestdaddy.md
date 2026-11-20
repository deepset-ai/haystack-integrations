---
layout: integration
name: NestDaddy
description: "Live web search, real-time news by topic or country, and the full text of any page for Haystack agents, as MCP tools from NestDaddy's own search index"
authors:
    - name: NestDaddy
      socials:
        github: nestdaddy
        twitter: nestdaddy_api
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/nestdaddy/nestdaddy-examples/issues
logo: /logos/nestdaddy.png
version: Haystack 2.0
toc: true
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Available tools](#available-tools)
- [License](#license)

## Overview

**[NestDaddy](https://nestdaddy.com)** is a web search and real-time news API that runs its own crawler and search index. Its hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://mcp.nestdaddy.com/mcp` gives a Haystack agent current information from the web: search results, news from around the world filtered by topic or country, the clean full text of any page, and research papers.

Use it when your agent has to answer questions about recent events, releases or prices, or when it has to cite its sources.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect any Haystack agent to the NestDaddy MCP server over Streamable HTTP. A free plan with 1,000 credits a month is available.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Create a free API key on the [NestDaddy dashboard](https://nestdaddy.com/dashboard) and set it as an environment variable:

```bash
export NESTDADDY_API_KEY="your-key"
```

The key is sent as an `Authorization: Bearer` header.

### Use the tools directly

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://mcp.nestdaddy.com/mcp",
    token=Secret.from_env_var("NESTDADDY_API_KEY"),
)

# Load only the tools you need to keep the model's context small
toolset = MCPToolset(server_info=server_info, tool_names=["web_search", "news_search", "read_page"])

tools = {tool.name: tool for tool in toolset}
print(tools["web_search"].invoke(query="supabase pricing"))
print(tools["news_search"].invoke(query="AI agents"))
```

### Use with an Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.nestdaddy.com/mcp",
        token=Secret.from_env_var("NESTDADDY_API_KEY"),
    ),
    tool_names=["web_search", "news_search", "read_page"],
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=toolset,
    system_prompt=(
        "Search the web and the news before answering questions about recent events. "
        "Read a page when the snippet is not enough. Cite the URLs you used."
    ),
)

result = agent.run(messages=[ChatMessage.from_user("What happened in AI agents this week? Cite sources.")])
print(result["messages"][-1].text)
```

## Available tools

Tool | Description
---- | -----------
`web_search` | Search the web with NestDaddy's own index: title, URL, snippet and domain of each result
`news_search` | Find news articles by key words, newest and best match first
`news` | Latest news headlines with links and summaries, refreshed every few minutes
`country_news` | Latest local news from one country, by two-letter country code
`read_page` | Read the full text of a web page or news article, without menus or ads
`research_papers` | Search scientific papers from arXiv, PubMed, OpenAlex, CrossRef and more
`ai_tools` | New AI models, apps and open-source projects, updated daily
`software` | Software and developer tools with their current version, updated daily
`games` | Top-selling, new and upcoming games, updated daily

More about the server: [NestDaddy MCP](https://nestdaddy.com/mcp) and the [API docs](https://nestdaddy.com/apis).

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. Use of the NestDaddy API is subject to the [NestDaddy terms](https://nestdaddy.com/terms).
