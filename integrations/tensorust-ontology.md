---
layout: integration
name: Tensorust Ontology MCP
description: "Give a Haystack agent who-owns-what answers from US public records: ownership and control of companies, homes and aircraft, private credit loan marks, federal award exposure, and which federal rules apply to an organization"
authors:
    - name: Tensorust
      socials:
        github: Mattbusel
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/tensorust.svg
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

The **[Tensorust Ontology](https://shop.tensorust.com/ontology)** resolves US public records (county property rolls, state business registries, SEC subsidiary lists and BDC filings, FCC licensing, USAC E-Rate, federal awards and the FAA aircraft registry) into one record per organization, links each organization to what it owns, holds and received, and evaluates the federal rules that apply to it. It is served as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://shop.tensorust.com/api/mcp`.

A Haystack agent connected to it can answer questions such as:

- Who owns this company, home or aircraft, and what control group does it belong to?
- What do the private credit lenders (BDC funds) holding a company's first-lien loan mark it at, and how far apart are they?
- Which federal research awards pay for work by vendors on banned-vendor lists (DoD 1260H, Section 889, FCC Covered List, UFLPA, BIOSECURE)?
- Which federal rules (ROAD Act investor ban, FCC foreign adversary attestation, Upper C-band elections, E-Rate deadlines) apply to an organization?

The server adds tools as new sources and rules land, so the snippets below discover the live toolset at connect time rather than hard-coding a list. The [MCP page](https://shop.tensorust.com/mcp) describes each tool.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to the Tensorust server over Streamable HTTP. The free tier needs no key and no sign-up: every tool returns a preview (sources, link counts, obligations and the first links of each kind).

## Installation

```bash
pip install mcp-haystack
```

## Usage

Connect and list the tools:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://shop.tensorust.com/api/mcp")
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description[:80]}")
```

Tools can also be called directly, without an agent:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://shop.tensorust.com/api/mcp"),
    tool_names=["lookup_organization"],
    eager_connect=True,
)
print(toolset.tools[0].invoke(name="Lockheed Martin"))
```

Most tools take an optional `full` argument. With `full=true` they return every linked object and property, which needs a Tensorust API key sent as an `Authorization: Bearer tdk_...` header. Pass it through `StreamableHttpServerInfo`'s `token` parameter; without a valid key the tools keep returning the free preview:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://shop.tensorust.com/api/mcp",
    token=Secret.from_env_var("TENSORUST_API_KEY"),
)
```

## Examples

A due-diligence agent that only gets the counterparty tools it needs. `tool_names` keeps the tool list (and the prompt) small:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://shop.tensorust.com/api/mcp"),
    tool_names=[
        "lookup_organization",
        "search_organizations",
        "get_object",
        "lender_marks",
        "credit_disagreements",
        "contractor_credit",
    ],
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-5-mini"),
    tools=toolset,
    system_prompt=(
        "You are a counterparty risk analyst. Answer from the Tensorust tools only, "
        "name the public source behind each fact, and say when a result is a preview."
    ),
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Which first-lien loans do BDC lenders disagree on most right now? "
            "For the top one, who are the lenders and what does each mark it at?"
        )
    ]
)
print(result["last_message"].text)
toolset.close()
```

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

The Tensorust Ontology MCP server is a hosted service run by Tensorust LLC and governed by its [terms](https://shop.tensorust.com/terms). Questions about the data: support@tensorust.com.
