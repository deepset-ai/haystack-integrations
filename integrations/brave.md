---
layout: integration
name: Brave Search
description: Search the web using the Brave Search API with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/brave-search-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Search & Extraction
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/brave.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [BraveWebSearch](#bravewebsearch)
- [License](#license)

## Overview

[Brave Search](https://brave.com/search/api/) is an independent search engine with its own web index. Unlike most search APIs, it does not rely on Google or Bing, making it a great choice for privacy-conscious applications.

This integration provides:
- [`BraveWebSearch`](https://docs.haystack.deepset.ai/docs/bravewebsearch): Searches the web using the Brave Search API and returns results as Haystack `Document` objects along with source URLs.

You need a Brave Search API key to use this integration. You can get one at [brave.com/search/api](https://brave.com/search/api/).

## Installation

```bash
pip install brave-search-haystack
```

## Usage

### BraveWebSearch

`BraveWebSearch` queries the Brave Search API and returns results as Haystack `Document` objects containing the content snippets and metadata (title, URL). Source URLs are also returned separately.

#### Basic Example

```python
from haystack_integrations.components.websearch.brave import BraveWebSearch

web_search = BraveWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

#### In a Pipeline

Here is an example of a RAG pipeline that uses `BraveWebSearch` to retrieve web content and answer a question:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.brave import BraveWebSearch

web_search = BraveWebSearch(top_k=3)

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
print(result["llm"]["replies"][0].text)
```

#### Async Support

The component supports asynchronous execution via `run_async`:

```python
import asyncio
from haystack_integrations.components.websearch.brave import BraveWebSearch

async def main():
    web_search = BraveWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

#### Parameters

- **`api_key`**: API key for Brave Search. Defaults to the `BRAVE_API_KEY` environment variable.
- **`top_k`**: Maximum number of results to return. Defaults to 10.
- **`country`**: 2-letter country code to bias search results (e.g. `"US"`, `"DE"`).
- **`search_lang`**: Language code for search results (e.g. `"en"`, `"de"`).
- **`extra_params`**: Additional query parameters passed directly to the Brave Search API.
- **`timeout`**: Timeout in seconds for the HTTP request. Defaults to 10.
- **`max_retries`**: Maximum number of retry attempts on transient failures. Defaults to 3.

### License

`brave-search-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
