---
layout: integration
name: boxd
description: Run Haystack Agent tools in boxd machines, isolated Ubuntu microVMs with a persistent disk, to execute bash commands and read, write, and list files
authors:
    - name: boxd
      socials:
        github: boxd-sh
pypi: https://pypi.org/project/boxd-haystack
repo: https://github.com/boxd-sh/boxd-haystack
type: Tool Integration
report_issue: https://github.com/boxd-sh/boxd-haystack/issues
logo: /logos/boxd.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[boxd](https://boxd.sh/?ref=haystack-integrations) runs machines: full Ubuntu 24.04 microVMs with a persistent
disk, Python, Node.js and Docker. The `boxd-haystack` package wraps the boxd Python SDK as Haystack
[Tools](https://docs.haystack.deepset.ai/docs/tool) that an [`Agent`](https://docs.haystack.deepset.ai/docs/agent)
calls to run bash commands and manage files in one machine.

All tools work on the same `BoxdSandbox`, so a file the agent writes with `write_file` is there for
`run_bash_command` and `read_file` in the next step. The tool names and arguments match the E2B integration,
so a prompt written for one works with the other.

Machines are created with network isolation on and never receive your boxd API key. A machine can be deleted
when the agent is done, or hibernated and picked up again later with its files and packages in place.

## Installation

```bash
pip install boxd-haystack
```

Create an API key at [app.boxd.sh/keys](https://app.boxd.sh/keys?ref=haystack-integrations) and set it:

```bash
export BOXD_API_KEY="bxd_..."
```

## Usage

### Components

This integration introduces the following tools and a toolset:

- `RunBashCommandTool`: runs a bash command in the machine and returns the exit code, stdout and stderr.
- `ReadFileTool`: reads a file from the machine.
- `WriteFileTool`: writes a file to the machine, creating parent directories.
- `ListDirectoryTool`: lists a directory in the machine.
- `BoxdToolset`: all four tools on one `BoxdSandbox`, ready to pass to an `Agent`.
- `BoxdSandbox.fork()`: a live copy of the machine for a second Agent.

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator

from boxd_haystack import BoxdToolset

toolset = BoxdToolset(delete_after=3600)
agent = Agent(
    chat_generator=AnthropicChatGenerator(model="claude-sonnet-5-5"),
    tools=toolset,
    system_prompt="You are a coding assistant with a Linux machine. Use the tools to write files and run commands.",
    max_agent_steps=10,
)

try:
    result = agent.run(
        messages=[ChatMessage.from_user("Write primes.py that prints the primes up to 50, run it, show the output.")]
    )
    print(result["last_message"].text)
finally:
    toolset.close()
```

### Keep a machine between runs

With `delete_on_close=False`, `close()` hibernates the machine instead of deleting it. Pass its id as
`machine_id` to use it again:

```python
from boxd_haystack import BoxdSandbox, ReadFileTool, WriteFileTool

first = BoxdSandbox(delete_on_close=False)
WriteFileTool(sandbox=first).invoke(path="notes.txt", content="kept on disk")
machine_id = first.active_machine_id
first.close()  # hibernates

later = BoxdSandbox(machine_id=machine_id)
print(ReadFileTool(sandbox=later).invoke(path="notes.txt"))  # kept on disk
later.close()  # hibernates again
```

`BoxdSandbox` also takes `from_snapshot` (start from a prepared boxd snapshot), `vcpu` and `memory`,
`environment_vars`, `labels`, `auto_suspend_timeout` and `delete_after`. See the
[package README](https://github.com/boxd-sh/boxd-haystack#configuration).

### License

`boxd-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
