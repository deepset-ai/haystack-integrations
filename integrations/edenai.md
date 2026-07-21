---
layout: integration
name: Eden AI
description: Use Eden AI to reach 500+ models from many providers through one OpenAI-compatible, EU-hosted API key.
authors:
    - name: Eden AI
      socials:
        github: edenai
        linkedin: https://www.linkedin.com/company/edenai
pypi: https://pypi.org/project/edenai-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/edenai
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/edenai.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Eden AI](https://www.edenai.co/) is a unified, OpenAI-compatible API that gives access to 500+ AI models from many providers (OpenAI, Anthropic, Mistral, Google, Cohere, and more) through a single API key, with built-in provider fallback and EU data residency. This makes it a convenient, sovereignty-friendly gateway for building LLM and RAG applications with Haystack.

Models are selected using Eden AI's `provider/model` naming convention, for example `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-5`, or `mistral/mistral-large-latest`. See the [Eden AI models catalog](https://www.edenai.co/models) for the full list.

To follow along with this guide, create an API key in your [Eden AI account](https://app.edenai.run/) and expose it as an environment variable, `EDENAI_API_KEY`.

## Installation

```bash
pip install edenai-haystack
```

## Usage

### Components

This integration introduces 3 components:

- The `EdenAIChatGenerator`: Generates chat responses using any Eden AI chat model through its OpenAI-compatible endpoint.
- The `EdenAITextEmbedder`: Creates embeddings for texts (such as queries) using Eden AI embedding models.
- The `EdenAIDocumentEmbedder`: Creates embeddings for Haystack Documents using Eden AI embedding models.

### Use Eden AI Chat Models

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.edenai import EdenAIChatGenerator

os.environ["EDENAI_API_KEY"] = "YOUR_EDENAI_API_KEY"

client = EdenAIChatGenerator(model="mistral/mistral-large-latest")

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```

Eden AI models also support streaming responses if you pass a callback into the `EdenAIChatGenerator`:

```python
import os
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.edenai import EdenAIChatGenerator

os.environ["EDENAI_API_KEY"] = "YOUR_EDENAI_API_KEY"

client = EdenAIChatGenerator(
    model="mistral/mistral-large-latest",
    streaming_callback=print_streaming_chunk,
)

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```

### Embed Documents and Queries

```python
import os
from haystack import Document
from haystack_integrations.components.embedders.edenai import (
    EdenAIDocumentEmbedder,
    EdenAITextEmbedder,
)

os.environ["EDENAI_API_KEY"] = "YOUR_EDENAI_API_KEY"

# Embed documents before writing them to a document store
document_embedder = EdenAIDocumentEmbedder(model="openai/text-embedding-3-small")
documents_with_embeddings = document_embedder.run([Document(content="I love pizza!")])["documents"]

# Embed a query at search time
text_embedder = EdenAITextEmbedder(model="openai/text-embedding-3-small")
query_embedding = text_embedder.run("What food do I love?")["embedding"]
```

This lets you build a fully sovereign RAG stack, retrieval and generation, on EU-hosted models through a single Eden AI key.

## License

`edenai-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/edenai/LICENSE.txt).
