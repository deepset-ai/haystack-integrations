---
layout: integration
name: Tavily
description: Search the web using Tavily's AI-powered search API, optimized for LLM applications
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/tavily-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Search & Extraction
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/tavily.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [TavilyWebSearch](#tavilywebsearch)
- [License](#license)

## Overview

[Tavily](https://tavily.com) is an AI-powered search API built for LLM applications. It returns high-quality, structured results with relevant content and source URLs — without the noise of traditional search engines.

This integration provides:
- [`TavilyWebSearch`](https://docs.haystack.deepset.ai/docs/tavilywebsearch): Searches the web using the Tavily API and returns results as Haystack `Document` objects along with source URLs.

You need a Tavily API key to use this integration. You can get one at [tavily.com](https://tavily.com).

## Installation

```bash
pip install tavily-haystack
```

## Usage

### TavilyWebSearch

`TavilyWebSearch` queries the Tavily Search API and returns results as Haystack `Document` objects containing the content snippets and metadata (title, URL). Source URLs are also returned separately.

#### Basic Example

```python
from haystack_integrations.components.websearch.tavily import TavilyWebSearch

web_search = TavilyWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

By default, the component reads the API key from the `TAVILY_API_KEY` environment variable. You can also pass it explicitly:

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.tavily import TavilyWebSearch

web_search = TavilyWebSearch(
    api_key=Secret.from_token("your-api-key"),
    top_k=5,
    search_params={"search_depth": "advanced"},
)
```

#### In a Pipeline

Here is an example of a RAG pipeline that uses `TavilyWebSearch` to retrieve web content and answer a question:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.tavily import TavilyWebSearch

web_search = TavilyWebSearch(top_k=3)

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

#### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.websearch.tavily import TavilyWebSearch

async def main():
    web_search = TavilyWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

#### Parameters

- **`api_key`**: API key for Tavily. Defaults to the `TAVILY_API_KEY` environment variable.
- **`top_k`**: Maximum number of results to return. Defaults to 10.
- **`search_params`**: Additional parameters passed to the Tavily Search API. Supported keys include `search_depth`, `include_answer`, `include_raw_content`, `include_domains`, `exclude_domains`. See the [Tavily API reference](https://docs.tavily.com/docs/tavily-api/rest_api) for all available options.

### License

`tavily-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
