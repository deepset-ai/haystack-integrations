---
layout: integration
name: ddgs
description: Keyless, multi-engine web search for Haystack via ddgs (Dux Distributed Global Search)
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/ddgs-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ddgs
type: Search & Extraction
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [DDGSWebSearch](#ddgswebsearch)
- [License](#license)

## Overview

[ddgs](https://github.com/deedy5/ddgs) ("Dux Distributed Global Search") is a free metasearch library that aggregates results from multiple backends — DuckDuckGo, Google, Bing, Brave, Yahoo, Yandex, and more.

This integration provides:
- [`DDGSWebSearch`](https://docs.haystack.deepset.ai/docs/ddgswebsearch): Searches the web through ddgs and returns results as Haystack `Document` objects along with source URLs.

No API key is required.

## Installation

```bash
pip install ddgs-haystack
```

## Usage

### DDGSWebSearch

`DDGSWebSearch` queries multiple search backends through ddgs and returns results as Haystack `Document` objects containing the content snippets and metadata (title, URL). Source URLs are also returned separately.

#### Basic Example

```python
from haystack_integrations.components.websearch.ddgs import DDGSWebSearch

web_search = DDGSWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

#### In a Pipeline

Here is an example of a RAG pipeline that uses `DDGSWebSearch` to retrieve web content and answer a question:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.ddgs import DDGSWebSearch

web_search = DDGSWebSearch(top_k=3)

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
from haystack_integrations.components.websearch.ddgs import DDGSWebSearch

async def main():
    web_search = DDGSWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

#### Parameters

- **`top_k`**: Maximum number of results to return. Defaults to 10.
- **`backend`**: Comma-separated ddgs backends to query, or `"auto"` to let ddgs choose (e.g. `"duckduckgo, google, brave"`). Defaults to `"auto"`.
- **`region`**: Region/locale for the search, e.g. `"us-en"`, `"de-de"`, or `"wt-wt"` (no region). Defaults to `"us-en"`.
- **`safesearch`**: Safe-search level: `"on"`, `"moderate"`, or `"off"`. Defaults to `"moderate"`.
- **`search_params`**: Additional keyword arguments forwarded to `DDGS().text()`, for example `page` or `timelimit`.

### License

`ddgs-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
