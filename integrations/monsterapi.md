---
layout: integration
name: MonsterAPI
description: Use open Language Models served by MonsterAPI
authors:
    - name: monsterapi
      socials:
        github: qblocks
        twitter: monsterapi
        linkedin: https://www.linkedin.com/company/monster-api/
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/monsterapi.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

MonsterAPI provides access to powerful language models designed for various text generation tasks. With the MonsterAPI integration, you can leverage these models within the Haystack framework for enhanced natural language processing capabilities.

To start using MonsterAPI, sign up for an API key [here](https://monsterapi.ai/). This key provides access to the MonsterAPI, which supports rapid inference and customization through various parameters.

## Usage

MonsterAPI's API is OpenAI compatible, making it easy to use within Haystack via OpenAI Generators.

### Using `Generator`

Here's an example of using a model served via MonsterAPI to perform question answering on a web page. You need to set the environment variable `MONSTER_API_KEY` and choose a [compatible model](https://developer.monsterapi.ai/).

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

fetcher = LinkContentFetcher()
converter = HTMLToDocument()
prompt_template = """
According to the contents of this website:
{% for document in documents %}
  {{document.content}}
{% endfor %}
Answer the given question: {{query}}
Answer:
"""
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(
    api_key=Secret.from_env_var("MONSTER_API_KEY"),
    api_base_url="https://llm.monsterapi.ai/v1/",
    model="microsoft/Phi-3-mini-4k-instruct",
    generation_kwargs = {"max_tokens": 256}
)
pipeline = Pipeline()
pipeline.add_component("fetcher", fetcher)
pipeline.add_component("converter", converter)
pipeline.add_component("prompt", prompt_builder)
pipeline.add_component("llm", llm)

pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.prompt")

result = pipeline.run({"fetcher": {"urls": ["https://developer.monsterapi.ai/docs/"]},
              "prompt": {"query": "What are the features of MonsterAPI?"}})

print(result["llm"]["replies"][0])
```

### Using `ChatGenerator`

Here's an example of engaging in a multi-turn conversation with a MonsterAPI model. You need to set the environment variable `MONSTER_API_KEY` and choose a [compatible model](https://developer.monsterapi.ai/).

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("MONSTER_API_KEY"),
    api_base_url="https://llm.monsterapi.ai/v1/",
    model="microsoft/Phi-3-mini-4k-instruct",
    generation_kwargs = {"max_tokens": 256}
)

messages = []

while True:
    msg = input("Enter your message or Q to exit\n ")
    if msg=="Q":
        break
    messages.append(ChatMessage.from_user(msg))
    response = generator.run(messages=messages)
    assistant_resp = response['replies'][0]
    print(assistant_resp.content)
    messages.append(assistant_resp)
```
