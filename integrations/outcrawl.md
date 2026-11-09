---
layout: integration
name: Outcrawl
description: Search the web and fetch pages as Markdown with Outcrawl
authors:
    - name: Outcrawl
      socials:
        github: outcrawlai
pypi: https://pypi.org/project/outcrawl-haystack
repo: https://github.com/outcrawlai/outcrawl-haystack
type: Data Ingestion
report_issue: https://github.com/outcrawlai/outcrawl-haystack/issues
logo: /logos/outcrawl.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [OutcrawlWebSearch](#outcrawlwebsearch)
  - [OutcrawlFetcher](#outcrawlfetcher)
- [License](#license)

## Overview

[Outcrawl](https://outcrawl.ai) is web infrastructure for AI agents. This integration provides two components:

- `OutcrawlWebSearch`: runs a web search through the Outcrawl Search API and returns the results as Haystack `Document`s, plus their links.
- `OutcrawlFetcher`: loads each URL in a browser through the Outcrawl Scrape API, so JavaScript-rendered pages work, and returns the page as a Markdown `Document`.

You need an Outcrawl API key, which you create at [outcrawl.ai/console](https://outcrawl.ai/console). The free plan includes credits every month. Set it as the `OUTCRAWL_API_KEY` environment variable.

## Installation

```bash
pip install outcrawl-haystack
```

## Usage

### OutcrawlWebSearch

```python
from haystack_integrations.components.websearch.outcrawl import OutcrawlWebSearch

search = OutcrawlWebSearch(top_k=5)
result = search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

### OutcrawlFetcher

```python
from haystack_integrations.components.fetchers.outcrawl import OutcrawlFetcher

fetcher = OutcrawlFetcher()
result = fetcher.run(urls=["https://docs.haystack.deepset.ai/docs/intro"])
documents = result["documents"]
```

Both components also have `run_async`. See the [source repository](https://github.com/outcrawlai/outcrawl-haystack) for details.

## License

`outcrawl-haystack` is distributed under the terms of the [Apache-2.0](https://github.com/outcrawlai/outcrawl-haystack/blob/main/LICENSE) license.
