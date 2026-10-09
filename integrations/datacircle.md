---
layout: integration
name: Datacircle
description: "Query your favorite B2B data APIs through us. Same request, same price, no markup."
authors:
    - name: Datacircle
      socials:
        twitter: datacircle_dev
        linkedin: https://www.linkedin.com/company/datacircle-org
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/datacircle.png
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

**[Datacircle](https://datacircle.dev)** is a data co-op.

Step 1: Query your favorite B2B data APIs through us. Same request, same price, no markup.

Step 2: You're DONE. Every morning, you get the flat file of your data plus everyone else's.

Right now we have 2 live LinkedIn profile APIs that we trust: Up2Data and HarvestAPI. Each request goes to the provider and gets the profile as it is today.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack agent to Datacircle's MCP server, `https://api.datacircle.dev/mcp`, over Streamable HTTP. Its tools are `get_linkedin_profile`, `get_balance`, `list_files`, `get_download_link`, `add_funds` and `get_invite_link` ([docs](https://docs.datacircle.dev/mcp-server)).

## Installation

```bash
pip install mcp-haystack
```

## Usage

Log in at [datacircle.dev/login](https://datacircle.dev/login) with your work email: your API key is on the page once you're in. Pass it through `StreamableHttpServerInfo`'s `token`, which sends it as an `Authorization: Bearer` header:

```python
import os

from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["DATACIRCLE_API_KEY"] = "YOUR_DATACIRCLE_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://api.datacircle.dev/mcp",
    token=Secret.from_env_var("DATACIRCLE_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

## Examples

An agent that reads a LinkedIn profile and the balance. `tool_names` keeps the toolset to those two tools, so the agent never starts a checkout (`add_funds`):

```python
import os

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

os.environ["DATACIRCLE_API_KEY"] = "YOUR_DATACIRCLE_API_KEY"
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://api.datacircle.dev/mcp",
    token=Secret.from_env_var("DATACIRCLE_API_KEY"),
)
toolset = MCPToolset(
    server_info=server_info,
    tool_names=["get_linkedin_profile", "get_balance"],
    eager_connect=True,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="You research people for a sales team. Use the Datacircle tools to read LinkedIn profiles.",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Look up https://www.linkedin.com/in/williamhgates and summarize his career in three lines. "
            "Then tell me what that lookup cost and what's left on my Datacircle balance."
        )
    ]
)

print(result["last_message"].text)
```

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

Datacircle's MCP server is a hosted service provided by Datacircle, separate from the license of the `mcp-haystack` client used to connect to it.
