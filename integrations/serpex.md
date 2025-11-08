---
layout: integration
name: Serpex
description: Multi-engine web search integration for Haystack — access Google, Bing, DuckDuckGo, Brave, Yahoo, and Yandex via Serpex API
authors:
    - name: Divyesh Radadiya
      socials:
        github: divyeshradadiya
pypi: https://pypi.org/project/serpex-haystack/
repo: https://github.com/divyeshradadiya/serpex-haystack
report_issue: https://github.com/divyeshradadiya/serpex-haystack/issues
type: Custom Component
logo: /logos/serpex.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Serpex](https://serpex.dev) is a unified web search API that provides access to multiple search engines through a single interface. This Haystack integration allows you to seamlessly incorporate web search results into your Haystack RAG (Retrieval-Augmented Generation) pipelines and AI applications.

### Key Features

- 🔍 **Multi-Engine Support**: Switch between Google, Bing, DuckDuckGo, Brave, Yahoo, and Yandex
- ⚡ **High Performance**: Fast and reliable API with automatic retries
- 🎯 **Rich Results**: Get organic search results with titles, snippets, and URLs
- 🕒 **Time Filters**: Filter results by day, week, month, or year
- 🔒 **Type-Safe**: Fully typed with comprehensive type hints
- 📝 **Haystack Native**: Seamless integration with Haystack 2.0+ components

## Installation

```bash
pip install serpex-haystack
```

## Usage

### Basic Usage

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.serpex import SerpexWebSearch

# Initialize the component
web_search = SerpexWebSearch(
    api_key=Secret.from_env_var("SERPEX_API_KEY"),
    engine="google",  # Options: google, bing, duckduckgo, brave, yahoo, yandex
)

# Perform a search
results = web_search.run(query="What is Haystack AI?")

# Access the results
for doc in results["documents"]:
    print(f"Title: {doc.meta['title']}")
    print(f"URL: {doc.meta['url']}")
    print(f"Snippet: {doc.content}\n")
```

### RAG Pipeline Example

Build a complete RAG pipeline with web search:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret
from haystack_integrations.components.websearch.serpex import SerpexWebSearch

# Define prompt template
prompt_template = """
Based on the following search results, answer the question comprehensively.

Search Results:
{% for doc in documents %}
{{ loop.index }}. {{ doc.meta.title }}
   {{ doc.content }}
   Source: {{ doc.meta.url }}

{% endfor %}

Question: {{ query }}

Answer:
"""

# Build the pipeline
pipe = Pipeline()
pipe.add_component("search", SerpexWebSearch(api_key=Secret.from_env_var("SERPEX_API_KEY")))
pipe.add_component("prompt", PromptBuilder(template=prompt_template))
pipe.add_component("llm", OpenAIGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY")))

# Connect components
pipe.connect("search.documents", "prompt.documents")
pipe.connect("prompt", "llm")

# Run the pipeline
result = pipe.run({
    "search": {"query": "Latest developments in AI agents"},
    "prompt": {"query": "Latest developments in AI agents"}
})

print(result["llm"]["replies"][0])
```

### Advanced Features

#### Multiple Search Engines

```python
# Compare results from different engines
google_search = SerpexWebSearch(engine="google")
bing_search = SerpexWebSearch(engine="bing")
duckduckgo_search = SerpexWebSearch(engine="duckduckgo")
```

#### Time Range Filtering

```python
# Get only recent results
recent_results = web_search.run(
    query="AI news",
    time_range="week"  # Options: "day", "week", "month", "year", "all"
)
```

#### Runtime Configuration Override

```python
# Override default settings per query
results = web_search.run(
    query="Python tutorials",
    engine="duckduckgo",  # Override default engine
)
```

### Component API

#### SerpexWebSearch

**Parameters:**
- `api_key` (Secret): Serpex API key. Defaults to `SERPEX_API_KEY` environment variable.
- `engine` (str): Search engine to use. Options: `"auto"`, `"google"`, `"bing"`, `"duckduckgo"`, `"brave"`, `"yahoo"`, `"yandex"`. Default: `"google"`.
- `timeout` (float): Request timeout in seconds. Default: `10.0`.
- `retry_attempts` (int): Number of retry attempts. Default: `2`.

**Inputs:**
- `query` (str): The search query string.
- `engine` (str, optional): Override the default search engine.
- `time_range` (str, optional): Filter by time range (`"all"`, `"day"`, `"week"`, `"month"`, `"year"`).

**Outputs:**
- `documents` (`List[Document]`): List of Haystack Document objects containing search results.

Each document includes:
- **content**: The search result snippet
- **meta**:
  - `title`: Result title
  - `url`: Result URL
  - `position`: Position in search results
  - `query`: Original search query
  - `engine`: Search engine used

## License

`serpex-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.