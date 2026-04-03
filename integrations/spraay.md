---
layout: integration
name: Spraay x402 Gateway
description: Multi-chain batch payments, balance checks, RPC calls, and oracle prices for Haystack agents and pipelines via the Spraay x402 gateway. Supports 15+ blockchains including Base, Ethereum, Solana, Stellar, and XRP Ledger.
authors:
  - name: plagtech
    socials:
      github: plagtech
      twitter: Spraay_app
pypi: https://pypi.org/project/haystack-spraay/
repo: https://github.com/plagtech/haystack-spraay
report_issue: https://github.com/plagtech/haystack-spraay/issues
type: Tool Integration
logo: /logos/spraay.png
version: Haystack 2.0
---
## Overview

`haystack-spraay` provides Haystack components and tools for interacting with the [Spraay x402 Gateway](https://gateway.spraay.app) — a multi-chain batch payment protocol that lets AI agents make USDC micropayments across 16+ blockchains using the [x402 HTTP payment protocol](https://github.com/coinbase/x402).

## Installation
```bash
pip install haystack-spraay
```

## Usage with Haystack Agent
```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_spraay.tools import spraay_batch_payment, spraay_check_balance

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[spraay_batch_payment, spraay_check_balance],
    system_prompt="You are a blockchain payment assistant.",
)

result = agent.run(
    messages=[ChatMessage.from_user("Check the USDC balance of 0xAd62...")]
)
```

## Usage as Pipeline Components
```python
from haystack_spraay.components import SpraayBalanceCheck

balance = SpraayBalanceCheck(chain="base")
result = balance.run(address="0xAd62f03C7514bb8c51f1eA70C2b75C37404695c8")
```

## Components

- **SpraayBatchPayment**: Send batch USDC payments to multiple recipients
- **SpraayBalanceCheck**: Check token balances on any chain
- **SpraayGasPrice**: Get real-time gas prices
- **SpraayRPCCall**: Make raw JSON-RPC calls
- **SpraayOraclePrice**: Get real-time token prices

## Supported Chains

Base, Ethereum, Arbitrum, Polygon, BNB Chain, Avalanche, Solana, Stellar, XRP Ledger, Bitcoin, BOB, Unichain, Plasma, Bittensor, Stacks.
