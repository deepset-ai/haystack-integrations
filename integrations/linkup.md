---
layout: integration
name: Linkup
description: Search the web using the Linkup API, optimized for LLM and agent applications
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/linkup-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Search & Extraction
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [LinkupWebSearch](#linkupwebsearch)
- [License](#license)

## Overview

[Linkup](https://www.linkup.so) is a web search API built for LLM and agent applications, returning grounded results with source URLs.

This integration provides:
- [`LinkupWebSearch`](https://docs.haystack.deepset.ai/docs/linkupwebsearch): Searches the web using the Linkup API and returns results as Haystack `Document` objects along with source URLs.

You need a Linkup API key to use this integration. You can get one at [linkup.so](https://www.linkup.so).

## Installation

```bash
pip install linkup-haystack
```

## Usage

### LinkupWebSearch

`LinkupWebSearch` queries the Linkup Search API and returns results as Haystack `Document` objects containing the content snippets and metadata (title, URL). Source URLs are also returned separately.

Set your API key as the `LINKUP_API_KEY` environment variable.

#### Basic Example

```python
from haystack_integrations.components.websearch.linkup import LinkupWebSearch

web_search = LinkupWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

#### In a Pipeline

Here is an example of a RAG pipeline that uses `LinkupWebSearch` to retrieve web content and answer a question:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.linkup import LinkupWebSearch

web_search = LinkupWebSearch(top_k=3)

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
from haystack_integrations.components.websearch.linkup import LinkupWebSearch

async def main():
    web_search = LinkupWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

#### Parameters

- **`api_key`**: API key for Linkup. Defaults to the `LINKUP_API_KEY` environment variable.
- **`top_k`**: Maximum number of results to return. Maps to the `max_results` parameter of the Linkup API. Defaults to 10.
- **`depth`**: The depth of the search. Can be `"fast"` (beta, sub-second, keyword-based queries only), `"standard"` for a simple search, or `"deep"` for a more powerful agentic workflow. Defaults to `"standard"`.
- **`search_params`**: Additional parameters passed to the Linkup search API, such as `include_images`, `from_date`, `to_date`, `include_domains`, and `exclude_domains`.

### License

`linkup-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
