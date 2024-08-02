---
layout: integration
name: Mistral
description: Use the Mistral API for embedding and text generation models.
authors:
    - name: deepset 
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/mistral-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mistral
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/mistral.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
[Mistral AI](https://mistral.ai/) currently provides two types of access to Large Language Models:

- An API providing pay-as-you-go access to the latest Mistral models like `mistral-embed` and `mistral-small`.
- Open-source models available under the Apache 2.0 License, available on [Hugging Face](https://huggingface.co/mistralai) which you can use with the `HuggingFaceTGIGenerator`.

For more information on models available via the Mistral API, see [the Mistal docs](https://docs.mistral.ai/).

In order to follow along with this guide, you'll need a [Mistal API key](https://console.mistral.ai/). Add it as an environment variable, `MISTRAL_API_KEY`.

## Installation

```bash
pip install mistral-haystack
```

## Usage
### Components
This instegration introduces 3 components:
- The [`MistralDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/mistraldocumentembedder): Creates embeddings for Haystack Documents using Mistral embedding models (currently only `mistral-embed`).
- The [`MistralTextEmbedder`](https://docs.haystack.deepset.ai/docs/mistraltextembedder): Creates embeddings for texts (such as queries) using Mistral embedding models (currently only `mistral-embed`)
- The [`MistralChatGenerator`](https://docs.haystack.deepset.ai/docs/mistralchatgenerator): Uses Mistral chat completion models such as `mistral-tiny` (default).
  
### Use Mistral Generative Models
```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.mistral import MistralChatGenerator

os.environ["MISTRAL_API_KEY"] = "YOUR_MISTRAL_API_KEY"
model = "mistral-medium"

client = MistralChatGenerator(model=model)


response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```
```bash
{'replies': [ChatMessage(content='The "best" French cheese is subjective and depends on personal taste...', role=<ChatRole.ASSISTANT: 'assistant'>, name=None, meta={'model': 'mistral-medium', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 231, 'prompt_tokens': 16, 'total_tokens': 247}})]}
```
Mistral LLMs also support streaming responses if you pass a callback into the `MistralChatGenerator` like so:

```python
import os

from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.mistral import MistralChatGenerator

os.environ["MISTRAL_API_KEY"] = "YOUR_MISTRAL_API_KEY"
model = "mistral-medium"

client = MistralChatGenerator(
    model=model,
    streaming_callback=print_streaming_chunk
)

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```

### Use a Mistral Embedding Models

Use the `MistralDocumentEmbedder` in an indexing pipeline:

```python
import os

from haystack_integrations.components.embedders.mistral.document_embedder import MistralDocumentEmbedder

os.environ["MISTRAL_API_KEY"] = "YOUR_MISTRAL_API_KEY"

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

embedder = MistralDocumentEmbedder()
writer = DocumentWriter(document_store=document_store)

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(name="embedder", instance=embedder)
indexing_pipeline.add_component(name="writer", instance=writer)

indexing_pipeline.run(data={"embedder": {"documents": documents}})
```

Use the `MistralTextEmbedder` in a RAG pipeline:

```python
import os

from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.mistral.document_embedder import MistralDocumentEmbedder
from haystack_integrations.components.embedders.mistral.text_embedder import MistralTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import ChatPromptBuilder

os.environ["MISTRAL_API_KEY"] = "YOUR_MISTRAL_API_KEY"

document_store = InMemoryDocumentStore()

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

document_embedder = MistralDocumentEmbedder()
documents_with_embeddings = document_embedder.run(documents)['documents']
document_store.write_documents(documents)

text_embedder = MistralTextEmbedder()
retriever = InMemoryEmbeddingRetriever(document_store=document_store)
prompt_builder = ChatPromptBuilder()
llm = MistralChatGenerator(streaming_callback=print_streaming_chunk)

messages = [ChatMessage.from_user("Here are some the documents: {{documents}} \\n Answer: {{query}}")]

rag_pipeline = Pipeline()
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)


rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "Who lives in Berlin?"

result = rag_pipeline.run(
    {
        "text_embedder": {"text": question},
        "prompt_builder": {"template_variables": {"query": question}, "template": messages},
        "llm": {"generation_kwargs": {"max_tokens": 165}},
    }
)
```

### License

`mistral-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
