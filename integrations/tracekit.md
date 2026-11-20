---
layout: integration
name: Tracekit
description: Allow, deny or hold each Agent tool call by policy, and keep a signed record of the run that can be verified offline
authors:
    - name: Cygnux Labs
      socials:
        github: Cygnux-Labs
pypi: https://pypi.org/project/tracekit-ai/
repo: https://github.com/Cygnux-Labs/Tracekit
type: Custom Component
report_issue: https://github.com/Cygnux-Labs/Tracekit/issues
logo: /logos/tracekit.png
version: Haystack 3.4
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [What it records and what it doesn't](#what-it-records-and-what-it-doesnt)
- [License](#license)

## Overview

[Tracekit](https://github.com/Cygnux-Labs/Tracekit) checks every tool call a Haystack `Agent` makes before the tool runs: a separate signer process allows the call, denies it, or holds it until a person approves, and a refused call never runs. Every call, decision and result goes into a signed, hash-chained log, and each run exports as one file that anyone can check offline with `tracekit verify`.

## Installation

```bash
pip install tracekit-ai "haystack-ai>=3.4,<3.5"
```

The Haystack integration is new in tracekit-ai 1.3 and is tested with Haystack 3.4 (Python 3.11 or later).

## Usage

### Components

This integration adds one hook, `Tracekit`. Register the same instance at `before_tool` and at `after_tool`, last in each list. At `before_tool` it asks the signer to decide each tool call the model asked for. At `after_tool` it records what each call returned.

### Gate an Agent's tool calls

`Client()` connects to the local Tracekit signer and starts a dev signer if none is running. The example runs offline: Haystack's `MockChatGenerator` stands in for the model and asks for two shell commands.

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import MockChatGenerator
from haystack.dataclasses import ChatMessage, ToolCall
from haystack.tools import tool

from tracekit.integrations.haystack import Tracekit
from tracekit.sdk.client import Client


@tool
def Bash(command: str) -> str:
    """Run a shell command."""
    return f"(pretend) ran {command}"


# Stands in for an LLM: first it asks for two shell commands, then it answers.
model = MockChatGenerator(responses=[
    ChatMessage.from_assistant(tool_calls=[
        ToolCall(tool_name="Bash", arguments={"command": "ls build"}, id="call-1"),
        ToolCall(tool_name="Bash", arguments={"command": "sudo rm -rf build"}, id="call-2"),
    ]),
    "Done.",
])

with Client().run(agent="haystack-agent") as run:
    tk = Tracekit(run)
    agent = Agent(chat_generator=model, tools=[Bash], hooks={"before_tool": [tk], "after_tool": [tk]})
    result = agent.run(messages=[ChatMessage.from_user("Clean up the build directory.")])

for message in result["messages"]:
    if message.tool_call_result:
        r = message.tool_call_result
        print(f"{r.origin.arguments['command']!r}: {r.result}")
```

It prints:

```text
'sudo rm -rf build': Tool call blocked by Tracekit policy: TK-D001, TK-F003
'ls build': (pretend) ran ls build
```

`ls build` ran. The default policy denies `sudo` (rule TK-D001; TK-F003 only labels the command destructive), so that tool never ran. The model got Tracekit's reason as an error tool result in its place, and the run went on. A rule that says `ask` holds the call until someone runs `tracekit approvals approve <id>`, and refuses it if nobody answers within 5 minutes.

Then export and check the run:

```bash
tracekit last        # exports the latest run to a .tkb file and verifies it
tracekit view --dev  # browse runs: calls, decisions, approvals
```

With a real model, pass any chat generator, for example `OpenAIChatGenerator()`, in place of `MockChatGenerator`. The default policy maps the tool name `Bash` to its shell rules. To decide your own tools, map them in a policy file ([policy reference](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/policy-v2.md)). The repository has a longer [offline example](https://github.com/Cygnux-Labs/Tracekit/tree/main/examples/v2/haystack) that also shows a held call being approved.

## What it records and what it doesn't

It records:

- each tool call the model asked for, under its call id, with the model's arguments and the decision;
- each result as the model reads it, and a tool that raised as an error;
- approvals, bound to the exact arguments they approved and used once.

It covers `Agent.run` and `Agent.run_async`, sync and async tools, `ComponentTool`, `PipelineTool`, `AgentTool` and the tools of a `Toolset`.

It doesn't cover:

- Calls a sub-agent makes, unless the sub-agent has the hook too. The outer agent's hook decides the call to an `AgentTool`; give the sub-agent the same `tk`.
- Tools the model provider runs itself, such as the built-in `web_search` of `OpenAIResponsesChatGenerator` or a remote MCP server. They never reach the hooks.
- Values passed between tools through the agent's state (`outputs_to_state`, `inputs_from_state`). They are not the model's arguments and are not decided.
- Calls a `before_tool` hook listed after Tracekit adds. List Tracekit last. A call such a hook changes still runs, but is recorded as an error.
- Serialization. The hook holds a live run, so `to_dict` and `dumps` on an agent or pipeline that holds it raise `SerializationError`. Build it in code.

An `ask` holds its whole step: Haystack runs a step's calls only after every `before_tool` hook returns. With `raise_on_tool_invocation_failure=True`, a tool that raises ends the run before `after_tool`, so that step's calls are recorded as decided but not completed.

The dev signer runs as your own user. It records what happened, but it can't stop an agent that runs as you from reaching its key. For tamper resistance, run the signer as another user, in a container or on another host ([deployment](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/deploy.md)). The full list of cases is in the [integration guide](https://github.com/Cygnux-Labs/Tracekit/blob/main/docs/integrations/haystack.md).

## License

Tracekit is released under the [MIT license](https://github.com/Cygnux-Labs/Tracekit/blob/main/LICENSE).
