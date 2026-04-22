---
layout: integration
name: SerperDev
description: Uses Serper.dev API for web searches
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
logo: /logos/serperdev.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `SerperDevWebSearch` component allows you to perform web searches using the [Serper.dev](https://serper.dev/) API. It retrieves relevant snippets and URLs that can be used directly in your Haystack applications, such as Retrieval-Augmented Generation (RAG) pipelines or with Haystack Agents.

This component is part of the core `haystack-ai` package, meaning you do not need to install an external integration package to use it.

When you pass a query to `SerperDevWebSearch`, it returns a list of URLs and text snippets that are most relevant to your search.

## Installation

Since the Serper.dev web search component is built into the core Haystack framework, you just need to install `haystack-ai`:

```bash
pip install haystack-ai
```

You will also need to get an API key from [Serper.dev](https://serper.dev/) and set it as an environment variable:

```bash
export SERPERDEV_API_KEY="your-api-key"
```

## Usage

### Components

This integration provides the following component:

- `SerperDevWebSearch`: A component that queries the Serper.dev API to find web pages relevant to a given query.

### Standalone Usage

Here is how you can use `SerperDevWebSearch` directly:

```python
from haystack.components.websearch import SerperDevWebSearch
from haystack.utils import Secret
import os

# Ensure the environment variable is set
os.environ["SERPERDEV_API_KEY"] = "your-api-key"

# Initialize the component (it automatically uses the SERPERDEV_API_KEY environment variable)
web_search = SerperDevWebSearch(api_key=Secret.from_env_var("SERPERDEV_API_KEY"))

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

### Usage within a Pipeline

You can integrate `SerperDevWebSearch` directly into a Generative QA pipeline to answer questions using the live web context:

```python
import os
from haystack import Pipeline
from haystack.components.websearch import SerperDevWebSearch
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator

os.environ["SERPERDEV_API_KEY"] = "your-serperdev-api-key"
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

template = """
Given the following web search results, answer the user's question.

Search Results:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}
Answer:
"""

pipe = Pipeline()
pipe.add_component("websearch", SerperDevWebSearch())
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OpenAIGenerator())

pipe.connect("websearch.documents", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = "What are the latest features in Haystack 2.0?"
response = pipe.run({
    "websearch": {"query": query},
    "prompt_builder": {"query": query}
})

print(response["llm"]["replies"][0])
```

## License

`haystack-ai` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
