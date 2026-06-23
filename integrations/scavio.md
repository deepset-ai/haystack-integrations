---
layout: integration
name: Scavio
description: Search the web using Scavio, a unified search API for AI agents
authors:
    - name: Scavio
      socials:
        github: scavio-ai
repo: https://github.com/scavio-ai/haystack-scavio
pypi: https://pypi.org/project/scavio-haystack
type: Search & Extraction
report_issue: https://github.com/scavio-ai/haystack-scavio/issues
logo: /logos/scavio.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [ScavioWebSearch](#scaviowebsearch)
- [License](#license)

## Overview

[Scavio](https://scavio.dev) is a unified search API built for AI agents. It provides real-time
search across Google, YouTube, Amazon, Walmart, Reddit, TikTok, and more through a single API,
returning structured results with content and source URLs.

This integration provides:
- `ScavioWebSearch`: Searches the web using Scavio's Google web search endpoint and returns results
  as Haystack `Document` objects along with source URLs.

You need a Scavio API key to use this integration. You can get one at
[dashboard.scavio.dev](https://dashboard.scavio.dev).

## Installation

```bash
pip install scavio-haystack
```

## Usage

### ScavioWebSearch

`ScavioWebSearch` queries the Scavio search API and returns results as Haystack `Document` objects
containing the content snippets and metadata (title, URL). Source URLs are also returned separately.

Set your API key as the `SCAVIO_API_KEY` environment variable.

#### Basic Example

```python
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

web_search = ScavioWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

#### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

template = """
Given the following web search results, answer the question.

Results:
{% for doc in documents %}{{ doc.content }}
{% endfor %}

Question: {{ query }}
Answer:
"""

pipe = Pipeline()
pipe.add_component("search", ScavioWebSearch(top_k=5))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OpenAIGenerator())
pipe.connect("search.documents", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = "What is Haystack by deepset?"
result = pipe.run(data={"search": {"query": query}, "prompt_builder": {"query": query}})
print(result["llm"]["replies"][0])
```

#### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

async def main():
    web_search = ScavioWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

#### Parameters

- **`api_key`**: API key for Scavio. Defaults to the `SCAVIO_API_KEY` environment variable.
- **`top_k`**: Maximum number of results to return. Defaults to 10.
- **`search_params`**: Additional parameters passed to the Scavio Google search endpoint. Supported
  keys include `country_code`, `language`, `page`, `search_type`, `device`, `nfpr`, `light_request`.

### License

`scavio-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
