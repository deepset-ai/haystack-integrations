---
layout: integration
name: Ollama
description: Use Ollama models with Haystack. Ollama allows you to get up and running with large language models, locally. 
authors:
    - name: Alistair Rogers
      socials:
        github: alistairlr112
        linkedin: https://www.linkedin.com/in/alistairlr/
    - name: Sachin Sachdeva
      socials:
        github: sachinsachdeva
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/ollama-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ollama
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/ollama.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Example](#example)

## Introduction

You can use [Ollama Models](https://ollama.ai/library) in your Haystack 2.0 pipelines with the OllamaGenerator.

[Ollama](https://ollama.ai/) is a project focused on running Large Language Models locally. Internally it uses the quantized GGUF format by default. This means it is possible to run LLMs on standard machines (even without GPUs), without having to handle complex installation procedures.

## Installation

```bash
pip install ollama-haystack
```

## Usage

You can leverage Ollama models through the OllamaGenerator Component

To use an Ollama model for text generation:

1. Follow instructions on the [Ollama Github Page](https://github.com/jmorganca/ollama) to pull and serve your model of choice 
2. Initialize an `OllamaGenerator` with the name of the model served in your Ollama instance and you can then use the `OllamaGenerator` instance in a question answering pipeline after the `PromptBuilder`.  


### Example
To run the example, you may choose to run a docker container serving an Ollama model of your choice. 
Here are some commands that work with this example:

```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama:latest
docker exec ollama ollama pull orca-mini
```

Below is the example of generative questions answering pipeline using RAG with `PromptBuilder` and  `OllamaGenerator`:

```python
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from ollama_haystack import OllamaGenerator

document_store = InMemoryDocumentStore()
document_store.write_documents(
    [
        Document(content="Super Mario was an important politician"),
        Document(content="Mario owns several castles and uses them to conduct important political business"),
        Document(
            content="Super Mario was a successful military leader who fought off several invasion attempts by "
            "his arch rival - Bowser"
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

pipe = Pipeline()

pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OllamaGenerator(model="orca-mini", url="http://localhost:11434/api/generate"))
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = "Who is Super Mario?"

response = pipe.run({"prompt_builder": {"query": query}, "retriever": {"query": query}})

print(response["llm"]["replies"])
```
You should receive an output like (output is not deterministic):
```
['Based on the information provided, Super Mario is a successful military leader who fought
off several invasion attempts by his arch rival - Bowser. He is also an important politician and owns several
castles where he conducts political business. ' 'Therefore, it can be inferred that Super Mario is a combination of
both a military leader and an important politician.']
```