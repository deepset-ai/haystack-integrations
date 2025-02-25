---
layout: integration
name: Milvus
description: Use the Milvus vector database with Haystack
authors:
    - name: Zilliz 
      socials:
        github: zilliztech
        twitter: zilliz_universe
pypi: https://pypi.org/project/milvus-haystack/
repo: https://github.com/milvus-io/milvus-haystack
type: Document Store
report_issue: https://github.com/milvus-io/milvus-haystack/issues
logo: /logos/milvus.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Dive deep usage](#dive-deep-usage)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/milvus-haystack.svg)](https://pypi.org/project/milvus-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/milvus-haystack.svg)](https://pypi.org/project/milvus-haystack)

---

## Installation

```shell
pip install --upgrade pymilvus milvus-haystack
```

*If you are using Google Colab, you may need to restart the runtime to enable dependencies just installed.*

## Usage

Use the `MilvusDocumentStore` in a Haystack pipeline as a quick start.

```python
from haystack import Document
from milvus_haystack import MilvusDocumentStore

document_store = MilvusDocumentStore(
    connection_args={"uri": "./milvus.db"},  # Milvus Lite
    # connection_args={"uri": "http://localhost:19530"},  # Milvus standalone docker service.
    drop_old=True,
)
documents = [Document(
    content="A Foo Document",
    meta={"page": "100", "chapter": "intro"},
    embedding=[-10.0] * 128,
)]
document_store.write_documents(documents)
print(document_store.count_documents())  # 1
```
In the `connection_args`, setting the URI as a local file, e.g.`./milvus.db`, is the most convenient method, as it automatically utilizes [Milvus Lite](https://milvus.io/docs/milvus_lite.md) to store all data in this file.

If you have large scale of data such as more than a million docs, we recommend setting up a more performant Milvus server on [docker or kubernetes](https://milvus.io/docs/quickstart.md). When using this setup, please use the server URI, e.g.`http://localhost:19530`, as your URI.

## Dive deep usage

Prepare an OpenAI API key and set it as an environment variable:

```shell
export OPENAI_API_KEY=<your_api_key>
```

Here are the ways to

- Create the indexing Pipeline
- Create the retrieval pipeline
- Create the RAG pipeline

### Create the indexing Pipeline and index some documents

```python
import os

from haystack import Pipeline
from haystack.components.converters import MarkdownToDocument
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter

from milvus_haystack import MilvusDocumentStore
from milvus_haystack.milvus_embedding_retriever import MilvusEmbeddingRetriever

current_file_path = os.path.abspath(__file__)
file_paths = [current_file_path]  # You can replace it with your own file paths.

document_store = MilvusDocumentStore(
    connection_args={"uri": "./milvus.db"},  # Milvus Lite
    # connection_args={"uri": "http://localhost:19530"},  # Milvus standalone docker service.
    drop_old=True,
)
indexing_pipeline = Pipeline()
indexing_pipeline.add_component("converter", MarkdownToDocument())
indexing_pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=2))
indexing_pipeline.add_component("embedder", OpenAIDocumentEmbedder())
indexing_pipeline.add_component("writer", DocumentWriter(document_store))
indexing_pipeline.connect("converter", "splitter")
indexing_pipeline.connect("splitter", "embedder")
indexing_pipeline.connect("embedder", "writer")
indexing_pipeline.run({"converter": {"sources": file_paths}})

print("Number of documents:", document_store.count_documents())
```

### Create the retrieval pipeline and try a query

```python
question = "How to set the service uri with milvus lite?"  # You can replace it with your own question. 

retrieval_pipeline = Pipeline()
retrieval_pipeline.add_component("embedder", OpenAITextEmbedder())
retrieval_pipeline.add_component("retriever", MilvusEmbeddingRetriever(document_store=document_store, top_k=3))
retrieval_pipeline.connect("embedder", "retriever")

retrieval_results = retrieval_pipeline.run({"embedder": {"text": question}})

for doc in retrieval_results["retriever"]["documents"]:
    print(doc.content)
    print("-" * 10)
```

### Create the RAG pipeline and try a query

```python
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

prompt_template = """Answer the following query based on the provided context. If the context does
                     not include an answer, reply with 'I don't know'.\n
                     Query: {{query}}
                     Documents:
                     {% for doc in documents %}
                        {{ doc.content }}
                     {% endfor %}
                     Answer: 
                  """

rag_pipeline = Pipeline()
rag_pipeline.add_component("text_embedder", OpenAITextEmbedder())
rag_pipeline.add_component("retriever", MilvusEmbeddingRetriever(document_store=document_store, top_k=3))
rag_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
rag_pipeline.add_component("generator", OpenAIGenerator(generation_kwargs={"temperature": 0}))
rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "generator")

results = rag_pipeline.run(
    {
        "text_embedder": {"text": question},
        "prompt_builder": {"query": question},
    }
)
print('RAG answer:', results["generator"]["replies"][0])

```
