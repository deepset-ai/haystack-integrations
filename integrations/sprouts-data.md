---
layout: integration
name: Sprouts Data
description: "Give a Haystack agent B2B company and people data: search about 45.7M companies and 204M people in plain English, find look-alike companies, look up records and map relationships, over the hosted Sprouts Data MCP server"
authors:
    - name: Sprouts Data
      socials:
        github: Sprouts-Data
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
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

**[Sprouts Data](https://sproutsdata.ai)** is a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://dashboard.sproutsdata.ai/mcp` that gives AI agents access to the Sprouts business-data index: about 45.7 million companies, 204 million people and 328 million person-to-company affiliations, plus patents, news, job openings and funding rounds.

The server exposes 12 tools. The main ones:

| Tool | What it does |
|---|---|
| `sprouts_search` | Finds companies, people, news, patents, job openings and other records that match a plain-English description |
| `sprouts_similar` | Finds companies that resemble 1 to 10 example companies you name, ideally by domain |
| `sprouts_entity_lookup` | Returns full records for domains, LinkedIn URLs or record IDs you already have, and charges only for records it finds |
| `sprouts_relationships` | Answers two-sided questions about how companies or people are connected |
| `sprouts_org_chart` | Shows how one company's headcount is spread across teams and levels |
| `sprouts_research_run` | Runs a multi-step research job in the background, states the price first, and charges only if it succeeds |
| `sprouts_coverage` | Lists what the index holds and its known gaps, free of charge |

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the Sprouts Data server over Streamable HTTP.

Billing uses prepaid Sprouts credits, and every billed response reports its cost. Test API keys (`sk_dsp_test_`) search the same data at zero credit cost, and new workspaces get 1,000 free credits.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Create an API key in the [Sprouts dashboard](https://dashboard.sproutsdata.ai) under API Keys. Use a `sk_dsp_test_` key while you're building. Sprouts reads the key from the `X-API-Key` header, which you pass through `StreamableHttpServerInfo`'s `headers` parameter:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret
import os

os.environ["SPROUTS_API_KEY"] = "sk_dsp_test_YOUR_KEY"

server_info = StreamableHttpServerInfo(
    url="https://dashboard.sproutsdata.ai/mcp",
    headers={"X-API-Key": Secret.from_env_var("SPROUTS_API_KEY")},
)
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["sprouts_search", "sprouts_similar", "sprouts_entity_lookup", "sprouts_coverage"],
    eager_connect=True,
)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

`tool_names` keeps the agent to the tools it needs. Leave it out to load all 12.

## Examples

The snippet below gives the toolset to a Haystack `Agent` and asks for companies matching a description:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret
import os

os.environ["SPROUTS_API_KEY"] = "sk_dsp_test_YOUR_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://dashboard.sproutsdata.ai/mcp",
    headers={"X-API-Key": Secret.from_env_var("SPROUTS_API_KEY")},
)
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["sprouts_search", "sprouts_similar", "sprouts_coverage"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="You answer questions about companies and people using the Sprouts Data tools. Say when a total is an estimate.",
)

result = agent.run(
    messages=[ChatMessage.from_user("Find 5 fintech companies in Berlin, then 3 companies similar to the first one.")]
)

print(result["last_message"].text)
```

To check what the index covers before you search, ask the agent "What does Sprouts have coverage of?". That call is free.

The rate limit is 60 tool calls per minute per key. A `401 auth.invalid_key` means the key is unknown, revoked or expired.

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

Sprouts Data is a hosted service provided by Sprouts Inc. and is governed by the [Sprouts Data terms](https://sproutsdata.ai/terms), separate from the license of the `mcp-haystack` client used to connect to it.
