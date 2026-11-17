---
layout: integration
name: CaptureKit
description: Fetch web pages as clean Markdown documents, loaded in a real browser with cookie banners removed, for Haystack pipelines and agents, through the CaptureKit API
authors:
    - name: CaptureKit
      socials:
        github: capturekitdev
pypi: https://pypi.org/project/capturekit-haystack/
repo: https://github.com/capturekitdev/capturekit-haystack
report_issue: https://github.com/capturekitdev/capturekit-haystack/issues
type: Search & Extraction
logo: /logos/capturekit.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[CaptureKit](https://www.capturekit.dev) is a web page API: it loads each page in a real browser on its own infrastructure, removes cookie banners, and returns the page as clean Markdown.

The `capturekit-haystack` package adds one component:

- **`CaptureKitFetcher`** fetches web pages and returns one `Document` per page. The content is the page as Markdown, and the metadata holds `url`, `title` and `description`. With `main_content_only` (the default), CaptureKit keeps the article or product and drops menus, sidebars and footers. Unlike `LinkContentFetcher`, it needs no HTML converter: its documents go straight to a splitter, an embedder or a prompt.

A failed request raises `CaptureKitError`, a Haystack `ComponentError` with the HTTP status; the API key never appears in the message. The component has `run_async`, `to_dict` and `from_dict`.

## Installation

```bash
pip install capturekit-haystack
```

Get an API key at [app.capturekit.dev](https://app.capturekit.dev) and set it in the environment:

```bash
export CAPTUREKIT_API_KEY="your-api-key"
```

## Usage

### Fetching pages

```python
from haystack_integrations.components.fetchers.capturekit import CaptureKitFetcher

fetcher = CaptureKitFetcher()  # reads CAPTUREKIT_API_KEY
result = fetcher.run(urls=["https://haystack.deepset.ai/overview/intro"])

for doc in result["documents"]:
    print(doc.meta["title"], doc.meta["url"])
    print(doc.content[:500])
```

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | `Secret.from_env_var("CAPTUREKIT_API_KEY")` | CaptureKit API key |
| `main_content_only` | `True` | Keep the article or product and drop menus, sidebars and footers |
| `raise_on_failure` | `True` | Raise when a single URL fails; with several URLs, failures are logged and skipped |
| `timeout` | `120` | Seconds to wait for each page |

### Indexing pages for RAG

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.fetchers.capturekit import CaptureKitFetcher

store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("fetcher", CaptureKitFetcher())
pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=200))
pipeline.add_component("writer", DocumentWriter(document_store=store))
pipeline.connect("fetcher.documents", "splitter.documents")
pipeline.connect("splitter.documents", "writer.documents")

pipeline.run({"fetcher": {"urls": ["https://haystack.deepset.ai/overview/intro"]}})
print(store.count_documents())
```

### Reading pages and answering

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.fetchers.capturekit import CaptureKitFetcher

template = [
    ChatMessage.from_user(
        "Answer the question from these pages.\n"
        "{% for doc in documents %}{{ doc.content[:4000] }}\n---\n{% endfor %}\n"
        "Question: {{ question }}"
    )
]

pipeline = Pipeline()
pipeline.add_component("fetcher", CaptureKitFetcher())
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["documents", "question"]))
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4.1-mini"))
pipeline.connect("fetcher.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.messages")

question = "What is Haystack used for?"
result = pipeline.run(
    {"fetcher": {"urls": ["https://haystack.deepset.ai/overview/intro"]}, "prompt": {"question": question}}
)
print(result["llm"]["replies"][0].text)
```

## License

`capturekit-haystack` is distributed under the terms of the [MIT](https://github.com/capturekitdev/capturekit-haystack/blob/main/LICENSE) license.
