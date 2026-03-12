---
layout: integration
name: Exa
description: Search the web with Exa's AI-powered search, get content, answers, and conduct deep research
authors:
  - name: Exa
    socials:
      github: exa-labs
      twitter: ExaAILabs
pypi: https://pypi.org/project/exa-haystack/
repo: https://github.com/exa-labs/exa-haystack
report_issue: https://github.com/exa-labs/exa-haystack/issues
type: Search & Extraction
toc: true
logo: /logos/exa.png
version: Haystack 2.0
---

## Overview

The Exa integration for Haystack provides components to search the web, fetch content, get AI-powered answers, and conduct deep research using Exa's API.

## Installation

```bash
pip install exa-haystack
```

### Components

- **ExaWebSearch**: AI-powered web search with multiple speed/quality modes (`auto`, `instant`, `fast`, `deep`, `deep-reasoning`, `deep-max`, `neural`)
- **ExaFindSimilar**: Find pages similar to a URL
- **ExaContents**: Fetch full content for URLs with freshness control
- **ExaAnswer**: Get AI-powered answers with citations and optional structured output
- **ExaStreamAnswer**: Streaming answers with SSE and optional structured output
- **ExaResearch**: Deep research with automatic source gathering

## Usage

### Web Search

```python
from haystack_integrations.components.websearch.exa import ExaWebSearch

search = ExaWebSearch(num_results=5, type="auto", text=True)
results = search.run(query="latest AI developments")

for doc in results["documents"]:
    print(doc.meta["title"], doc.meta["url"])
```

Use `type="instant"` for sub-150ms searches, `type="deep"` or `type="deep-reasoning"` for higher-quality results, or `type="auto"` (default) to let Exa choose.

#### Category Filtering

```python
search = ExaWebSearch(num_results=5, category="research paper")
results = search.run(query="transformer architectures")
```

Available categories: `company`, `research paper`, `news`, `pdf`, `tweet`, `personal site`, `financial report`, `people`.

#### Content Freshness

```python
search = ExaWebSearch(num_results=5, max_age_hours=24, text=True)
results = search.run(query="breaking news today")
```

Use `max_age_hours` to control content freshness: `0` = always livecrawl, `-1` = cache only, positive integer = max cache age in hours.

#### Structured Deep Search Output

```python
search = ExaWebSearch(
    type="deep",
    output_schema={"type": "object", "properties": {"summary": {"type": "string"}}},
)
results = search.run(query="AI in healthcare")
print(results["deep_output"])  # Structured output from deep search
```

### Find Similar Pages

```python
from haystack_integrations.components.websearch.exa import ExaFindSimilar

similar = ExaFindSimilar(num_results=5)
results = similar.run(url="https://example.com/article")
```

### Fetch Content from URLs

```python
from haystack_integrations.components.websearch.exa import ExaContents

contents = ExaContents(text=True, max_age_hours=0)
results = contents.run(urls=["https://example.com/page1", "https://example.com/page2"])

for doc in results["documents"]:
    print(doc.meta["title"], len(doc.content), "chars")

# Per-URL status info
for status in results["statuses"]:
    print(status["id"], status["status"])
```

### AI-Powered Answers

```python
from haystack_integrations.components.websearch.exa import ExaAnswer

answer = ExaAnswer()
result = answer.run(query="What is retrieval augmented generation?")
print(result["answer"])

for citation in result["citations"]:
    print(citation.meta["title"], citation.meta["url"])
```

#### Structured Answer Output

```python
answer = ExaAnswer(
    output_schema={
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {"type": "array", "items": {"type": "string"}},
        },
    }
)
result = answer.run(query="What is RAG?")
```

### Streaming Answers

```python
from haystack_integrations.components.websearch.exa import ExaStreamAnswer

stream = ExaStreamAnswer()
result = stream.run(query="Explain quantum computing")
for chunk in result["stream"]:
    print(chunk, end="", flush=True)
```

### Deep Research

```python
from haystack_integrations.components.websearch.exa import ExaResearch

research = ExaResearch()
result = research.run(query="Impact of AI on healthcare")
print(result["report"])
```

### Authentication

Set your Exa API key as an environment variable:

```bash
export EXA_API_KEY="your-api-key"
```

Or pass it directly:

```python
from haystack.utils import Secret
search = ExaWebSearch(api_key=Secret.from_token("your-api-key"))
```
