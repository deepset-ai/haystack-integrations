---
layout: integration
name: LoopGrid
description: Signed, tamper-evident decision evidence for consequential Haystack Agent actions.
authors:
  - name: LoopGrid
    socials:
      github: loopgridio
pypi: https://pypi.org/project/loopgrid-haystack/
repo: https://github.com/loopgridio/loopgrid-haystack
report_issue: https://github.com/loopgridio/loopgrid-haystack/issues
type: Monitoring Tool
logo: /logos/loopgrid.png
version: Haystack 2.0
toc: true
---

## Overview

LoopGrid provides signed, tamper-evident decision evidence for consequential Haystack Agent actions.

The [`loopgrid-haystack`](https://pypi.org/project/loopgrid-haystack/) package integrates with Haystack's native Agent hooks and tracing interfaces so applications can preserve evidence around an agent decision without moving tool execution or authorization into LoopGrid.

LoopGrid is designed to complement Haystack rather than replace Haystack's Agent runtime, tool execution, or human-in-the-loop controls.

Typical evidence captured for a consequential Agent decision includes:

- agent identity and version
- delegated authority supplied by the application
- model and context provenance
- application policy and policy version
- explicit human approval or rejection when applicable
- the surviving tool request
- actual Haystack-owned tool execution
- an authoritative downstream outcome supplied by the application
- signed, tamper-evident verification evidence

The evidence lifecycle is:

```text
decision_created
→ policy_evaluated
→ model_completed
→ human_approved / human_rejected when applicable
→ tool_requested
→ tool_executed
→ model_completed
→ outcome_observed
→ evidence_complete
→ cryptographic verification
```

LoopGrid does **not** execute tools, invent delegated authority, invent policy, infer reviewer identity, infer human approval from successful tool execution, or infer a real-world outcome merely because a Haystack tool returned successfully.

The current `loopgrid-haystack` v0.1.0 release targets Haystack 3.3.x and supports both synchronous and asynchronous Agent execution.

Documentation:

- [LoopGrid Haystack integration guide](https://loopgrid.io/integrations/haystack/)
- [GitHub repository](https://github.com/loopgridio/loopgrid-haystack)
- [PyPI package](https://pypi.org/project/loopgrid-haystack/)

### Native Haystack integration surfaces

The integration uses two Haystack-native boundaries for different evidence facts.

**Haystack `Tracer` / `Span`**

Completed `haystack.agent.step.llm` spans are mapped to LoopGrid `model_completed` evidence.

**Agent `before_tool` / `after_tool` hooks**

The Agent hooks record the tool request that actually survives Haystack's pre-tool controls and then record the resulting tool execution.

This distinction is intentional. LoopGrid does not use Haystack tool tracing spans as authoritative action evidence when Agent hooks provide the execution boundary directly.

### Human-in-the-loop behavior

Haystack's native `ConfirmationHook` remains responsible for controlling whether a tool executes.

Confirmation, rejection, or modification hooks are placed before LoopGrid's `before_tool` hook.

That means:

```text
model proposes tool call
        ↓
ConfirmationHook / other application controls
        ↓
rejected call
    → no LoopGrid tool_requested event

or

modified/approved call
        ↓
LoopGrid before_tool
        ↓
tool_requested
        ↓
actual Haystack tool execution
        ↓
tool_executed
```

A modified call is therefore recorded using the final parameters that survive confirmation.

Human reviewer identity is not inferred from the fact that the tool ran. The application records the authenticated reviewer explicitly with `record_human_review()`.

### Privacy

The integration defaults to:

```python
capture_content=False
```

When content capture is disabled, model span tags and tool input/output payloads are represented with SHA-256 commitments rather than raw content.

Applications should only enable content capture when their own privacy and data-handling policy permits it.

## Installation

Install the integration from PyPI:

```bash
pip install loopgrid-haystack
```

Current compatibility:

```text
Python >=3.10
haystack-ai >=3.3.0,<3.4
loopgrid >=0.8.0,<0.9
```

A running LoopGrid Core service is required to record and verify evidence.

The v0.1.0 release was validated against:

```text
haystack-ai 3.3.0
loopgrid 0.8.0
LoopGrid Core 0.8.1-design-partner
```

## Usage

### Deterministic Haystack Agent example

The following example uses a scripted Haystack chat generator so it exercises the real Haystack Agent and Tool runtime without requiring a model-provider API request.

It assumes LoopGrid Core is available at:

```text
http://127.0.0.1:8000
```

```python
from __future__ import annotations

from typing import Any

from haystack import component
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage, ToolCall
from haystack.tools import Tool
from loopgrid import LoopGrid

from loopgrid_haystack import LoopGridHaystack


@component
class ScriptedChatGenerator:
    def __init__(self) -> None:
        self.calls = 0

    @component.output_types(replies=list[ChatMessage])
    def run(
        self,
        messages: list[ChatMessage],
        tools: Any = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self.calls += 1

        if self.calls == 1:
            return {
                "replies": [
                    ChatMessage.from_assistant(
                        tool_calls=[
                            ToolCall(
                                id="call_refund_1",
                                tool_name="sandbox_refund",
                                arguments={"amount": 25},
                            )
                        ],
                        meta={"model": "scripted-haystack"},
                    )
                ]
            }

        return {
            "replies": [
                ChatMessage.from_assistant(
                    "Sandbox refund completed.",
                    meta={"model": "scripted-haystack"},
                )
            ]
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ScriptedChatGenerator",
            "init_parameters": {},
        }


client = LoopGrid(
    base_url="http://127.0.0.1:8000",
    workspace_id="default",
)

loopgrid = LoopGridHaystack(
    client=client,
    workspace_id="default",
    agent_id="support-agent",
)

# Haystack tracing is enabled explicitly.
loopgrid.enable_tracing()

decision = loopgrid.start_decision(
    decision_type="sandbox_refund",
    agent={
        "id": "support-agent",
        "version": "1",
    },
    authority={
        "acting_for": "Example Store",
        "scope": ["refund:create"],
        "limit_usd": 100,
    },
    model={
        "provider": "scripted",
        "name": "scripted-haystack",
    },
    context={
        "prompt_version": "support-v1",
    },
    proposed_action={
        "tool": "sandbox_refund",
        "amount": 25,
        "currency": "USD",
    },
    policy={
        "policy_id": "refund-policy",
        "version": "1",
        "decision": "auto_allowed",
    },
    metadata={
        "sandbox": True,
        "real_money_moved": False,
    },
)

decision_id = decision["decision_id"]


def sandbox_refund(amount: int) -> dict:
    return {
        "status": "succeeded",
        "sandbox": True,
        "real_money_moved": False,
        "amount": amount,
    }


tool = Tool(
    name="sandbox_refund",
    description="Execute a sandbox-only refund simulation",
    parameters={
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
            }
        },
        "required": ["amount"],
    },
    function=sandbox_refund,
)

agent = Agent(
    chat_generator=ScriptedChatGenerator(),
    tools=[tool],
    hooks=loopgrid.agent_hooks(decision_id),
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Handle the sandbox refund."
        )
    ]
)

# Ensure queued tracing/hook evidence reached LoopGrid.
loopgrid.flush()
loopgrid.assert_healthy()

print(result["last_message"].text)

# Record the authoritative downstream outcome only after
# the application has actually observed it.
loopgrid.record_outcome(
    decision_id,
    {
        "status": "succeeded",
        "sandbox": True,
        "real_money_moved": False,
        "external_reference": "sandbox-refund-1",
    },
    observer="billing-system",
)
```

The resulting action path is:

```text
Haystack Agent
→ model_completed
→ tool_requested
→ Haystack executes the tool
→ tool_executed
→ application observes downstream result
→ outcome_observed
```

LoopGrid then exposes the completed decision evidence and cryptographic verification through LoopGrid Core.

### Human approval with `ConfirmationHook`

For consequential operations that require human review, continue using Haystack's native `ConfirmationHook`.

The confirmation hook must be placed before LoopGrid's request hook:

```python
agent = Agent(
    chat_generator=chat_generator,
    tools=tools,
    hooks=loopgrid.agent_hooks(
        decision_id,
        before_tool_prefix=[confirmation_hook],
    ),
)
```

When your application authenticates the reviewer and receives the review decision, record that fact explicitly:

```python
loopgrid.record_human_review(
    decision_id,
    reviewer="reviewer@example.com",
    approved=True,
    reason="Reviewed refund evidence",
)
```

This produces the evidence ordering:

```text
model_completed
→ human_approved
→ tool_requested
→ tool_executed
```

If `ConfirmationHook` rejects the call, the rejected tool does not become a LoopGrid `tool_requested` event.

If `ConfirmationHook` modifies the call, LoopGrid records the final tool arguments that survive confirmation.

### Existing Haystack tracing backends

Haystack exposes a process-level tracing facade.

`LoopGridHaystack.enable_tracing()` is explicit and never runs automatically when the integration object is constructed.

```python
loopgrid.enable_tracing()
```

If your application already owns a concrete Haystack tracer backend, pass that concrete backend explicitly:

```python
loopgrid.enable_tracing(
    delegate=my_existing_haystack_tracer,
)
```

Do not pass Haystack's process-level tracing facade itself as the delegate.

### Synchronous and asynchronous Agents

`loopgrid-haystack` supports both:

```python
agent.run(...)
```

and:

```python
await agent.run_async(...)
```

The same decision isolation, tool correlation, privacy, and evidence semantics apply to both paths.

### Transport health

Model and tool evidence is queued so temporary LoopGrid transport failures do not raise through the Haystack Agent execution path.

Applications should explicitly validate evidence transport after an Agent run:

```python
loopgrid.flush()
loopgrid.assert_healthy()
```

A successful Haystack Agent run alone does not imply that evidence transport succeeded.

## Validation

`loopgrid-haystack` v0.1.0 was validated with:

- 29 automated integration and runtime tests
- real synchronous Haystack Agent runtime execution
- real asynchronous Haystack Agent runtime execution
- native `ConfirmationHook` approval behavior
- native `ConfirmationHook` rejection behavior
- native `ConfirmationHook` modification behavior
- parallel and repeated tool-call correlation
- privacy-default regression coverage
- concurrency isolation
- transport-failure observability
- real Haystack → LoopGrid Core end-to-end validation
- real human-approval → LoopGrid Core end-to-end validation
- `evidence_complete`
- 100% applicable evidence coverage
- successful cryptographic verification with no verification failures
- clean wheel and source distribution builds
- clean fresh PyPI installation

The deterministic release examples are available here:

- [Agent → LoopGrid Core E2E](https://github.com/loopgridio/loopgrid-haystack/blob/main/examples/core_e2e.py)
- [ConfirmationHook approval E2E](https://github.com/loopgridio/loopgrid-haystack/blob/main/examples/human_approval_e2e.py)

## Resources

- [LoopGrid Haystack documentation](https://loopgrid.io/integrations/haystack/)
- [LoopGrid Haystack GitHub repository](https://github.com/loopgridio/loopgrid-haystack)
- [loopgrid-haystack on PyPI](https://pypi.org/project/loopgrid-haystack/)
- [LoopGrid](https://loopgrid.io/)
- [Issue tracker](https://github.com/loopgridio/loopgrid-haystack/issues)

## License

`loopgrid-haystack` is released under the Apache-2.0 License.

See the [LICENSE](https://github.com/loopgridio/loopgrid-haystack/blob/main/LICENSE) file for details.
