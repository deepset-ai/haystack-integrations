---
layout: integration
name: Unstructured Transform MCP
description: "Call Unstructured Transform's document-processing pipeline (partition, enrich, chunk, embed) as MCP tools from a Haystack agent: parse PDFs, spreadsheets, and dozens of file types with tables and layout intact"
authors:
    - name: Unstructured
      socials:
        github: Unstructured-IO
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/unstructured.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

**[Unstructured Transform](https://docs.unstructured.io/transform/overview)** turns any file into agent-ready data, called directly from your agent with no separate pipeline to wire up. It is Unstructured's document-processing pipeline, exposed as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://mcp.transform.unstructured.io`. Drop in a PDF, spreadsheet, scan, or email and get back partitioned, enriched, chunked, and embedded output ready for RAG, vector stores, or agent memory, with tables and layout intact. It exposes four tools:

- `transform_files`: submits one or more files (by URL or a previously returned reference) for processing and returns a `job_id` right away; the job runs asynchronously through configurable stages (`partition` -> `enrich` -> `chunk` -> `embed`)
- `check_transform_status`: polls a job's status until it reaches `COMPLETED`
- `get_transform_results`: fetches a completed job's rendered output as markdown, JSON, HTML, or plain text
- `request_file_upload_url`: returns a presigned upload URL and a durable reference for a local file that isn't already reachable over HTTPS

This integration doesn't ship its own package. Instead, it uses `mcp-haystack`'s `MCPToolset` to connect any Haystack agent to the Transform MCP server over Streamable HTTP. The free tier includes 15,000 pages a month.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Transform MCP supports two ways to authenticate: interactive browser-based OAuth/OIDC (for clients that speak remote MCP natively), and a static API key passed as an `Authorization: Bearer` header (for headless frameworks like Haystack). Get your Unstructured API key from the [Transform get-started page](https://transform.unstructured.io/get-started) after signing in, and pass it through `StreamableHttpServerInfo`'s native `token` parameter:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret

server_info = StreamableHttpServerInfo(
    url="https://mcp.transform.unstructured.io",
    token=Secret.from_env_var("UNSTRUCTURED_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

If your MCP client doesn't support native remote-MCP OAuth (or only supports local stdio servers), bridge to the hosted server with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) instead:

```bash
npm install -g mcp-remote
npx -y mcp-remote https://mcp.transform.unstructured.io
```

## Examples

The snippet below connects the toolset to a Haystack `Agent` and asks it to parse and chunk a PDF end-to-end. Because `transform_files` is asynchronous, the agent's system prompt walks it through the `transform_files` -> `check_transform_status` -> `get_transform_results` polling loop:

```python
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret

server_info = StreamableHttpServerInfo(
    url="https://mcp.transform.unstructured.io",
    token=Secret.from_env_var("UNSTRUCTURED_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

agent = Agent(
    chat_generator=AnthropicChatGenerator(model="claude-opus-4-6"),
    tools=toolset,
    system_prompt="""You are a document-processing assistant with access to Unstructured Transform MCP tools.

Transform jobs are asynchronous. When asked to process a document:
1. Call `transform_files` with the file reference(s) and the requested processing stages. This returns a `job_id` immediately; the job itself runs in the background.
2. Call `check_transform_status` with that `job_id`, repeating until the status is COMPLETED.
3. Call `get_transform_results` with the `job_id` to fetch the rendered output, and summarize it for the user.
""",
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Parse and chunk the PDF at https://arxiv.org/pdf/1706.03762 using the "
            "'hi_res' partition strategy and chunk_by_title with max_characters=1000. "
            "Once processing is complete, fetch the results as markdown and show me "
            "the first two chunks."
        )
    ]
)

print(result["last_message"].text)
```

For a full walkthrough, see the [Document Processing with Unstructured Transform MCP](https://haystack.deepset.ai/cookbook/unstructured_transform_mcp) cookbook.

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

Unstructured Transform MCP itself is a hosted service provided by Unstructured and is governed by [Unstructured's terms of service](https://unstructured.io/terms-and-conditions), separate from the license of the `mcp-haystack` client used to connect to it.
