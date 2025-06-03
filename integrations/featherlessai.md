---
layout: integration
name: Featherless AI
description: Featherless.ai provides access to thousands of open source language models
authors:
    - name: Featherless AI
      socials:
        github: featherlessai
        twitter: FeatherlessAI
        linkedin: https://www.linkedin.com/company//feather-serverless-ai/
        
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/featherless.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

**Featherless AI** is a serverless AI inference platform. Our goal is to make all AI models available for serverless inference and we’ve started with large language models (e.g. Qwen, Llama, Mistral, DeepSeek, RWKV). We provide inference via API to a continually expanding library of open-weight models, including the most popular models for role-playing, creative writing, coding assistance, and more. 

To start using Featherless, sign up for an API key [here](https://featherless.ai/).

## Usage

Featherless AI is OpenAI compatible, making it easy to use in Haystack via OpenAI Generators.


### Using `Generator`

Here's an example of using Llama served via Featherless AI to perform question perform question answering on a docs page.
You need to set the environment variable `FEATHERLESS_API_KEY` and choose a model from our [catalog](https://featherless.ai/models).

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
import os 
os.environ["FEATHERLESS_API_KEY"] = "YOUR FEATHERLESS API KEY"

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
    api_key=Secret.from_env_var("FEATHERLESS_API_KEY"),
    api_base_url="https://api.featherless.ai/v1",
    model="deepseek-ai/DeepSeek-V3-0324"
)
pipeline = Pipeline()
pipeline.add_component("fetcher", fetcher)
pipeline.add_component("converter", converter)
pipeline.add_component("prompt", prompt_builder)
pipeline.add_component("llm", llm)

pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.prompt")

result = pipeline.run({"fetcher": {"urls": ["https://featherless.ai/docs/getting-started"]},
              "prompt": {"query": "What is the mission of Featherless AI?"}})

print(result["llm"]["replies"][0])
```

### Using `ChatGenerator`

See an example of engaging in a multi-turn conversation with mistralai/Mistral-Small-24B-Instruct-2501
You need to set the environment variable `FEATHERLESS_API_KEY` and choose a model from our [catalog](https://featherless.ai/models).

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
import os

os.environ["FEATHERLESS_API_KEY"] = "YOUR_FEATHERLESS_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FEATHERLESS_API_KEY"),
    api_base_url="https://api.featherless.ai/v1",
    model="mistralai/Mistral-Small-24B-Instruct-2501",
    generation_kwargs = {"max_tokens": 512}
)


messages = []

while True:
    msg = input("Enter your message or Q to exit\n🧑 ")
    if msg=="Q":
        break
    messages.append(ChatMessage.from_user(msg))
    response = generator.run(messages=messages)
    assistant_resp = response['replies'][0]
    print("🤖 "+assistant_resp.text)
    messages.append(assistant_resp)
```
