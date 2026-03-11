---
layout: integration
name: Firecrawl
description: Crawl websites, search the web, and extract LLM-ready content using Firecrawl
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/firecrawl-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/firecrawl.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [FirecrawlCrawler](#firecrawlcrawler)
  - [FirecrawlWebSearch](#firecrawlwebsearch)
- [License](#license)

## Overview

[Firecrawl](https://firecrawl.dev) turns websites into LLM-ready data. It handles JavaScript rendering, anti-bot bypassing, and outputs clean Markdown.

This integration provides two components:
- [`FirecrawlCrawler`](https://docs.haystack.deepset.ai/docs/firecrawlcrawler): Crawls one or more URLs and follows links to discover subpages, returning extracted content as Haystack `Document` objects.
- [`FirecrawlWebSearch`](https://docs.haystack.deepset.ai/docs/firecrawlwebsearch): Searches the web using a query, scrapes the resulting pages, and returns the structured content as Haystack `Document` objects.

You need a Firecrawl API key to use this integration. You can get one at [firecrawl.dev](https://firecrawl.dev).

## Installation

```bash
pip install firecrawl-haystack
```

## Usage

### FirecrawlCrawler

#### Basic Example

```python
from haystack_integrations.components.fetchers.firecrawl import FirecrawlCrawler

crawler = FirecrawlCrawler(params={"limit": 5})

result = crawler.run(urls=["https://docs.haystack.deepset.ai/docs/intro"])
documents = result["documents"]
```

By default, the component reads the API key from the `FIRECRAWL_API_KEY` environment variable. You can also pass it explicitly:

```python
from haystack.utils import Secret
from haystack_integrations.components.fetchers.firecrawl import FirecrawlCrawler

crawler = FirecrawlCrawler(
    api_key=Secret.from_token("your-api-key"),
    params={"limit": 10, "scrape_options": {"formats": ["markdown"]}},
)
```

#### Parameters

- **`api_key`**: API key for Firecrawl. Defaults to the `FIRECRAWL_API_KEY` environment variable.
- **`params`**: Parameters for the crawl request. Defaults to `{"limit": 1, "scrape_options": {"formats": ["markdown"]}}`. See the [Firecrawl API reference](https://docs.firecrawl.dev/api-reference/endpoint/crawl-post) for all available parameters. Without a limit, Firecrawl may crawl all subpages and consume credits quickly.

#### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.fetchers.firecrawl import FirecrawlCrawler

async def main():
    crawler = FirecrawlCrawler(params={"limit": 5})
    
    result = await crawler.run_async(urls=["https://docs.haystack.deepset.ai/docs/intro"])
    print(f"Crawled {len(result['documents'])} documents")

asyncio.run(main())
```

### FirecrawlWebSearch

`FirecrawlWebSearch` searches the web using the Firecrawl Search API, scrapes the resulting pages, and returns the structured text as Haystack `Document` objects along with the result URLs. Because Firecrawl actively scrapes and structures page content into LLM-friendly formats, you generally don't need an additional component like `LinkContentFetcher` to read the web pages.

#### Basic Example

```python
from haystack_integrations.components.websearch.firecrawl import FirecrawlWebSearch

web_search = FirecrawlWebSearch(
    top_k=5,
    search_params={"scrape_options": {"formats": ["markdown"]}},
)

result = web_search.run(query="What is Haystack by deepset?")

for doc in result["documents"]:
    print(doc.content)
```

#### In a Pipeline

Here is an example of a RAG pipeline that uses `FirecrawlWebSearch` to look up an answer on the web. Because Firecrawl returns the actual text of the scraped pages, you can pass the `documents` output directly into a `ChatPromptBuilder` to give the LLM the necessary context.

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.firecrawl import FirecrawlWebSearch

web_search = FirecrawlWebSearch(
    top_k=2,
    search_params={"scrape_options": {"formats": ["markdown"]}},
)

prompt_template = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user(
        "Given the information below:\n"
        "{% for document in documents %}{{ document.content }}\n{% endfor %}\n"
        "Answer the following question: {{ query }}.\nAnswer:",
    ),
]

prompt_builder = ChatPromptBuilder(
    template=prompt_template,
    required_variables={"query", "documents"},
)

llm = OpenAIChatGenerator(
    api_key=Secret.from_env_var("OPENAI_API_KEY"),
    model="gpt-4o-mini",
)

pipe = Pipeline()
pipe.add_component("search", web_search)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", llm)

pipe.connect("search.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.messages")

query = "What is Haystack by deepset?"
result = pipe.run(data={"search": {"query": query}, "prompt_builder": {"query": query}})
print(result["llm"]["replies"][0].content)
```

#### Parameters

- **`api_key`**: API key for Firecrawl. Defaults to the `FIRECRAWL_API_KEY` environment variable.
- **`top_k`**: Maximum number of documents to return. Defaults to 10. Can be overridden by the `"limit"` parameter in `search_params`.
- **`search_params`**: Additional parameters for the Firecrawl Search API (e.g., time filters, location, scrape options). See the [Firecrawl Search API reference](https://docs.firecrawl.dev/api-reference/endpoint/search) for all available parameters.

#### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.websearch.firecrawl import FirecrawlWebSearch

async def main():
    web_search = FirecrawlWebSearch(top_k=3)

    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

### License

`firecrawl-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
