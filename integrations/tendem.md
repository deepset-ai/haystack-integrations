---
layout: integration
name: Tendem
description: Delegate tasks to vetted human experts - research, writing, analysis, and data work.
authors:
    - name: Tendem
      socials:
        github: Toloka
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/Toloka/tendem-mcp
report_issue: https://github.com/Toloka/tendem-mcp/issues
type: Tool Integration
logo: /logos/tendem.svg
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

[Tendem](https://tendem.ai) is a hybrid AI + human task service, exposed to Haystack as a
remote MCP server. Your agent submits a task in natural language; Tendem's orchestrator
scopes it and quotes a transparent price; after explicit approval a vetted human expert
executes it and returns verified results as markdown plus files.

This gives a Haystack `Agent` a way to hand off the work that a model alone cannot reliably
finish — research and competitive analysis, fact-checking, copywriting and editing, design
review, presentation polish, data cleaning and list building. Tendem declines data scraping
and extraction tasks by policy, and quick general-knowledge questions are better answered by
the model itself.

The server is hosted at `https://mcp.tendem.ai/mcp` over streamable HTTP, so there is no
Tendem-specific Haystack package to install — the
[MCP integration](https://haystack.deepset.ai/integrations/mcp) connects to it directly.

The main tools it exposes are `create_task`, `send_message` and `read_chat` (agent-to-agent
scoping), `get_contract` (scope and price), `approve_task`, `get_task` and `get_task_result`.

> Tasks are billed. `create_task` and scoping are free; nothing is charged until
> `approve_task` is called, so keep a human in the loop before approving a quote.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Interactive clients authenticate with OAuth 2.0 on first use. For scripts and pipelines,
create an API key at [agent.tendem.ai/mcp](https://agent.tendem.ai/mcp) (the "Agent builders"
tab) and pass it as an `Authorization` header:

```bash
export TENDEM_AUTH="ApiKey <your-token>"
```

### Load the Tendem tools

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.tendem.ai/mcp?utm_hash=b3b2da7bd9",
        headers={"Authorization": Secret.from_env_var("TENDEM_AUTH")},
    ),
)

for tool in toolset:
    print(tool.name)
```

### Use it in an Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mcp.tendem.ai/mcp?utm_hash=b3b2da7bd9",
        headers={"Authorization": Secret.from_env_var("TENDEM_AUTH")},
    ),
    tool_names=[
        "create_task",
        "read_chat",
        "send_message",
        "get_contract",
        "get_task",
        "get_task_result",
    ],
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=list(toolset),
    system_prompt=(
        "You can delegate work to human experts through Tendem. Pass the user's own words "
        "into create_task and let Tendem drive scoping. Always call get_contract and show "
        "the scope and price to the user, and never call approve_task without an explicit "
        "go-ahead. Poll with get_task(task_id, wait_for_change_seconds=30) rather than "
        "looping."
    ),
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Have a human expert compare the top 5 open-source vector databases "
            "on licensing and hybrid search support, with sources."
        )
    ]
)
print(result["messages"][-1].text)
```

Selecting a subset of tools with `tool_names` keeps the approval and cancellation tools out
of the model's reach, which is a good default for unattended pipelines.

### Retrieving results

Once a task is approved and executed, `get_task_result` returns markdown plus pre-signed URLs
for any files the expert produced, so results can be fed straight into a Haystack pipeline —
for example converted and written to a Document Store.

## License

The Tendem MCP server is a hosted commercial service; use is governed by the
[Tendem terms](https://tendem.ai). The client-side plugin configuration in
[Toloka/tendem-mcp](https://github.com/Toloka/tendem-mcp) is Apache-2.0 licensed.
