---
layout: integration
name: E2B
description: Use E2B cloud sandboxes as tools in a Haystack Agent to run bash commands and read, write, and list files in an isolated Linux environment
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/e2b-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/e2b
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/e2b.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[E2B](https://e2b.dev/) provides secure, isolated cloud sandboxes that let LLM-powered agents execute
arbitrary code and shell commands without touching the host machine. The `e2b-haystack` integration
wraps the E2B SDK as a set of Haystack [Tools](https://docs.haystack.deepset.ai/docs/tool) that an
[`Agent`](https://docs.haystack.deepset.ai/docs/agent) can invoke to run bash commands and manage
files inside a shared sandbox.

All tools provided by the integration operate on the same live `E2BSandbox`, so files written by
one tool call are immediately available to the next — the agent can, for example, write a Python
script with `write_file`, execute it with `run_bash_command`, and read the result back with
`read_file`.

## Installation

```bash
pip install e2b-haystack
```

Set your [E2B API key](https://e2b.dev/) as an environment variable:

```bash
export E2B_API_KEY="your-e2b-api-key"
```

## Usage

### Components

This integration introduces the following tools and a toolset wrapper:

- `RunBashCommandTool`: Runs a bash command inside the sandbox and returns stdout, stderr, and exit code.
- `ReadFileTool`: Reads a file from the sandbox filesystem.
- `WriteFileTool`: Writes content to a file in the sandbox filesystem.
- `ListDirectoryTool`: Lists the contents of a directory inside the sandbox.
- `E2BToolset`: A bundle of all four tools sharing a single `E2BSandbox`, ready to plug into an `Agent`.

### Use with a Haystack Agent

The `E2BToolset` enables you to give an `Agent` access to a sandbox:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.tools.e2b import E2BToolset

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=E2BToolset(sandbox_template="base", timeout=120),
    system_prompt=(
        "You are a helpful coding assistant with access to a live Linux sandbox. "
        "Use the available tools freely to explore, write files, and run commands."
    ),
    max_agent_steps=10,
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Write a Python script to /tmp/primes.py that prints all prime numbers "
            "up to 50, run it, then read the file back so I can see both the script "
            "and its output."
        )
    ]
)

print(result["last_message"].text)
```

### Sharing a sandbox across individual tools

If you prefer to assemble the tools yourself, instantiate a single `E2BSandbox` and pass it to each
tool so they share the same environment:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.tools.e2b import (
    E2BSandbox,
    ListDirectoryTool,
    ReadFileTool,
    RunBashCommandTool,
    WriteFileTool,
)

sandbox = E2BSandbox()
tools = [
    RunBashCommandTool(sandbox=sandbox),
    ReadFileTool(sandbox=sandbox),
    WriteFileTool(sandbox=sandbox),
    ListDirectoryTool(sandbox=sandbox),
]

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=tools,
    max_agent_steps=15,
)

result = agent.run(
    messages=[ChatMessage.from_user("Generate the first 10 Fibonacci numbers using bash.")]
)
print(result["last_message"].text)
```

### License

`e2b-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.