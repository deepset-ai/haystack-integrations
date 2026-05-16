---
layout: integration
name: SearchApi
description: Uses SearchApi for web searches
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/searchapi.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `SearchApiWebSearch` component allows you to perform web searches using the [SearchApi](https://www.searchapi.io/) service. It retrieves relevant snippets and URLs that can be used directly in your Haystack applications, such as Retrieval-Augmented Generation (RAG) pipelines or with Haystack Agents.

This component is part of the core `haystack-ai` package, meaning you do not need to install an external integration package to use it.

When you pass a query to `SearchApiWebSearch`, it returns a list of URLs and text snippets that are most relevant to your search.

## Installation

Since the SearchApi web search component is built into the core Haystack framework, you just need to install `haystack-ai`:

```bash
pip install haystack-ai
```

You will also need to get an API key from [SearchApi](https://www.searchapi.io/) and set it as an environment variable:

```bash
export SEARCHAPI_API_KEY="your-api-key"
```

## Usage

### Components

This integration provides the following component:

- [`SearchApiWebSearch`](https://docs.haystack.deepset.ai/docs/searchapiwebsearch): A component that queries the SearchApi service to find web pages relevant to a given query.

### Standalone Usage

Here is how you can use `SearchApiWebSearch` directly:

```python
from haystack.components.websearch import SearchApiWebSearch
from haystack.utils import Secret
import os

# Ensure the environment variable is set
os.environ["SEARCHAPI_API_KEY"] = "your-api-key"

# Initialize the component (it automatically uses the SEARCHAPI_API_KEY environment variable)
web_search = SearchApiWebSearch(api_key=Secret.from_env_var("SEARCHAPI_API_KEY"))

# Run a search query
results = web_search.run(query="What is Haystack AI?")

# Access the search results
documents = results["documents"]
links = results["links"]

for doc in documents:
    print(f"Title: {doc.meta.get('title')}")
    print(f"Snippet: {doc.content}")
    print(f"URL: {doc.meta.get('link')}")
    print("-" * 50)
```


## License

`haystack-ai` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
