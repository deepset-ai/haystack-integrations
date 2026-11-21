---
layout: integration
name: Reserp
description: Google Search API v2 for Haystack
authors:
    - name: Reserp
      socials:
        github: reserp-ai
        twitter: reserp_ai
        linkedin: https://www.linkedin.com/company/reserp-ai
pypi: https://pypi.org/project/reserp-haystack
repo: https://github.com/reserp-ai/reserp-haystack
type: Search & Extraction
report_issue: https://github.com/reserp-ai/reserp-haystack/issues
logo: /logos/reserp.png
version: Haystack 2.0
toc: true
---

## Overview

[`Reserp`](https://reserp.ai/) is a Google Search API that accepts a complete Google Search URL. API v2 offers flat search results and a separate structured SERP response.

`ReserpWebSearch` uses `POST /v2/serp/search`. One component invocation makes one API request and exposes the public JSON response. Its `results[]` array is flat, page ordered, and deduplicated, with optional visible text for each URL. Retries, timeouts, task queues, concurrency, caching, observability, and pagination remain under the pipeline's control.

## Installation

```bash
pip install reserp-haystack
```

Set the API key in the environment:

```bash
export RESERP_API_KEY='your-api-key'
```

## Usage

### Components

- `ReserpWebSearch`: sends one complete Google Search URL to the v2 Search endpoint and exposes the public response under the `response` output.

```python
from haystack_integrations.components.websearch.reserp import ReserpWebSearch

search = ReserpWebSearch()
response = search.run(
    url="https://www.google.com/search?q=haystack+ai&gl=us&hl=en"
)["response"]

if response["ok"]:
    for item in response["results"]:
        print(item.get("text"), item["url"])
```

Every successful response includes `pagination.next_url`. Submit it in a later component call to advance, but do not treat its presence as proof that another page contains results or infer pagination from `len(response["results"])`.

Version 0.3 adopts the stable Search endpoint and its flat `results[]` response. It also exposes the v2 field names `request.url`, `page.url`, `pagination.next_url`, and `billing_source`. For typed, page-ordered SERP blocks and explicit positions, use Reserp's structured v2 endpoint or an official Reserp SDK.

See the complete [Reserp API documentation](https://reserp.ai/docs) for request, response, errors, and pagination.

## License

`reserp-haystack` is distributed under the MIT license.
