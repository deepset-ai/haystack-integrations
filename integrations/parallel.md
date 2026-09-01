---
layout: integration
name: Parallel
description: Use the Parallel Search API and Parallel's web-research model in Haystack pipelines.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/parallel-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/parallel
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/parallel.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Parallel](https://parallel.ai) builds web research infrastructure for AI agents. The `parallel-haystack` package brings it to Haystack through two components:

- `ParallelWebSearch` — web search through the [Parallel Search API](https://docs.parallel.ai/api-reference/search/search), returning LLM-optimized excerpts as Haystack `Document` objects.
- `ParallelChatGenerator` — chat completion through the [Parallel Responses API](https://docs.parallel.ai/responses-api/responses-quickstart), where every answer is grounded in live web research with citations.

For more information about the Parallel APIs, see [the Parallel docs](https://docs.parallel.ai).

To follow along with this guide, you'll need a Parallel API key from the [Parallel platform](https://platform.parallel.ai). Add it as an environment variable, `PARALLEL_API_KEY`.

## Installation

```bash
pip install parallel-haystack
```

## Usage

You can use the Parallel components as standalone components or in Haystack pipelines.

### Use Parallel Web Search (Search API)

`ParallelWebSearch` returns three outputs: `documents` (excerpts with `title`, `url` and, where available, `publish_date` metadata), `links` (the result URLs), and `session_id`.

```python
import os

from haystack.utils import Secret
from haystack_integrations.components.websearch.parallel import ParallelWebSearch

os.environ["PARALLEL_API_KEY"] = "YOUR_PARALLEL_API_KEY"

websearch = ParallelWebSearch(
    api_key=Secret.from_env_var("PARALLEL_API_KEY"),
    top_k=5,
)
result = websearch.run(query="What is Haystack by deepset?")

print(result["documents"])
print(result["links"])
```

The Search API offers four modes — `turbo`, `fast`, `basic` and `advanced` — in increasing order of latency and quality. Pass the mode and any other Search API parameter through `search_params`, either at initialization or per `run()` call:

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.parallel import ParallelWebSearch

websearch = ParallelWebSearch(
    api_key=Secret.from_env_var("PARALLEL_API_KEY"),
    top_k=5,
    search_params={
        "mode": "turbo",
        "advanced_settings": {"source_policy": {"include_domains": ["arxiv.org"]}},
    },
)
result = websearch.run(query="Latest retrieval-augmented generation research")

for document in result["documents"]:
    print(document.meta["title"], document.meta["url"])
```

Searches that belong to the same task can share a session. Pass the `session_id` returned by one search back into the next one to get better contextual results:

```python
from haystack.utils import Secret
from haystack_integrations.components.websearch.parallel import ParallelWebSearch

websearch = ParallelWebSearch(api_key=Secret.from_env_var("PARALLEL_API_KEY"))

first = websearch.run(query="What is Haystack by deepset?")
second = websearch.run(
    query="Who maintains Haystack?",
    search_params={"session_id": first["session_id"]},
)

print(second["links"])
```

### Use Parallel Web Research (Responses API)

`ParallelChatGenerator` runs live web research for every call and returns an answer with citations. The `reasoning.effort` parameter selects the research tier: `low` (~5-10s), `medium` (~15-20s, the default) or `high` (~30-60s).

```python
import os

from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.parallel import ParallelChatGenerator

os.environ["PARALLEL_API_KEY"] = "YOUR_PARALLEL_API_KEY"

client = ParallelChatGenerator(generation_kwargs={"reasoning": {"effort": "low"}})
response = client.run(
    messages=[ChatMessage.from_user("What did Parallel Web Systems announce this year?")]
)

print(response["replies"][0].text)
```

Because web grounding is built into the model, tool calling and sampling parameters such as `tools`, `temperature` and `top_p` are accepted for SDK compatibility but have no effect on the response; the component logs a warning when it sees them.

### Use Parallel in a pipeline

This RAG pipeline searches the web with `ParallelWebSearch` and answers from the retrieved excerpts.

```python
import os

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.generators.parallel import ParallelChatGenerator
from haystack_integrations.components.websearch.parallel import ParallelWebSearch

os.environ["PARALLEL_API_KEY"] = "YOUR_PARALLEL_API_KEY"

prompt_builder = ChatPromptBuilder(
    template=[
        ChatMessage.from_system("You are a helpful assistant."),
        ChatMessage.from_user(
            "Given the information below:\n"
            "{% for document in documents %}{{ document.content }}\n{% endfor %}\n"
            "Answer the following question: {{ query }}.\nAnswer:"
        ),
    ],
    required_variables=["query", "documents"],
)

pipe = Pipeline()
pipe.add_component("search", ParallelWebSearch(api_key=Secret.from_env_var("PARALLEL_API_KEY"), top_k=3))
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", ParallelChatGenerator(generation_kwargs={"reasoning": {"effort": "low"}}))

pipe.connect("search.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.messages")

query = "What is Haystack by deepset?"
result = pipe.run(data={"search": {"query": query}, "prompt_builder": {"query": query}})

print(result["llm"]["replies"][0].text)
```

### License

`parallel-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
