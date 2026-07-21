---
layout: integration
name: Haunt
description: Extract structured data or clean markdown from public web pages, with honest error codes instead of invented content
authors:
    - name: Haunt
      socials:
        github: Darko893
pypi: https://pypi.org/project/hauntapi
repo: https://github.com/Darko893/hauntapi-python
type: Data Ingestion
report_issue: https://github.com/Darko893/hauntapi-python/issues
logo: /logos/haunt.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Haunt](https://hauntapi.com?utm_source=haystack&utm_medium=integration&utm_campaign=sweep-2026-07) is a web extraction API built for AI applications. Give it a URL and get the page back as clean markdown, or pass a plain-language prompt ("the product name, price and stock status") and get structured JSON.

The design choice that matters for pipelines: honest failure. When a page cannot be read (bot wall, login wall, missing page), Haunt returns a structured `error_code` such as `access_denied`, `login_required`, or `not_found` instead of invented content, so your pipeline can branch on the failure rather than indexing made-up text. Failed reads are not charged.

You need a Haunt API key. Get a free one (1,000 credits, no card) at [hauntapi.com](https://hauntapi.com/#signup). To try the engine without signing up, prepend `https://hauntapi.com/r/` to any URL for the free no-key reader.

## Installation

```bash
pip install hauntapi haystack-ai
```

## Usage

Set your API key as the `HAUNT_API_KEY` environment variable, then wrap the client in a small custom component that turns pages into Haystack `Document` objects:

```python
from typing import List, Optional

from haystack import Document, component
from hauntapi import Haunt


@component
class HauntFetcher:
    """Fetch public web pages as clean markdown Documents via the Haunt API.

    Unreadable pages (bot wall, login wall, missing page) come back in
    `failures` with an honest error code instead of invented content.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = Haunt(api_key=api_key)  # falls back to HAUNT_API_KEY

    @component.output_types(documents=List[Document], failures=List[dict])
    def run(self, urls: List[str]):
        documents, failures = [], []
        for url in urls:
            result = self.client.extract(
                url, "Return the readable page content.", response_format="markdown"
            )
            if not result.success:
                failures.append(
                    {
                        "url": url,
                        "error_code": result.error_code or "extraction_failed",
                        "message": result.message or result.error,
                    }
                )
                continue
            data = result.data
            content = (
                data["markdown"]
                if isinstance(data, dict) and "markdown" in data
                else str(data)
            )
            documents.append(Document(content=content, meta={"url": url}))
        return {"documents": documents, "failures": failures}


fetcher = HauntFetcher()
out = fetcher.run(urls=["https://example.com"])
print(out["documents"][0].content)
# '# Example Domain ...'
```

Use it like any other fetcher at the front of an indexing pipeline, then split, embed, and write the documents as usual. The `failures` output can feed logging or a retry branch.

For structured extraction instead of markdown, call `self.client.extract(url, "your prompt")` without `response_format` and the `data` field carries JSON matched to your prompt. The [hauntapi package](https://pypi.org/project/hauntapi) also ships ready-made tool helpers for agent frameworks.

## License

`hauntapi` is distributed under the MIT license.
