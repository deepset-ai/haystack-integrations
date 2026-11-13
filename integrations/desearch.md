---
layout: integration
name: Desearch
description: Use Desearch web, X and AI search tools in Haystack through the Desearch MCP server
authors:
    - name: Desearch
      socials:
        github: Desearch-ai
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/Desearch-ai/mcp-desearch
type: Tool Integration
report_issue: https://github.com/Desearch-ai/mcp-desearch/issues
logo: /logos/desearch.png
version: Haystack 2.0
toc: true
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Desearch](https://www.desearch.ai) provides AI search, X search and web search for AI agents, plus page extraction and X data tools. Its hosted MCP server at `https://mcp.desearch.ai/mcp` exposes these as 22 tools, for example `web-search`, `ai-search`, `x-search`, `extract` and `x-trends`.

With the [MCP Haystack integration](https://haystack.deepset.ai/integrations/mcp), you can use these tools in Haystack pipelines and agents with `MCPTool` or `MCPToolset`. You need a Desearch API key, set as the `DESEARCH_API_KEY` environment variable.

## Installation

```bash
pip install mcp-haystack
```

`mcp-haystack` requires Python 3.11 or later.

## Usage

### Components
This integration uses the MCP Haystack components:

- `MCPTool`: wraps one Desearch tool, such as `web-search`.
- `MCPToolset`: loads all Desearch tools from the server at once.

### Run a Desearch web search

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPTool, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://mcp.desearch.ai/mcp",
    token=Secret.from_env_var("DESEARCH_API_KEY"),
)

tool = MCPTool(name="web-search", server_info=server_info, eager_connect=True)
print(tool.parameters["properties"].keys())

result = tool.invoke(query="Haystack MCP integration")
print(str(result)[:200])
```

`eager_connect=True` connects at creation, so the tool's parameters are loaded before the first call.

### License

The Desearch MCP server is released under the MIT license.
