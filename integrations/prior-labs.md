---
layout: integration
name: Prior Labs
description: Tabular data science via MCP - predict missing values, classify, and run regression on tabular datasets using Prior Labs' foundation model.
authors:
    - name: Prior Labs
      socials:
        github: priorlabs
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/priorlabs
type: Tool Integration
report_issue: https://github.com/priorlabs
logo: /logos/prior-labs.svg
version: Haystack 2.0
toc: true
mcp: true
---

**Table of Contents**

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Connecting to Prior Labs](#connecting-to-prior-labs)
  - [Predicting Tabular Data with an Agent](#predicting-tabular-data-with-an-agent)
- [License](#license)

## Overview

[Prior Labs](https://priorlabs.ai) is a foundation model platform specialized in tabular data science. It exposes its capabilities as tools via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), enabling Haystack agents to perform tasks like:

- **Missing value prediction** - fill in incomplete columns using patterns from known rows
- **Classification** - predict categorical outcomes from tabular features
- **Regression** - predict continuous values from tabular features

This integration does not require a separate Prior Labs Python package. Instead, it uses the existing `mcp-haystack` package to connect to the Prior Labs MCP server and discover its tools automatically. The agent then decides which tools to call based on the user's request.

## Prerequisites

1. Sign up for a Prior Labs account at [priorlabs.ai](https://priorlabs.ai) and obtain an API token.
2. Set the required environment variable:

```bash
export PRIOR_LABS_MCP_TOKEN="your-prior-labs-token"
```

## Installation

```bash
pip install mcp-haystack
```

## Usage

### Connecting to Prior Labs

Use `StreamableHttpServerInfo` to point to the Prior Labs MCP server and `MCPToolset` to connect and fetch all available tools:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret

server_info = StreamableHttpServerInfo(
    url="https://api.priorlabs.ai/mcp/server",
    token=Secret.from_env_var("PRIOR_LABS_MCP_TOKEN"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)
```

`eager_connect=True` causes the toolset to immediately connect and fetch the tool definitions from the server.

### Predicting Tabular Data with an Agent

The following example sets up a Haystack `Agent` that uses Prior Labs tools to predict missing values in a CSV-style dataset:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator
from haystack.utils import Secret
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage

server_info = StreamableHttpServerInfo(
    url="https://api.priorlabs.ai/mcp/server",
    token=Secret.from_env_var("PRIOR_LABS_MCP_TOKEN"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

llm = AnthropicChatGenerator(model="claude-opus-4-6", tools=toolset)

agent = Agent(
    chat_generator=llm,
    tools=toolset,
    system_prompt=(
        "You are a data scientist working on tabular data. "
        "Use provided tools to solve all the given tasks. "
        "Always use the tools when you can, and only answer directly if you are sure "
        "you have the correct answer. If you are not sure, use the tools to find the answer. "
        "Always think step by step."
    ),
    max_agent_steps=10,
)

input_table = """age,income,purchased
22,32000,0
25,45000,0
28,51000,0
31,58000,1
34,62000,1
37,75000,1
40,88000,1
43,95000,1
26,48000,
33,61000,
29,39000,
41,82000,
"""

output = agent.run(messages=[
    ChatMessage.from_user(
        "I have a dataset with columns 'age', 'income', and 'purchased' "
        "(0 = did not purchase, 1 = purchased). Some rows are missing the 'purchased' value. "
        "Can you predict the missing values based on the known examples?"
    ),
    ChatMessage.from_user(input_table),
])
print(output["last_message"].text)
```

The agent connects to Prior Labs, determines which tool to call (e.g. a classification tool), and returns the predicted `purchased` values for the incomplete rows.

## License

The `mcp-haystack` package is distributed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. Use of the Prior Labs API is subject to [Prior Labs' terms of service](https://priorlabs.ai).
