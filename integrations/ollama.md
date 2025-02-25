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
        linkedin: https://www.linkedin.com/company/deepset-ai/
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
  - [Examples](#examples)
    - [Text Generation](#text-generation)
    - [Chat Generation](#chat-generation)
    - [Document and Text Embedders](#embedders)

## Introduction

You can use [Ollama Models](https://ollama.ai/library) in your Haystack pipelines with the OllamaGenerator.

[Ollama](https://ollama.ai/) is a project focused on running Large Language Models locally. Internally it uses the quantized GGUF format by default. This means it is possible to run LLMs on standard machines (even without GPUs), without having to handle complex installation procedures.

## Installation

```bash
pip install ollama-haystack
```

## Usage

This integration provides 2 components that allow you to leverage Ollama models:
- The [`OllamaGenerator`](https://docs.haystack.deepset.ai/docs/ollamagenerator)
- The [`OllamaChatGenerator`](https://docs.haystack.deepset.ai/docs/ollamachatgenerator)

To use an Ollama model:

1. Follow instructions on the [Ollama Github Page](https://github.com/jmorganca/ollama) to pull and serve your model of choice 
2. Initialize one of the Ollama generators with the name of the model served in your Ollama instance. 


### Examples
To run the example, you may choose to run a docker container serving an Ollama model of your choice. 
Here are some commands that work with this example:

```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama:latest
docker exec ollama ollama pull orca-mini
```

#### Text Generation

Below is the example of generative questions-answering pipeline using RAG with `PromptBuilder` and  `OllamaGenerator`:

```python
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from haystack_integrations.components.generators.ollama import OllamaGenerator

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
pipe.add_component("llm", OllamaGenerator(model="orca-mini", url="http://localhost:11434"))
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

#### Chat Generation

```python
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.generators.ollama import OllamaChatGenerator

messages = [
    ChatMessage.from_user("What's Natural Language Processing?"),
    ChatMessage.from_system(
        "Natural Language Processing (NLP) is a field of computer science and artificial "
        "intelligence concerned with the interaction between computers and human language"
    ),
    ChatMessage.from_user("How do I get started?"),
]
client = OllamaChatGenerator(model="orca-mini", timeout=45, url="http://localhost:11434")

response = client.run(messages, generation_kwargs={"temperature": 0.2})

print(response["replies"][0].text)

```
You should receive an output like (output is not deterministic):

```
Natural Language Processing (NLP) is a complex field with many different tools and techniques to learn. Here are some steps you can take to get started:

1. Understand the basics of natural language processing: Before diving into the specifics of NLP, it's important to have a basic understanding of what natural language is and how it works. You can start by reading up on linguistics and semantics.

2. Learn about the different components of NLP: There are several components of NLP that you need to understand, including syntax, semantics, morphology, and pragmatics. You can start by learning about these components individually.

3. Choose a tool or library to use: There are many different tools and libraries available for NLP, such as NLTK, spaCy, and Stanford CoreNLP. Choose one that you feel comfortable working with and that fits your needs.

4. Practice: The best way to learn NLP is by practicing. Start with simple tasks like sentiment analysis or tokenization and work your way up to more complex ones like machine translation

```
#### Embedders

- `OllamaDocumentEmbedder` helps compute embeddings for a list of Documents and updates each Document's embedding field with its embedding vector.
- `OllamaTextEmbedder` computes the embeddings of a particular string.

Both `OllamaTextEmbedder` and `OllamaDocumentEmbedder` use embedding models compatible with the Ollama Library.

To run the below example, use the below command to serve a `nomic-embed-text` model from Ollama:

```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama:latest
docker exec ollama ollama pull nomic-embed-text
```

Below is an example that uses both `OllamaDocumentEmbedder` and `OllamaTextEmbedder`.
```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [
    Document(content="I saw a black horse running"),
    Document(content="Germany has many big cities"),
    Document(content="My name is Wolfgang and I live in Berlin"),
]

document_embedder = OllamaDocumentEmbedder()
documents_with_embeddings = document_embedder.run(documents)["documents"]
document_store.write_documents(documents_with_embeddings)

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", OllamaTextEmbedder())
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

query = "Who lives in Berlin?"

result = query_pipeline.run({"text_embedder": {"text": query}})

print(result["retriever"]["documents"][0])
```
