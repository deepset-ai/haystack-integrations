---
layout: integration
name: Olostep
description: Search the web, scrape and crawl sites, get answers with sources, and batch-extract up to 100k URLs, as Haystack Documents
authors:
  - name: Olostep
    socials:
      github: olostep-api
pypi: https://pypi.org/project/olostep-haystack/
repo: https://github.com/olostep-api/olostep-haystack
report_issue: https://github.com/olostep-api/olostep-haystack/issues
type: Search & Extraction
logo: /logos/olostep.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [OlostepWebSearch](#olostepwebsearch)
  - [OlostepScraper](#olostepscraper)
  - [OlostepAnswer](#olostepanswer)
  - [OlostepMapper and OlostepScraper in a pipeline](#olostepmapper-and-olostepscraper-in-a-pipeline)
  - [OlostepCrawler and OlostepBatchScraper](#olostepcrawler-and-olostepbatchscraper)
- [License](#license)

## Overview

[Olostep](https://www.olostep.com) is a web data API for AI agents and pipelines: live web search, scraping, crawling and structured extraction. Pages are rendered with JavaScript and returned as clean markdown, and a single batch job handles up to 100,000 URLs.

This integration provides six components that return Haystack `Document` objects:

- `OlostepWebSearch`: searches the web and returns the results, optionally with each page's full content.
- `OlostepScraper`: fetches pages as markdown, text or HTML.
- `OlostepAnswer`: answers a question from the live web, with its source URLs, optionally as structured JSON.
- `OlostepMapper`: lists a website's URLs, ranked by relevance or filtered by patterns.
- `OlostepCrawler`: crawls a site from a start URL and returns every page.
- `OlostepBatchScraper`: scrapes up to 100,000 URLs in one batch job.

Every component has `run` and `run_async` and is serializable. You need an Olostep API key, which you can get at [olostep.com](https://www.olostep.com/dashboard); new accounts get 500 free credits.

## Installation

```bash
pip install olostep-haystack
```

Set your API key as an environment variable:

```bash
export OLOSTEP_API_KEY="your-api-key"
```

## Usage

### OlostepWebSearch

```python
from haystack_integrations.components.websearch.olostep import OlostepWebSearch

search = OlostepWebSearch(top_k=5)
result = search.run(query="What is retrieval-augmented generation?")

for doc in result["documents"]:
    print(doc.meta["title"], doc.meta["url"])
```

Set `scrape_results=True` to use each result page's markdown as the Document content.

### OlostepScraper

```python
from haystack_integrations.components.websearch.olostep import OlostepScraper

scraper = OlostepScraper(output_format="markdown")
documents = scraper.run(urls=["https://haystack.deepset.ai/overview/intro"])["documents"]
```

### OlostepAnswer

```python
from haystack_integrations.components.websearch.olostep import OlostepAnswer

answer = OlostepAnswer(json_format={"company": "", "founded": ""})
result = answer.run(query="When was deepset founded?")
print(result["answer"], result["links"])
```

### OlostepMapper and OlostepScraper in a pipeline

Index a documentation site: list its relevant pages, fetch them, and write them to a document store.

```python
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.websearch.olostep import OlostepMapper, OlostepScraper

store = InMemoryDocumentStore()
pipeline = Pipeline()
pipeline.add_component("mapper", OlostepMapper(top_n=20, include_url_patterns=["/docs/**"]))
pipeline.add_component("scraper", OlostepScraper())
pipeline.add_component("writer", DocumentWriter(document_store=store))
pipeline.connect("mapper.links", "scraper.urls")
pipeline.connect("scraper.documents", "writer.documents")

pipeline.run({"mapper": {"url": "https://docs.haystack.deepset.ai", "search_query": "retrievers"}})
```

### OlostepCrawler and OlostepBatchScraper

```python
from haystack_integrations.components.websearch.olostep import OlostepBatchScraper, OlostepCrawler

crawled = OlostepCrawler(max_pages=50).run(url="https://example.com/blog")["documents"]

# One batch holds up to 100,000 URLs; the component waits for it to finish.
scraped = OlostepBatchScraper().run(urls=product_urls)["documents"]
```

## License

`olostep-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
