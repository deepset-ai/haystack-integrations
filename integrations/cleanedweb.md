---
layout: integration
name: CleanedWeb
description: "Give a Haystack agent maintained website APIs: find a catalog API for a site, check its sample records, and run it for structured records through CleanedWeb's MCP server"
authors:
    - name: CleanedWeb
      socials:
        github: cleanedweb
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/cleanedweb/cleanedweb-mcp
type: Tool Integration
report_issue: https://github.com/cleanedweb/cleanedweb-mcp/issues
logo: /logos/cleanedweb.png
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

**[CleanedWeb](https://cleanedweb.com/?utm_source=haystack&utm_medium=integrations)** turns public website collections (search results, listings, category pages) into maintained REST APIs that return structured records with known fields. Its [catalog](https://cleanedweb.com/catalog/?utm_source=haystack&utm_medium=integrations) covers job boards, marketplaces, stores, app and game stores, code hosts and research indexes; each API is health-checked and rebuilt when its site changes, so an agent gets the same fields every run instead of parsing pages.

CleanedWeb runs a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://api.cleanedweb.com/mcp`. This integration doesn't ship its own package: it uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to that server over Streamable HTTP. The main tools:

| Tool | What it does |
| --- | --- |
| `find_api` | Searches the catalog by `site`, `topic` words and the `fields` you need. Each match lists its fields, inputs, recent health and `run_with`, the ready `run_api` call. Nothing runs. |
| `get_api` | Shows one API: coverage, limitations, health, and for each endpoint its fields, inputs and saved sample records. Nothing runs. |
| `run_api` | Runs a catalog endpoint and answers with its records. |
| `request_source` | Asks CleanedWeb to add a site the catalog does not cover. Nothing is charged. |

The server also exposes tools to read past runs and to schedule runs.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Running APIs needs a CleanedWeb API key: [sign up](https://cleanedweb.com/?utm_source=haystack&utm_medium=integrations) and create one on the console's API keys page. New accounts get 5,000 records free; after that, runs are charged per record from prepaid credit ([pricing](https://cleanedweb.com/pricing/?utm_source=haystack&utm_medium=integrations)). Pass the key as a bearer token through `StreamableHttpServerInfo`'s `token` parameter:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://api.cleanedweb.com/mcp?profile=catalog",
    token=Secret.from_env_var("CLEANEDWEB_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(tool.name)
```

To browse the catalog without a key, connect to `?profile=public` and leave out the token. The agent then gets `find_api` and `get_api` only:

```python
toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://api.cleanedweb.com/mcp?profile=public"),
    eager_connect=True,
)
```

## Examples

An agent that finds an API for the request, checks its sample records and runs it with a small `max_items`:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.cleanedweb.com/mcp?profile=catalog",
        token=Secret.from_env_var("CLEANEDWEB_API_KEY"),
    ),
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-5-mini"),
    tools=toolset,
    system_prompt=(
        "Use the CleanedWeb tools: find_api, then get_api to check sample records, "
        "then run_api with a small max_items and an idempotency_key."
    ),
)

result = agent.run(messages=[ChatMessage.from_user(
    "Get the 3 most-starred GitHub repositories under the llm topic, with name, stars and URL."
)])
print(result["messages"][-1].text)
```

The agent calls `find_api` (`site: github.com`, `fields: name, stars, url`), reads the match with `get_api`, then calls `run_api` with the endpoint's input (`topics: llm`, `sort: desc_stars`) and answers from the returned records.

When no catalog API covers a site, `find_api` answers with `next: "request_source"`; the agent can then ask CleanedWeb to add it.

More on the tools and their arguments: [MCP guide](https://cleanedweb.com/docs/mcp/?utm_source=haystack&utm_medium=integrations).

## License

The connection settings and docs in [cleanedweb/cleanedweb-mcp](https://github.com/cleanedweb/cleanedweb-mcp) are MIT licensed. `mcp-haystack` is Apache 2.0. Use of the CleanedWeb service is subject to its [terms](https://cleanedweb.com/legal/terms/?utm_source=haystack&utm_medium=integrations).
