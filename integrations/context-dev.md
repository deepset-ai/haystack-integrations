---
layout: integration
name: Context.dev
description: Search the live web and fetch webpages as Haystack Documents with Context.dev.
authors:
    - name: Context.dev
      socials:
        github: context-dot-dev
pypi: https://pypi.org/project/context-dev-haystack
repo: https://github.com/context-dot-dev/context-haystack
type: Search & Extraction
report_issue: https://github.com/context-dot-dev/context-haystack/issues
logo: /logos/context-dev.svg
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Context.dev](https://context.dev) provides web search and page retrieval APIs. The Context.dev-maintained [Haystack integration](https://github.com/context-dot-dev/context-haystack) includes `ContextWebSearch` for retrieving search results, `ContextFetcher` for converting known URLs to Markdown Documents, and `ContextCrawler` for bounded website crawling.

## Installation

```bash
pip install context-dev-haystack
```

Create an API key in the [Context.dev dashboard](https://context.dev/dashboard/api-keys) and set the `CONTEXT_API_KEY` environment variable:

```bash
export CONTEXT_API_KEY="your-api-key"
```

## Usage

### Search the web

`ContextWebSearch` returns Haystack `Document` objects containing search descriptions and metadata, including the title and source URL. It also returns source URLs in `links`. Set `include_markdown=True` to request page content with the search results.

```python
from haystack_integrations.components.websearch.context import ContextWebSearch

search = ContextWebSearch(top_k=5)
result = search.run(query="What is Haystack by deepset?")

documents = result["documents"]
links = result["links"]
```

### Fetch a known URL

`ContextFetcher` returns the retrieved Markdown in each Document's `content` and the source URL in its `meta` dictionary.

```python
from haystack_integrations.components.fetchers.context import ContextFetcher

fetcher = ContextFetcher()
result = fetcher.run(urls=["https://haystack.deepset.ai"])

documents = result["documents"]
```

Both components support `run_async()`. See the [package documentation](https://github.com/context-dot-dev/context-haystack#readme) for asynchronous usage, search filters, and crawling options.

## License

`context-dev-haystack` is distributed under the [Apache-2.0 license](https://github.com/context-dot-dev/context-haystack/blob/main/LICENSE).
