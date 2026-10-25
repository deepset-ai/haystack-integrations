---
layout: integration
name: String Web Access
description: Search the web, fetch any URL and map a site as clean, LLM-ready Markdown.
authors:
    - name: String
      socials:
        github: usestring
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/usestring/string-ai-mcp/issues
logo: /logos/string-web-access.svg
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

**[String Web Access](https://usestring.ai)** lets an agent read the live web. Search the web, fetch any URL
or send it a request, and map a site's URLs — all returned as clean, LLM-ready Markdown.

It is exposed as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at
`https://mcp.usestring.ai/v3/mcp`, over Streamable HTTP.

This integration does not ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack
agent or pipeline to that server, so the toolset is discovered at connect time. The `/v3` tool set is fixed:
String adds new tools on a new endpoint rather than changing this one, so the table below stays accurate.

| Tool | What it does |
| --- | --- |
| `web_access_search` | Search the web and return structured organic results. |
| `web_access_fetch` | Fetch a URL with a `GET` as Markdown, the raw body, or a JSON envelope with status and headers. Changes nothing on the destination. |
| `web_access_request` | Send a `POST`, `PUT` or `PATCH` with a body to a URL — for GraphQL queries and JSON APIs that refuse `GET`. |
| `web_access_sitemap_quote` | Quote a crawl of one site. Creates a job waiting for approval and crawls nothing. |
| `web_access_sitemap_start` | Start a quoted crawl. This is the step that spends your balance. |
| `web_access_sitemap_status` | Check a crawl's progress and, once it has ended, page through the URLs it found. |

Every tool carries MCP annotations saying whether it only reads, and the
[`/v3` reference](https://portal.usestring.ai/docs/mcp/v3) lists each tool's inputs, outputs and billing.

## Installation

```bash
pip install mcp-haystack
```

## Usage

String Web Access supports two ways to authenticate: browser-based OAuth for clients that speak remote MCP
natively, and a static API key sent as an `Authorization: Bearer` header for headless frameworks like Haystack.
Get an API key at [usestring.ai](https://usestring.ai) and pass it through `StreamableHttpServerInfo`'s `token`
parameter, which builds that header for you:

```python
import os

from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["STRING_API_KEY"] = "YOUR_STRING_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://mcp.usestring.ai/v3/mcp",
    token=Secret.from_env_var("STRING_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

Pass `tool_names` to narrow the toolset to the tools a given agent should have — for a read-only research
agent, keep it to search and fetch:

```python
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["web_access_search", "web_access_fetch"],
)
```

## Examples

### Fetch a page as Markdown

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPTool, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://mcp.usestring.ai/v3/mcp",
    token=Secret.from_env_var("STRING_API_KEY"),
)

fetch = MCPTool(name="web_access_fetch", server_info=server_info)
result = fetch.invoke(url="https://example.com")

print(result)
```

### Give an Agent the web

`MCPToolset` is a Haystack `Toolset`, so it goes straight into an `Agent`. The agent picks the right String
tool for each step — searching first, then fetching the pages worth reading.

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.usestring.ai/v3/mcp",
        token=Secret.from_env_var("STRING_API_KEY"),
    ),
    tool_names=["web_access_search", "web_access_fetch"],
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-5-mini"),
    tools=toolset,
    system_prompt=(
        "You research questions using the live web. Search first, then fetch the pages "
        "worth reading, and cite every URL you used."
    ),
)

result = agent.run(
    messages=[ChatMessage.from_user("What does String Web Access charge per search?")]
)
print(result["messages"][-1].text)
```

`tool_names` limits this agent to searching and fetching. `web_access_request` sends `POST`, `PUT` and `PATCH`
requests that can change data on the target site, and `web_access_sitemap_start` spends your balance on a crawl,
so give those only to an agent that is meant to use them.

## License

`mcp-haystack` is distributed under the terms of the
[Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
The String Web Access API is a commercial service; see [usestring.ai](https://usestring.ai) for its terms.
