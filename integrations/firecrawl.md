---
layout: integration
name: Firecrawl
description: Scrape, crawl, search, and map the web using Firecrawl's Python SDK.
authors:
  - name: Firecrawl
    socials:
      github: firecrawl
      twitter: firecrawl_dev
pypi: https://pypi.org/project/firecrawl-py/
repo: https://github.com/firecrawl/firecrawl
type: Data Ingestion
report_issue: https://github.com/firecrawl/firecrawl/issues
logo: /logos/firecrawl.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Scrape a Page](#scrape-a-page)
  - [Search the Web](#search-the-web)
  - [Crawl a Website](#crawl-a-website)
  - [RAG Pipeline Example](#rag-pipeline-example)
- [License](#license)

## Overview

[Firecrawl](https://firecrawl.dev) turns websites into LLM-ready data. It handles JavaScript rendering, anti-bot bypassing, and outputs clean Markdown. The Python SDK provides four main operations:

- **Scrape**: Extract content from a single URL as Markdown, HTML, or structured data
- **Search**: Search the web and optionally scrape the results
- **Crawl**: Crawl an entire site and extract content from every page
- **Map**: Discover all URLs on a site

You need a Firecrawl API key to use this integration. Sign up at [firecrawl.dev](https://firecrawl.dev) to get one.

## Installation

```bash
pip install firecrawl-py haystack-ai
```

## Usage

### Scrape a Page

Scrape a URL and convert the result into a Haystack Document:

```python
from firecrawl import FirecrawlApp
from haystack import Document

app = FirecrawlApp(api_key="your-api-key")

result = app.scrape_url("https://docs.haystack.deepset.ai/docs/intro", params={
    "formats": ["markdown"]
})

doc = Document(
    content=result.get("markdown", ""),
    meta={"url": result.get("metadata", {}).get("sourceURL", "")}
)
print(doc)
```

### Search the Web

Search the web and convert results into Haystack Documents:

```python
from firecrawl import FirecrawlApp
from haystack import Document

app = FirecrawlApp(api_key="your-api-key")

results = app.search("haystack AI framework", params={"limit": 5})

documents = []
for result in results.get("data", []):
    documents.append(Document(
        content=result.get("markdown", result.get("description", "")),
        meta={
            "url": result.get("url", ""),
            "title": result.get("title", ""),
        }
    ))

print(f"Found {len(documents)} documents")
for doc in documents:
    print(f"- {doc.meta['title']}: {doc.meta['url']}")
```

### Crawl a Website

Crawl a site and convert all pages into Haystack Documents:

```python
from firecrawl import FirecrawlApp
from haystack import Document

app = FirecrawlApp(api_key="your-api-key")

crawl_result = app.crawl_url("https://docs.haystack.deepset.ai", params={
    "limit": 10,
    "scrapeOptions": {"formats": ["markdown"]}
})

documents = []
for page in crawl_result.get("data", []):
    documents.append(Document(
        content=page.get("markdown", ""),
        meta={"url": page.get("metadata", {}).get("sourceURL", "")}
    ))

print(f"Crawled {len(documents)} pages")
```

### RAG Pipeline Example

Scrape web content with Firecrawl and use it in a Haystack RAG pipeline:

```python
import os
from firecrawl import FirecrawlApp
from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.dataclasses import ChatMessage

os.environ["OPENAI_API_KEY"] = "your-openai-key"

# Scrape pages with Firecrawl
app = FirecrawlApp(api_key="your-firecrawl-key")

urls = [
    "https://docs.haystack.deepset.ai/docs/intro",
    "https://docs.haystack.deepset.ai/docs/pipelines",
    "https://docs.haystack.deepset.ai/docs/components",
]

documents = []
for url in urls:
    result = app.scrape_url(url, params={"formats": ["markdown"]})
    documents.append(Document(
        content=result.get("markdown", ""),
        meta={"url": result.get("metadata", {}).get("sourceURL", url)}
    ))

# Index documents
document_store = InMemoryDocumentStore()
docs_embedder = OpenAIDocumentEmbedder()
embeddings = docs_embedder.run(documents)
document_store.write_documents(embeddings["documents"])

# Build RAG pipeline
text_embedder = OpenAITextEmbedder()
retriever = InMemoryEmbeddingRetriever(document_store)
generator = OpenAIChatGenerator()

messages = [
    ChatMessage.from_system("Answer questions based on the provided context."),
    ChatMessage.from_user("""
Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
""")
]

prompt_builder = ChatPromptBuilder(template=messages)

pipe = Pipeline()
pipe.add_component("embedder", text_embedder)
pipe.add_component("retriever", retriever)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)

pipe.connect("embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

question = "What are Haystack pipelines?"
response = pipe.run({
    "embedder": {"text": question},
    "prompt_builder": {"question": question}
})

print(f"Q: {question}")
print(f"A: {response['llm']['replies'][0].text}")
```

### Authentication

Set your Firecrawl API key as an environment variable:

```bash
export FIRECRAWL_API_KEY="your-api-key"
```

Or pass it directly:

```python
from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key="your-api-key")
```

### License

`firecrawl-py` is distributed under the terms of the [AGPL-3.0](https://spdx.org/licenses/AGPL-3.0.html) license.
