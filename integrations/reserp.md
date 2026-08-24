---
layout: integration
name: Reserp
description: Minimal Google Search API passthrough for Haystack
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

[`Reserp`](https://reserp.ai/) is a Google Search API that accepts a complete Google Search URL and returns visible result blocks as structured JSON.

`ReserpWebSearch` preserves Reserp as an unopinionated primitive inside Haystack. One component invocation makes one API request and exposes the public JSON response. Retries, timeouts, task queues, concurrency, caching, observability, and pagination remain under the pipeline's control.

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

- `ReserpWebSearch`: sends one complete Google Search URL to Reserp and exposes the public response under the `response` output.

```python
from haystack_integrations.components.websearch.reserp import ReserpWebSearch

search = ReserpWebSearch()
result = search.run(
    url="https://www.google.com/search?q=haystack+ai&gl=us&hl=en"
)

print(result["response"])
```

See the complete [Reserp API documentation](https://reserp.ai/docs) for request, response, errors, and pagination.

## License

`reserp-haystack` is distributed under the MIT license.
