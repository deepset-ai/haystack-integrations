---
layout: integration
name: AgentBroker
description: Crypto exchange API purpose-built for AI agents — register, trade 8 pairs (BTC, ETH, SOL, BNB, DOGE, ADA, XRP, AVAX), stream real-time prices via WebSocket. OpenAPI 3.1 spec available.
authors:
    - name: AgentBroker Team
      socials:
        github: agentbroker-tech
repo: https://github.com/agentbroker-tech
report_issue: https://agentbroker.polsia.app
type: Tool Integration
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Agent Example](#agent-example)

## Overview

[AgentBroker](https://agentbroker.polsia.app) is a crypto exchange API designed specifically for AI agents. It provides a clean REST API with no UI friction, ideal for autonomous trading agents built with Haystack.

**Website**: [agentbroker.polsia.app](https://agentbroker.polsia.app)
**OpenAPI Spec**: [agentbroker.polsia.app/openapi.json](https://agentbroker.polsia.app/openapi.json)

### Key Features

- Agent-First Design: REST API built for programmatic access
- 8 Trading Pairs: BTC, ETH, SOL, BNB, DOGE, ADA, XRP, AVAX
- WebSocket Streaming: Real-time price feeds
- Simple Auth: Register and get an API key in one call
- OpenAPI 3.1: Full spec for automatic tool generation

## Installation

```bash
pip install requests haystack-ai
```

## Usage

```python
import requests
from haystack.tools import Tool

AGENTBROKER_URL = "https://agentbroker.polsia.app"

api_key = requests.post(
    f"{AGENTBROKER_URL}/register",
    json={"name": "my-haystack-agent"}
).json()["api_key"]

def get_price(pair: str) -> str:
    r = requests.get(f"{AGENTBROKER_URL}/price/{pair}")
    d = r.json()
    return f"{pair}: ${d['price']:,.4f}"

def execute_trade(pair: str, side: str, amount: float) -> str:
    r = requests.post(
        f"{AGENTBROKER_URL}/order",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"pair": pair, "side": side, "amount": amount}
    )
    return str(r.json())

price_tool = Tool(
    name="get_price",
    description="Get current price for BTC-USD, ETH-USD, SOL-USD, BNB-USD, DOGE-USD, ADA-USD, XRP-USD, AVAX-USD",
    function=get_price,
    parameters={"pair": {"type": "string"}}
)

trade_tool = Tool(
    name="execute_trade",
    description="Execute a buy or sell order on AgentBroker exchange",
    function=execute_trade,
    parameters={
        "pair": {"type": "string"},
        "side": {"type": "string", "enum": ["buy", "sell"]},
        "amount": {"type": "number"}
    }
)
```

## Agent Example

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

trading_agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    system_prompt="You are an autonomous crypto trading agent. Check prices and make data-driven trade decisions.",
    tools=[price_tool, trade_tool],
)

result = trading_agent.run(messages=[
    ChatMessage.from_user("Check ETH and BTC prices, then buy the one with better momentum.")
])
print(result["last_message"].text)
```

## License

AgentBroker API is free to use for AI agents. See [agentbroker.polsia.app](https://agentbroker.polsia.app) for terms.
