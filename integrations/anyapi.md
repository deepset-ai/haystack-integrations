---
layout: integration
name: AnyAPI
description: One key and one USD wallet for hundreds of data and scraping APIs, with free discovery components and five agent tools.
authors:
  - name: AnyAPI
    socials:
      github: getanyapi-com
repo: https://github.com/getanyapi-com/integrations/tree/main/anyapi-haystack
report_issue: https://github.com/getanyapi-com/integrations/issues
type: Tool Integration
logo: /logos/anyapi.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [In a pipeline](#in-a-pipeline)
  - [In an agent](#in-an-agent)
  - [Pricing](#pricing)
  - [Errors](#errors)
- [License](#license)

## Overview

[AnyAPI](https://getanyapi.com) is a marketplace for data and scraping APIs behind one key and
one USD wallet: Reddit, Instagram, TikTok, YouTube, X, LinkedIn, Facebook, Google search results,
Google Maps, Amazon, and clean JSON out of pages that block a plain fetch. Every API publishes a
normalized input and output JSON Schema, billing is pay per request in USD with no subscription,
and the provider is reported as AnyAPI.

`anyapi-haystack` is a thin adapter over the official
[`getanyapi`](https://pypi.org/project/getanyapi/) Python SDK. HTTP, authentication, retries,
pricing, and schema handling belong to that SDK and to the gateway behind it, so this package
adds no second source of truth for a price.

AnyAPI publishes hundreds of APIs. One component per API would exhaust an agent's context window
before it asked its first question, so this integration instead exposes the five that make up the
AnyAPI MCP server's discovery-then-run loop: search or list to find an API, describe it to read
its strict input schema, then run it.

Documentation lives at [getanyapi.com/docs](https://getanyapi.com/docs). Get a key at
[getanyapi.com](https://getanyapi.com) and set it once:

```bash
export ANYAPI_API_KEY="..."
```

## Installation

The package is not on PyPI yet. Install it from its directory in the source repository:

```bash
pip install "git+https://github.com/getanyapi-com/integrations.git#subdirectory=anyapi-haystack"
```

It requires Python 3.10 or newer and installs `haystack-ai` and the `getanyapi` SDK.

## Usage

### Components

Five components, imported from `haystack_integrations.components.connectors.anyapi`. Only
`AnyAPIRunAPI` spends anything.

| Component | Tool name | Charges? |
| --- | --- | --- |
| `AnyAPISearchAPIs` | `anyapi_search_apis` | no |
| `AnyAPIListAPIs` | `anyapi_list_apis` | no |
| `AnyAPIGetAPI` | `anyapi_get_api` | no |
| `AnyAPIRunAPI` | `anyapi_run_api` | yes |
| `AnyAPIGetBalance` | `anyapi_get_balance` | no |

Each one publishes its result as separate output sockets rather than one blob, so a pipeline can
wire each part where it belongs. `AnyAPIGetAPI` publishes `api`, plus `input_schema` (the input to
the next step of the loop) and `pricing` (what you read to bound spend). `AnyAPIRunAPI` publishes
`data`, `found`, `cost_usd`, `items`, `provider`, `result_id`, and `error`.

Every component takes an optional `api_key` as a Haystack `Secret`, defaulting to
`Secret.from_env_var("ANYAPI_API_KEY")`. Every component also implements `run_async` on the SDK's
async client, and `to_dict` / `from_dict`, so a pipeline containing them serializes to YAML with
the key kept as a `Secret` reference rather than a value.

### In a pipeline

Read the strict input schema and the price ceiling first, then run the API and hand its payload
straight to a downstream component. Input schemas are strict, so an unknown field is rejected
rather than ignored, and an input built from a description instead of a schema usually fails.

```python
import json

from haystack import Pipeline
from haystack.components.converters import OutputAdapter

from haystack_integrations.components.connectors.anyapi import AnyAPIGetAPI, AnyAPIRunAPI

SLUG = "reddit.trending_posts"

described = AnyAPIGetAPI().run(slug=SLUG)
if described["error"] is not None:
    raise SystemExit(f"could not describe {SLUG}: {described['error']}")
print("input schema:", json.dumps(described["input_schema"], indent=2))
print("ceiling for any run, USD:", described["pricing"]["failoverMaxUsd"])

pipe = Pipeline()
pipe.add_component("anyapi", AnyAPIRunAPI())
pipe.add_component("titles", OutputAdapter("{{ data.posts | map(attribute='title') | list }}", list))
pipe.connect("anyapi.data", "titles.data")

result = pipe.run({"anyapi": {"slug": SLUG, "input": {"limit": 2}}})
run = result["anyapi"]
if run["error"] is not None:
    raise SystemExit(f"run failed: {run['error']}")

print("provider:", run["provider"], "items:", run["items"], "costUsd:", run["cost_usd"])
print("titles:", result["titles"]["output"])
```

### In an agent

`anyapi_tools()` returns the same five as `ComponentTool`s carrying the AnyAPI MCP server's own
tool descriptions, and `ANYAPI_INSTRUCTIONS` is the system prompt that teaches the loop.

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.tools.anyapi import ANYAPI_INSTRUCTIONS, anyapi_tools

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=anyapi_tools(),
    system_prompt=ANYAPI_INSTRUCTIONS,
)

result = agent.run(messages=[ChatMessage.from_user("What is trending on r/python right now?")])
print(result["messages"][-1].text)
```

Each tool is also importable on its own, as `AnyAPISearchAPIsTool`, `AnyAPIListAPIsTool`,
`AnyAPIGetAPITool`, `AnyAPIRunAPITool`, and `AnyAPIGetBalanceTool`.

### Pricing

Prices are USD and are never scaled by this package. `AnyAPIGetAPI` publishes `pricing`, where
`pricing.from.maxUsd` is the most a first-choice run is billed and `pricing.failoverMaxUsd` is the
ceiling for any run, so spend is bounded before the call. A completed call reports its actual
charge on the `cost_usd` socket, and `AnyAPIGetBalance` reports the remaining wallet balance in
USD. Response shaping through `fields`, `max_items`, or `summary` never changes the charge.

### Errors

Every AnyAPI failure is caught at the component boundary and returned on the `error` socket as
`{"error": ..., "status": ..., "code": ..., "requestId": ...}`, so a failed call gives the agent
something recoverable instead of aborting the run. On that path the unknowable sockets are `None`
rather than a fabricated zero. Anything that is not an AnyAPI error propagates.

## License

`anyapi-haystack` is licensed under the
[MIT License](https://github.com/getanyapi-com/integrations/blob/main/LICENSE).

Questions or problems: [support@getanyapi.com](mailto:support@getanyapi.com), or open an issue at
[getanyapi-com/integrations](https://github.com/getanyapi-com/integrations/issues).
