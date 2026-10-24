---
layout: integration
name: SoChain
description: Give Haystack agents Bitcoin, Litecoin, Dogecoin and Zcash data (balances, transactions, blocks, fees) through SoChain's hosted MCP server
authors:
    - name: SoChain
      socials:
        github: BlockIo
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/sochain.svg
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

[SoChain](https://sochain.com) is a block explorer and API for Bitcoin, Litecoin, Dogecoin and Zcash, and their testnets (BTCTEST is Bitcoin testnet4). It runs a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://sochain.com/mcp` (Streamable HTTP) with read-only tools for:

- addresses: balance, summary, transactions, unspent outputs, balance history
- transactions: details and status (pending, mined, replaced or dropped)
- blocks: by height or hash, and the latest blocks
- networks: mempool, projected fee rates, charts and the largest holders

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the server. See the [SoChain docs](https://sochain.com/docs) for the REST API behind the same tools.

## Installation

```bash
pip install mcp-haystack
```

## Usage

The API key is optional. Without one, the tools work within a daily limit per IP address. For higher limits, create a free account and key at [sochain.com/dashboard](https://sochain.com/dashboard), set `SOCHAIN_API_KEY`, and it is sent as the `API-KEY` header. Plans are at [sochain.com/pricing](https://sochain.com/pricing).

### Connecting to SoChain

```python
import os

from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

# Send the key only when one is set; without it, requests are keyless.
headers = {"API-KEY": Secret.from_env_var("SOCHAIN_API_KEY")} if os.getenv("SOCHAIN_API_KEY") else None

server_info = StreamableHttpServerInfo(url="https://sochain.com/mcp", headers=headers)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

`tool_names` limits the agent to the tools it needs:

```python
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["get_address_summary", "get_transactions", "get_transaction", "get_network_info"],
    eager_connect=True,
)
```

### Using SoChain with an Agent

```python
import os

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

headers = {"API-KEY": Secret.from_env_var("SOCHAIN_API_KEY")} if os.getenv("SOCHAIN_API_KEY") else None

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://sochain.com/mcp", headers=headers),
    tool_names=["get_address_summary", "get_transactions", "get_transaction", "get_network_info"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="You answer questions about blockchain addresses and transactions. Quote addresses and transaction IDs in full and give amounts with their coin.",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "What is the balance of the Dogecoin address DGUzATWpGdehtujWNyM464LB9Zx7Ch1Z67, "
            "and what was its most recent transaction?"
        )
    ]
)

print(result["last_message"].text)
```

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

SoChain is a hosted service governed by the [SoChain terms](https://sochain.com/terms), separate from the license of the `mcp-haystack` client used to connect to it.
