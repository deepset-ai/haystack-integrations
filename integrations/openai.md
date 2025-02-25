---
layout: integration
name: OpenAI
description: Use OpenAI Models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/openai.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

You can use [OpenAI Models](https://openai.com/) in your Haystack pipelines with the [Generators](https://docs.haystack.deepset.ai/docs/generators), [Embedders](https://docs.haystack.deepset.ai/docs/embedders), [LocalWhisperTranscriber](https://docs.haystack.deepset.ai/docs/localwhispertranscriber) and [RemoteWhisperTranscriber](https://docs.haystack.deepset.ai/docs/remotewhispertranscriber).

## Installation

```bash
pip install haystack-ai
```

## Usage

You can use OpenAI models in various ways:

### Embedding Models

You can leverage embedding models from OpenAI through two components: [OpenAITextEmbedder](https://docs.haystack.deepset.ai/docs/openaitextembedder) and [OpenAIDocumentEmbedder](https://docs.haystack.deepset.ai/docs/openaidocumentembedder).

To create semantic embeddings for documents, use `OpenAIDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `OpenAITextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and OpenAI API key.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `OpenAIDocumentEmbedder` and  `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.writers import DocumentWriter

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", OpenAIDocumentEmbedder(api_key=Secret.from_token("YOUR_OPENAI_API_KEY"), model="text-embedding-ada-002"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

### Generative Models (LLMs)

You can leverage OpenAI models through two components: [OpenAIGenerator](https://docs.haystack.deepset.ai/docs/openaigenerator) and [OpenAIChatGenerator](https://docs.haystack.deepset.ai/docs/openaichatgenerator).

To use OpenAI's GPT models for text generation, initialize a `OpenAIGenerator` with the model name and OpenAI API key. You can then use the `OpenAIGenerator` instance in a question answering pipeline after the `PromptBuilder`.  

Below is the example of generative questions answering pipeline using RAG with `PromptBuilder` and  `OpenAIGenerator`:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack import Document

docstore = InMemoryDocumentStore()
docstore.write_documents([Document(content="Rome is the capital of Italy"), Document(content="Paris is the capital of France")])

query = "What is the capital of France?"

template = """
Given the following information, answer the question.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}?
"""
pipe = Pipeline()

pipe.add_component("retriever", InMemoryBM25Retriever(document_store=docstore))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OpenAIGenerator(api_key=Secret.from_token("YOUR_OPENAI_API_KEY")))
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

res=pipe.run({
    "prompt_builder": {
        "query": query
    },
    "retriever": {
        "query": query
    }
})

print(res)   
```

### Transcriber Models

To use Whisper models from OpenAI, initialize a `LocalWhisperTranscriber` or `RemoteWhisperTranscriber` based on hosting options. To use Whisper locally, install it following the instructions on the Whisper [GitHub repo](https://github.com/openai/whisper). To use the OpenAI API, provide an API key. You can then use the suitable component to transcribe audio files.

Below is the example of indexing pipeline with `LocalWhisperTranscriber`. If you'd like to run the Whisper model locally, you need to install two additional packages:

```bash
pip install transformers[torch]
pip install -U openai-whisper
```

```python
from pathlib import Path
from haystack import Pipeline
from haystack.components.audio import LocalWhisperTranscriber
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore()
pipeline = Pipeline()
pipeline.add_component(instance=LocalWhisperTranscriber(model="small"), name="transcriber")
pipeline.add_component(instance=DocumentCleaner(), name="cleaner")
pipeline.add_component(instance=DocumentSplitter(), name="splitter")
pipeline.add_component(instance=DocumentWriter(document_store=document_store), name="writer")

pipeline.connect("transcriber.documents", "cleaner.documents")
pipeline.connect("cleaner.documents", "splitter.documents")
pipeline.connect("splitter.documents", "writer.documents")

pipeline.run({"transcriber": {"audio_files": list(Path("path/to/audio/folder").iterdir())}})
```
