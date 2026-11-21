---
layout: integration
name: Agent Threat Rules
description: Check an Agent's tool calls and tool results against open, local detection rules for agent attacks
authors:
    - name: Agent Threat Rules
      socials:
        github: Agent-Threat-Rule
repo: https://github.com/Agent-Threat-Rule/haystack-atr
type: Custom Component
report_issue: https://github.com/Agent-Threat-Rule/haystack-atr/issues
version: Haystack 3.4
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Agent Threat Rules](https://github.com/Agent-Threat-Rule/agent-threat-rules) (ATR) is an MIT-licensed set of detection rules for attacks on AI agents, such as prompt injection in tool results, tool calls that open a reverse shell, and attempts to read or send credentials. Each rule is YAML with its own true-positive and true-negative test cases.

`haystack-atr` runs these rules locally with the [pyatr](https://pypi.org/project/pyatr/) engine: no network calls and no API key. It uses the Agent hooks Haystack already provides:

- `ATRToolCallStrategy`: a confirmation strategy for `ConfirmationHook` that rejects a pending tool call when a high or critical rule in its blocking lane matches.
- `ATRToolResultHook`: an `after_tool` hook that replaces a tool result with an error before the model reads it, when a high or critical rule in its blocking lane matches.
- `ATRMessageScanner`: a pipeline component that scans user messages and tool results and returns the findings and a `blocked` flag.

## Installation

`haystack-atr` is not on PyPI yet. Install it from the repository (Haystack 3.4 or later):

```bash
pip install "haystack-atr @ git+https://github.com/Agent-Threat-Rule/haystack-atr"
```

## Usage

```python
from haystack.components.agents import Agent
from haystack.hooks.human_in_the_loop import ConfirmationHook
from haystack_atr import ATRToolCallStrategy, ATRToolResultHook

agent = Agent(
    chat_generator=...,
    tools=[...],
    hooks={
        "before_tool": [ConfirmationHook({"*": ATRToolCallStrategy()})],
        "after_tool": [ATRToolResultHook()],
    },
)
```

A rejected tool call does not run, and the model receives a tool result naming the rules that matched. Because `ATRToolCallStrategy` is a confirmation strategy, it can share one `ConfirmationHook` with human approval for specific tools. A tool with its own entry uses that strategy instead of the `"*"` ATR entry, so its calls are not checked by ATR.

Rules have a maturity, and `block_lane` chooses which ones may block: `"enforce"` (stable rules, the default), `"alert"` (stable and test rules, which catch more and also block some ordinary content) or `None` to only log findings. See the [README](https://github.com/Agent-Threat-Rule/haystack-atr#lanes-and-blocking) for what each setting blocked in our tests, including false positives on benign text. We suggest starting with `block_lane=None` and an `on_finding` callback.

## License

`haystack-atr` and the rules are released under the MIT license.
