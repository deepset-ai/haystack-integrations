---
layout: integration
name: Keenable
description: Web search and page fetch built for AI agents, keyless by default
authors:
    - name: Keenable
      socials:
        github: keenableai
pypi: https://pypi.org/project/keenable-haystack
repo: https://github.com/keenableai/keenable-haystack
report_issue: https://github.com/keenableai/keenable-haystack/issues
type: Data Ingestion
logo: /logos/keenable.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [KeenableWebSearch](#keenablewebsearch)
  - [KeenableFetcher](#keenablefetcher)
- [License](#license)

## Overview

[Keenable](https://keenable.ai) is a web search and page-fetch API built for AI
agents. This integration provides two components:

- `KeenableWebSearch`: searches the web and returns results as Haystack
  `Document` objects plus their URLs (`links`), the same output shape as the
  `SerperDevWebSearch` / `SearchApiWebSearch` integrations, so it drops into existing
  web-search pipelines.
- `KeenableFetcher`: fetches one or more URLs and returns their main content as
  Haystack `Document` objects (extracted to clean markdown server-side, so you
  don't need a separate `LinkContentFetcher` + `HTMLToDocument` step).

**Keyless by default.** With no API key, the components use Keenable's keyless
public endpoints — no signup required to try it. Set a `KEENABLE_API_KEY` to use
the authenticated endpoints (required for `mode="realtime"` and for higher rate
limits).

## Installation

```bash
pip install keenable-haystack
```

## Usage

### KeenableWebSearch

#### Basic Example

```python
from haystack_integrations.components.websearch.keenable import KeenableWebSearch

# No API key -> keyless public endpoint. Set KEENABLE_API_KEY to lift limits.
web_search = KeenableWebSearch(top_k=5)

result = web_search.run(query="latest developments in AI agents")
for doc in result["documents"]:
    print(doc.content)
print(result["links"])
```

You can pass an API key explicitly instead of using the environment variable:

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.keenable import KeenableWebSearch

web_search = KeenableWebSearch(api_key=Secret.from_token("your-api-key"), top_k=5)
```

#### Parameters

- **`api_key`**: Keenable API key. Defaults to the `KEENABLE_API_KEY` environment
  variable; when absent the keyless public endpoint is used.
- **`top_k`**: Keep at most this many results (applied client-side). `None` keeps all.
- **`mode`**: Default search mode, `"pro"` (deeper) or `"realtime"` (low latency,
  key required). Overridable per `run`.
- **`site`**: Default single-domain restriction (e.g. `"github.com"`). Overridable per `run`.

`run` also accepts optional per-query filters: `site`, `published_after`,
`published_before`, `acquired_after`, `acquired_before`, `mode`.

#### In a Pipeline

`KeenableWebSearch` is a drop-in for any web-search component — connect its
`documents` output downstream:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.websearch.keenable import KeenableWebSearch

pipe = Pipeline()
pipe.add_component("search", KeenableWebSearch(top_k=5))
pipe.add_component("prompt", PromptBuilder(template="Answer using:\n{{ documents }}"))
pipe.connect("search.documents", "prompt.documents")
```

### KeenableFetcher

`KeenableFetcher` fetches web pages via Keenable and returns their main content
as markdown. Pair it with `KeenableWebSearch`: discover URLs with search, then
read the full pages with the fetcher.

```python
from haystack_integrations.components.fetchers.keenable import KeenableFetcher

fetcher = KeenableFetcher()
result = fetcher.run(urls=["https://example.com/article"])
print(result["documents"][0].content)
```

Non-`http(s)` and private/internal URLs are rejected before sending, and (like
`LinkContentFetcher`) failed URLs are skipped by default — set
`raise_on_failure=True` to surface errors instead.

## License

`keenable-haystack` is distributed under the terms of the MIT license.
