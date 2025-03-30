---
layout: integration
name: Model Context Protocol - MCP
description: Haystack Tool Integration with the MCP
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mcp
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/mcp.png
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

MCP Haystack Integration adds support for the Model Context Protocol (MCP) to Haystack. MCP is an open protocol that standardizes how applications provide context to LLMs, similar to how USB-C provides a standardized way to connect devices.

This integration allows you to easily connect external tools and services to your Haystack pipelines using the Model Context Protocol, enabling more powerful and flexible agentic applications.

## Installation

```bash
pip install mcp-haystack
```

## Usage

```python
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo

# Create an MCP tool that connects to an HTTP server
server_info = SSEServerInfo(base_url="http://localhost:8000")
tool = MCPTool(name="my_tool", server_info=server_info)

# Use the tool
result = tool.invoke(param1="value1", param2="value2")
```

## Examples

Check out the examples directory to see practical demonstrations of how to integrate the MCPTool into Haystack's tooling architecture. These examples will help you get started quickly with your own agentic applications.

### What is uvx?

In some examples below, we use the `StdioServerInfo` class which relies on uvx behind the scenes. uvx is a convenient command from the uv package that runs Python tools in temporary, isolated environments. You only need to install uvx once, and it will automatically fetch any required packages on first use without needing manual installation.

### Example 1: MCP Server with SSE Transport

This example demonstrates how to create a simple calculator server using MCP and connect to it using the MCPTool with SSE transport.

**Step 1: Run the MCP Server**

First, run the [server](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/mcp/examples/mcp_sse_server.py) that exposes calculator functionality (addition and subtraction) via MCP:

```bash
python examples/mcp_sse_server.py
```

This creates a FastMCP server with two tools:

- `add(a, b)`: Adds two numbers
- `subtract(a, b)`: Subtracts two numbers

The server runs on http://localhost:8000 by default.

**Step 2: Connect with the MCP Client**

In a separate terminal, run the [client](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/mcp/examples/mcp_sse_client.py) that connects to the calculator server:

```bash
python examples/mcp_sse_client.py
```

The client creates MCPTool instances that connect to the server, inspect the tool specifications, and invoke the calculator functions remotely.

### Example 2: MCP with StdIO Transport

This [example](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/mcp/examples/mcp_stdio_client.py) shows how to use MCPTool with stdio transport to execute a local program directly:

```bash
python examples/mcp_stdio_client.py
```

The example creates an MCPTool that uses stdio transport with StdioServerInfo, which automatically uses uvx behind the scenes to run the mcp-server-time tool without requiring manual installation. It queries the current time in different timezones (New York and Los Angeles) by invoking the tool with different parameters.

This demonstrates how MCPTool can work with local programs without running a separate server process, using standard input/output for communication.

### Example 3: MCPTool in a Haystack Pipeline

This [example](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/mcp/examples/time_pipeline.py) showcases how to integrate MCPTool into a Haystack pipeline along with an LLM:



```python
from haystack import Pipeline
from haystack.components.converters import OutputAdapter
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.tools import ToolInvoker
from haystack.dataclasses import ChatMessage

from haystack_integrations.tools.mcp import MCPTool, StdioServerInfo

time_tool = MCPTool(
    name="get_current_time",
    server_info=StdioServerInfo(command="uvx", args=["mcp-server-time", "--local-timezone=Europe/Berlin"]),
)
pipeline = Pipeline()
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini", tools=[time_tool]))
pipeline.add_component("tool_invoker", ToolInvoker(tools=[time_tool]))
pipeline.add_component(
    "adapter",
    OutputAdapter(
        template="{{ initial_msg + initial_tool_messages + tool_messages }}",
        output_type=list[ChatMessage],
        unsafe=True,
    ),
)
pipeline.add_component("response_llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipeline.connect("llm.replies", "tool_invoker.messages")
pipeline.connect("llm.replies", "adapter.initial_tool_messages")
pipeline.connect("tool_invoker.tool_messages", "adapter.tool_messages")
pipeline.connect("adapter.output", "response_llm.messages")

user_input = "What is the time in New York? Be brief."  # can be any city
user_input_msg = ChatMessage.from_user(text=user_input)

result = pipeline.run({"llm": {"messages": [user_input_msg]}, "adapter": {"initial_msg": [user_input_msg]}})

print(result["response_llm"]["replies"][0].text)

```
When you run:
```bash
python examples/time_pipeline.py
```

The output will be something similar to:
```## The current time in New York is 1:57 PM.```

In a nutshell, this example creates a pipeline that:

1. Takes a user query about the current time in a city
2. Uses an LLM (GPT-4o-mini) to interpret the query and decide which tool to use
3. Invokes the MCP time tool with the appropriate parameters (using uvx behind the scenes)
4. Sends the tool's response back to the LLM to generate a final answer

This demonstrates how MCPTool can be seamlessly integrated into Haystack's agentic architecture, allowing LLMs to use external tools via the Model Context Protocol.

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
