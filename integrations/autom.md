---
layout: integration
name: Autom
description: Live Google, Bing, Brave, DuckDuckGo and Yahoo search results for Haystack pipelines and agents, through the Autom SERP API
authors:
    - name: Autom
      socials:
        github: automdev
pypi: https://pypi.org/project/autom-haystack/
repo: https://github.com/automdev/autom-haystack
report_issue: https://github.com/automdev/autom-haystack/issues
type: Search & Extraction
logo: /logos/autom.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Autom](https://www.autom.dev) is a SERP API: it runs a search on Google, Bing, Brave, DuckDuckGo or Yahoo at the time of the call and returns the results as JSON.

The `autom-haystack` package adds one component, `AutomWebSearch`. It returns one `Document` per organic result, with the snippet as content and the `title`, `link` and `position` in its metadata (plus `date` and `source` when the engine shows them), and the list of result links. Use it to ground a RAG pipeline in current web results, or give it to an agent as a search tool.

- **Five engines:** `google` (the default), `bing`, `brave`, `duckduckgo` or `yahoo`.
- **Search options:** country and language (`gl`, `hl`), Google time filters (`tbs`), and `allowed_domains` to search only some sites.
- **Errors you can act on:** a failed request raises `AutomError`, a Haystack `ComponentError` with the HTTP status; the API key never appears in the message.
- `run_async` is available for async pipelines.

## Installation

```bash
pip install autom-haystack
```

Get an API key at [app.autom.dev](https://app.autom.dev) and set it in the environment:

```bash
export AUTOM_API_KEY="your-api-key"
```

## Usage

### On its own

```python
from haystack_integrations.components.websearch.autom import AutomWebSearch

search = AutomWebSearch(top_k=5)  # reads AUTOM_API_KEY
result = search.run(query="What is Haystack?")

for doc in result["documents"]:
    print(doc.meta["title"], doc.meta["link"])
    print(doc.content)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | `Secret.from_env_var("AUTOM_API_KEY")` | Autom API key |
| `top_k` | `10` | Maximum number of results; `None` keeps the whole page |
| `engine` | `google` | `google`, `bing`, `brave`, `duckduckgo` or `yahoo` |
| `allowed_domains` | | Only search these domains, added to the query as `site:` filters |
| `search_params` | | Extra parameters for Autom, such as `{"gl": "us", "hl": "en"}`, or `{"tbs": "qdr:w"}` for the past week on Google |
| `timeout` | `60` | Seconds to wait for Autom |

### In a RAG pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.websearch.autom import AutomWebSearch

template = [
    ChatMessage.from_user(
        "Answer the question from these search results.\n"
        "{% for doc in documents %}- {{ doc.content }} ({{ doc.meta.link }})\n{% endfor %}\n"
        "Question: {{ question }}"
    )
]

pipeline = Pipeline()
pipeline.add_component("search", AutomWebSearch(top_k=5))
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["documents", "question"]))
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4.1-mini"))
pipeline.connect("search.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.messages")

question = "What is new in Python 3.13?"
result = pipeline.run({"search": {"query": question}, "prompt": {"question": question}})
print(result["llm"]["replies"][0].text)
```

### As an agent tool

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import ComponentTool
from haystack_integrations.components.websearch.autom import AutomWebSearch

search_tool = ComponentTool(
    component=AutomWebSearch(top_k=5),
    name="web_search",
    description="Search the web and get the top results with their links.",
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4.1-mini"),
    system_prompt="You answer with current information from the web and cite the links you used.",
    tools=[search_tool],
)

result = agent.run(messages=[ChatMessage.from_user("What did the latest Haystack release add?")])
print(result["last_message"].text)
```

### Other engines and filters

```python
from haystack_integrations.components.websearch.autom import AutomWebSearch

# Brave results from Germany, in German
brave = AutomWebSearch(engine="brave", search_params={"gl": "de", "hl": "de"})

# Google results from the past week, only from two sites
recent = AutomWebSearch(search_params={"tbs": "qdr:w"}, allowed_domains=["python.org", "peps.python.org"])
```

## License

`autom-haystack` is distributed under the terms of the [MIT](https://github.com/automdev/autom-haystack/blob/main/LICENSE) license.
