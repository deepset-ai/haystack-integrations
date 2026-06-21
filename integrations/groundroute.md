---
layout: integration
name: GroundRoute
description: Route web search across six engines through one API, with price-based routing and automatic failover
authors:
    - name: GroundRoute
      socials:
        github: jp0xz
        twitter: groundroute
        linkedin: https://www.linkedin.com/company/groundroute
pypi: https://pypi.org/project/groundroute-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Search & Extraction
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/groundroute.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [GroundRouteWebSearch](#groundroutewebsearch)
- [License](#license)

## Overview

[GroundRoute](https://groundroute.ai) is a meta search layer: one API in front of six search engines (Serper, Brave, Exa, Tavily, Firecrawl, Perplexity). It routes each query to the cheapest engine that clears a quality bar and fails over to another engine if one is unavailable, so a search-heavy pipeline keeps running through a single provider's rate limit or outage. Pricing is gain-share: you keep about half of any cache savings and never pay more than going to a single engine direct.

This integration provides:
- [`GroundRouteWebSearch`](https://docs.haystack.deepset.ai/docs/groundroutewebsearch): searches the web through GroundRoute and returns results as Haystack `Document` objects along with source URLs.

You need a GroundRoute API key, which includes $10 of free credit with no card required, available at [groundroute.ai/keys](https://groundroute.ai/keys).

## Installation

```bash
pip install groundroute-haystack
```

## Usage

### GroundRouteWebSearch

`GroundRouteWebSearch` queries the GroundRoute search API and returns results as Haystack `Document` objects containing the content snippets and metadata (title, URL, and the engine each result came from). Source URLs are also returned separately.

#### Basic Example

```python
from haystack_integrations.components.websearch.groundroute import GroundRouteWebSearch

web_search = GroundRouteWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

By default, the component reads the API key from the `GROUNDROUTE_API_KEY` environment variable. You can also pass it explicitly:

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.groundroute import GroundRouteWebSearch

web_search = GroundRouteWebSearch(
    api_key=Secret.from_token("your-api-key"),
    top_k=5,
)
```

## License

`groundroute-haystack` is distributed under the terms of the Apache-2.0 license.
