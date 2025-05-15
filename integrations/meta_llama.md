---
layout: integration
name: Meta Llama API
description: Use Llama Models with Haystack
authors:
    - name: Young Han
      socials:
        github: https://github.com/seyeong-han
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/meta-llama-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/meta_llama
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/meta_llama.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

This integration supports Meta Llama models provided through Meta’s own inferencing infrastructure. To get the `LLAMA_API_KEY`, check out [the Llama API website](https://llama.developer.meta.com?utm_source=partner-haystack&utm_medium=website).

You can use Llama models with `MetaLlamaChatGenerator`.

Currently, available models are:

| Model ID | Input context length | Output context length | Input Modalities | Output Modalities |
| --- | --- | --- | --- | --- |
| `Llama-4-Scout-17B-16E-Instruct-FP8` | 128k | 4028 | Text, Image | Text |
| `Llama-4-Maverick-17B-128E-Instruct-FP8` | 128k | 4028 | Text, Image | Text |
| `Llama-3.3-70B-Instruct` | 128k | 4028 | Text | Text |
| `Llama-3.3-8B-Instruct` | 128k | 4028 | Text | Text |

## Installation

```bash
pip install meta-llama-haystack
```

## Usage

Based on your use case, you can choose between `MetaLlamaChatGenerator`.
Before using, make sure to set the `LLAMA_API_KEY` environment variable.

### Using `MetaLlamaChatGenerator`

This example showcases how to build a complete RAG system that can answer questions based on the information in your document store using Meta's Llama models.

```python
# To run this example, you will need to set a `LLAMA_API_KEY` environment variable.

# Copyright (c) Meta Platforms, Inc. and affiliates
from haystack import Document, Pipeline
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.utils import print_streaming_chunk
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

from haystack_integrations.components.generators.meta_llama import MetaLlamaChatGenerator

# Write documents to InMemoryDocumentStore
document_store = InMemoryDocumentStore()
document_store.write_documents(
    [
        Document(content="My name is Jean and I live in Paris."),
        Document(content="My name is Mark and I live in Berlin."),
        Document(content="My name is Giorgio and I live in Rome."),
    ]
)

# Build a RAG pipeline
prompt_template = [
    ChatMessage.from_user(
        "Given these documents, answer the question.\n"
        "Documents:\n{% for doc in documents %}{{ doc.content }}{% endfor %}\n"
        "Question: {{question}}\n"
        "Answer:"
    )
]

# Define required variables explicitly
prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"question", "documents"})

retriever = InMemoryBM25Retriever(document_store=document_store)
llm = MetaLlamaChatGenerator(
    api_key=Secret.from_env_var("LLAMA_API_KEY"),
    streaming_callback=print_streaming_chunk,
)

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm.messages")

# Ask a question
question = "Who lives in Paris?"
rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)
```

### Using `MetaLlamaChatGenerator`

Below is an example of using `MetaLlamaChatGenerator`:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.meta_llama import (
    MetaLlamaChatGenerator,
)

client = MetaLlamaChatGenerator()
response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)

>>{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='The best French cheese is a matter of personal preference, but some of the most popular and highly-regarded French cheeses include:\n\n1. **Camembert**: A soft, creamy, and earthy cheese from Normandy, often served with bread and fruit.\n2. **Brie**: A soft, white, and mild cheese from the Île-de-France region, often baked or served with crackers.\n3. **Roquefort**: A pungent, blue-veined cheese from the Roquefort-sur-Soulzon region, often served as a dessert or used in salad dressings.\n4. **Époisses**: A strong, golden, and washed-rind cheese from Burgundy, often served with fruit and bread.\n5. **Pont l\'Évêque**: A semi-soft, golden, and washed-rind cheese from Normandy, often served with crackers or bread.\n\nOf course, there are many other excellent French cheeses, and the "best" one will depend on your personal taste preferences. Some other notable mentions include:\n\n* **Comté**: A firm, nutty, and golden cheese from Franche-Comté.\n* **Gruyère**: A nutty, creamy, and firm cheese from the Savoie region.\n* **Bucheron**: A semi-soft, white, and mild cheese from the Loire Valley.\n* **Bleu d\'Auvergne**: A creamy, blue-veined cheese from the Auvergne region.\n\nFrance is home to over 400 different types of cheese, each with its own unique characteristics and flavor profiles. So, feel free to explore and find your own favorite French cheese!')], _name=None, _meta={'model': 'Llama-4-Scout-17B-16E-Instruct-FP8', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 335, 'prompt_tokens': 17, 'total_tokens': 352, 'completion_tokens_details': None, 'prompt_tokens_details': None}})]}
```
