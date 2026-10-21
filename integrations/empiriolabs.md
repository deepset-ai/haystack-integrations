---
layout: integration
name: EmpirioLabs AI
description: Use open and proprietary models served by EmpirioLabs AI
authors:
    - name: EmpirioLabs AI Team
      socials:
        github: EmpirioLabs-AI
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/empiriolabs.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

**[EmpirioLabs AI](https://empiriolabs.ai)** is a specialized AI inference and integration provider. It hosts open-source models on GPU infrastructure it manages, runs optimized endpoints for proprietary models, helps teams ship their own models, and offers on-demand GPU Cloud instances and hosted AI agents. Its model catalog spans text, image, audio, video, transcription, embedding, reranking, research, and 3D models.

To start using EmpirioLabs AI, create an API key in the [EmpirioLabs AI dashboard](https://platform.empiriolabs.ai/dashboard/api-keys). The full model catalog with per-model context windows and pricing is at [empiriolabs.ai/models](https://empiriolabs.ai/models), and the [EmpirioLabs AI documentation](https://docs.empiriolabs.ai/integrations#haystack) covers the Haystack setup.

## Usage

The EmpirioLabs AI API is OpenAI compatible, making it easy to use in Haystack via the OpenAI Generators and Embedders.

### Using `ChatGenerator`

Here's an example of chatting with a model served via EmpirioLabs AI using the `OpenAIChatGenerator`.
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

### Using `TextEmbedder`

EmpirioLabs AI serves OpenAI-compatible embedding models too, so the OpenAI Embedders work the same way:

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
