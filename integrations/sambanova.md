---
layout: integration
name: Sambanova
description: Use open Language Models served by Sambanova
authors:
    - name: Sambanova Team
      socials:
        twitter: SambaNovaAI
        linkedin: https://www.linkedin.com/company/sambanova
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/sambanova.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

SambaNova is an AI company that developes SN40L Reconfigurable Dataflow Unit (RDU), a processor that provides native dataflow processing and high-performance for fast inference of Large Language Models.

To start using SambaNova, sign up for an API key [here](https://cloud.sambanova.ai/).
This will give you access to SambaNova Cloud API, which offers rapid inference of open Language Models like Llama 3 and Qwen.

## Usage

SambaNova Cloud API is OpenAI compatible, making it easy to use in Haystack via OpenAI Generators.


### Using `Generator`

Here's an example of using Llama served via SambaNova to perform question answering using RAG with `PromptBuilder`.
You need to set the environment variable `SAMBANOVA_API_KEY` and choose a [compatible model](https://cloud.sambanova.ai/).

```python
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from haystack.components.generators import OpenAIGenerator
import os

os.environ["SAMBANOVA_API_KEY"] = "YOUR_SAMBANOVA_API_KEY"

document_store = InMemoryDocumentStore()
document_store.write_documents(
    [
        Document(content="The Function-Calling API enables dynamic, agentic workflows by allowing the model to suggest and select function calls based on user input."
                "This feature facilitates flexible agentic workflows that adapt to varied needs."),
        Document(content="Interact with multimodal models directly through the Inference API (OpenAI compatible) and Playground"
                 "for seamless text and image processing."),
        Document(
            content="New Python and Gradio code samples make it easier to build and deploy applications on SambaNova Cloud. These examples simplify"
            "integrating AI models, enabling faster prototyping and reducing setup time."
        ),
    ]
)

template = """
Given only the following information, answer the question.
Ignore your own knowledge.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}?
"""

llm = OpenAIGenerator(
    api_key=Secret.from_env_var("SAMBANOVA_API_KEY"),
    api_base_url="https://api.sambanova.ai/v1",
    model="Meta-Llama-3.3-70B-Instruct",
    generation_kwargs = {"max_tokens": 512}
)

pipe = Pipeline()

pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", llm)
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = "Functionalities of Sambanova API?"

response = pipe.run({"prompt_builder": {"query": query}, "retriever": {"query": query}})

print(response["llm"]["replies"])
```

### Using `ChatGenerator`

See an example of engaging in a multi-turn conversation with Llama 3.3.
You need to set the environment variable `SAMBANOVA_API_KEY` and choose a [compatible model](https://cloud.sambanova.ai/).

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
import os

os.environ["SAMBANOVA_API_KEY"] = "YOUR_SAMBANOVA_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("SAMBANOVA_API_KEY"),
    api_base_url="https://api.sambanova.ai/v1",
    model="Meta-Llama-3.3-70B-Instruct",
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
