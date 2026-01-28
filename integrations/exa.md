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
type: Custom Component
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

## Components

- **ExaWebSearch**: AI-powered web search (auto, fast, deep modes)
- **ExaFindSimilar**: Find pages similar to a URL
- **ExaContents**: Fetch full content for URLs
- **ExaAnswer**: Get AI-powered answers with citations
- **ExaStreamAnswer**: Streaming answers with SSE
- **ExaResearch**: Deep research with automatic source gathering

## Usage

```python
from haystack_integrations.components.websearch.exa import ExaWebSearch, ExaAnswer

# Search the web
search = ExaWebSearch(num_results=5)
results = search.run(query="latest AI developments")

# Get answers with citations
answer = ExaAnswer()
result = answer.run(query="What is retrieval augmented generation?")
print(result["answer"])
```

## Authentication

Set your Exa API key as an environment variable:

```bash
export EXA_API_KEY="your-api-key"
```

Or pass it directly:

```python
from haystack.utils import Secret
search = ExaWebSearch(api_key=Secret.from_token("your-api-key"))
```
