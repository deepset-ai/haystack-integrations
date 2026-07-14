---
layout: integration
name: iFlytek Spark
description: Use iFlytek Spark chat models in Haystack through an OpenAI-compatible chat generator.
authors:
    - name: FenjuFu
      socials:
        github: FenjuFu
pypi: https://pypi.org/project/iflytek-haystack/
repo: https://github.com/FenjuFu/iflytek-haystack
type: Model Provider
report_issue: https://github.com/FenjuFu/iflytek-haystack/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/iflytek-haystack.svg)](https://pypi.org/project/iflytek-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/iflytek-haystack.svg)](https://pypi.org/project/iflytek-haystack/)

---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [IFlytekChatGenerator](#iflytekchatgenerator)
- [License](#license)

## Overview

[iFlytek Spark](https://www.xfyun.cn/) provides chat-completion models through an OpenAI-compatible API. This integration brings iFlytek Spark to Haystack with `IFlytekChatGenerator`, which builds on Haystack's `OpenAIChatGenerator`.

Use this integration when you want to plug Spark models such as `generalv3.5`, `4.0Ultra`, or `lite` into an existing Haystack pipeline with minimal changes.

## Installation

```bash
pip install iflytek-haystack
```

## Usage

### IFlytekChatGenerator

Get an API password from the [iFlytek open platform console](https://console.xfyun.cn/) and set it as the `IFLYTEK_API_KEY` environment variable.

#### Basic Example

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.iflytek import IFlytekChatGenerator

client = IFlytekChatGenerator(model="4.0Ultra")
response = client.run([ChatMessage.from_user("Use one sentence to introduce yourself.")])

print(response["replies"][0].text)
```

You can switch models by changing only the `model` argument, for example `generalv3.5`, `4.0Ultra`, or `lite`.

#### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.iflytek import IFlytekChatGenerator

messages = [
    ChatMessage.from_system("You are a concise assistant."),
    ChatMessage.from_user("Answer briefly: {{question}}"),
]

pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder(template=messages))
pipe.add_component("llm", IFlytekChatGenerator(model="generalv3.5"))
pipe.connect("prompt_builder.prompt", "llm.messages")

result = pipe.run({"prompt_builder": {"template_variables": {"question": "What is Haystack?"}}})
print(result["llm"]["replies"][0].text)
```

### License

`iflytek-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
