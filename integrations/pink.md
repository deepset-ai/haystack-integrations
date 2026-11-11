---
layout: integration
name: Pink Agentic AI Payments
description: Approval layer between AI agents and company money — plain-language rules, per-agent budgets, and human approvals gate every payment via MCP or REST before it executes.
authors:
  - name: PinkWallet
    socials:
      github: Pink-Agentic-Payments
type: Tool Integration
repo: https://github.com/Pink-Agentic-Payments/sandbox-examples/tree/main/07-haystack
---

## Overview

Pink Agentic AI Payments (by PinkWallet) sits between an AI agent and company money. Before any payment executes, Pink checks it against plain-language rules, per-agent budgets, and (when configured) a human approval step.

**Status: early access, free public sandbox.** The remote MCP server (`https://agentic-sandbox.pinkwallet.com/mcp`, Bearer agent key, streamable HTTP) exposes 7 tools: `pink.check_policy`, `pink.get_budget`, `pink.get_credential`, `pink.list_payees`, `pink.list_rules`, `pink.report_receipt`, `pink.request_payment`. A REST API with an OpenAPI 3.1 spec is also available. Sandbox credentials only — no real money moves.

## Using Pink with Haystack

Load Pink's tools with the official MCP integration (`pip install haystack-ai mcp-haystack`) and give them to an `Agent`. Spending limits, approvals and blocks are enforced server-side on every `pink.request_payment` call, not in the prompt:

```python
import os
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://agentic-sandbox.pinkwallet.com/mcp",
    token=os.environ["PINK_AGENT_KEY"],  # free sandbox agent key
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)
# agent = Agent(chat_generator=..., tools=toolset)
```

A runnable example (Haystack `Agent` + Gemini, plus a no-LLM script) showing an allowed payment, one routed to human approval, and one blocked: https://github.com/Pink-Agentic-Payments/sandbox-examples/tree/main/07-haystack

- Sandbox examples: https://github.com/Pink-Agentic-Payments/sandbox-examples
- Connect guide: https://pinkwallet.com/agentic/connect/

*Disclosure: I work on Pink Agentic AI Payments.*
