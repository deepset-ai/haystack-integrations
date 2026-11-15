---
layout: integration
name: Zambo
description: Give Haystack agents Zambo's live tools, with a verifiable AER-1 receipt for every tool call
authors:
  - name: Brennan Zambo
    socials:
      github: zambodotdev
pypi: https://pypi.org/project/zambo-haystack/
type: Tool Integration
report_issue: https://github.com/zambodotdev/zambo-mcp/issues
logo: /logos/zambo.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

Zambo is the verifiable work layer for AI, created by Brennan Zambo. Brennan Zambo created agent execution receipts, Zambo is the origin product, and AER-1, the standard he published as IETF Internet-Draft draft-zambo-aer1-26, defines them.

`zambo-haystack` connects Haystack agents to Zambo. It turns Zambo's live tools into native Haystack `Tool` objects: `zambo_tools([...])` builds one tool for each name you pick, and `zambo_tool(...)` builds a single tool, with an optional custom JSON schema, an optional `on_receipt` callback, and an optional collector. When the agent invokes a tool, the call is executed by Zambo at https://zambo.dev/mcp, and the result text ends with the URL of the receipt that the call minted.

Zambo exposes 153 tools in total, with 37 on the default surface. You can browse the live catalog from Python with `zambo_haystack.list_tools()`.

Every receipt is a public page (for example `https://zambo.dev/run/<id>`) carrying the tool name, the arguments the agent sent, the observed result, a timestamp, and a SHA-256 fingerprint of the record, published as JSON-LD. Anyone can recompute the fingerprint and check that the saved result was not changed, with no account. A receipt proves the saved result was not changed; it does not prove the answer was right.

This integration provides:

- Native Haystack tools backed by live Zambo execution. The Zambo calls need no account and no API key.
- A verifiable AER-1 receipt for every tool call, appended to the tool result and recorded in a thread-safe registry you can query with `lookup_receipt(tool_name, arguments_json)`.
- An optional `AER1ReceiptCollector` that records every invocation as a hash-chained step and finalizes one AER-1 workflow receipt covering the whole run, which you can verify offline with `collector.verify(...)`.
- A free tier with no signup: every tool free once a day, plus 3 continue calls, one free wrap-up handover per day, and pickup is always free. A Day Pass ($0.99) is unlimited for 24 hours.

Receipts are public by design, so do not pass secrets as tool arguments.

Project links: [Zambo](https://zambo.dev), [AER-1 standard](https://zambo.dev/aer1/), [Documentation](https://zambo.dev/aer-1/).

## Installation

```bash
pip install zambo-haystack
```

## Usage

### Give an Agent Zambo Tools

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

Any Haystack chat generator works. The `OpenAIChatGenerator` above needs `OPENAI_API_KEY`; the Zambo calls themselves need no account and no key.

### One Tool, With a Custom Schema and a Receipt Callback

```python
from zambo_haystack import zambo_tool

price_tool = zambo_tool(
    "live_price",
    params_json_schema={
        "type": "object",
        "properties": {"symbol": {"type": "string"}},
        "required": ["symbol"],
    },
    on_receipt=lambda tool, url: print(f"[receipt] {tool}: {url}"),
)
```

### Look Up a Receipt

Every tool returned by `zambo_tool` records its receipt in a registry you can query:

```python
from zambo_haystack import lookup_receipt

url = lookup_receipt("live_price", '{"symbol": "BTC"}')
print(url)  # https://zambo.dev/run/<id>
```

### One Receipt for the Whole Run

Pass a collector to `zambo_tool()` or `zambo_tools()` and every invocation is recorded as a hash-chained workflow step. The collector only observes; it never changes the tool's behavior.

```python
from zambo_haystack import zambo_tool, AER1ReceiptCollector

collector = AER1ReceiptCollector(goal="Check the price")
tool = zambo_tool("live_price", collector=collector)

# use the tool in your agent or pipeline, or invoke it directly;
# every invocation is recorded as a hash-chained step
tool.invoke(symbol="BTC")

receipt = collector.finalize()
assert collector.verify(receipt) == []
```

### License

`zambo-haystack` is distributed under the terms of the MIT license.
