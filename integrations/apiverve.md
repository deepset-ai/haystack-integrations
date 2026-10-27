---
layout: integration
name: APIVerve
description: "Call APIVerve's catalog of about 380 REST APIs as MCP tools from a Haystack agent: validate emails and phone numbers, look up IPs, DNS and SSL certificates, and fetch exchange and VAT rates"
authors:
    - name: APIVerve
      socials:
        github: apiverve
        twitter: apiverveHQ
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/apiverve/mcp-server
type: Tool Integration
report_issue: https://github.com/apiverve/mcp-server/issues
logo: /logos/apiverve.png
version: Haystack 2.0
toc: true
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

**[APIVerve](https://apiverve.com)** is a catalog of about 380 REST APIs behind one key: email and phone validation, IP geolocation, DNS, WHOIS and SSL certificate lookups, exchange and VAT rates, VIN decoding, document conversion, and more. The whole catalog is exposed as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://api.apiverve.com/v1/mcp`, with one tool per API (`EmailValidator`, `IPLookup`, `DNSLookup`, `ExchangeRate`, ...). Every tool returns structured JSON, so an agent can check facts instead of guessing them.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect any Haystack agent to the APIVerve MCP server over Streamable HTTP. A free plan is available, with no card required.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Create a free account at [dashboard.apiverve.com](https://dashboard.apiverve.com) and copy your API key. The server accepts the key as an `Authorization: Bearer` header, which `StreamableHttpServerInfo` sends through its `token` parameter.

The server exposes a tool for every API in the catalog. Each tool definition is sent to the model on every turn, so pass the handful your agent needs in `tool_names`:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
import os

os.environ["APIVERVE_API_KEY"] = "YOUR_APIVERVE_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://api.apiverve.com/v1/mcp",
    token=Secret.from_env_var("APIVERVE_API_KEY"),
)
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["EmailValidator", "IPLookup", "DNSLookup"],
    eager_connect=True,
)

for tool in toolset.tools:
    print(tool.name)
```

You can also call a tool directly, without an agent:

```python
email_validator = next(tool for tool in toolset.tools if tool.name == "EmailValidator")
print(email_validator.invoke(email="support@apiverve.com"))
```

Tool names match the API names in the [APIVerve catalog](https://apiverve.com/marketplace). Leave out `tool_names` to load every tool.

## Examples

The snippet below gives a Haystack `Agent` the email, phone and IP tools and asks it to check a signup:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
import os

os.environ["APIVERVE_API_KEY"] = "YOUR_APIVERVE_API_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.apiverve.com/v1/mcp",
        token=Secret.from_env_var("APIVERVE_API_KEY"),
    ),
    tool_names=["EmailValidator", "PhoneNumberValidator", "IPLookup"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=toolset,
    system_prompt=(
        "You review new signups. Use the APIVerve tools to check each detail you are given, "
        "and base your verdict only on what the tools return."
    ),
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "A user signed up with the email support@apiverve.com, the phone number "
            "+1 212 555 0100 and the IP address 8.8.8.8. Does anything look wrong?"
        )
    ]
)

print(result["last_message"].text)
```

Each tool call uses credits from your APIVerve plan; connecting and listing tools is free. See [APIVerve pricing](https://apiverve.com/pricing).

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

APIVerve is a hosted service governed by [APIVerve's terms of service](https://apiverve.com/terms), separate from the license of the `mcp-haystack` client used to connect to it.
