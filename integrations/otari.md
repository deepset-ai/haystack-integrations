---
layout: integration
name: Otari
description: Send LLM, embedding, and rerank calls through Otari, an open-source LLM gateway with API keys, budgets, and cost tracking.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/otari-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/otari
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/otari.svg
version: Haystack 3.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Otari](https://github.com/mozilla-ai/otari) is an open-source, OpenAI-compatible LLM gateway by mozilla.ai. It routes requests to over 40 model providers through one endpoint and adds API keys, budgets that are checked before each request, usage and cost tracking, and routing policies such as failover. The provider credentials stay in the gateway, so your Haystack application only needs an Otari API key.

You can use [otari.ai](https://otari.ai), the gateway that mozilla.ai runs, or run Otari yourself. By default, the components call otari.ai at `https://api.otari.ai/api/v1`. For an account in otari.ai's EU region, whose API keys start with `otk_v1_eu_`, set `api_base_url` to `https://eu.api.otari.ai/api/v1`. For a gateway you run yourself, set `api_base_url` to its address followed by `/api/v1`, for example `http://localhost:8000/api/v1`.

Models are named with selectors that the gateway accepts, such as `openai:gpt-5-mini` or `anthropic:claude-sonnet-4-6`. The gateway needs a credential for each provider you use. On otari.ai, add a provider key on your organization's Providers page. On a gateway you run yourself, add the provider on the Providers page of its dashboard, or declare it in the gateway's `config.yml` as described in [Configuring a provider](https://github.com/mozilla-ai/otari/blob/main/docs/models.md#configuring-a-provider).

To follow along with this guide, create an Otari API key and expose it as an environment variable, `OTARI_API_KEY`.

## Installation

```bash
pip install otari-haystack
```

## Usage

### Components

This integration introduces 4 components:

- The [`OtariChatGenerator`](https://docs.haystack.deepset.ai/docs/otarichatgenerator): Generates chat responses with models from any provider the gateway routes to. It supports streaming and tool calling.
- The [`OtariTextEmbedder`](https://docs.haystack.deepset.ai/docs/otaritextembedder): Creates embeddings for texts, such as queries.
- The [`OtariDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/otaridocumentembedder): Creates embeddings for Haystack Documents.
- The [`OtariRanker`](https://docs.haystack.deepset.ai/docs/otariranker): Reranks Documents by their relevance to a query.

### Use chat models

You can use `OtariChatGenerator` as a standalone component, within a [pipeline](https://docs.haystack.deepset.ai/docs/pipelines) or with the [Agent component](https://docs.haystack.deepset.ai/docs/agent).

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.otari import OtariChatGenerator

client = OtariChatGenerator(model="openai:gpt-5-mini")
response = client.run([ChatMessage.from_user("What are Agentic Pipelines? Be brief.")])

print(response["replies"][0].text)
# >> Agentic pipelines are workflows in which an LLM-driven agent decides which steps
# >> to take, such as calling tools or retrieving data, to complete a task.
# The cost of the request in US dollars, when the gateway prices it
print(response["replies"][0].meta["usage"]["cost_usd"])
# >> 0.000279
```

To stream the response, pass a callback:

```python
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.otari import OtariChatGenerator

client = OtariChatGenerator(streaming_callback=print_streaming_chunk)
client.run([ChatMessage.from_user("Summarize RAG in two lines.")])
```

### Embed documents and queries

```python
from haystack import Document
from haystack_integrations.components.embedders.otari import (
    OtariDocumentEmbedder,
    OtariTextEmbedder,
)

# Embed documents before writing them to a document store
document_embedder = OtariDocumentEmbedder(model="openai:text-embedding-3-small")
documents_with_embeddings = document_embedder.run([Document(content="I love pizza!")])["documents"]

# Embed a query at search time
text_embedder = OtariTextEmbedder(model="openai:text-embedding-3-small")
query_embedding = text_embedder.run("What food do I love?")["embedding"]
```

### Rerank documents

```python
from haystack import Document
from haystack_integrations.components.rankers.otari import OtariRanker

ranker = OtariRanker(model="cohere:rerank-v3.5")

docs = [
    Document(content="The capital of Brazil is Brasilia."),
    Document(content="The capital of France is Paris."),
]
result = ranker.run(query="What is the capital of France?", documents=docs)
print(result["documents"][0].content)
# >> The capital of France is Paris.
```

## License

`otari-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/otari/LICENSE.txt).
