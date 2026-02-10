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

- **ExaWebSearch**: AI-powered web search (auto, fast, deep modes)
- **ExaFindSimilar**: Find pages similar to a URL
- **ExaContents**: Fetch full content for URLs
- **ExaAnswer**: Get AI-powered answers with citations
- **ExaStreamAnswer**: Streaming answers with SSE
- **ExaResearch**: Deep research with automatic source gathering

## Usage

### Web Search

```python
from haystack_integrations.components.websearch.exa import ExaWebSearch

search = ExaWebSearch(num_results=5)
results = search.run(query="latest AI developments")
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

contents = ExaContents()
results = contents.run(urls=["https://example.com/page1", "https://example.com/page2"])
```

### AI-Powered Answers

```python
from haystack_integrations.components.websearch.exa import ExaAnswer

answer = ExaAnswer()
result = answer.run(query="What is retrieval augmented generation?")
print(result["answer"])
```

### Streaming Answers

```python
from haystack_integrations.components.websearch.exa import ExaStreamAnswer

stream = ExaStreamAnswer()
for chunk in stream.run(query="Explain quantum computing"):
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
