---
layout: integration
name: BotsRated
description: Check an x402 seller with BotsRated's signed probes before your Haystack Agent pays it
authors:
    - name: BotsRated
      socials:
        github: botsrated
pypi: https://pypi.org/project/botsrated/
repo: https://github.com/botsrated/botsrated/tree/main/integrations/haystack
type: Tool Integration
report_issue: https://github.com/botsrated/botsrated/issues
logo: /logos/botsrated.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Hosted MCP server with MCPToolset](#hosted-mcp-server-with-mcptoolset)
  - [Pre-payment check tool](#pre-payment-check-tool)
- [Paid lookups](#paid-lookups)
- [License](#license)

## Overview

[BotsRated](https://botsrated.com) (beta) checks an [x402](https://www.x402.org/) seller before an agent pays it.
It probes about 4,800 x402 seller hosts on Base, plus the remote MCP servers in the Official MCP Registry, without
paying them. Each probe (HTTP status, whether the 402 challenge is valid, latency, quoted price and payTo address)
is recorded as a signed receipt. BotsRated also makes real paid test purchases and publishes their transaction
links.

With Haystack you can use BotsRated in two ways. Both are free and need no API key or wallet:

- the hosted MCP server at `https://botsrated.com/mcp`, through [`MCPToolset`](/integrations/mcp)
- a small `@tool` built on the [`botsrated`](https://pypi.org/project/botsrated/) package that tells the agent whether to
  `allow`, `warn` or `block` a specific x402 payment option

Results are measurements, not endorsements.

## Installation

```bash
pip install haystack-ai mcp-haystack botsrated
```

## Usage

### Hosted MCP server with MCPToolset

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

botsrated = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://botsrated.com/mcp"),
    tool_names=["preflight", "coverage", "sample", "history"],  # the free tools
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=botsrated,
    system_prompt=(
        "Before paying any x402 seller, call the BotsRated preflight tool with the seller URL. "
        "Do not pay if the payTo you are about to pay differs from the payTo BotsRated observed."
    ),
)
result = agent.run(messages=[ChatMessage.from_user(
    "Is https://blockrun.ai/api/v1/chat/completions safe to pay right now?")])
print(result["last_message"].text)
botsrated.close()
```

The free tools are `preflight` (is the host covered, and which payTo and price did the probes see),
`coverage`, `sample` and `history`. The server also lists `check`, `report` and `best`, which are paid
x402 routes, so leave them out of `tool_names` unless your agent can pay x402.

### Pre-payment check tool

This tool asks BotsRated's free preflight about the exact payment option the agent is about to sign:

```python
import json

from botsrated import BotsRatedClient, PrePaymentGuard
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.tools import tool

guard = PrePaymentGuard(BotsRatedClient())  # free preflight only


@tool
def botsrated_check_payment(url: str, pay_to: str, amount: str, network: str = "eip155:8453") -> str:
    """Check an x402 payment option against BotsRated's measurements BEFORE paying it.

    :param url: The seller URL you are about to pay.
    :param pay_to: The payTo address from the seller's 402 payment option.
    :param amount: The amount in atomic units from that option.
    :param network: The CAIP-2 network of that option.
    """
    d = guard.decide(url, {"scheme": "exact", "network": network, "payTo": pay_to, "amount": amount})
    return json.dumps({
        "action": d.action,
        "reasons": [{"code": r.code, "detail": r.detail} for r in d.reasons],
        "receipt_url": d.facts.receipt_url if d.facts else None,
    })


agent = Agent(chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"), tools=[botsrated_check_payment])
```

The tool returns `block` when the payTo differs from every payTo BotsRated's own probes saw for that host on
that network. A host BotsRated doesn't cover, or an unreachable BotsRated, returns `allow` with an info reason.
You can change this with `GuardPolicy` and `fail_open=False`.

If your application pays with the x402 Python SDK directly, register the same guard on the x402 client:
`client.on_before_payment_creation(PrePaymentGuard().x402_hook)`.

Seller-supplied text in the results (descriptions, URLs) is untrusted data, not instructions for the model.

## Paid lookups

`check` ($0.001), `report` ($0.002) and `best` ($0.01) are paid in USDC on Base over x402. The first 100 checks
and 10 reports per client per UTC day are free. In the `botsrated` package they are opt-in and capped by a budget
you set (`BotsRatedClient(budget_usd="0.05", ...)`). See the
[package README](https://github.com/botsrated/botsrated/tree/main/integrations/python-core) and the
[BotsRated docs](https://botsrated.com/docs).

## License

The `botsrated` package and the examples are MIT licensed.
