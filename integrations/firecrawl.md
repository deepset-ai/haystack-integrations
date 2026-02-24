---
layout: integration
name: Firecrawl
description: Crawl websites and extract LLM-ready content using Firecrawl
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/firecrawl-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/firecrawl.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Firecrawl](https://firecrawl.dev) turns websites into LLM-ready data. It handles JavaScript rendering, anti-bot bypassing, and outputs clean Markdown. 

This integration provides a `FirecrawlCrawler` component that crawls one or more URLs and returns the content as Haystack `Document` objects. Crawling starts from each given URL and follows links to discover subpages, up to a configurable limit.

You need a Firecrawl API key to use this integration. You can get one at [firecrawl.dev](https://firecrawl.dev).

## Installation

```bash
pip install firecrawl-haystack
```

## Usage

### Components

This integration provides the following component:

- **`FirecrawlCrawler`**: Crawls URLs and their subpages, returning extracted content as Haystack Documents.

### Basic Example

```python
from haystack_integrations.components.fetchers.firecrawl import FirecrawlCrawler

crawler = FirecrawlCrawler(params={"limit": 5})
crawler.warm_up()

result = crawler.run(urls=["https://docs.haystack.deepset.ai/docs/intro"])
documents = result["documents"]
```

By default, the component reads the API key from the `FIRECRAWL_API_KEY` environment variable. You can also pass it explicitly:

```python
from haystack.utils import Secret
from haystack_integrations.components.fetchers.firecrawl import FirecrawlCrawler

crawler = FirecrawlCrawler(
    api_key=Secret.from_token("your-api-key"),
    params={"limit": 10, "scrape_options": {"formats": ["markdown"]}},
)
```

### Parameters

- **`api_key`**: API key for Firecrawl. Defaults to the `FIRECRAWL_API_KEY` environment variable.
- **`params`**: Parameters for the crawl request. Defaults to `{"limit": 1, "scrape_options": {"formats": ["markdown"]}}`. See the [Firecrawl API reference](https://docs.firecrawl.dev/api-reference/endpoint/crawl-post) for all available parameters. Without a limit, Firecrawl may crawl all subpages and consume credits quickly.

### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.fetchers.firecrawl import FirecrawlCrawler

async def main():
    crawler = FirecrawlCrawler(params={"limit": 5})
    crawler.warm_up()
    result = await crawler.run_async(urls=["https://docs.haystack.deepset.ai/docs/intro"])
    print(f"Crawled {len(result['documents'])} documents")

asyncio.run(main())
```

### License

`firecrawl-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
