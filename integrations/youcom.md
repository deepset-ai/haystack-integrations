---
layout: integration
name: You.com
description: Search the web using the You.com Search API with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/youcom-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/youcom
type: Search & Extraction
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [YouComWebSearch](#youcomwebsearch)
- [License](#license)

## Overview

[You.com](https://you.com/) provides a Search API built for AI agents and applications, returning
clean, structured web and news results.

This integration provides:
- [`YouComWebSearch`](https://docs.haystack.deepset.ai/docs/youcomwebsearch): Searches the web using the You.com Search API and returns results as Haystack `Document` objects along with source URLs.

`YouComWebSearch` works with zero configuration: when no API key is available, it searches using
You.com's keyless free tier (rate limited per IP), so getting-started pipelines run without any
setup. Set the `YOUDOTCOM_API_KEY` environment variable to use the keyed You.com Search API with
higher limits. You can get a free API key at [you.com/platform](https://you.com/platform).

## Installation

```bash
pip install youcom-haystack
```

## Usage

### YouComWebSearch

`YouComWebSearch` queries the You.com Search API and returns results as Haystack `Document` objects
containing content snippets and metadata (title, URL, source section, page age). Source URLs are
also returned separately.

#### Basic Example

```python
from haystack_integrations.components.websearch.youcom import YouComWebSearch

web_search = YouComWebSearch(top_k=5)  # no API key needed to get started

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

#### In a Pipeline

Here is an example of a RAG pipeline that uses `YouComWebSearch` to retrieve web content and answer a question:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.youcom import YouComWebSearch

web_search = YouComWebSearch(top_k=3)

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
from haystack_integrations.components.websearch.youcom import YouComWebSearch

async def main():
    web_search = YouComWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

#### Requiring an API key

By default, `YouComWebSearch` falls back to the rate-limited keyless tier when no API key resolves.
Pass `keyless_fallback=False` to require a key and fail fast instead, which is useful in production
pipelines where a missing key should surface as an error:

```python
from haystack_integrations.components.websearch.youcom import YouComWebSearch, YouComError

web_search = YouComWebSearch(keyless_fallback=False)

try:
    result = web_search.run(query="What is Haystack by deepset?")
except YouComError as error:
    print(f"Search failed: {error}")
```

#### Parameters

- **`api_key`**: You.com API key. Defaults to the `YOUDOTCOM_API_KEY` environment variable.
- **`keyless_fallback`**: When `True` (the default), searches use the keyless free tier if no API key
  resolves. When `False`, raises `YouComError` instead of silently degrading. Defaults to `True`.
- **`top_k`**: Maximum number of results to return per section (web, news). Defaults to 10.
- **`freshness`**: Only return results from within a given window, e.g. `"day"`, `"week"`, `"month"`,
  `"year"`, or a date range like `"YYYY-MM-DDtoYYYY-MM-DD"`.
- **`country`**: 2-letter country code determining the geographical focus of web results (e.g. `"US"`, `"DE"`).
- **`search_lang`**: Language of the returned web results in BCP 47 format (e.g. `"EN"`, `"PT-BR"`).
- **`safesearch`**: Content moderation level: `"off"`, `"moderate"`, or `"strict"`.
- **`extra_params`**: Additional query parameters passed directly to the You.com Search API.
- **`timeout`**: Timeout in seconds for the HTTP request. Defaults to 10.
- **`max_retries`**: Maximum number of retry attempts on transient failures. Defaults to 3.

### License

`youcom-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
