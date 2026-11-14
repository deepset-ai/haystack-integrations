---
layout: integration
name: SpecStream
description: Live web search, page extraction and structured rows for Haystack pipelines and agents, as Documents with their source URL
authors:
    - name: SpecStream
      socials:
        github: specstream
pypi: https://pypi.org/project/specstream-haystack
repo: https://github.com/specstream/specstream-tools/tree/main/packages/specstream-haystack
type: Search & Extraction
report_issue: https://github.com/specstream/specstream-tools/issues
logo: /logos/specstream.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [SpecStreamWebSearch](#specstreamwebsearch)
  - [SpecStreamExtractor](#specstreamextractor)
  - [SpecStreamListFetcher](#specstreamlistfetcher)
  - [SpecStreamListTool](#specstreamlisttool)
- [License](#license)

## Overview

[SpecStream](https://specstream.ai) is the live web data engine for teams and agents. It has three products on one key: a Search API that answers a question from the live web in a few seconds, an Extract API that returns the main text of web pages, PDF, Word and Excel files, and Deep Search, which turns a request in plain words (companies, local businesses, people, grants, tenders, products, papers, repositories) into structured rows, each with the page it was read from. Search is $5 per 1,000 searches of up to 10 results, or $1 on the fast tier. Extract is $0.80 per 1,000 pages. Deep Search is priced per delivered row, and the price ceiling is quoted before anything runs.

This integration provides:

- `SpecStreamWebSearch`: a component that searches the live web and returns one `Document` per result, with `title`, `source_url` and `published` in the metadata, plus an `answer` when the question has one.
- `SpecStreamExtractor`: a component that reads the main text of 1 to 20 URLs and returns one `Document` per page, as Markdown or plain text.
- `SpecStreamListFetcher`: a component that turns a plain-English request into Haystack `Document` objects, one per matching row. The content is the row as JSON. The metadata holds `source_url` (the page the row was read from), `checked_at`, `list_id`, `list_link` and the row's `fields`.
- `SpecStreamListTool`: the same fetcher as a `ComponentTool` for a Haystack `Agent`. The model writes the request and picks how many rows. You set the price ceiling in code, and the model can't raise it.

You need a SpecStream API key (Agents & API in your SpecStream workspace). A free account comes with $10 of credit and needs no card: [specstream.ai/signup](https://specstream.ai/signup). The API reference is at [api.specstream.ai/openapi.json](https://api.specstream.ai/openapi.json).

## Installation

```bash
pip install specstream-haystack
```

Set your key as an environment variable:

```bash
export SPECSTREAM_API_KEY="ss_live_..."
```

## Usage

### SpecStreamWebSearch

```python
from haystack_integrations.components.fetchers.specstream import SpecStreamWebSearch

search = SpecStreamWebSearch()
result = search.run(q="latest stable release of PostgreSQL")

print(result["answer"])
for doc in result["documents"]:
    print(doc.meta["source_url"], doc.content)
```

Each `Document` is one result. `content` is the snippet, and `meta` carries `title`, `source_url` and `published`.

### SpecStreamExtractor

```python
from haystack_integrations.components.fetchers.specstream import SpecStreamExtractor

extractor = SpecStreamExtractor()
result = extractor.run(urls=["https://www.postgresql.org/docs/release/"])

for doc in result["documents"]:
    print(doc.meta["status"], doc.meta["title"], len(doc.content))
```

`content` is the page's main text as Markdown (`format="text"` for plain text). `meta["status"]` is `ok` for a page that was read.

### SpecStreamListFetcher

```python
from haystack_integrations.components.fetchers.specstream import SpecStreamListFetcher

fetcher = SpecStreamListFetcher(max_price_usd=3, max_results=25)
result = fetcher.run(request="Breweries in Portland, Oregon that host events, with their website")

for doc in result["documents"]:
    print(doc.meta["source_url"], doc.content)
```

`run` also returns `list_id`, `status`, `list_link` and, when the list was still running after `wait_seconds`, a `message`. If the quoted price is above `max_price_usd`, or the request is too vague to price, nothing runs and `SpecStreamError` says why.

Calling the same request with the same limits within the hour reaches the run it already started, so a retried step doesn't pay for the list twice.

To pass the key explicitly:

```python
from haystack.utils import Secret
from haystack_integrations.components.fetchers.specstream import SpecStreamListFetcher

fetcher = SpecStreamListFetcher(api_key=Secret.from_token("your-api-key"), max_price_usd=3)
```

#### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.fetchers.specstream import SpecStreamListFetcher

template = [
    ChatMessage.from_user(
        "Using only these rows, answer the question and cite each row's source_url.\n"
        "{% for doc in documents %}{{ doc.content }} (source: {{ doc.meta.source_url }})\n{% endfor %}\n"
        "Question: {{ question }}"
    )
]

pipe = Pipeline()
pipe.add_component("fetcher", SpecStreamListFetcher(max_price_usd=3, max_results=20))
pipe.add_component("prompt", ChatPromptBuilder(template=template))
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipe.connect("fetcher.documents", "prompt.documents")
pipe.connect("prompt.prompt", "llm.messages")

question = "Which of these dental clinics in Lisbon offer online booking?"
result = pipe.run({"fetcher": {"request": "Dental clinics in Lisbon with online booking"}, "prompt": {"question": question}})
print(result["llm"]["replies"][0].text)
```

### SpecStreamListTool

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.specstream import SpecStreamListTool

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o"),
    tools=[SpecStreamListTool(max_price_usd=5)],
)

result = agent.run(
    messages=[ChatMessage.from_user("Find open grants for urban beekeeping in the EU and list their deadlines.")]
)
print(result["last_message"].text)
```

### License

`specstream-haystack` is distributed under the terms of the [MIT license](https://github.com/specstream/specstream-tools/blob/main/packages/specstream-haystack/LICENSE).
