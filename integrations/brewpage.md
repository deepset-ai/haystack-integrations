---
layout: integration
name: BrewPage
description: Publish HTML, Markdown, files, JSON and key-value data from Haystack and get a shareable HTTPS link, through BrewPage's remote MCP server
authors:
    - name: Maksim Kochetkov
      socials:
        github: kochetkov-ma
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/kochetkov-ma/brewpage-openapi
type: Tool Integration
report_issue: https://github.com/kochetkov-ma/brewpage-openapi/issues
logo: /logos/brewpage.svg
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

[BrewPage](https://brewpage.app) is a free hosting service for HTML pages, Markdown documents, small static sites, files, JSON documents and key-value data. A publish call returns an HTTPS link and an owner token; the owner token updates the content in place at the same URL or deletes it. No account or API key is needed.

Connect Haystack to `https://brewpage.app/mcp` over Streamable HTTP. BrewPage MCP 3.0.0 exposes 13 tools, including `publish`, `update_publication` and `delete_publication`. The hosted endpoint supports anonymous publishing and optional OAuth for a BrewPage profile. [Server source and tool reference](https://github.com/kochetkov-ma/brewpage-openapi/tree/main/mcp-server#tools)

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect Haystack to the BrewPage MCP server, for example so a pipeline or agent can publish the report it generated and hand back a link.

Limits to know:

- Content expires: 15 days by default, 1 to 30 days on request (up to 90 with an optional free profile). It is not permanent storage.
- See [BrewPage Help](https://brewpage.app/help) for current size limits.
- Without `namespace="public"`, content goes to a generated private namespace: unlisted and not indexed, but anyone with the link can open it. `public` content is listed in BrewPage's public gallery, so don't publish secrets there.
- Rate limits are per IP; the server answers `429` with `Retry-After` when they are reached.

Disclosure: this page is maintained by the maker of BrewPage.

## Installation

```bash
pip install mcp-haystack==2.1.1 haystack-ai==3.4.1
```

## Usage

Connect to the server and list its tools:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://brewpage.app/mcp")
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description[:80]}")
print(len(toolset.tools))
toolset.close()
```

Publish a Markdown page that expires after one day. Without a `namespace` argument it is unlisted:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://brewpage.app/mcp"),
    tool_names=["publish"],
    eager_connect=True,
)

publish = next(tool for tool in toolset.tools if tool.name == "publish")
receipt = publish.invoke(
    content="# Haystack run report\n\nAll 12 pipeline checks passed.",
    format="markdown",
    ttlDays=1,
)
toolset.close()
```

Share the page URL from the receipt. Keep the owner token and management link private so the workflow can update or delete the publication later with `update_publication` or `delete_publication`.

To let an LLM decide when to publish, give these tools to a chat generator and a `ToolInvoker`, as in the pipeline example on the [MCP integration page](https://haystack.deepset.ai/integrations/mcp).

## License

`mcp-haystack` is distributed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The BrewPage MCP server (`brewpage-mcp`) is MIT-licensed. BrewPage itself is a hosted service governed by its [terms](https://brewpage.app/terms).
