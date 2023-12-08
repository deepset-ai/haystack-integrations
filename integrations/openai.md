---
layout: integration
name: OpenAI
description: Use OpenAI Models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/openai.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)
- [Haystack 1.x](#haystack-1x)
  - [Installation (1.x)](#installation-1x)
  - [Usage (1.x)](#usage-1x)

## Haystack 2.0

You can use [OpenAI Models](https://openai.com/) in your Haystack 2.0 pipelines with the [Generators](https://docs.haystack.deepset.ai/v2.0/docs/generators), [Embedders](https://docs.haystack.deepset.ai/v2.0/docs/embedders), [LocalWhisperTranscriber](https://docs.haystack.deepset.ai/v2.0/docs/localwhispertranscriber) and [RemoteWhisperTranscriber](https://docs.haystack.deepset.ai/v2.0/docs/remotewhispertranscriber).

### Installation

```bash
pip install haystack-ai
```

### Usage

You can use OpenAI models in various ways:

#### Embedding Models

You can leverage embedding models from OpenAI through two components: [OpenAITextEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/openaitextembedder) and [OpenAIDocumentEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/openaidocumentembedder).

To create semantic embeddings for documents, use `OpenAIDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `OpenAITextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and OpenAI API key.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `OpenAIDocumentEmbedder` and  `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.writers import DocumentWriter

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", OpenAIDocumentEmbedder(api_key="OPENAI_API_KEY", model_name="text-embedding-ada-002"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

#### Generative Models (LLMs)

You can leverage OpenAI models through two components: [GPTGenerator](https://docs.haystack.deepset.ai/v2.0/docs/gptgenerator) and [GPTChatGenerator](https://docs.haystack.deepset.ai/v2.0/docs/gptchatgenerator).

To use OpenAI's GPT models for text generation, initialize a `GPTGenerator` with the model name and OpenAI API key. You can then use the `GPTGenerator` instance in a question answering pipeline after the `PromptBuilder`.  

Below is the example of generative questions answering pipeline using RAG with `PromptBuilder` and  `GPTGenerator`:

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import GPTGenerator

template = """
Given the following information, answer the question.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: What's the official language of {{ country }}?
"""
pipe = Pipeline()

pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", GPTGenerator(model="gpt-4", api_key="OPENAI_API_KEY"))
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

pipe.run({
    "prompt_builder": {
        "country": "France"
    }
})   
```

#### Transcriber Models

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
from haystack.document_stores import InMemoryDocumentStore

document_store = InMemoryDocumentStore()
pipeline = Pipeline()
pipeline.add_component(instance=LocalWhisperTranscriber(model_name_or_path="small"), name="transcriber")
pipeline.add_component(instance=DocumentCleaner(), name="cleaner")
pipeline.add_component(instance=DocumentSplitter(), name="splitter")
pipeline.add_component(instance=DocumentWriter(document_store=document_store), name="writer")

pipeline.connect("transcriber.documents", "cleaner.documents")
pipeline.connect("cleaner.documents", "splitter.documents")
pipeline.connect("splitter.documents", "writer.documents")

pipeline.run({"transcriber": {"audio_files": list(Path("path/to/audio/folder").iterdir())}})
```


### Installation (1.x)

```bash
pip install farm-haystack
```

### Usage (1.x)

You can use OpenAI models in various ways:

#### Embedding Models

To use embedding models from OpenAI, initialize an `EmbeddingRetriever` with the model name and OpenAI API key. You can then use this `EmbeddingRetriever` in an indexing pipeline to create OpenAI embeddings for documents and index them to a document store. 

Below is the example indexing pipeline with `PreProcessor`, `InMemoryDocumentStore` and  `EmbeddingRetriever`:

```python
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import Pipeline
from haystack.schema import Document

document_store = InMemoryDocumentStore(embedding_dim=1024)
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(
    embedding_model="ada", document_store=document_store, api_key=OPENAI_API_KEY
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=preprocessor, name="Preprocessor", inputs=["File"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["Preprocessor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=["Retriever"])
indexing_pipeline.run(documents=[Document("This is my document")])
```

#### Generative Models (LLMs) 

To use GPT models from OpenAI, initialize a `PromptNode` with the model name, OpenAI API key and the prompt template. You can then use this `PromptNode` in a question answering pipeline to generate answers based on the given context.  

Below is the example of generative questions answering pipeline using RAG with `EmbeddingRetriever` and  `PromptNode`:

```python
from haystack.nodes import PromptNode, EmbeddingRetriever
from haystack.pipelines import Pipeline

retriever = EmbeddingRetriever(
    embedding_model="babbage", document_store=document_store, api_key=OPENAI_API_KEY
)
prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo", 
    api_key=OPENAI_API_KEY, 
    default_prompt_template="deepset/question-answering"
)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
query_pipeline.run("YOUR_QUERY")
```

#### Transcriber Models

To use Whisper models from OpenAI, initialize a `WhisperTranscriber`. To use Whisper locally, install it following the instructions on the Whisper [GitHub repo](https://github.com/openai/whisper). To use the API implementation, provide an API key. You can then use this `WhisperTranscriber` to transcribe audio files.

Below is the example of summarization pipeline with `WhisperTranscriber` and  `PromptNode`:

```python
from haystack.nodes import WhisperTranscriber, PromptNode
from haystack.pipelines import Pipeline

whisper = WhisperTranscriber(api_key=api_key)
prompt_node = PromptNode(
        model_name_or_path="gpt-4", 
        api_key=api_key,
        default_prompt_template="deepset/summarization"
)

pipeline = Pipeline()
pipeline.add_node(component=whisper, name="whisper", inputs=["File"])
pipeline.add_node(component=prompt_node, name="prompt", inputs=["whisper"])

output = pipeline.run(file_paths=["path/to/audio/file"])
```



## Haystack 1.x

You can use [OpenAI Models](https://openai.com/) in your Haystack pipelines with the [EmbeddingRetriever](https://docs.haystack.deepset.ai/docs/retriever#embedding-retrieval-recommended), [PromptNode](https://docs.haystack.deepset.ai/docs/prompt_node), and [WhisperTranscriber](https://docs.haystack.deepset.ai/docs/whisper_transcriber).

### Installation (1.x)

```bash
pip install farm-haystack
```

### Usage (1.x)

You can use OpenAI models in various ways:

#### Embedding Models

To use embedding models from OpenAI, initialize an `EmbeddingRetriever` with the model name and OpenAI API key. You can then use this `EmbeddingRetriever` in an indexing pipeline to create OpenAI embeddings for documents and index them to a document store. 

Below is the example indexing pipeline with `PreProcessor`, `InMemoryDocumentStore` and  `EmbeddingRetriever`:

```python
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import Pipeline
from haystack.schema import Document

document_store = InMemoryDocumentStore(embedding_dim=1024)
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(
    embedding_model="ada", document_store=document_store, api_key=OPENAI_API_KEY
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=preprocessor, name="Preprocessor", inputs=["File"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["Preprocessor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=["Retriever"])
indexing_pipeline.run(documents=[Document("This is my document")])
```

#### Generative Models (LLMs) 

To use GPT models from OpenAI, initialize a `PromptNode` with the model name, OpenAI API key and the prompt template. You can then use this `PromptNode` in a question answering pipeline to generate answers based on the given context.  

Below is the example of generative questions answering pipeline using RAG with `EmbeddingRetriever` and  `PromptNode`:

```python
from haystack.nodes import PromptNode, EmbeddingRetriever
from haystack.pipelines import Pipeline

retriever = EmbeddingRetriever(
    embedding_model="babbage", document_store=document_store, api_key=OPENAI_API_KEY
)
prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo", 
    api_key=OPENAI_API_KEY, 
    default_prompt_template="deepset/question-answering"
)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
query_pipeline.run("YOUR_QUERY")
```

#### Transcriber Models

To use Whisper models from OpenAI, initialize a `WhisperTranscriber`. To use Whisper locally, install it following the instructions on the Whisper [GitHub repo](https://github.com/openai/whisper). To use the API implementation, provide an API key. You can then use this `WhisperTranscriber` to transcribe audio files.

Below is the example of summarization pipeline with `WhisperTranscriber` and  `PromptNode`:

```python
from haystack.nodes import WhisperTranscriber, PromptNode
from haystack.pipelines import Pipeline

whisper = WhisperTranscriber(api_key=api_key)
prompt_node = PromptNode(
        model_name_or_path="gpt-4", 
        api_key=api_key,
        default_prompt_template="deepset/summarization"
)

pipeline = Pipeline()
pipeline.add_node(component=whisper, name="whisper", inputs=["File"])
pipeline.add_node(component=prompt_node, name="prompt", inputs=["whisper"])

output = pipeline.run(file_paths=["path/to/audio/file"])
```
