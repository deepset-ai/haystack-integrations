---
layout: integration
name: ScrapeUnblocker
description: Scrape pages behind anti-bot protections and read Google search results with ScrapeUnblocker
authors:
    - name: ScrapeUnblocker
      socials:
        github: ScrapeUnblocker
pypi: https://pypi.org/project/scrapeunblocker-haystack
repo: https://github.com/ScrapeUnblocker/scrapeunblocker-haystack
type: Data Ingestion
report_issue: https://github.com/ScrapeUnblocker/scrapeunblocker-haystack/issues
logo: /logos/scrapeunblocker.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [ScrapeUnblockerFetcher](#scrapeunblockerfetcher)
  - [ScrapeUnblockerWebSearch](#scrapeunblockerwebsearch)
  - [In a Pipeline](#in-a-pipeline)
- [License](#license)

## Overview

[ScrapeUnblocker](https://www.scrapeunblocker.com) renders web pages in a real
browser behind anti-bot protections such as Cloudflare, DataDome, PerimeterX and
Akamai. Use it when an ordinary HTTP request returns a block page, a captcha, or
an empty JavaScript shell instead of the content you need.

The integration provides two components:

- [`ScrapeUnblockerFetcher`](#scrapeunblockerfetcher) - fetch URLs and return one
  Document per page, as HTML or AI-parsed structured JSON
- [`ScrapeUnblockerWebSearch`](#scrapeunblockerwebsearch) - search Google and
  return the organic results as Documents

You need a ScrapeUnblocker API key to use both. Get one at
[scrapeunblocker.com](https://www.scrapeunblocker.com) and expose it as
`SCRAPEUNBLOCKER_API_KEY`, which both components read by default.

## Installation

```bash
pip install scrapeunblocker-haystack
```

## Usage

### ScrapeUnblockerFetcher

Fetches URLs and returns one `Document` per page.

#### Basic Example

```python
from scrapeunblocker_haystack import ScrapeUnblockerFetcher

fetcher = ScrapeUnblockerFetcher()
result = fetcher.run(urls=["https://example.com"])

print(result["documents"][0].content[:200])
```

#### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | `SCRAPEUNBLOCKER_API_KEY` env var | ScrapeUnblocker API key |
| `parsed_data` | `False` | Return AI-parsed structured JSON instead of raw HTML |
| `proxy_country` | `None` | Two-letter country code for the exit IP |
| `time_sleep` | `None` | Seconds to wait after load before capturing |
| `base_url` | `https://api.scrapeunblocker.com` | API base URL |
| `timeout` | `180` | HTTP timeout in seconds |
| `raise_on_failure` | `False` | Raise instead of skipping a URL that fails |

By default a URL that cannot be fetched is logged and skipped, so one bad URL
does not discard the rest of the batch.

### ScrapeUnblockerWebSearch

Searches Google and returns the organic results as Documents, with the snippet as
content and `title` / `link` / `position` in the metadata.

#### Basic Example

```python
from scrapeunblocker_haystack import ScrapeUnblockerWebSearch

search = ScrapeUnblockerWebSearch(top_k=5)
result = search.run(query="best web scraping api")

for doc in result["documents"]:
    print(doc.meta["title"], doc.meta["link"])
```

#### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | `SCRAPEUNBLOCKER_API_KEY` env var | ScrapeUnblocker API key |
| `pages_to_check` | `1` | How many result pages to scrape |
| `proxy_country` | `None` | Two-letter country code for localised results |
| `top_k` | `None` | Keep at most this many results |

### In a Pipeline

Fetch a protected page and answer questions about it:

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from scrapeunblocker_haystack import ScrapeUnblockerFetcher

prompt = [
    ChatMessage.from_user(
        "Answer the question using the pages below.\n\n"
        "{% for doc in documents %}{{ doc.content }}\n{% endfor %}\n"
        "Question: {{ question }}"
    )
]

pipe = Pipeline()
pipe.add_component("fetcher", ScrapeUnblockerFetcher())
pipe.add_component("converter", HTMLToDocument())
pipe.add_component("prompt_builder", ChatPromptBuilder(template=prompt, required_variables="*"))
pipe.add_component("llm", OpenAIChatGenerator())

pipe.connect("fetcher.documents", "converter.sources")
pipe.connect("converter.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run(
    {
        "fetcher": {"urls": ["https://example.com"]},
        "prompt_builder": {"question": "What is this page about?"},
    }
)
print(result["llm"]["replies"][0].text)
```

Both components implement `to_dict()` and `from_dict()`, so pipelines using them
can be serialized and reloaded. The API key is stored as a Haystack `Secret`
reference rather than its value.

## License

`scrapeunblocker-haystack` is distributed under the terms of the
[Apache-2.0](https://github.com/ScrapeUnblocker/scrapeunblocker-haystack/blob/main/LICENSE)
license.
