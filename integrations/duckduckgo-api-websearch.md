---
layout: integration
name: DuckDuckGo
description: Uses DuckDuckGo API for web searches
authors:
    - name: Giovanni Alzetta
      socials:
        github: GivAlz
pypi: https://pypi.org/project/duckduckgo-api-haystack/
repo: https://github.com/GivAlz/duckduckgo-api-haystack
type: Data Ingestion
logo: /logos/duckduckgo.png
version: Haystack 2.0
toc: true
---

Implements a component of the kind *WebSearch*, but through the freely available DuckDuckGo API.

### **Table of Contents**
- [Overview](#Overview)
- [Installation](#Installation)
- [Usage](#Usage)
- [License](#License)

## Overview

`DuckduckgoApiWebSearch` performs web searches using the DuckDuckGo search engine.

This repository provides a Python module similar to `SearchApiWebSearch` and `SerperDevWebSearch`,
but utilizes the free DuckDuckGo API.

When you pass a query to `DuckduckgoWebSearch`, it returns a list of URLs that are most relevant to your search.
The results are based on page snippets (the brief text displayed beneath the page titles in search results) rather
than the content of the entire page.

While the functionality is comparable to the aforementioned APIs, there are two important considerations:
- *Rate limitations*: The API may impose some restrictions on the number of queries allowed.
- *Result quality*: The quality of search results may vary.

## Installation

```bash
pip install duckduckgo-api-haystack
```

## Usage

The `DuckduckgoApiWebSearch` class allows you to perform web searches using the DuckDuckGo search engine.
Here's how to use it:

1. Import and initialize the `DuckduckgoApiWebSearch` class:

```python
from duckduckgo_api_haystack import DuckduckgoApiWebSearch

websearch = DuckduckgoApiWebSearch(top_k=10)
```

2. Perform a search:

```python
results = websearch.run(query="What is frico?")

# Access the search results
documents = results["documents"]
links = results["links"]
```

### Configuration Options

You can customize the search behavior by passing parameters to the `DuckduckgoApiWebSearch` constructor:

```python
websearch = DuckduckgoApiWebSearch(
    top_k=10,                 # Maximum number of documents to return
    max_results=10,           # Maximum number of documents to consider in the search
    region="wt-wt",           # Region for search results (default: no region)
    safesearch="moderate",    # SafeSearch setting ("on", "moderate", or "off")
    timelimit=None,           # Time limit for results (e.g., "d" for day, "w" for week, "m" for month)
    backend="auto",           # Search backend ("auto", "html", or "lite")
    allowed_domain="",        # Restrict search to a specific domain
    timeout=10,               # Timeout for each search request (in seconds)
    use_answers=False,        # Include DuckDuckGo's answer box in results
    proxy=None                # Web address of proxy server (if needed)
)
```

For more details on the configuration options, refer to the [duckduckgo_search documentation](https://github.com/deedy5/duckduckgo_search).

### License

Apache 2.0
