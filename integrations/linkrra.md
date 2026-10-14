---
layout: integration
name: Linkrra
description: Use open-weight models served by Linkrra through an OpenAI-compatible API
authors:
    - name: Linkrra
      socials:
        github: jimmyplup
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/linkrra.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Linkrra](https://linkrra.com/) is an OpenAI-compatible inference API for open-weight models.

To start using Linkrra, sign in on the [account page](https://synap.linkrra.com/account) and create an API key. The API is described in the [Linkrra documentation](https://synap.linkrra.com/docs), and the model IDs currently served are listed at [`/v1/models?format=openrouter`](https://pool.linkrra.com/v1/models?format=openrouter).

## Usage

The Linkrra API is OpenAI compatible, so no extra package is needed: use the OpenAI chat generator that ships with Haystack and point it at the Linkrra base URL.

```bash
pip install haystack-ai
```

Set your API key as an environment variable:

```bash
export LINKRRA_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

Here's an example of chatting with a model served by Linkrra using the `OpenAIChatGenerator`.

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("LINKRRA_API_KEY"),
    api_base_url="https://pool.linkrra.com/v1",
    model="qwen3-coder-30b",
)

result = generator.run([ChatMessage.from_user("Write a one-line Python function that reverses a string.")])
print(result["replies"][0].text)
```

### Streaming

Pass a `streaming_callback` to print the answer as it is generated:

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("LINKRRA_API_KEY"),
    api_base_url="https://pool.linkrra.com/v1",
    model="qwen3-coder-30b",
    streaming_callback=print_streaming_chunk,
)

generator.run([ChatMessage.from_user("Count from 1 to 5, separated by spaces.")])
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder(
    template=[ChatMessage.from_user("Answer in one sentence using only this context: {{context}}\n\nQuestion: {{question}}")],
    required_variables=["context", "question"],
))
pipe.add_component("llm", OpenAIChatGenerator(
    api_key=Secret.from_env_var("LINKRRA_API_KEY"),
    api_base_url="https://pool.linkrra.com/v1",
    model="qwen3-coder-30b",
))
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {
    "context": "Haystack is an open-source framework for building LLM applications.",
    "question": "What is Haystack?",
}})
print(result["llm"]["replies"][0].text)
```
