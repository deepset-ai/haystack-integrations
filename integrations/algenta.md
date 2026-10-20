---
layout: integration
name: Algenta
description: Governed decision-engine tools for Haystack agents — connect a self-hosted Algenta engine over MCP with observe/govern/execute tool profiles, execution receipts, and typed policy denials
authors:
    - name: thyn-ai
      socials:
        github: thyn-ai
pypi: https://pypi.org/project/haystack-algenta/
repo: https://github.com/thyn-ai/algenta-integrations/tree/main/python/haystack-algenta
type: Tool Integration
report_issue: https://github.com/thyn-ai/algenta-integrations/issues
version: Haystack 3.0
toc: true
mcp: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Algenta](https://algenta.ai) is a governed decision engine: it evaluates decision scenarios under
explicit contracts and policies, and it gates real-world execution behind named policy checks,
producing an execution receipt for every attempt. `haystack-algenta` is the community-maintained
integration that connects a Haystack `Agent` to your own self-hosted Algenta Engine over the
[Model Context Protocol](https://modelcontextprotocol.io/), built on Haystack's own `MCPToolset`
(from the `mcp-haystack` package).

The integration provides two pieces:

- `create_algenta_tools` — returns a Haystack `Toolset` exposing only the tools allowed by the
  selected governance profile, filtered at connection time via `MCPToolset(tool_names=...)` so
  excluded tools never reach the model. Operator/break-glass fields (`force`, `override_safety`)
  are stripped from both the advertised tool schemas and the arguments forwarded to each call.
- `build_algenta_governance_hooks` — an `Agent` `after_tool` hook that parses the synchronous
  outcome of `execute_decision` and raises a typed `AlgentaToolDenied` when the engine blocks a
  call, naming the gate that denied it. Successful executions are left untouched, and the
  execution receipt stays available in the tool result for your audit trail.

The governance profiles:

| Profile | Tools exposed | Notes |
|---|---|---|
| `observe` (default) | `get_contract`, `query_data`, `simulate`, `recommend` | Read-only. |
| `govern` | + `plan_decision`, `log_decision` | Propose and record decisions; never executes. |
| `execute` | + `execute_decision` | Real-world execution, gated by engine policy. |
| `full` | Everything the connected engine advertises | Opt-in; admin/ops tooling. |

A blocked `execute_decision` call names exactly one of three gates: `"idempotency"` (the decision
was already delivered), `"confidence"` (below the policy's minimum confidence), or `"risk_floor"`
(below the policy's risk floor). The denial is synchronous — there is no asynchronous "pending"
state to poll.

## Installation

```bash
pip install haystack-algenta
```

Requires Python 3.10 or newer, a running self-hosted Algenta Engine reachable over MCP, and an API
key for your chat model provider (for example `OPENAI_API_KEY` for the `OpenAIChatGenerator` used
below). The engine endpoint resolves from the `base_url=` argument, the `ALGENTA_BASE_URL`
environment variable, or `http://localhost:8000/mcp` by default.

## Usage

An agent restricted to the read-only `observe` profile:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_algenta import create_algenta_tools

toolset = create_algenta_tools(base_url="http://localhost:8000/mcp", profile="observe")
agent = Agent(chat_generator=OpenAIChatGenerator(), tools=toolset)
result = agent.run(messages=[ChatMessage.from_user("What's the expected value of scenario X?")])
print(result["messages"][-1].text)
toolset.close()
```

An agent allowed to execute decisions, with the governance hook wired so a policy denial surfaces
as a typed exception instead of an ordinary tool error:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_algenta import AlgentaToolDenied, build_algenta_governance_hooks, create_algenta_tools

toolset = create_algenta_tools(base_url="http://localhost:8000/mcp", profile="execute")
agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    hooks=build_algenta_governance_hooks(),
)

try:
    result = agent.run(messages=[ChatMessage.from_user("Execute decision decision-123.")])
except AlgentaToolDenied as denial:
    print(denial.gate)  # one of "idempotency", "confidence", "risk_floor"
```

For `Pipeline` use or direct `Tool.invoke()` calls (where `Agent` hooks do not apply),
`haystack_algenta.extract_execution_outcome_from_tool_result` parses any tool result into either
an `ExecutionReceipt` or an `ExecutionBlocked` so you can handle the outcome yourself. See the
[package README](https://github.com/thyn-ai/algenta-integrations/tree/main/python/haystack-algenta)
for the full denial-mapping semantics and a no-live-engine local walkthrough.

## License

`haystack-algenta` is distributed under the terms of the
[Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
