---
layout: integration
name: GateCore
description: Discover and procure governed AI capabilities from the GateCore marketplace, with machine-readable price, scope, and trust terms on every listing.
authors:
    - name: GateCore AI
      socials:
        github: GateCoreAI-com
repo: https://github.com/GateCoreAI-com/gatecore-mcp
type: Tool Integration
report_issue: https://github.com/GateCoreAI-com/gatecore-mcp/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

[GateCore](https://gatecoreai.com) is the governed transaction layer for AI agents. Every agent request is identity-verified, policy-checked, priced, settled, and receipted on a tamper-evident ledger before it touches tools, data, or money.

This integration connects Haystack pipelines and Agents to the GateCore marketplace through GateCore's public MCP server, using Haystack's native MCP support ([`MCPTool`](https://docs.haystack.deepset.ai/docs/mcptool) and [`MCPToolset`](https://docs.haystack.deepset.ai/docs/mcptoolset) from the [`mcp-haystack`](https://pypi.org/project/mcp-haystack/) package). Your Haystack agent can:

- **Discover governed capabilities.** `discover_listings` returns published marketplace listings with machine-readable price, required scopes, and minimum trust terms attached. No key and no account required.
- **Read the contract before committing.** `get_listing` returns one listing and its machine-enforceable contract: price in cents, required scopes, minimum trust, target, and data classification. The agent evaluates terms programmatically instead of parsing marketing copy.
- **Request governed procurement.** With a GateCore MCP access key (`gcmk_` prefix), `procure` returns a PROCURE, REVIEW, or DENY decision, and every decision produces a signed, independently verifiable receipt.

The MCP endpoint is `https://mcp.gatecoreai.com/mcp` (streamable HTTP). The server manifest lives at `https://mcp.gatecoreai.com/.well-known/mcp.json`, and the [gatecore-mcp repository](https://github.com/GateCoreAI-com/gatecore-mcp) carries the quickstart and runnable client examples.

## Installation

The integration uses Haystack's official MCP tooling:

```bash
pip install mcp-haystack
```

## Usage

Point an `MCPTool` at GateCore's public endpoint and call a discovery tool directly. Discovery is anonymous: no key, no account.

```python
from haystack_integrations.tools.mcp import MCPTool, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://mcp.gatecoreai.com/mcp")

discover = MCPTool(name="discover_listings", server_info=server_info)

# All arguments are optional filters: query, tags, max_price_cents, min_trust
result = discover.invoke(max_price_cents=500)
print(result)
```

Fetch the full machine-enforceable contract for a listing found in discovery:

```python
get_listing = MCPTool(name="get_listing", server_info=server_info)

listing = get_listing.invoke(listing_id="listing:example-capability")
print(listing)
```

The returned contract carries the price in cents, the required scopes, the minimum trust threshold, the target, and the data classification, so the agent can decide whether to proceed without a human reading a sales page.

## Examples

### Give a Haystack Agent the GateCore marketplace tools

`MCPToolset` loads the marketplace tools as a single unit. Filter with `tool_names` so the agent sees only what it needs:

```python
from haystack import Pipeline
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://mcp.gatecoreai.com/mcp")

toolset = MCPToolset(
    server_info=server_info,
    tool_names=["discover_listings", "get_listing"],
)

pipeline = Pipeline()
pipeline.add_component(
    "agent",
    Agent(chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"), tools=toolset),
)

result = pipeline.run(
    {
        "agent": {
            "messages": [
                ChatMessage.from_user(
                    "Find marketplace listings under five dollars and summarize "
                    "their price, required scopes, and trust terms."
                )
            ]
        }
    }
)
print(result["agent"]["messages"][-1].text)
```

### Governed procurement

The `procure`, `list_procurements`, and `submit_lead` tools require a GateCore MCP access key sent as a bearer token (`Authorization: Bearer gcmk_<your-key>`). Without a key these tools fail closed with a tool-level refusal. Every governed decision produces an Ed25519-signed receipt that binds the request, the policy decision, and the settlement together; receipts verify entirely client-side at [gatecoreai.com/verify](https://gatecoreai.com/verify) with no account and no callback to GateCore.

See the [quickstart](https://github.com/GateCoreAI-com/gatecore-mcp/blob/main/QUICKSTART.md) for the full tool reference and copy-pasteable calls.

## License

The GateCore public MCP integration surface is distributed under the MIT license.
