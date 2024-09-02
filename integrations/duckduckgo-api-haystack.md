---
layout: integration
name: Your integration name
description: The description of your integration
authors:
    - name: Author Name
      socials:
        github: author-github-username
        twitter: author-twitter-username
        linkedin: author-linkedin-url
pypi: https://pypi.org/project/your-project
repo: https://github.com/your-repo
type: Type of your integration (like Model Provider or Document Store etc)
report_issue: https://github.com/yout-repo/issues
logo: /logos/your-logo.png
version: Haystack 2.0
toc: true
---
# Duckduckgo API Websearch

Implements a component of the kind *WebSearch*, but through the freely available duckduckgo API.

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This repository implements a module in the style of **SearchApiWebSearch**
and **SerperDevWebSearch**, but using the freely-available duckduckgo API.

This repository provides a Python module similar to **SearchApiWebSearch** and **SerperDevWebSearch**,
but utilizes the free DuckDuckGo API.

When you pass a query to **DuckduckgoWebSearch**, it returns a list of URLs that are most relevant to your search.
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
    backend="api",            # Search backend ("api", "html", or "lite")
    allowed_domain="",        # Restrict search to a specific domain
    timeout=10,               # Timeout for each search request (in seconds)
    use_answers=False,        # Include DuckDuckGo's answer box in results
    proxy=None                # Web address of proxy server (if needed)
)
```

For more details on the configuration options, refer to the [duckduckgo_search documentation](https://github.com/deedy5/duckduckgo_search).

### License

Info about your integration license
