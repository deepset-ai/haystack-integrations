---
layout: integration
name: EmpirioLabs
description: Use open and proprietary models served by EmpirioLabs
authors:
    - name: EmpirioLabs Team
      socials:
        github: EmpirioLabs-ai
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/empiriolabs.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

**EmpirioLabs** is a multi-model API platform that hosts open and proprietary models (Qwen, DeepSeek, GLM, Kimi, MiniMax, Gemma, and more) behind one OpenAI-compatible API with pay-as-you-go pricing.

To start using EmpirioLabs, create an API key in the [EmpirioLabs dashboard](https://platform.empiriolabs.ai/dashboard/api-keys). The full model catalog with per-model context windows and pricing is at [empiriolabs.ai/models](https://empiriolabs.ai/models).

## Usage

The EmpirioLabs API is OpenAI compatible, making it easy to use in Haystack via the OpenAI Generators and Embedders.

### Using `ChatGenerator`

Here's an example of chatting with a model served via EmpirioLabs using the `OpenAIChatGenerator`.
You need to set the environment variable `EMPIRIOLABS_API_KEY` and choose a model from the [catalog](https://empiriolabs.ai/models).

```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

os.environ["EMPIRIOLABS_API_KEY"] = "YOUR_EMPIRIOLABS_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("EMPIRIOLABS_API_KEY"),
    api_base_url="https://api.empiriolabs.ai/v1",
    model="qwen3-7-plus",
)
result = generator.run([ChatMessage.from_user("What are the main components of a RAG pipeline?")])
print(result["replies"][0].text)
```

### Using `Generator`

EmpirioLabs also works with the plain `OpenAIGenerator` for prompt-in, text-out generation:

```python
import os
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

os.environ["EMPIRIOLABS_API_KEY"] = "YOUR_EMPIRIOLABS_API_KEY"

generator = OpenAIGenerator(
    api_key=Secret.from_env_var("EMPIRIOLABS_API_KEY"),
    api_base_url="https://api.empiriolabs.ai/v1",
    model="qwen3-7-plus",
)
result = generator.run("Explain retrieval augmented generation in one paragraph.")
print(result["replies"][0])
```

### Using `TextEmbedder`

EmpirioLabs serves OpenAI-compatible embedding models too, so the OpenAI Embedders work the same way:

```python
import os
from haystack.components.embedders import OpenAITextEmbedder
from haystack.utils import Secret

os.environ["EMPIRIOLABS_API_KEY"] = "YOUR_EMPIRIOLABS_API_KEY"

embedder = OpenAITextEmbedder(
    api_key=Secret.from_env_var("EMPIRIOLABS_API_KEY"),
    api_base_url="https://api.empiriolabs.ai/v1",
    model="text-embedding-v4",
)
print(embedder.run("The quick brown fox jumped over the lazy dog")["embedding"][:5])
```
