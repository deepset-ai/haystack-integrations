---
layout: integration
name: Scavio
description: Search the web using Scavio, a unified search API for AI agents
authors:
    - name: Scavio
      socials:
        github: scavio-ai
repo: https://github.com/scavio-ai/haystack-scavio
pypi: https://pypi.org/project/scavio-haystack
type: Search & Extraction
report_issue: https://github.com/scavio-ai/haystack-scavio/issues
logo: /logos/scavio.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [ScavioWebSearch](#scaviowebsearch)
  - [Parameters](#parameters)
- [Beyond web search](#beyond-web-search)
- [License](#license)

## Overview

[Scavio](https://scavio.dev) is a unified search API built for AI agents. One key reaches
real-time data across Google, Amazon, Walmart, Target, eBay, Home Depot, YouTube, Reddit, TikTok,
TikTok Shop, Instagram, X, Threads, Kuaishou, LinkedIn, Indeed, Glassdoor, Zillow, Redfin,
Booking.com, Airbnb, Tripadvisor, Yelp, the Apple App Store, Google Play, SEC EDGAR, Companies
House, G2, Capterra, Google Ads Transparency and the Meta Ad Library, plus an extract endpoint
that turns any URL into HTML, Markdown or plain text. Everything comes back as structured JSON,
with no scraping or proxies to run.

This integration is deliberately small. It ships **one** component:

- `ScavioWebSearch`: searches the web using Scavio's Google web search endpoint and returns
  results as Haystack `Document` objects along with source URLs.

That makes it a drop-in peer of Haystack's other web-search components, so it slots into an
existing pipeline without rewiring. The rest of Scavio's coverage is reachable from Haystack as
well, but through the MCP server or the Python SDK rather than as one component per endpoint --
see [Beyond web search](#beyond-web-search).

You need a Scavio API key to use this integration. You can get one at
[dashboard.scavio.dev](https://dashboard.scavio.dev/sign-up).

## Installation

```bash
pip install scavio-haystack
```

## Usage

### ScavioWebSearch

`ScavioWebSearch` queries the Scavio search API and returns results as Haystack `Document` objects
containing the content snippets and metadata (title, URL). Source URLs are also returned separately.

Set your API key as the `SCAVIO_API_KEY` environment variable.

#### Basic Example

```python
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

web_search = ScavioWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

#### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

async def main():
    web_search = ScavioWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

### Parameters

The component takes three arguments:

- **`api_key`**: API key for Scavio. Defaults to the `SCAVIO_API_KEY` environment variable.
- **`top_k`**: Maximum number of results to return. Defaults to 10.
- **`search_params`**: Additional parameters forwarded to the Scavio Google search endpoint. Set
  them once on the constructor, or pass `search_params` to `run` / `run_async` to replace them for
  a single call.

#### `search_params` keys

| Key | Description |
| --- | --- |
| `gl` | Country of the search, ISO 3166-1 alpha-2 (e.g. `us`). |
| `hl` | UI language, ISO 639-1 (e.g. `en`). |
| `start` | Result **offset**, not a page number: `0` is the first page, `10` the second, and so on up to `990`. |
| `google_domain` | Regional Google domain (e.g. `google.co.uk`). |
| `location` | Canonical location name; encoded to a UULE string for you. |
| `uule` | Pre-encoded UULE location string. Takes priority over `location`. |
| `device` | `desktop` or `mobile`. |
| `lr` | Language restrict (e.g. `lang_en`). |
| `cr` | Country restrict (e.g. `countryUS`). |
| `safe` | Set to `active` to enable SafeSearch. |
| `nfpr` | `True` disables spelling correction and auto-fixes. |
| `filter` | `"0"` disables the omitted / similar-results filter. |
| `time_period` | One of `last_hour`, `last_day`, `last_week`, `last_month`, `last_year`. |
| `resolve_ai_overview` | Resolve a deferred AI Overview. Enabled server-side by default. |

```python
web_search = ScavioWebSearch(
    top_k=5,
    search_params={"gl": "de", "hl": "de", "time_period": "last_week"},
)
```

#### Legacy keys

Earlier versions of this page documented a different set of names. Three of them are still
accepted and translated for you, so existing pipelines keep working:

| Legacy key | Translated to |
| --- | --- |
| `country_code` | `gl` |
| `language` | `hl` |
| `page` | `start`, as `(page - 1) * 10` |

Two more, `search_type` and `light_request`, belonged to a retired version of the endpoint. They
are accepted but ignored -- passing them has no effect on the request. Drop them.

## Beyond web search

`scavio-haystack` wraps a single endpoint on purpose. To reach the rest of Scavio's coverage from
a Haystack agent, use either:

- the **MCP server** at [mcp.scavio.dev](https://mcp.scavio.dev), which exposes the full endpoint
  set as tools to any MCP-capable agent; or
- the **Python SDK** (`pip install scavio`), called from a custom Haystack component or a
  `@tool`-decorated function.

The endpoint reference lives at [scavio.dev/docs](https://scavio.dev/docs).

## License

`scavio-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
