---
layout: integration
name: Proxmint
description: Fetch web pages through residential, datacenter and mobile proxies with country, city and ASN targeting, and get them back as Documents
authors:
    - name: Proxmint
      socials:
        github: proxmint
pypi: https://pypi.org/project/proxmint-haystack
repo: https://github.com/proxmint/proxmint-haystack
type: Data Ingestion
report_issue: https://github.com/proxmint/proxmint-haystack/issues
logo: /logos/proxmint.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [ProxmintFetcher](#proxmintfetcher)
  - [In a Pipeline](#in-a-pipeline)
  - [As an Agent Tool](#as-an-agent-tool)
- [License](#license)

## Overview

[Proxmint](https://proxmint.com?utm_source=haystack&utm_medium=integration&utm_campaign=haystack-integration) sells residential, premium residential, datacenter and 4G/5G mobile proxies by the GB, with
packs that never expire. Use this integration when a pipeline or an agent has to read pages as a visitor from a
specific country or city, or when one IP address gets rate limited.

The integration provides one component:

- [`ProxmintFetcher`](#proxmintfetcher) - fetch a list of URLs through a Proxmint proxy and return one `Document`
  per page, as readable text or raw HTML

Requests go straight from your machine to the Proxmint gateway, and the bandwidth comes out of your own Proxmint
account. You need an API key (Settings in the [dashboard](https://proxmint.com/dashboard?utm_source=haystack&utm_medium=integration&utm_campaign=haystack-integration)), exposed as `PROXMINT_API_KEY`, which the component reads by default.
The key looks up the proxy login of the product you choose, so there is nothing else to copy.

Full guide: [proxmint.com/docs/haystack](https://proxmint.com/docs/haystack?utm_source=haystack&utm_medium=integration&utm_campaign=haystack-integration).

## Installation

```bash
pip install proxmint-haystack
```

## Usage

### ProxmintFetcher

Fetches URLs and returns one `Document` per page, plus the list of URLs that failed.

```python
from haystack_integrations.components.fetchers.proxmint import ProxmintFetcher

fetcher = ProxmintFetcher(country="gb")  # reads PROXMINT_API_KEY
result = fetcher.run(urls=["https://example.com", "https://example.org"])

print(result["documents"][0].content)  # readable page text
print(result["documents"][0].meta)     # source, requested_url, status, title, content_type, country
print(result["failed_urls"])
```

Useful options:

| Option | Default | What it does |
| --- | --- | --- |
| `product` | `"residential"` | `residential`, `premium-residential`, `datacenter` or `mobile` |
| `country` | any | Exit country as a two-letter code. `run(urls, country=...)` overrides it for one run |
| `state`, `city`, `zip_code`, `asn` | none | Finer targeting inside the country |
| `session_minutes` | none | Keep one exit IP across runs for 1 to 120 minutes. Default: a new IP for every URL |
| `output` | `"text"` | `"text"` for readable text, `"html"` for the raw page |
| `raise_on_failure` | `False` | Raise on a failed URL instead of listing it in `failed_urls` |

### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.fetchers.proxmint import ProxmintFetcher

store = InMemoryDocumentStore()
pipe = Pipeline()
pipe.add_component("fetcher", ProxmintFetcher(country="us", city="New York", session_minutes=30))
pipe.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
pipe.add_component("writer", DocumentWriter(store))
pipe.connect("fetcher.documents", "splitter.documents")
pipe.connect("splitter.documents", "writer.documents")

pipe.run({"fetcher": {"urls": ["https://example.com/pricing", "https://example.org/pricing"]}})
```

### As an Agent Tool

```python
from haystack.tools import ComponentTool
from haystack_integrations.components.fetchers.proxmint import ProxmintFetcher

tool = ComponentTool(
    component=ProxmintFetcher(),
    name="fetch_pages",
    description="Fetch web pages through a proxy in a chosen country and return their text.",
)
```

Pass the tool to an `Agent` or a chat generator as usual. The model can set `urls` and an optional `country`
on each call.

### License

`proxmint-haystack` is distributed under the terms of the [MIT](https://github.com/proxmint/proxmint-haystack/blob/main/LICENSE) license.
