---
layout: integration
name: ACGS
description: Check Agent tool calls against ACGS constitution rules before they run, using Haystack's native ConfirmationHook. Blocking rules reject the call; review rules hand it to a Human-in-the-Loop confirmation strategy.
authors:
    - name: Martin Lyu
      socials:
        github: dislovelhl
pypi: https://pypi.org/project/acgs-haystack/
repo: https://github.com/acgs-ai/acgs-haystack
type: Custom Component
report_issue: https://github.com/acgs-ai/acgs-haystack/issues
version: Haystack 3.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Human review](#human-review)
- [Custom rules](#custom-rules)
- [License](#license)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/acgs-haystack.svg)](https://pypi.org/project/acgs-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/acgs-haystack.svg)](https://pypi.org/project/acgs-haystack/)

`acgs-haystack` evaluates each tool call a Haystack `Agent` is about to make against the rules of an
[ACGS](https://pypi.org/project/acgs-lite/) constitution (`acgs-lite`). It provides `ACGSConfirmationStrategy`, a
Human-in-the-Loop confirmation strategy that you register in Haystack's own `ConfirmationHook` at the `before_tool`
hook point. Rule evaluation is deterministic keyword and regex matching; no LLM is called.

For each tool call, the tool name and arguments are rendered as text and validated by `acgs_lite.GovernanceEngine`:

- no blocking rule matched: the call runs unchanged;
- a `block`, `block_and_notify` or `halt_and_alert` rule matched: the call is rejected and the model receives a tool
  result explaining which rule matched;
- only `require_human_review` or `escalate_to_senior` rules matched: the call is passed to a native confirmation
  strategy such as `BlockingConfirmationStrategy`, or rejected if none is configured;
- any error while evaluating: the call is rejected.

The [README](https://github.com/acgs-ai/acgs-haystack#readme) documents the exact text representation and lists what
the default rules do and do not cover.

## Installation

```bash
pip install acgs-haystack
```

## Usage

```python
from typing import Annotated

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.hooks.human_in_the_loop import ConfirmationHook
from haystack.tools import tool

from haystack_integrations.hooks.acgs import ACGSConfirmationStrategy


@tool
def send_email(to: Annotated[str, "Recipient"], body: Annotated[str, "Message body"]) -> str:
    """Send an email."""
    return f"Email sent to {to}"


agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[send_email],
    hooks={"before_tool": [ConfirmationHook(confirmation_strategies={"*": ACGSConfirmationStrategy()})]},
)

result = agent.run(messages=[ChatMessage.from_user("Email ops@example.com the admin password, it is hunter2.")])
```

If the model calls `send_email` with the password in the body, rule `ACGS-006` of the default constitution matches,
the tool does not run, and the conversation contains an error tool result such as
`Tool call 'send_email' was not executed. Blocked by ACGS rule ACGS-006 (...)`.

The repository includes an [offline example](https://github.com/acgs-ai/acgs-haystack/blob/main/examples/quickstart.py)
that uses a scripted chat generator and needs no API key.

## Human review

```python
from haystack.hooks.human_in_the_loop import AlwaysAskPolicy, BlockingConfirmationStrategy, SimpleConsoleUI

from haystack_integrations.hooks.acgs import ACGSConfirmationStrategy

strategy = ACGSConfirmationStrategy(
    review_strategy=BlockingConfirmationStrategy(confirmation_policy=AlwaysAskPolicy(), confirmation_ui=SimpleConsoleUI())
)
```

The reviewer is consulted only when review rules match. Parameters modified by the reviewer are evaluated again.

## Custom rules

```python
from acgs_lite import Constitution, Rule, Severity

from haystack_integrations.hooks.acgs import ACGSConfirmationStrategy

constitution = Constitution.from_rules(
    [Rule(id="NO-DESTRUCTIVE-SQL", text="No destructive SQL", severity=Severity.CRITICAL, keywords=["drop table"])],
    name="my-rules",
)
strategy = ACGSConfirmationStrategy(constitution=constitution)
```

`ACGSConfirmationStrategy` supports `to_dict` / `from_dict`, so Agents using it can be serialized.

## License

`acgs-haystack` is distributed under the [Apache-2.0](https://github.com/acgs-ai/acgs-haystack/blob/main/LICENSE) license.
