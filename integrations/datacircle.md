---
layout: integration
name: Datacircle
description: Give a Haystack Agent tools to find the best GTM APIs and compare their plans, from Datacircle's free API with no key
authors:
    - name: Datacircle
      socials:
        github: waynehamadi
        linkedin: https://www.linkedin.com/company/datacircle-org
pypi: https://pypi.org/project/datacircle-haystack
repo: https://github.com/waynehamadi/datacircle-haystack
report_issue: https://github.com/waynehamadi/datacircle-haystack/issues
type: Tool Integration
logo: /logos/datacircle.png
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/datacircle-haystack.svg)](https://pypi.org/project/datacircle-haystack)

-----

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

Find the best GTM APIs. We benchmark all the GTM APIs and we put the results on our website, [datacircle.dev](https://datacircle.dev).

`datacircle-haystack` gives a Haystack [`Agent`](https://docs.haystack.deepset.ai/docs/agent) four [Tools](https://docs.haystack.deepset.ai/docs/tool) that call our public API, `https://api.datacircle.dev/v1`. You need no key and no account.

## Installation

```bash
pip install datacircle-haystack
```

The package needs Haystack 2.15 or later (`haystack-ai`) and Python 3.10 or later.

## Usage

### Components

This integration introduces four tools and a toolset:

- `datacircle_list_apis`: every GTM API on Datacircle, with the API's slug, number of plans, number of providers and best plan (`GET /apis`).
- `datacircle_best_plans`: one API's plans, sorted by score out of 100, best first. Each plan comes with a rank and a price per 1,000 calls (`GET /apis/{slug}/best`).
- `datacircle_search_plans`: plans that match a provider or plan name, on all APIs or on one API, sorted by score, provider or price (`GET /plans`).
- `datacircle_provider`: the APIs a provider sells, and the provider's rank on each API (`GET /providers/{slug}`).
- `DatacircleToolset`: the four tools, ready for an `Agent`. To give the agent fewer tools, list their names: `DatacircleToolset(tool_names=["datacircle_best_plans"])`.

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.datacircle import DatacircleToolset

agent = Agent(chat_generator=OpenAIChatGenerator(), tools=DatacircleToolset())
agent.warm_up()
result = agent.run(messages=[ChatMessage.from_user("Which email finder API is best for under $5 per 1,000?")])
print(result["last_message"].text)
```

`OpenAIChatGenerator` reads your key from `OPENAI_API_KEY`. Any Haystack chat generator that calls tools works the same way.

You can also use the toolset in an `Agent` inside a pipeline. On Haystack 2, you can pass the toolset to a chat generator's `tools` and to a `ToolInvoker`. Set `raise_on_failure=False` on the `ToolInvoker` so the model sees the error message. Save a pipeline and Haystack stores the toolset as a list of tool names.

### Call a tool yourself

Each tool returns our API's answer as a dict:

```python
from haystack_integrations.tools.datacircle import datacircle_tool

print(datacircle_tool("datacircle_best_plans").invoke(slug="email-finder", limit=3))
```

The model gets each answer as JSON. If the model passes an unknown slug, the tool raises a `DatacircleError` with the API's error message. For an unknown API slug, the message lists every valid slug. The Agent gives the message to the model, and the model can call the tool again.

The API takes up to 60 calls a minute from one IP address.

## License

`datacircle-haystack` is distributed under the terms of the MIT license.
