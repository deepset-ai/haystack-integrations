---
layout: integration
name: SpecStream
description: Give a Haystack pipeline or agent any list from the live web, as Documents with the page every row came from
authors:
    - name: SpecStream
      socials:
        github: Specstreamai
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
  - [SpecStreamListFetcher](#specstreamlistfetcher)
  - [SpecStreamListTool](#specstreamlisttool)
- [License](#license)

## Overview

[SpecStream](https://specstream.ai) is a live web data engine for teams and agents. Search components hand a pipeline pages to read; SpecStream hands it the finished list. You describe a list in plain words (companies, local businesses, people, grants, tenders, products, papers, repositories) and get back every row that matches, each with the page it was read from. It is priced per match, and the price ceiling is quoted before anything runs.

This integration provides:

- `SpecStreamListFetcher`: a component that turns a plain-English request into Haystack `Document` objects, one per matching row. The content is the row as JSON. The metadata holds `source_url` (the page the row was read from), `checked_at`, `list_id`, `list_link` and the row's `fields`.
- `SpecStreamListTool`: the same fetcher as a `ComponentTool` for a Haystack `Agent`. The model writes the request and picks how many rows. You set the price ceiling in code, and the model can't raise it.

You need a SpecStream API key (Agents & API in your SpecStream workspace). A free account comes with $10 of work to use within 30 days and needs no card: [specstream.ai/signup](https://specstream.ai/signup). The API reference is at [api.specstream.ai/openapi.json](https://api.specstream.ai/openapi.json).

## Installation

```bash
pip install specstream-haystack
```

Set your key as an environment variable:

```bash
export SPECSTREAM_API_KEY="ss_live_..."
```

## Usage

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
