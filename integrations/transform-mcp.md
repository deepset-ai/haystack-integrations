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
mcp: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

**[Unstructured Transform](https://docs.unstructured.io/transform/overview)** turns any file into agent-ready data, called directly from your agent with no separate pipeline to wire up. It is Unstructured's document-processing pipeline, exposed as a hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://mcp.transform.unstructured.io`. Drop in a PDF, spreadsheet, scan, or email and get back partitioned, enriched, chunked, and embedded output ready for RAG, vector stores, or agent memory, with tables and layout intact.

The pipeline itself runs asynchronously as a job: submit a file for processing, poll until it's done, then fetch the rendered result; a separate helper mints an upload URL for files that aren't already reachable over HTTPS. Unstructured adds tools and capabilities to this server as they ship new features, so rather than list exact tool names and a fixed count here (which would go stale the next time they do), the snippets below discover the live toolset at connect time and let the agent match tools to the task by their description.

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
import os

os.environ["UNSTRUCTURED_API_KEY"] = "YOUR_UNSTRUCTURED_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://mcp.transform.unstructured.io",
    token=Secret.from_env_var("UNSTRUCTURED_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

## Examples

The snippet below connects the toolset to a Haystack `Agent` and asks it to parse and chunk a PDF end-to-end. Because job submission is asynchronous, the agent's system prompt walks it through a submit -> poll -> fetch flow, described by behavior rather than by hardcoded tool name so it keeps working as Unstructured renames or adds tools:

```python
import time
from typing import Annotated

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack.utils import Secret
import os

os.environ["UNSTRUCTURED_API_KEY"] = "YOUR_UNSTRUCTURED_API_KEY"

server_info = StreamableHttpServerInfo(
    url="https://mcp.transform.unstructured.io",
    token=Secret.from_env_var("UNSTRUCTURED_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True)


@tool
def wait(seconds: Annotated[int, "How many seconds to pause before the next tool call"]) -> str:
    """Pause execution for the given number of seconds. A chat generator can't control timing on
    its own, so call this between status checks instead of just waiting in the response text."""
    time.sleep(seconds)
    return f"Waited {seconds} second(s)."


agent = Agent(
    chat_generator=AnthropicChatGenerator(model="claude-opus-4-6"),
    tools=toolset + wait,
    system_prompt="""You are a document-processing assistant with access to Unstructured Transform MCP tools. Check the tools available to you and use whichever ones match the steps below by description, since exact tool names may change over time.

Transform jobs are asynchronous. When asked to process a document:
1. Submit the file reference(s) and the requested processing stages to start a processing job. This returns a job ID immediately; the job itself runs in the background.
2. Check the job's status. If it isn't complete yet, call the wait tool for a few seconds, then check again, repeating until it reports as complete.
3. Fetch the job's rendered output using its job ID, and summarize it for the user.
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
