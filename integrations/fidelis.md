---
layout: integration
name: Fidelis Memory
description: Local-first, zero-LLM agent memory for Haystack agents — BM25, dense-vector, and reciprocal-rank-fusion retrieval that returns original passages verbatim through a Model Context Protocol server.
authors:
    - name: Hermes Labs
      socials:
        github: hermes-labs-ai
pypi: https://pypi.org/project/fidelis-memory/
repo: https://github.com/hermes-labs-ai/fidelis
type: Custom Component
report_issue: https://github.com/hermes-labs-ai/fidelis/issues
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

[Fidelis](https://github.com/hermes-labs-ai/fidelis) is a local-first memory and retrieval service for AI agents. It stores notes and session context locally (`~/.cogito/`) and retrieves them with BM25, dense-vector, and reciprocal-rank-fusion (RRF) scoring, returning the original stored passages verbatim rather than paraphrasing them. The default retrieval path makes no LLM call.

Fidelis ships as an MCP server (`fidelis mcp serve`, stdio transport) and is already published on the [official MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.hermes-labs-ai%2Ffidelis-memory/versions/0.1.0) as `io.github.hermes-labs-ai/fidelis-memory`. A Haystack agent can connect to it the same way it connects to any other MCP server, using Haystack's own `mcp-haystack` integration (`MCPTool`/`MCPToolset` with `StdioServerInfo`), to give the agent a private, verbatim-recall memory backend instead of a hosted memory platform.

On a checked-in 470-question LongMemEval-S retrieval run, Fidelis measured 83.2% R@1.

## Installation

```bash
pip install fidelis-memory mcp-haystack
```

## Usage

```python
from haystack_integrations.tools.mcp import MCPTool, StdioServerInfo

server_info = StdioServerInfo(
    command="uvx",
    args=["--from", "fidelis-memory", "fidelis", "mcp", "serve"],
)
tool = MCPTool(name="fidelis_memory", server_info=server_info)

# Use directly, or add `tool` to a Haystack Agent's tools list
result = tool.invoke(query="what did we decide about the retrieval backend?")
```

See the [Fidelis README](https://github.com/hermes-labs-ai/fidelis#readme) for the full MCP tool surface and the [user-fit matrix](https://github.com/hermes-labs-ai/fidelis/blob/main/docs/user-fit.md) for supported workflows and prerequisites.

## License

MIT — see the [Fidelis repository](https://github.com/hermes-labs-ai/fidelis/blob/main/LICENSE).
