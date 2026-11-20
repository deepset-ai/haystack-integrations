---
layout: integration
name: Piloterr
description: Google search results and web page fetching with a crawler, a headless browser or a web unlocker, for Haystack pipelines and agents, through the Piloterr web data API
authors:
    - name: Piloterr
      socials:
        github: piloterr
pypi: https://pypi.org/project/piloterr-haystack/
repo: https://github.com/piloterr/piloterr-haystack
report_issue: https://github.com/piloterr/piloterr-haystack/issues
type: Search & Extraction
logo: /logos/piloterr.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Piloterr](https://www.piloterr.com) is a web data API: it searches Google and downloads web pages on its own infrastructure, then returns the results as JSON or HTML.

The `piloterr-haystack` package adds two components:

- **`PiloterrWebSearch`** searches Google and returns one `Document` per organic result, with the snippet as content and the `title`, `link` and `position` in its metadata, plus the list of result links.
- **`PiloterrFetcher`** fetches web pages and returns their HTML as `ByteStream`s, like Haystack's `LinkContentFetcher`, so `HTMLToDocument` can turn them into Documents. Piloterr loads each page with one of three engines:
  - `crawler` (the default): a plain HTTP request, the fastest;
  - `rendering`: a headless browser, for pages that need JavaScript, with an optional extra wait;
  - `webunlocker`: for pages behind anti-bot protection such as Cloudflare or DataDome.

A failed request raises `PiloterrError`, a Haystack `ComponentError` with the HTTP status; the API key never appears in the message. Both components have `run_async`.

## Installation

```bash
pip install piloterr-haystack
```

The page-fetching examples convert HTML with Haystack's `HTMLToDocument`, which needs `trafilatura`:

```bash
pip install trafilatura
```

Get an API key at [app.piloterr.com](https://app.piloterr.com) and set it in the environment:

```bash
export PILOTERR_API_KEY="your-api-key"
```

## Usage

### Web search

```python
from haystack_integrations.components.websearch.piloterr import PiloterrWebSearch

search = PiloterrWebSearch(top_k=5, search_params={"gl": "us", "hl": "en"})  # reads PILOTERR_API_KEY
result = search.run(query="What is Haystack?")

for doc in result["documents"]:
    print(doc.meta["title"], doc.meta["link"])
    print(doc.content)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | `Secret.from_env_var("PILOTERR_API_KEY")` | Piloterr API key |
| `top_k` | `10` | Results requested from Google, 1 to 100 |
| `allowed_domains` | | Only search these domains, added to the query as `site:` filters |
| `search_params` | | Extra parameters, such as `gl` (country), `hl` (language) or `location` |
| `timeout` | `60` | Seconds to wait for Piloterr |

### Fetching pages

```python
from haystack import Pipeline
from haystack.components.converters import HTMLToDocument
from haystack_integrations.components.fetchers.piloterr import PiloterrFetcher

pipeline = Pipeline()
pipeline.add_component("fetcher", PiloterrFetcher(engine="rendering", wait_in_seconds=2))
pipeline.add_component("converter", HTMLToDocument())
pipeline.connect("fetcher.streams", "converter.sources")

result = pipeline.run({"fetcher": {"urls": ["https://example.com"]}})
print(result["converter"]["documents"][0].content)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | `Secret.from_env_var("PILOTERR_API_KEY")` | Piloterr API key |
| `engine` | `crawler` | `crawler`, `rendering` or `webunlocker` |
| `wait_in_seconds` | | Rendering only: extra wait after the page loads, 0 to 30 |
| `raise_on_failure` | `True` | Raise when a single URL fails; with several URLs, failures are logged and skipped |
| `timeout` | `120` | Seconds to wait for each page |

### Search, read and answer

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.fetchers.piloterr import PiloterrFetcher
from haystack_integrations.components.websearch.piloterr import PiloterrWebSearch

template = [
    ChatMessage.from_user(
        "Answer the question from these pages.\n"
        "{% for doc in documents %}{{ doc.content[:2000] }}\n---\n{% endfor %}\n"
        "Question: {{ question }}"
    )
]

pipeline = Pipeline()
pipeline.add_component("search", PiloterrWebSearch(top_k=3))
pipeline.add_component("fetcher", PiloterrFetcher())
pipeline.add_component("converter", HTMLToDocument())
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["documents", "question"]))
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4.1-mini"))
pipeline.connect("search.links", "fetcher.urls")
pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.messages")

question = "What are the main features of Haystack?"
result = pipeline.run({"search": {"query": question}, "prompt": {"question": question}})
print(result["llm"]["replies"][0].text)
```

## License

`piloterr-haystack` is distributed under the terms of the [MIT](https://github.com/piloterr/piloterr-haystack/blob/main/LICENSE) license.
