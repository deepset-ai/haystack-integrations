---
layout: integration
name: Runcrate
description: Use 200+ open models served by Runcrate through its OpenAI-compatible API
authors:
    - name: Runcrate Team
      socials:
        github: aeonmindai
        twitter: runcrate
        linkedin: https://www.linkedin.com/company/runcrate/
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/runcrate.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

**Runcrate** is a GPU cloud for AI developers and agents. Alongside on-demand GPU instances, it serves 200+ open models (DeepSeek, Qwen, Llama, Kimi, GLM and more) behind one OpenAI-compatible API, billed per token from a prepaid balance.

To start using Runcrate, create an API key as described in the [Runcrate docs](https://www.runcrate.ai/docs/account/api-keys?utm_source=haystack-integrations&utm_medium=directory&utm_campaign=gpu_pricing). The full model catalog is available from `GET https://api.runcrate.ai/v1/models` and in the [models docs](https://www.runcrate.ai/docs/models/overview?utm_source=haystack-integrations&utm_medium=directory&utm_campaign=gpu_pricing).

## Usage

The Runcrate API is OpenAI compatible, so it works in Haystack through the OpenAI generators by pointing `api_base_url` at `https://api.runcrate.ai/v1`.

### Using `ChatGenerator`

Here's an example of chatting with a model served by Runcrate using the `OpenAIChatGenerator`.
You need to set the environment variable `RUNCRATE_API_KEY` and choose a model ID from the catalog.

```python
import os
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

os.environ["RUNCRATE_API_KEY"] = "YOUR_RUNCRATE_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("RUNCRATE_API_KEY"),
    api_base_url="https://api.runcrate.ai/v1",
    model="deepseek-ai/DeepSeek-V3.2",
)
result = generator.run([ChatMessage.from_user("What are the main components of a RAG pipeline?")])
print(result["replies"][0].text)
```

### Streaming

Pass a `streaming_callback` to receive tokens as they are generated:

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("RUNCRATE_API_KEY"),
    api_base_url="https://api.runcrate.ai/v1",
    model="moonshotai/Kimi-K2.6",
    streaming_callback=print_streaming_chunk,
)
generator.run([ChatMessage.from_user("Summarize what a vector database does in two sentences.")])
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

template = [ChatMessage.from_user("Answer in one paragraph: {{ question }}")]

pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder(template=template, required_variables=["question"]))
pipe.add_component(
    "llm",
    OpenAIChatGenerator(
        api_key=Secret.from_env_var("RUNCRATE_API_KEY"),
        api_base_url="https://api.runcrate.ai/v1",
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    ),
)
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {"question": "Why do LLMs need retrieval?"}})
print(result["llm"]["replies"][0].text)
```
