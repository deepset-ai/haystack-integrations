---
layout: integration
name: GridPin
description: "Geocode addresses and reverse geocode coordinates offline from a Haystack agent: GridPin's MCP server answers from one local file per country, with no API key"
authors:
    - name: GridPin
      socials:
        github: gridpin
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/gridpin/gridpin
type: Tool Integration
report_issue: https://github.com/gridpin/gridpin/issues
logo: /logos/gridpin.png
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

**[GridPin](https://gridpin.dev)** is an open-source geocoder that runs on your own machine. Each covered country is a single file: once it is downloaded, forward geocoding (address to coordinates) and reverse geocoding (coordinates to nearby addresses) are answered locally, with no server to run, no API key and no rate limit. The list of covered countries is on [gridpin.dev](https://gridpin.dev).

The [`gridpin-mcp`](https://pypi.org/project/gridpin-mcp/) package exposes GridPin as a local [Model Context Protocol](https://modelcontextprotocol.io/) server over stdio. It has five tools:

| Tool | What it does |
|------|--------------|
| `list_countries` | Covered countries, their file sizes, and which files are already downloaded |
| `download_sheet` | Downloads one country file and checks it against the signed GridPin release. This is the only tool that uses the network |
| `geocode` | Address text to ranked candidates with `lat`, `lon`, `precision` and `confidence` |
| `reverse` | Coordinates to the nearest indexed addresses, each with `distance_m` |
| `batch` | Up to 1000 addresses of one country in one call, in input order |

An address that the file cannot place comes back as an empty result list, not as a guessed location, so an agent can tell a match from a miss. Results with `street` or `city` precision are approximate.

This integration doesn't ship its own package. Instead, it uses `mcp-haystack`'s `MCPToolset` to start `gridpin-mcp` with `uvx` and connect any Haystack agent to it.

## Installation

```bash
pip install mcp-haystack
```

The server is started with `uvx`, which comes with [uv](https://docs.astral.sh/uv/getting-started/installation/); `uvx` fetches `gridpin-mcp` from PyPI on first use. Without uv, run `pip install gridpin-mcp` in the same environment and use `StdioServerInfo(command="gridpin-mcp")` instead.

## Usage

Start the server and list its tools:

```python
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

server_info = StdioServerInfo(command="uvx", args=["gridpin-mcp"])
toolset = MCPToolset(server_info=server_info, invocation_timeout=600.0, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

`invocation_timeout` is raised from its 30-second default because `download_sheet` fetches a whole country file (tens to hundreds of MB) in a single call.

Country files are stored in `~/.cache/gridpin`. To use another directory, pass it in the server environment: `StdioServerInfo(command="uvx", args=["gridpin-mcp"], env={"GRIDPIN_HOME": "/path/to/dir"})`. The MCP client passes only a few variables such as `PATH` and `HOME` to the server, so setting `GRIDPIN_HOME` in `os.environ` of your Python process has no effect.

The tools can also be called directly, without a language model. Each call returns the MCP result as a JSON string; the tool output is under `structuredContent`:

```python
import json

tools = {tool.name: tool for tool in toolset.tools}

# Once per country. This is the only call that uses the network.
tools["download_sheet"].invoke(country="rs")

found = json.loads(tools["geocode"].invoke(query="Knez Mihailova 5, Beograd", country="rs"))
top = found["structuredContent"]["results"][0]
print(top["precision"], top["street"], top["housenumber"], top["lat"], top["lon"])
# house Kneza Mihaila 5 44.8154522 20.4593897

nearby = json.loads(tools["reverse"].invoke(lat=top["lat"], lon=top["lon"], country="rs", k=3))
for hit in nearby["structuredContent"]["results"]:
    print(hit["street"], hit["housenumber"], hit["distance_m"])

missing = json.loads(tools["geocode"].invoke(query="1 rue de la Paix, 75002 Paris", country="rs"))
print(missing["structuredContent"]["results"])
# []

toolset.close()
```

## Examples

The snippet below gives the toolset to a Haystack `Agent`. The system prompt tells the agent to download a country file only when it is missing and to report a miss instead of estimating coordinates:

```python
import os

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

toolset = MCPToolset(
    server_info=StdioServerInfo(command="uvx", args=["gridpin-mcp"]),
    invocation_timeout=600.0,
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="""You geocode addresses with the GridPin tools.
Call list_countries first. If the file for the address's country is not downloaded, call download_sheet once.
If geocode returns an empty result list, say that the address was not found; do not estimate coordinates.
Give the precision with every answer: street- and city-level results are approximate.""",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Geocode 'Knez Mihailova 5, Beograd' and 'Bulevar oslobodjenja 1, Novi Sad', "
            "then tell me the nearest address to 44.8125, 20.4612."
        )
    ]
)

print(result["last_message"].text)
```

For pipelines that do not need an agent, the same engine is available as the `gridpin` Python package, a command-line tool and a DuckDB extension: see the [documentation](https://gridpin.dev/docs).

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

GridPin and `gridpin-mcp` are distributed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The country files are built from open data; their sources and licenses are listed in [ATTRIBUTIONS.md](https://github.com/gridpin/gridpin/blob/main/ATTRIBUTIONS.md).
