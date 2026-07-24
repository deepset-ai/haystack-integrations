---
layout: integration
name: Live Tennis API
description: Live tennis scores, matches and players as Haystack Documents for RAG and agent pipelines
authors:
    - name: Ben
      socials:
        github: bensynapse
pypi: https://pypi.org/project/livetennisapi-haystack/
repo: https://github.com/livetennisapi/livetennisapi-haystack
type: Data Ingestion
report_issue: https://github.com/livetennisapi/livetennisapi-haystack/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [LiveTennisMatchFetcher](#livetennismatchfetcher)
  - [LiveTennisPlayerSearch](#livetennisplayersearch)
- [License](#license)

## Overview

The [Live Tennis API](https://livetennisapi.com) serves live scores, matches and player data
across the ATP, WTA, Challenger, ITF and junior tours.

This integration provides:

- **`LiveTennisMatchFetcher`**: fetches live, upcoming or completed matches (optionally one
  match by id, optionally filtered by tour) and returns them as Haystack `Document` objects.
  Each Document's `content` is a clean human-readable match summary and its `meta` carries
  the structured fields (ids, players, sets/games/points, server, winner).
- **`LiveTennisPlayerSearch`**: searches players by name (ranked players first) and returns
  them as `Document` objects with the same content/meta split.

You need a Live Tennis API key to use this integration (a free tier is available). The
components read it from the `LIVETENNISAPI_KEY` environment variable via Haystack's `Secret`,
so serialized pipelines never contain the key. Built on the official
[`livetennisapi`](https://pypi.org/project/livetennisapi/) Python client.

## Installation

```bash
pip install livetennisapi-haystack
```

## Usage

Set your API key as the `LIVETENNISAPI_KEY` environment variable.

### LiveTennisMatchFetcher

#### Basic Example

```python
from livetennisapi_haystack import LiveTennisMatchFetcher

fetcher = LiveTennisMatchFetcher(limit=5)
result = fetcher.run(status="live")
for doc in result["documents"]:
    print(doc.content)
```

#### In a Pipeline

A RAG pipeline that answers questions about the matches on court right now:

```python
from haystack import Pipeline
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from livetennisapi_haystack import LiveTennisMatchFetcher

prompt_template = [
    ChatMessage.from_system("You are a tennis commentator."),
    ChatMessage.from_user(
        "Current matches:\n"
        "{% for document in documents %}{{ document.content }}\n{% endfor %}\n"
        "Answer the following question: {{ query }}\nAnswer:"
    ),
]

pipe = Pipeline()
pipe.add_component("matches", LiveTennisMatchFetcher(limit=10))
pipe.add_component(
    "prompt_builder",
    ChatPromptBuilder(template=prompt_template, required_variables={"query", "documents"}),
)
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipe.connect("matches.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.messages")

query = "Who is closest to winning right now?"
result = pipe.run({"matches": {"status": "live"}, "prompt_builder": {"query": query}})
print(result["llm"]["replies"][0].text)
```

#### Parameters

- **`api_key`**: API key for the Live Tennis API. Defaults to the `LIVETENNISAPI_KEY`
  environment variable.
- **`status`**: Default lifecycle status: `"live"`, `"upcoming"` or `"completed"`.
  Overridable per `run()`.
- **`tour`**: Optional tour filter: `"atp"`, `"wta"`, `"challenger"`, `"itf"` or
  `"juniors"`. Each value covers its singles and doubles draws.
- **`limit`**: Maximum number of matches to return (1-200). Defaults to 10.
- **`run(match_id=...)`**: fetches one specific match instead of a listing.

If your key's tier does not unlock an endpoint (HTTP 403), the component returns a single
readable Document tagged `meta["error"] = "upgrade_required"` instead of raising, so agents
can surface the message and RAG pipelines can filter it.

### LiveTennisPlayerSearch

```python
from livetennisapi_haystack import LiveTennisPlayerSearch

search = LiveTennisPlayerSearch(limit=3)
result = search.run(query="alcaraz")
for doc in result["documents"]:
    print(doc.content)
```

#### Parameters

- **`api_key`**: API key. Defaults to the `LIVETENNISAPI_KEY` environment variable.
- **`limit`**: Maximum number of players to return (1-200). Defaults to 10.

## License

`livetennisapi-haystack` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
