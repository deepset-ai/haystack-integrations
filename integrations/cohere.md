---
layout: integration
name: Cohere
description: Use Cohere models with Haystack
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/cohere-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/cohere
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/cohere.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Embedding Models](#embedding-models)
  - [Generative Models (LLMs)](#generative-models-llms)
  - [Ranker Models](#ranker-models)

## Overview

You can use [Cohere Models](https://cohere.com/) in your Haystack pipelines with the [Generators](https://docs.haystack.deepset.ai/docs/generators) and [Embedders](https://docs.haystack.deepset.ai/docs/embedders).

## Installation

```bash
pip install cohere-haystack
```

## Usage

You can use Cohere models in various ways:

### Embedding Models

You can leverage `/embed` models from Cohere through two components: [CohereTextEmbedder](https://docs.haystack.deepset.ai/docs/coheretextembedder) and [CohereDocumentEmbedder](https://docs.haystack.deepset.ai/docs/coheredocumentembedder). These components support both **Embed v2** and **Embed v3** models.

To create semantic embeddings for documents, use `CohereDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `CohereTextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name. By default, the Cohere API key with be automatically read from either the `COHERE_API_KEY` environment variable or the `CO_API_KEY` environment variable.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `CohereDocumentEmbedder` and `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.cohere import CohereDocumentEmbedder

document_store = InMemoryDocumentStore()

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="People speak French in France"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", CohereDocumentEmbedder(model="embed-multilingual-v3.0", input_type="search_document"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

### Generative Models (LLMs)

To use `/generate` models from Cohere, initialize a [CohereGenerator](https://docs.haystack.deepset.ai/docs/coheregenerator) with the model name. By default, the Cohere API key with be automatically read from either the `COHERE_API_KEY` environment variable or the `CO_API_KEY` environment variable. You can then use this `CohereGenerator` in a question answering pipeline after the `PromptBuilder`.

Below is the example of generative questions answering pipeline using RAG with `PromptBuilder` and `CohereGenerator`:

```python
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.embedders.cohere import CohereTextEmbedder
from haystack_integrations.components.generators.cohere import CohereGenerator

template = """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.text }}
{% endfor %}

Question: What's the official language of {{ country }}?
"""
pipe = Pipeline()
pipe.add_component("embedder", CohereTextEmbedder(model="embed-multilingual-v3.0"))
pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", CohereGenerator(model="command-light"))
pipe.connect("embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

pipe.run({
    "embedder": {"text": "France"},
    "prompt_builder": {"country": "France"}
})
```

Similar to the above example, you can also use [`CohereChatGenerator`](https://docs.haystack.deepset.ai/docs/coherechatgenerator) to use Cohere `/chat` models and features (streaming, connectors) in your pipeline.

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.cohere.chat import CohereChatGenerator


pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder())
pipe.add_component("llm", CohereChatGenerator())
pipe.connect("prompt_builder", "llm")

country = "Germany"
system_message = ChatMessage.from_system("You are an assistant giving out valuable information to language learners.")
messages = [system_message, ChatMessage.from_user("What's the official language of {{ country }}?")]

res = pipe.run(data={"prompt_builder": {"template_variables": {"country": "Germany"}, "prompt_source": messages}})
print(res)
```

### Ranker Models

To use `/ranker` models from Cohere, initialize a [CohereRanker](https://docs.haystack.deepset.ai/docs/cohereranker) with the model name. By default, the Cohere API key with be automatically read from either the `COHERE_API_KEY` environment variable or the `CO_API_KEY` environment variable. You can then use this `CohereRanker` to rank documents based on semantic relevance to a specified query.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `InMemoryBM25Retriever` and `CohereRanker`:

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.rankers.cohere import CohereRanker

docs = [
    Document(content="Paris is in France"),
    Document(content="Berlin is in Germany"),
    Document(content="Lyon is in France"),
]
document_store = InMemoryDocumentStore()
document_store.write_documents(docs)

retriever = InMemoryBM25Retriever(document_store=document_store)
ranker = CohereRanker()

document_ranker_pipeline = Pipeline()
document_ranker_pipeline.add_component(instance=retriever, name="retriever")
document_ranker_pipeline.add_component(instance=ranker, name="ranker")

document_ranker_pipeline.connect("retriever.documents", "ranker.documents")

query = "Cities in France"
res = document_ranker_pipeline.run(data = {"retriever": {"query": query, "top_k": 3}, "ranker": {"query": query, "top_k": 2}})
```
