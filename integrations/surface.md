---
layout: integration
name: Surface
description: URL preflight for Haystack agents. Unwrap short links and decide fetch or skip before spending tokens on a page.
authors:
    - name: Surface
      socials:
        github: Surface-ops
repo: https://github.com/Surface-ops/surface
report_issue: https://github.com/Surface-ops/surface/issues
type: Tool Integration
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Response](#response)
- [Pricing](#pricing)
- [License](#license)

## Overview

[Surface](https://nova-otter-delta-cloud.grok.me) is a hosted URL preflight for AI agents. Its `preflight_url` tool follows redirects, unwraps short links (t.co, bit.ly, lnkd.in, youtu.be), and returns a verdict, `next: fetch` or `next: skip`, with a reason. It never returns the page body, so it is a cheap check to run before a fetcher or web-search component spends tokens on a dead or unwanted link.

Surface is a remote MCP server (Streamable HTTP) at `https://nova-otter-delta-cloud.grok.me/mcp`, so it works with Haystack's `MCPTool` from `mcp-haystack` with no extra package. A plain REST endpoint, `POST /v1/preflight`, is also available.

## Installation

```bash
pip install haystack-ai mcp-haystack
```

## Usage

### Use the tool directly

```python
from haystack_integrations.tools.mcp import MCPTool, StreamableHttpServerInfo

surface = MCPTool(
    name="preflight_url",
    server_info=StreamableHttpServerInfo(url="https://nova-otter-delta-cloud.grok.me/mcp"),
)

print(surface.invoke(url="https://bit.ly/3xyz"))
```

### Use it in an Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPTool, StreamableHttpServerInfo

surface = MCPTool(
    name="preflight_url",
    server_info=StreamableHttpServerInfo(url="https://nova-otter-delta-cloud.grok.me/mcp"),
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[surface],
    system_prompt=(
        "Before fetching any URL, call preflight_url. "
        "If next is 'skip', do not fetch it; report the verdict and reason."
    ),
)

result = agent.run(messages=[ChatMessage.from_user("Is https://example.com worth opening?")])
print(result["messages"][-1].text)
```

### REST (no MCP)

```bash
curl -s -X POST https://nova-otter-delta-cloud.grok.me/v1/preflight \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com"}'
```

## Response

```json
{
  "ok": true,
  "url": "https://example.com/",
  "final_url": "https://example.com/",
  "status": 200,
  "redirects": 0,
  "content_type": "text/html",
  "shortener": false,
  "unwrapped": false,
  "verdict": "fetch",
  "next": "fetch",
  "reason": "alive, worth a fetch",
  "billed": 0,
  "free_tier": true,
  "free_remaining": 999991
}
```

## Pricing

The first 1,000,000 requests every month are free, with no card needed. After that, preflight is $0.25 USD per 1,000 requests. See [nova-otter-delta-cloud.grok.me](https://nova-otter-delta-cloud.grok.me).

## License

See the [Surface repository](https://github.com/Surface-ops/surface).
