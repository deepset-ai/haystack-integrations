---
layout: integration
name: Plasmate
description: Browser engine for AI agents. Fetches web pages as Semantic Object Model (SOM) — typed JSON optimized for LLM consumption with ~17× fewer tokens than raw HTML on average, and peaks above 100×.
authors:
  - name: Plasmate Labs
    socials:
      github: plasmate-labs
pypi: https://pypi.org/project/haystack-plasmate
repo: https://github.com/plasmate-labs/haystack-plasmate
type: Data Ingestion
report_issue: https://github.com/plasmate-labs/haystack-plasmate/issues
logo: /logos/plasmate.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Components](#components)
  - [PlasmateWebFetcher](#plasmatewebfetcher)
  - [PlasmateSOMConverter](#plasmatesomconverter)
- [RAG pipeline example](#rag-pipeline-example)
- [License](#license)

## Overview

[Plasmate](https://plasmate.app) is an open-source (Apache 2.0) browser engine designed from the ground up for AI agents. Instead of rendering pixels, Plasmate produces the Semantic Object Model (SOM) — a flat, typed JSON document representing a web page in a form optimized for LLM consumption.

Across 38 measured production sites, Plasmate achieves an average **~17× token reduction** versus raw HTML, with peaks above **100×** on large SaaS marketing pages. The reproducible benchmark is published at [webtaskbench.com](https://webtaskbench.com), and the SOM/1.0 format is specified at [somspec.org](https://somspec.org/spec).

This integration exposes Plasmate to Haystack 2.0 RAG pipelines as a drop-in alternative to `LinkContentFetcher` and `HTMLToDocument`. The headline benefit is dramatically lower token cost per page in any pipeline that fetches web content for downstream LLM consumption.

## Installation

```bash
pip install haystack-plasmate
```

You also need the Plasmate engine available on PATH. The engine ships as a single binary:

```bash
# Python install of Plasmate itself
pip install plasmate

# Or via the project's release binaries
# https://github.com/plasmate-labs/plasmate/releases
```

## Components

### PlasmateWebFetcher

Fetches web pages and converts them to Haystack `Document` objects with SOM content.

```python
from haystack_plasmate import PlasmateWebFetcher

# Basic usage — fetches each URL and returns a Haystack Document
fetcher = PlasmateWebFetcher()
result = fetcher.run(urls=["https://example.com"])
docs = result["documents"]

print(docs[0].content)         # Concise SOM text representation
print(docs[0].meta["url"])     # https://example.com
print(docs[0].meta["title"])   # Page title
print(docs[0].meta["som_tokens"])   # ~hundreds
print(docs[0].meta["html_tokens"])  # ~tens of thousands
print(docs[0].meta["compression_ratio"])  # e.g. 47.3

# With custom headers (e.g. for authenticated pages)
fetcher = PlasmateWebFetcher(
    headers={"Authorization": "Bearer token123"},
    timeout=60,
)

# Text-only mode — extracts readable text without SOM structure
fetcher = PlasmateWebFetcher(text_only=True)
```

### PlasmateSOMConverter

Converts raw HTML strings to SOM `Document` objects without making HTTP requests. Useful when HTML is already in hand (from a database, a different fetcher, or in-process rendering).

```python
from haystack_plasmate import PlasmateSOMConverter

converter = PlasmateSOMConverter()

# Convert a single HTML string
result = converter.run(html="<html><body><h1>Hello</h1></body></html>")
doc = result["documents"][0]

# Convert multiple HTML sources, attaching metadata to each
result = converter.run(sources=[
    {"html": "<html>...</html>", "meta": {"source": "page1.html"}},
    {"html": "<html>...</html>", "meta": {"source": "page2.html"}},
])
```

## RAG pipeline example

A web-aware RAG pipeline that fetches documentation pages, embeds them, and answers questions:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_plasmate import PlasmateWebFetcher

document_store = InMemoryDocumentStore()

# Indexing pipeline — fetch with Plasmate, embed, write
indexing = Pipeline()
indexing.add_component("fetcher", PlasmateWebFetcher())
indexing.add_component("embedder", OpenAIDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store=document_store))
indexing.connect("fetcher.documents", "embedder.documents")
indexing.connect("embedder.documents", "writer.documents")

indexing.run({
    "fetcher": {
        "urls": [
            "https://docs.haystack.deepset.ai/docs/intro",
            "https://docs.haystack.deepset.ai/docs/components_overview",
        ],
    },
})
```

The same indexing pipeline using `LinkContentFetcher` would consume **roughly an order of magnitude more tokens per URL** during embedding and downstream generation, because Plasmate strips layout scaffolding, design-system runtime, analytics initialisation, and other non-content tokens before the document reaches the embedder.

## SOM directives — making your own pages Plasmate-friendly

If you publish content that you would like AI agents to read efficiently, advertise a SOM endpoint via [SOM Directives in robots.txt](https://somspec.org/directives). The five-line opt-in tells any compatible agent to fetch a structured representation of your pages instead of the full HTML rendering. Verify your site is SOM-ready at [somready.com](https://somready.com).

## License

`haystack-plasmate` is open source under the Apache 2.0 License. The Plasmate engine itself is also Apache 2.0.

The SOM/1.0 specification is hosted under the W3C Web Content for AI Community Group at [somspec.org](https://somspec.org).
