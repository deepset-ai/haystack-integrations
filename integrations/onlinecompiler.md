---
layout: integration
name: OnlineCompiler.io
description: Run code in 46 languages in a sandbox with no network, and judge it against test cases, as MCP tools in a Haystack Agent
authors:
    - name: OnlineCompiler.io
      socials:
        github: onlinecompiler-io
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/onlinecompiler-io/onlinecompiler-mcp
type: Tool Integration
report_issue: https://github.com/onlinecompiler-io/onlinecompiler-mcp/issues
logo: /logos/onlinecompiler.png
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

[OnlineCompiler.io](https://onlinecompiler.io) runs programs in 46 languages, among them Python, JavaScript, Java, C, C++, Go, Rust and SQL. Each run happens in a fresh gVisor sandbox with no network access, so code that an agent writes never runs on the machine where the agent runs. Besides running a single program, it can judge a program against test cases (an input and the expected output for each) and return a verdict for every test and a score.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack `Agent` to the [OnlineCompiler.io MCP server](https://onlinecompiler.io/mcp-code-execution), either the hosted one over Streamable HTTP or the same server started locally over stdio. The server provides these tools:

| Tool | What it does |
| --- | --- |
| `list_compilers` | Lists the compiler ids (languages and versions) that the other tools accept, such as `python-3.14`, `g++-15` or `openjdk-25` |
| `run_code` | Runs one program with optional standard input and returns its output, errors, exit code, time and memory |
| `run_tests` | Runs one program against up to 10 test cases and returns a verdict for each test, an overall verdict and a score |
| `judge_problem` | Judges a program against a problem stored in your OnlineCompiler.io account and returns a verdict, a score and a signed receipt |

Typical uses are agents that check the code they write before they answer, tutoring and grading agents, and agents that need a language not installed where they run.

## Installation

```bash
pip install mcp-haystack
```

Get a free API key: sign in at [OnlineCompiler.io](https://onlinecompiler.io) and create one under **API keys** (key type API). The free plan needs no card. Set it as an environment variable:

```bash
export ONLINECOMPILER_API_KEY="your-onlinecompiler-api-key"
```

## Usage

### Connect to the hosted server

The hosted server takes the API key as a bearer token, which `StreamableHttpServerInfo` sends through its `token` parameter:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(
    url="https://api.onlinecompiler.io/mcp",
    token=Secret.from_env_var("ONLINECOMPILER_API_KEY"),
)
toolset = MCPToolset(server_info=server_info, eager_connect=True, invocation_timeout=60)

for tool in toolset.tools:
    print(f"{tool.name}: {tool.description}")
```

A program may run for up to 30 seconds, so an `invocation_timeout` of 60 seconds leaves room for the round trip.

### Run the server locally

The same server is on PyPI as [`onlinecompiler-mcp`](https://pypi.org/project/onlinecompiler-mcp/). With [uv](https://docs.astral.sh/uv/) installed, `StdioServerInfo` starts it for you. The programs still run on OnlineCompiler.io, not on your machine:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

server_info = StdioServerInfo(
    command="uvx",
    args=["onlinecompiler-mcp", "--transport", "stdio"],
    env={"ONLINECOMPILER_API_KEY": Secret.from_env_var("ONLINECOMPILER_API_KEY")},
)
toolset = MCPToolset(server_info=server_info, eager_connect=True, invocation_timeout=60)
```

### Call a tool directly

Each tool can also be called without an agent, for example from a pipeline component that grades a submission:

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.onlinecompiler.io/mcp",
        token=Secret.from_env_var("ONLINECOMPILER_API_KEY"),
    ),
    tool_names=["run_tests"],
    eager_connect=True,
    invocation_timeout=60,
)
run_tests = toolset.tools[0]

result = run_tests.invoke(
    compiler="python-3.14",
    code="a, b = map(int, input().split())\nprint(a + b)",
    tests=[
        {"input": "2 3", "expected_output": "5"},
        {"input": "10 -4", "expected_output": "6"},
    ],
)
print(result)
```

The result holds a JSON object with `"verdict": "accepted"`, `"score": 100.0` and one entry per test.

## Examples

This agent writes a program, runs it with `run_code` and answers from the real output. `tool_names` limits the toolset to the three tools that need nothing stored in your account:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.onlinecompiler.io/mcp",
        token=Secret.from_env_var("ONLINECOMPILER_API_KEY"),
    ),
    tool_names=["list_compilers", "run_code", "run_tests"],
    invocation_timeout=60,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt=(
        "You are a coding assistant. Before you answer, run the code you write with run_code "
        "and base your answer on its real output. Use list_compilers to find a compiler id."
    ),
    max_agent_steps=10,
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Write a Go program that prints the first 10 Fibonacci numbers, run it, "
            "and show me the program and its output."
        )
    ]
)
print(result["last_message"].text)
```

To grade code instead, ask the agent to check a solution with `run_tests` and give it the test cases. More on the tools, limits and response fields is in the [OnlineCompiler.io MCP docs](https://onlinecompiler.io/mcp-code-execution) and the [API docs](https://onlinecompiler.io/docs).

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The `onlinecompiler-mcp` server is [MIT licensed](https://github.com/onlinecompiler-io/onlinecompiler-mcp). OnlineCompiler.io itself is a hosted service governed by its own [terms](https://onlinecompiler.io/terms).
