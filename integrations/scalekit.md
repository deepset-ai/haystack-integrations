---
layout: integration
name: Scalekit
description: "Give Haystack agents per-user access to 500+ apps (Gmail, Slack, GitHub, Salesforce, ...) through Scalekit's MCP servers: each tool call runs with the end user's own credentials, tools are scoped per agent, and every call is logged"
authors:
    - name: Scalekit
      socials:
        github: scalekit-inc
pypi: https://pypi.org/project/scalekit-sdk-python/
repo: https://github.com/scalekit-inc/scalekit-sdk-python
type: Tool Integration
report_issue: https://github.com/scalekit-inc/scalekit-sdk-python/issues
logo: /logos/scalekit.svg
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

**[Scalekit](https://www.scalekit.com)** is an agent integration platform. It lets an AI agent act in third-party apps on behalf of each of your users: a user authorizes Gmail, Slack, GitHub, Salesforce or any of 500+ connectors once, and the agent calls 20,000+ prebuilt tools with that user's own credentials.

- **Authentication and authorization:** Scalekit runs each user's OAuth flow and also handles API keys, RSA key pairs, and Basic and bearer credentials. Tokens are refreshed automatically and stored in an encrypted, per-tenant token vault (with bring-your-own KMS key on Enterprise), so they never appear in your agent code, logs, or the LLM context.
- **Scoped tools:** Virtual MCP servers expose only the tools you choose for an agent role, and a session token can be limited to read-only tools.
- **Audit:** every tool call is logged with the tool, connection, user and outcome, and can be streamed to a SIEM.
- **Enterprise:** SOC 2 Type II, HIPAA BAA, and VPC or self-hosted deployment.

This integration doesn't ship a separate Haystack package. Every Scalekit connection has its own MCP server at `<environment URL>/mcp/v3/connections/<connection name>`. Your backend uses the Scalekit Python SDK to mint a short-lived session token for one user, and `mcp-haystack`'s `MCPToolset` connects the Haystack agent to that server over Streamable HTTP. Tools are discovered at connect time, so the snippets below don't hardcode a tool list.

## Installation

```bash
pip install mcp-haystack scalekit-sdk-python
```

## Usage

Create a Scalekit environment and a connection (for example `gmail`) in the [Scalekit dashboard](https://app.scalekit.com), then set `SCALEKIT_ENVIRONMENT_URL`, `SCALEKIT_CLIENT_ID`, and `SCALEKIT_CLIENT_SECRET`.

```python
import os
from datetime import timedelta

from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from scalekit import ScalekitClient

scalekit = ScalekitClient(
    env_url=os.environ["SCALEKIT_ENVIRONMENT_URL"],
    client_id=os.environ["SCALEKIT_CLIENT_ID"],
    client_secret=os.environ["SCALEKIT_CLIENT_SECRET"],
)
actions = scalekit.actions

user_id = "user_123"       # your app's identifier for the end user
connection_name = "gmail"  # a connection configured in Scalekit

# 1. Make sure the user has authorized the connection
account = actions.get_or_create_connected_account(
    connection_name=connection_name, identifier=user_id
).connected_account
if account.status != "ACTIVE":
    link = actions.get_authorization_link(connection_name=connection_name, identifier=user_id)
    print("Ask the user to authorize:", link.link)

# 2. Mint a short-lived session token for this user and this connection's MCP server
session = actions.mcp.create_session_token(
    connection_name=connection_name,
    identifier=user_id,
    expiry=timedelta(hours=1),
)

# 3. Connect Haystack to the user's Scalekit MCP server
server_info = StreamableHttpServerInfo(
    url=f"{os.environ['SCALEKIT_ENVIRONMENT_URL']}/mcp/v3/connections/{connection_name}",
    token=Secret.from_token(session.token),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

A session token is bound to one user and one server and lasts between 60 seconds and 24 hours, so mint a new one for each run. To give the agent only tools that don't change anything, pass `access_level="READ_ONLY"` when minting it.

To expose tools from several connections behind one URL, or only a subset of a connection's tools, create a [Virtual MCP server](https://docs.scalekit.com/agentkit/mcp/overview/), mint the token with `mcp_config_id=` instead of `connection_name=`, and use the server's `mcp_server_url`.

## Examples

Connect the toolset to a Haystack `Agent` and let it work in the user's inbox:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt="You are an email assistant. Use the available Gmail tools to answer the user's request.",
)

result = agent.run(messages=[ChatMessage.from_user("Summarize my five most recent unread emails.")])
print(result["last_message"].text)
```

See the [Scalekit docs](https://docs.scalekit.com/agentkit/overview/) for the connector catalog, Virtual MCP servers, and production auth flows.

## License

`scalekit-sdk-python` is distributed under the MIT license, and `mcp-haystack` under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

Scalekit itself is a hosted service governed by [Scalekit's terms of service](https://www.scalekit.com/legal/terms-of-service), separate from the licenses of the client libraries used to connect to it.
