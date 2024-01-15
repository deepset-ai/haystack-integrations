---
layout: integration
name: Mistral
description: TBD
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/elasticsearch-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opensearch
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/elastic.png
version: Haystack 2.0
toc: true
---

This page demonstrates how to use OpenAIGenerator within Haystack make use of Mistral models.

[Mistral AI](https://mistral.ai/) currently provides two types of access to Large Language Models:

- An API providing pay-as-you-go access to our latest models,
- Open source models available under the Apache 2.0 License, available on Hugging Face or directly from the documentation.

For more information see [the Mistal docs](https://docs.mistral.ai/).

In order to follow along with this guide, you'll need a [Mistal API key](https://console.mistral.ai/).

### Installation

```bash
pip install haystack-ai
```

### Usage

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

api_key = "MISTRAL-API-KEY"
model = "mistral-medium"

client = OpenAIChatGenerator(
    api_key=api_key, model_name=model, api_base_url="https://api.mistral.ai/v1"
)

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```

```python
from haystack.components.embedders import OpenAITextEmbedder

api_key = "MISTRAL-API-KEY"
model = "mistral-embed"

embedder = OpenAITextEmbedder(api_key=api_key, model_name=model, api_base_url="https://api.mistral.ai/v1")

response = embedder.run(text="What is the best French cheese?")
print(response)
# {'embedding': [-0.0186004638671875, ...],
# 'meta': {'model': 'mistral-embed', 
#'usage': {'prompt_tokens': 9, 'total_tokens': 9, 'completion_tokens': 0}}}
```