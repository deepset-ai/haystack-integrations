---
layout: integration
name: AlphaAI
description: AI-scored financial news and SEC Form 4 insider events as Haystack Documents
authors:
    - name: AlphaAI
      socials:
        github: makeev
        twitter: alphai_io
        linkedin: https://www.linkedin.com/company/alphai-io
pypi: https://pypi.org/project/alphai-haystack
repo: https://github.com/makeev/alphai-haystack
type: Data Ingestion
report_issue: https://github.com/makeev/alphai-haystack/issues
logo: /logos/alphai.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [AlphaAINewsFetcher](#alphaainewsfetcher)
  - [AlphaAIInsiderNewsFetcher](#alphaaiinsidernewsfetcher)
  - [In a Pipeline](#in-a-pipeline)
- [Document shape](#document-shape)
- [License](#license)

## Overview

[AlphaAI](https://alphai.io) is a financial-news platform built for AI agents: every article is
enriched at ingest with per-ticker impact analysis, a category, and a 1-10 relevance score, and
SEC Form 4 insider filings become structured events about 6 minutes after they hit EDGAR.

This integration provides:

- `AlphaAINewsFetcher`: fetches the scored news feed as Haystack `Document` objects, with
  ticker / category / relevance filters and optional same-story collapsing.
- `AlphaAIInsiderNewsFetcher`: fetches SEC Form 4 insider events with a structured
  `meta["insider"]` block (side, shares, average price, total value, who traded, 10b5-1 flag).

An API key is required — the free tier (20 requests/min, 100/day, no card) is enough to try it:
[alphai.io/developers](https://alphai.io/developers). The components read the key from the
`ALPHAI_API_KEY` environment variable.

## Installation

```bash
pip install alphai-haystack
```

## Usage

### AlphaAINewsFetcher

```python
from alphai_haystack import AlphaAINewsFetcher

fetcher = AlphaAINewsFetcher(symbol="NVDA", min_relevance=7)
documents = fetcher.run()["documents"]

for doc in documents:
    print(doc.meta["relevance_score"], doc.meta["title"])
```

Filters set in `__init__` (`symbol`, `category`, `min_relevance`, `top_k`) can be overridden
per `run()` call.

### AlphaAIInsiderNewsFetcher

```python
from alphai_haystack import AlphaAIInsiderNewsFetcher

fetcher = AlphaAIInsiderNewsFetcher(min_relevance=7)  # higher floor = larger trades only
for doc in fetcher.run()["documents"]:
    insider = doc.meta["insider"]
    print(insider["insider_name"], insider["side"], insider["total_value_usd"], doc.meta["tickers"])
```

### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator

from alphai_haystack import AlphaAINewsFetcher

template = """Summarize what moved {{ symbol }} today, using only these articles:
{% for doc in documents %}
- {{ doc.content }} (relevance {{ doc.meta.relevance_score }}/10)
{% endfor %}
"""

pipeline = Pipeline()
pipeline.add_component("news", AlphaAINewsFetcher(min_relevance=6, collapse_stories=True))
pipeline.add_component("prompt", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipeline.connect("news.documents", "prompt.documents")
pipeline.connect("prompt", "llm")

result = pipeline.run({"news": {"symbol": "NVDA"}, "prompt": {"symbol": "NVDA"}})
print(result["llm"]["replies"][0].text)
```

Both components serialize with the rest of the pipeline (`to_dict` / `from_dict`); the API key
is stored as an environment-variable reference, never as the raw value.

## Document shape

`content` is the article title plus summary. `meta` carries `uid`, `url`, `title`, `source`,
`source_domain`, `published_at` (ISO 8601), `tickers`, `category`, `relevance_score` (1-10),
and — on the insider feed — the structured `insider` block.

## License

MIT — see the [repository](https://github.com/makeev/alphai-haystack).
