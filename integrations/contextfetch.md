---
layout: integration
name: ContextFetch
description: Search the web and fetch pages as Markdown with the ContextFetch API
authors:
    - name: ContextFetch
      socials:
        github: lachy3433
pypi: https://pypi.org/project/contextfetch-haystack/
repo: https://github.com/lachy3433/contextfetch-haystack
report_issue: https://github.com/lachy3433/contextfetch-haystack/issues
type: Search & Extraction
version: Haystack 2.0+ and 3.0
toc: true
logo: /logos/contextfetch.svg
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[ContextFetch](https://contextfetch.dev) is a web search and web-page-to-Markdown API for AI agents. This integration
provides two components:

- `ContextFetchWebSearch`: searches the web and returns the results as Documents, with page content as Markdown.
  By default each Document holds the page pruned to the parts relevant to the query.
- `ContextFetchFetcher`: fetches a list of URLs and returns one Markdown Document per page that loaded.

See the [ContextFetch API reference](https://contextfetch.dev/docs/reference) for the underlying endpoints.

## Installation

```bash
pip install contextfetch-haystack
```

Set your API key in the `CONTEXTFETCH_API_KEY` environment variable. Without a key, requests use the keyless tier,
which has a small daily allowance per IP. Get a key at [contextfetch.dev/get-started](https://contextfetch.dev/get-started).

```bash
export CONTEXTFETCH_API_KEY="your-api-key"
```

## Usage

### Web search

```python
from haystack_integrations.components.websearch.contextfetch import ContextFetchWebSearch

websearch = ContextFetchWebSearch(top_k=3)
result = websearch.run(query="What are asyncio task groups?")

for doc in result["documents"]:
    print(doc.meta["title"], doc.meta["url"])
print(result["links"])
```

`search_params` takes `include_domains`, `exclude_domains`, `start_published_date` and the content options `text`
(whole page), `highlights` (most relevant chunks) and `pruned_context`:

```python
websearch = ContextFetchWebSearch(top_k=5, search_params={"include_domains": ["docs.python.org"], "text": True})
```

### Fetch pages

```python
from haystack_integrations.components.fetchers.contextfetch import ContextFetchFetcher

fetcher = ContextFetchFetcher()
result = fetcher.run(urls=["https://docs.python.org/3/library/asyncio-task.html"])
print(result["documents"][0].content[:500])
```

URLs that fail to load are skipped with a warning.

### License

`contextfetch-haystack` is distributed under the terms of the
[Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
