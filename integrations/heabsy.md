---
layout: integration
name: Heabsy
description: Use open models served on dedicated GPUs in the EEA with zero data retention
authors:
    - name: Kostiantyn Fomichov
      socials:
        github: kafomichev
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[Heabsy](https://heabsy.com/platform) is an inference API for open models operated by FEYA, s.r.o.
(Bratislava, Slovakia). Models in its EEA tier run on dedicated GPUs in EEA data centres; prompts and
completions are processed in memory and are not stored or logged. The data processing agreement and
the sub-processor list are published at [heabsy.com/dpa](https://heabsy.com/dpa).

The [model catalog](https://heabsy.com/models) lists prices per model and marks which models run in
the EEA tier and which are routed through third-party providers. Performance figures measured on the
live system are published on the [platform page](https://heabsy.com/platform).

## Usage

The [Heabsy API](https://api.heabsy.com/docs) is OpenAI compatible, so it works in Haystack through
the OpenAI generators by pointing them at the Heabsy endpoint.

Set your API key as an environment variable:

```bash
export HEABSY_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("HEABSY_API_KEY"),
    api_base_url="https://api.heabsy.com/v1",
    model="qwen38",
)

messages = [ChatMessage.from_user("Summarise the following contract clause: ...")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
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
    template=[ChatMessage.from_user("Answer using only this context: {{context}}\n\nQuestion: {{question}}")]
))
pipe.add_component("llm", OpenAIChatGenerator(
    api_key=Secret.from_env_var("HEABSY_API_KEY"),
    api_base_url="https://api.heabsy.com/v1",
    model="qwen38",
))
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {"context": "...", "question": "..."}})
print(result["llm"]["replies"][0].text)
```
