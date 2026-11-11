---
layout: integration
name: Zambo
description: Give Haystack agents 153 tools behind one MCP endpoint, with a verifiable receipt for every job
authors:
  - name: Zambo
    socials:
      github: zambodotdev
      twitter: zambodotdev
pypi: https://pypi.org/project/zambo-haystack/
report_issue: https://github.com/zambodotdev/zambo-mcp/issues
type: Tool Integration
toc: true
logo: /logos/zambo.svg
version: Haystack 2.0
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Zambo](https://zambo.dev) is the verifiable work layer for AI: 153 tools behind one MCP endpoint (https://zambo.dev/mcp), memory and handover across AIs, and a verifiable receipt for every job an agent does.

The `zambo-haystack` package turns Zambo tools into native Haystack tools, so a Haystack agent can call them like any other tool. Zambo executes each call itself and issues a verifiable AER-1 receipt for it: a public page carrying the tool name, the arguments, the observed result, a timestamp, and a SHA-256 fingerprint of the record. Anyone can open the receipt and check that the saved result was not changed after the fact. The receipt shows the work was recorded as it happened; it does not certify that the underlying data was right.

No account and no API key are needed. Free tier: 20 calls and 1 wrap-up free every day, and picking up in another AI is always free. A Day Pass is $0.99 for unlimited use for 24 hours.

## Installation

```bash
pip install zambo-haystack
```

## Usage

### Give an agent Zambo tools

Pick the tools your agent needs by name and hand them to the agent:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from zambo_haystack import zambo_tools

agent = Agent(
    chat_generator=OpenAIChatGenerator(),  # any Haystack chat generator works
    tools=zambo_tools(["live_price", "prompt_shield"]),
)
result = agent.run([{"role": "user", "content": "What is the live BTC price?"}])
```

Any Haystack chat generator works (`OpenAIChatGenerator` above needs `OPENAI_API_KEY`; the Zambo calls themselves need no account and no key).

### Work with the receipts

Every tool returned by `zambo_tool` appends the receipt URL to its result text, and records it in a registry you can query with `lookup_receipt(tool_name, arguments_json)`:

```python
from zambo_haystack import lookup_receipt

url = lookup_receipt("live_price", '{"symbol": "BTC"}')
print(url)  # https://zambo.dev/run/<id>
```

Or register a callback to capture each receipt as it is issued:

```python
from zambo_haystack import zambo_tool

price_tool = zambo_tool(
    "live_price",
    on_receipt=lambda tool, url: print(f"[receipt] {tool}: {url}"),
)
```

### License

`zambo-haystack` is released under the MIT license.
