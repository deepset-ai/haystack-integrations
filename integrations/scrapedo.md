---
layout: integration
name: Scrape.do
description: Fetch any web page as Markdown or HTML through Scrape.do, with proxies, JavaScript rendering and anti-bot handling built in.
authors:
    - name: Scrape.do
      socials:
        github: bugrahansss
pypi: https://pypi.org/project/scrapedo-haystack
repo: https://github.com/bugrahansss/scrapedo-haystack
type: Data Ingestion
report_issue: https://github.com/bugrahansss/scrapedo-haystack/issues
logo: /logos/scrapedo.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [Fetch pages](#fetch-pages)
  - [Use in a RAG pipeline](#use-in-a-rag-pipeline)
- [License](#license)

## Overview

[Scrape.do](https://scrape.do) is a web scraping API. You send it a URL and it returns the page, handling proxies, retries, CAPTCHAs and anti-bot protection for you.

This integration adds a `ScrapeDoFetcher` component that fetches web pages through Scrape.do and returns them as Haystack `Document`s. Pages can be returned as Markdown, ready to pass to an LLM, or as raw HTML.

You need a Scrape.do API token. You can get one from [Scrape.do](https://scrape.do). See the [Scrape.do documentation](https://scrape.do/documentation/) for all API parameters.

## Installation

```bash
pip install scrapedo-haystack
```

## Usage

### Components

This integration introduces one component:

- `ScrapeDoFetcher`: takes a list of URLs and returns one `Document` per page. The page content is in `content`, and `meta` holds `url`, `status_code` and `content_type`.

Main options:

| Option | Default | What it does |
|---|---|---|
| `output` | `"markdown"` | `"markdown"` or `"raw"` (original HTML) |
| `render` | `False` | Run JavaScript in a headless browser |
| `super_proxy` | `False` | Use residential and mobile IPs |
| `geo_code` | `None` | Route the request through a country, for example `"us"` |
| `extra_params` | `None` | Any other Scrape.do parameter, passed as-is |
| `raise_on_failure` | `False` | Raise on a failed URL instead of skipping it |

### Fetch pages

```python
import os
from scrapedo_haystack import ScrapeDoFetcher

os.environ["SCRAPEDO_API_KEY"] = "your-token"

fetcher = ScrapeDoFetcher(render=True, geo_code="us")
result = fetcher.run(urls=["https://example.com"])

doc = result["documents"][0]
print(doc.meta["url"])
print(doc.content)
```

### Use in a RAG pipeline

Fetch pages, split them, and answer a question from their content:

```python
import os
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.preprocessors import DocumentSplitter
from haystack.dataclasses import ChatMessage

from scrapedo_haystack import ScrapeDoFetcher

os.environ["SCRAPEDO_API_KEY"] = "your-token"
os.environ["OPENAI_API_KEY"] = "your-openai-key"

template = [
    ChatMessage.from_user(
        """Answer the question using only these pages.

{% for doc in documents %}
Source: {{ doc.meta.url }}
{{ doc.content }}
{% endfor %}

Question: {{ question }}"""
    )
]

pipe = Pipeline()
pipe.add_component("fetcher", ScrapeDoFetcher(render=True))
pipe.add_component("splitter", DocumentSplitter(split_by="word", split_length=300))
pipe.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["question"]))
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))

pipe.connect("fetcher.documents", "splitter.documents")
pipe.connect("splitter.documents", "prompt.documents")
pipe.connect("prompt.prompt", "llm.messages")

result = pipe.run({
    "fetcher": {"urls": ["https://haystack.deepset.ai/overview/intro"]},
    "prompt": {"question": "What is Haystack?"},
})
print(result["llm"]["replies"][0].text)
```

When loading a saved pipeline from YAML, allow this package's module:

```python
pipe = Pipeline.loads(yaml_text, allowed_modules=["scrapedo_haystack.fetcher"])
```

## License

`scrapedo-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
