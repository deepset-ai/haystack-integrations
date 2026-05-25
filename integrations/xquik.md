---
layout: integration
name: Xquik
description: Fetch public X/Twitter posts and user timelines as Haystack Documents.
authors:
    - name: Xquik
      socials:
        github: Xquik-dev
pypi: https://pypi.org/project/xquik-haystack/
repo: https://github.com/Xquik-dev/xquik-haystack
type: Search & Extraction
report_issue: https://github.com/Xquik-dev/xquik-haystack/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `xquik-haystack` package provides Haystack web search components for public X/Twitter data through the Xquik REST API.

It includes:

- `XquikTweetSearch`: searches public posts and returns Haystack `Document` objects.
- `XquikUserTweetsFetcher`: fetches recent public posts for an X user and returns Haystack `Document` objects.

Both components return `documents`, `links`, `has_more`, and `next_cursor`, making them usable in standalone retrieval steps or larger Haystack pipelines.

## Installation

```bash
pip install xquik-haystack
```

Create an API key from the [Xquik dashboard](https://xquik.com), or follow the [Xquik quickstart](https://docs.xquik.com/quickstart) for account and API-key setup.

Set your Xquik API key:

```bash
export XQUIK_API_KEY="your-api-key"
```

## Usage

### Tweet Search

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack_integrations.components.websearch.xquik import XquikTweetSearch

search = XquikTweetSearch(api_key=Secret.from_env_var("XQUIK_API_KEY"), top_k=10)

pipeline = Pipeline()
pipeline.add_component("x_search", search)

result = pipeline.run({"x_search": {"query": "haystack ai"}})
documents = result["x_search"]["documents"]
links = result["x_search"]["links"]
```

### User Tweets

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.xquik import XquikUserTweetsFetcher

fetcher = XquikUserTweetsFetcher(api_key=Secret.from_env_var("XQUIK_API_KEY"))

result = fetcher.run(user_id="xquikcom", include_replies=False)
documents = result["documents"]
links = result["links"]
```

Each returned `Document` includes tweet text in `content` and available metadata such as tweet ID, URL, creation time, author details, and public metrics.

## License

`xquik-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
