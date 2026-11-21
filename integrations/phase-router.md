---
layout: integration
name: Phase Router
description: Use Phase Router's OpenAI-compatible API (about 400 models, per-call pricing) with Haystack's OpenAIChatGenerator.
authors:
    - name: Phase
      socials:
        github: devcells
repo: https://github.com/devcells/phase-router-skills
type: Model Provider
report_issue: https://github.com/devcells/phase-router-skills/issues
logo: /logos/phase-router.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Phase Router](https://router.phase.xyz) is an OpenAI-compatible model router. One base URL (`https://router.phase.xyz/v1`) and one API key give access to about 400 models: open LLMs (DeepSeek, Qwen, Llama, gpt-oss, Kimi, GLM and others), embedding and rerank models. The model `auto` sends each request to the cheapest model that can handle it; any model can also be called by id. Every response reports the model that ran and its price in `usage.cost`, and every paid call has a signed receipt.

Because the API is OpenAI-compatible, Haystack's built-in `OpenAIChatGenerator` works with it by setting `api_base_url`. No extra package is needed.

To follow along, create an API key at [router.phase.xyz](https://router.phase.xyz) and set it as the `PHASE_API_KEY` environment variable. The model list with prices is at [router.phase.xyz/models](https://router.phase.xyz/models).

## Installation

```bash
pip install haystack-ai
```

## Usage

### Chat generation

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("PHASE_API_KEY"),
    api_base_url="https://router.phase.xyz/v1",
    model="deepseek-v3.2",
)

result = generator.run(messages=[ChatMessage.from_user("What is Haystack in one sentence?")])
print(result["replies"][0].text)
```

### Automatic model selection

```python
generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("PHASE_API_KEY"),
    api_base_url="https://router.phase.xyz/v1",
    model="auto",
)
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder

prompt_builder = ChatPromptBuilder(
    template=[ChatMessage.from_user("Summarize in one line: {{ text }}")],
    required_variables=["text"],
)

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component(
    "llm",
    OpenAIChatGenerator(
        api_key=Secret.from_env_var("PHASE_API_KEY"),
        api_base_url="https://router.phase.xyz/v1",
        model="gpt-oss-120b",
    ),
)
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {"text": "Haystack is an open-source framework for building LLM applications."}})
print(result["llm"]["replies"][0].text)
```

More examples and client configs: [phase-router-skills](https://github.com/devcells/phase-router-skills). API docs: [router.phase.xyz/docs](https://router.phase.xyz/docs).

## License

`haystack-ai` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. Phase Router is a hosted commercial service.
