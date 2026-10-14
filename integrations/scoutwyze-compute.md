---
layout: integration
name: ScoutWyze Compute
description: Ranks live GPU placement offers (8x H100 80GB, RunPod) by price and freshness as a Haystack Tool - pay per successful match with a prepaid key, or per call via x402/USDC on Base with no signup at all.
authors:
    - name: ScoutWyze
      socials:
        github: scoutwyze-max
repo: https://github.com/scoutwyze-max/scoutwyze-compute
type: Tool Integration
report_issue: https://github.com/scoutwyze-max/scoutwyze-compute/issues
version: Haystack 3.2
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[ScoutWyze Compute](https://scoutwyze-compute.fly.dev) is a machine-readable GPU placement recommendation API for AI infrastructure agents and MLOps pipelines. It ranks live 8x H100 80GB (InfiniBand/RDMA) offers by price and data freshness, and strictly separates what a provider reported (`provider_observed`) from what ScoutWyze calculated (`scoutwyze_estimated`) - it is a routing/recommendation layer, never an execution platform (it never reserves, provisions, or runs anything).

`examples/haystack_tool.py` in the [repo](https://github.com/scoutwyze-max/scoutwyze-compute) wraps the `POST /v1/compute/rank` endpoint as a Haystack [`Tool`](https://docs.haystack.deepset.ai/docs/tool) that a Haystack `Agent` can call mid-pipeline. Two variants are provided:

- `make_bearer_tool` - the endpoint is billed per successful match (a `no_match` result is never charged), backed by a prepaid credit account. Suited to a human-operated pipeline that already manages one API key the same way it would for any other service.
- `make_x402_tool` - for a fully autonomous agent with its own funded [Base](https://base.org) wallet: no signup, no API key, pays per call over the real x402 "exact" EVM scheme (EIP-3009 `TransferWithAuthorization`, gasless for the caller). Settlement happens before scoring on this rail, so a `no_match` result is still billed - a real x402 protocol property, not an integration bug.

## Installation

No package to install from PyPI yet - copy `examples/haystack_tool.py` and `examples/python_client.py` from the [repo](https://github.com/scoutwyze-max/scoutwyze-compute/tree/main/examples) into your project (or `git submodule`/`pip install` the repo directly), then:

```bash
pip install haystack-ai eth_account
```

## Usage

### Components

This integration provides two Tool factories, both returning a real `haystack.tools.Tool`:

- `make_bearer_tool(api_key=None, base_url=...)`: reads `SCOUTWYZE_API_KEY` from the environment if `api_key` isn't passed. Get a free key with `POST https://scoutwyze-compute.fly.dev/v1/signup`, then fund it via `POST /v1/checkout-sessions` (real Stripe Checkout).
- `make_x402_tool(private_key=None, base_url=...)`: reads `SCOUTWYZE_WALLET_PRIVATE_KEY` from the environment if `private_key` isn't passed. No signup needed - just a Base wallet holding a little USDC.

### Use in a Haystack Agent

```python
import os
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_tool import make_bearer_tool

os.environ["SCOUTWYZE_API_KEY"] = "sw_live_..."  # from POST /v1/signup

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[make_bearer_tool()],
)

result = agent.run(
    messages=[ChatMessage.from_user("Find the cheapest available 8x H100 80GB offer right now.")]
)
print(result["messages"][-1].text)
```

### Standalone usage

```python
from haystack_tool import make_bearer_tool

tool = make_bearer_tool(api_key="sw_live_...")
offers = tool.invoke(gpuClass="H100", preference="cheapest")
print(offers["recommended"])
```

## License

The `scoutwyze-compute` repository, including `examples/haystack_tool.py`, is distributed under the [MIT](https://github.com/scoutwyze-max/scoutwyze-compute/blob/main/LICENSE) license.
