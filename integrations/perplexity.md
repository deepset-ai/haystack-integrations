---
layout: integration
name: Perplexity
description: Use the Perplexity API for chat completions, embeddings, and grounded web search.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/perplexity-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/perplexity
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/perplexity.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `perplexity-haystack` package lets you use Perplexity models and grounded search capabilities in Haystack pipelines through three components:

- `PerplexityChatGenerator` uses chat completions powered by the Perplexity Agent API and defaults to `sonar-pro`.
- `PerplexityTextEmbedder` and `PerplexityDocumentEmbedder` create embeddings through the Perplexity Embeddings API.
- `PerplexityWebSearch` retrieves grounded web search results through the Perplexity Search API.

For more information about the Perplexity API, see [the Perplexity docs](https://docs.perplexity.ai).

In order to follow along with this guide, you'll need a Perplexity API key. Add it as an environment variable, `PERPLEXITY_API_KEY`.

## Installation

```bash
pip install perplexity-haystack
```

## Usage

You can use the Perplexity components as standalone components or in Haystack pipelines.

### Use Perplexity Chat Completions

`PerplexityChatGenerator` is powered by the Perplexity Agent API and uses `sonar-pro` by default.

```python
import os

from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.perplexity import PerplexityChatGenerator

os.environ["PERPLEXITY_API_KEY"] = "YOUR_PERPLEXITY_API_KEY"

client = PerplexityChatGenerator(model="sonar-pro")
response = client.run(
    messages=[ChatMessage.from_user("What are Agentic Pipelines? Be brief.")]
)

print(response["replies"])
```

### Use Perplexity Embeddings

```python
import os

from haystack_integrations.components.embedders.perplexity import PerplexityTextEmbedder

os.environ["PERPLEXITY_API_KEY"] = "YOUR_PERPLEXITY_API_KEY"

embedder = PerplexityTextEmbedder()
response = embedder.run(text="What is Haystack by deepset?")

print(response["embedding"])
```

### Use Perplexity Web Search

```python
import os

from haystack.utils import Secret
from haystack_integrations.components.websearch.perplexity import PerplexityWebSearch

os.environ["PERPLEXITY_API_KEY"] = "YOUR_PERPLEXITY_API_KEY"

websearch = PerplexityWebSearch(
    api_key=Secret.from_env_var("PERPLEXITY_API_KEY"),
    top_k=5,
)
result = websearch.run(query="What is Haystack by deepset?")

documents = result["documents"]
links = result["links"]

print(documents)
print(links)
```

### License

`perplexity-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
