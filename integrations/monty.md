---
layout: integration
name: Monty
description: Let a Haystack Agent run Python code in Monty, a minimal and secure Python sandbox written in Rust by Pydantic
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/monty-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/monty
type: Tool Integration
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/monty-haystack.svg)](https://pypi.org/project/monty-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/monty-haystack.svg)](https://pypi.org/project/monty-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/monty.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/monty.yml)

-----

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Security model](#security-model)
- [License](#license)

## Overview

[Monty](https://pydantic.dev/docs/monty/) is a minimal, secure Python interpreter written in Rust by
[Pydantic](https://pydantic.dev/), built to run code written by AI. It avoids the latency, complexity, and cost of a
container-based sandbox: a new sandbox starts in under a millisecond from a running pool, on your own machine, with no
service to set up and no API key.

The `monty-haystack` integration wraps Monty as a Haystack [`Tool`](https://docs.haystack.deepset.ai/docs/tool) that an
[`Agent`](https://docs.haystack.deepset.ai/docs/agent) can invoke to run Python code. Use it for calculations, data
processing, and anything else that is more reliable to compute than for the LLM to guess. The tool returns what the code
printed, the value of its last expression, and any error as a traceback, so the LLM can read the result and fix its code.

## Installation

```bash
pip install monty-haystack
```

## Usage

### Components

This integration introduces the following:

- `MontyPythonTool`: A Haystack `Tool` named `run_python` that takes a single `code` parameter. It keeps a pool of Monty
  worker processes and runs every call in a fresh interpreter, so nothing leaks between calls, users, or concurrent tool
  invocations. Its default description tells the LLM which subset of Python and the standard library Monty supports.

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.tools.monty import MontyPythonTool

# Requires the OPENAI_API_KEY environment variable
tool = MontyPythonTool()
agent = Agent(chat_generator=OpenAIChatGenerator(), tools=[tool])

result = agent.run(messages=[ChatMessage.from_user("What is the sum of the first 100 prime numbers?")])
print(result["last_message"].text)
# >> The sum of the first 100 prime numbers is 24133.

tool.close()
```

The Agent starts the pool of Monty workers on `warm_up()`. Call `close()` when you are done to shut the workers down.

### Run code without an Agent

Invoke the tool directly to see what the LLM will get back:

```python
from haystack_integrations.tools.monty import MontyPythonTool

tool = MontyPythonTool()

print(tool.invoke(code="import math\nprint('choosing 5 of 52 cards')\nmath.comb(52, 5)"))
# >> output:
# >> choosing 5 of 52 cards
# >>
# >> result:
# >> 2598960

print(tool.invoke(code="1 / 0"))
# >> error:
# >> Traceback (most recent call last):
# >>   File "<python-input-0>", line 1, in <module>
# >>     1 / 0
# >>     ~~~~~
# >> ZeroDivisionError: division by zero

tool.close()
```

### Configure resource limits and type checking

By default, each call can run for 30 seconds and use 256 MiB of heap memory. Pass `resource_limits` to change these
limits (set a key to `None` to disable it), and `type_check=True` to type-check the code with Monty's bundled type
checker before running it:

```python
from haystack_integrations.tools.monty import MontyPythonTool

tool = MontyPythonTool(
    resource_limits={"max_feed_duration_secs": 5.0, "max_memory": 64 * 1024 * 1024},
    type_check=True,
)
```

Other options are `name` and `description` for what the LLM sees, and `max_output_chars` (default `20000`) to cap how
much of the output, result, and error goes back to the LLM. `MontyPythonTool` is serializable, so Pipelines that use it
can be saved to and loaded from YAML.

### Supported Python

Monty supports a subset of Python: functions, lambdas, closures, comprehensions, simple classes, dataclasses,
`try`/`except`, f-strings, and `async`/`await`. Class inheritance, generators, `match`, `del`, method decorators, and
third-party packages are not supported. Only these standard library modules can be imported, some of them partially:
`asyncio`, `base64`, `binascii`, `collections`, `copy`, `dataclasses`, `datetime`, `functools`, `itertools`, `json`,
`math`, `random`, `re`, `sys`, `time`, `typing`, `unicodedata`. Variables, functions, and imports don't persist between
calls.

## Security model

Monty is a language-level sandbox: its interpreter implements no operation that reaches the host, so the code has no
access to files, the network, environment variables, or subprocesses. The code runs in worker subprocesses started with
an empty environment, so a crash never takes down the host process, and execution time and heap memory are capped by
`resource_limits`. The tool mounts no directories and exposes no host functions to the sandbox.

## License

`monty-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
Monty itself is distributed under the [MIT](https://github.com/pydantic/monty/blob/main/LICENSE) license.
