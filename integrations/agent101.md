---
layout: integration
name: agent101
description: Search 300+ AI tools across 15 categories. MCP server for AI agent tool discovery.
authors:
  - name: Ventify AI
    socials:
      github: rachelsu-blip
      website: https://ventify.ai
type: Tool
repo: https://github.com/rachelsu-blip/agent101-mcp
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Agent101](https://github.com/rachelsu-blip/agent101-mcp) is an MCP (Model Context Protocol) server for AI agent tool discovery. It provides a searchable directory of 300+ AI tools organized across 15 categories, enabling AI agents to dynamically discover and select the right tools for any task.

With Agent101, your Haystack pipelines can leverage intelligent tool discovery to find the most relevant AI tools based on natural language queries, categories, or specific capabilities.

## Installation

```bash
pip install agent101-mcp
```

## Usage

Agent101 runs as an MCP server that AI agents can query to discover tools. It supports searching by keyword, filtering by category, and retrieving detailed tool information.

```python
from agent101_mcp import Agent101Server

# Start the MCP server
server = Agent101Server()

# Search for tools by query
results = server.search_tools("image generation")

# Filter tools by category
tools = server.get_tools_by_category("text-to-image")

# Get detailed information about a specific tool
tool_info = server.get_tool_details("tool-name")
```

You can integrate Agent101 into your Haystack pipelines to dynamically discover and use the best AI tools for your specific use case.
