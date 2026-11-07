---
layout: integration
name: cloro
description: Search Google with the AI Overview, and get ChatGPT, Google AI Mode, Gemini and Bing AI Mode answers with their cited sources, through the cloro API
authors:
    - name: cloro
      socials:
        github: cloro-dev
pypi: https://pypi.org/project/cloro-haystack
repo: https://github.com/cloro-dev/cloro-haystack
type: Search & Extraction
report_issue: https://github.com/cloro-dev/cloro-haystack/issues
logo: /logos/cloro.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [CloroWebSearch](#clorowebsearch)
  - [CloroAIAnswer](#cloroaianswer)
  - [In a Pipeline](#in-a-pipeline)
- [License](#license)

## Overview

[cloro](https://cloro.dev/?utm_source=haystack-integrations&utm_medium=byok) is an API that returns the results of Google Search and the answers of AI search engines as structured JSON. This integration provides two components:

- `CloroWebSearch`: searches Google and returns the organic results as Haystack `Document` objects, with their links. It can also return the Google AI Overview as the first `Document`.
- `CloroAIAnswer`: sends a query to ChatGPT, Google AI Mode, Gemini or Bing AI Mode and returns the answer as Markdown, with one `Document` for each source that the answer cites.

You need a cloro API key. You can get one at [dashboard.cloro.dev](https://dashboard.cloro.dev/api-keys?utm_source=haystack-integrations&utm_medium=byok). The free plan includes 500 credits each month.

| Component | Credits per run |
|---|--:|
| `CloroWebSearch` | 5, or 7 with the AI Overview |
| `CloroAIAnswer` | ChatGPT 7, Google AI Mode 6, Gemini 6, Bing AI Mode 6 |

## Installation

```bash
pip install cloro-haystack
```

## Usage

Set your API key as the `CLORO_API_KEY` environment variable.

### CloroWebSearch

```python
from haystack_integrations.components.websearch.cloro import CloroWebSearch

web_search = CloroWebSearch(top_k=5, country="US", include_ai_overview=True)

result = web_search.run(query="What is retrieval-augmented generation?")
documents = result["documents"]
links = result["links"]
```

Each organic result is a `Document`. Its content is the Google snippet, and its meta has `title`, `link` and `position`. The AI Overview `Document` has `meta["source"] == "google_ai_overview"` and the URLs it cites in `meta["links"]`.

Parameters:

- **`api_key`**: cloro API key. Defaults to the `CLORO_API_KEY` environment variable.
- **`top_k`**: Maximum number of organic results. Defaults to 10. One request returns one page of Google results.
- **`country`**: ISO 3166-1 alpha-2 country code. Defaults to `"US"`.
- **`allowed_domains`**: Domains to limit the search to.
- **`include_ai_overview`**: Return the Google AI Overview as the first `Document`. Defaults to `False`.
- **`search_params`**: Other request fields, such as `device`, `location`, `hl` or `pages`.

### CloroAIAnswer

```python
from haystack_integrations.components.websearch.cloro import CloroAIAnswer

ai_answer = CloroAIAnswer(engine="aimode")  # "chatgpt", "aimode", "gemini" or "bing_aimode"

result = ai_answer.run(query="What is retrieval-augmented generation?")
print(result["replies"][0])
print(result["links"])
```

An answer can take 15 to 60 seconds. The default timeout is 180 seconds.

With `engine="bing_aimode"`, the query can have a maximum of 3,500 characters after URL encoding, and fewer for non-Latin scripts. To send the query from a US state, set `search_params={"state": "CA"}` with `country="US"` (2 more credits).

### In a Pipeline

This RAG pipeline uses `CloroWebSearch` to get web results and an LLM to answer the question:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.cloro import CloroWebSearch

prompt_template = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user(
        "Given the information below:\n"
        "{% for document in documents %}{{ document.content }}\n{% endfor %}\n"
        "Answer the following question: {{ query }}.\nAnswer:",
    ),
]

pipe = Pipeline()
pipe.add_component("search", CloroWebSearch(top_k=5, include_ai_overview=True))
pipe.add_component(
    "prompt_builder",
    ChatPromptBuilder(template=prompt_template, required_variables={"query", "documents"}),
)
pipe.add_component("llm", OpenAIChatGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"), model="gpt-4o-mini"))

pipe.connect("search.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.messages")

query = "What is retrieval-augmented generation?"
result = pipe.run(data={"search": {"query": query}, "prompt_builder": {"query": query}})
print(result["llm"]["replies"][0].text)
```

The outputs of `CloroAIAnswer` (`replies` and `documents`) connect directly to `AnswerBuilder`:

```python
from haystack import Pipeline
from haystack.components.builders import AnswerBuilder
from haystack_integrations.components.websearch.cloro import CloroAIAnswer

pipe = Pipeline()
pipe.add_component("ai", CloroAIAnswer(engine="chatgpt"))
pipe.add_component("answer", AnswerBuilder())
pipe.connect("ai.replies", "answer.replies")
pipe.connect("ai.documents", "answer.documents")

query = "Which vector databases support hybrid search?"
result = pipe.run({"ai": {"query": query}, "answer": {"query": query}})
print(result["answer"]["answers"][0].data)
```

Both components have `run_async` for use in an `AsyncPipeline`.

### License

`cloro-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
