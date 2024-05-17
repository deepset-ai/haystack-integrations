---
layout: integration
name: Groq
description: Use open Language Models served by Groq
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/groq.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

Groq is an AI company that has developed Language Processing Unit (LPU), a high-performance engine designed for fast inference of Large Language Models.

To start using Groq, sign up for an API key [here](https://console.groq.com/).
This will give you access to Groq API, which offers rapid inference of open Language Models like Mixtral and Llama 3.

## Usage

Groq API is OpenAI compatible, making it easy to use in Haystack via OpenAI Generators.


### Using `Generator`

Here's an example of using Mixtral served via Groq to perform question answering on a web page.
You need to set the environment variable `GROQ_API_KEY` and choose a [compatible model](https://console.groq.com/docs/models).

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
    api_key=Secret.from_env_var("GROQ_API_KEY"),
    api_base_url="https://api.groq.com/openai/v1",
    model="mixtral-8x7b-32768",
    generation_kwargs = {"max_tokens": 512}
)
pipeline = Pipeline()
pipeline.add_component("fetcher", fetcher)
pipeline.add_component("converter", converter)
pipeline.add_component("prompt", prompt_builder)
pipeline.add_component("llm", llm)

pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.prompt")

result = pipeline.run({"fetcher": {"urls": ["https://wow.groq.com/why-groq/"]},
              "prompt": {"query": "Why should I use Groq for serving LLMs?"}})

print(result["llm"]["replies"][0])
```

### Using `ChatGenerator`

See an example of engaging in a multi-turn conversation with Llama 3.
You need to set the environment variable `GROQ_API_KEY` and choose a [compatible model](https://console.groq.com/docs/models).

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("GROQ_API_KEY"),
    api_base_url="https://api.groq.com/openai/v1",
    model="llama3-8b-8192",
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
    print("🤖 "+assistant_resp.content)
    messages.append(assistant_resp)
```
