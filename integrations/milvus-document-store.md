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

- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Dive deep usage](#dive-deep-usage)
- [Haystack 1.x](#haystack-1x)
  - [Installation (1.x)](#installation-1x)
  - [Usage (1.x)](#usage-1x)

## Haystack 2.0

[![PyPI - Version](https://img.shields.io/pypi/v/milvus-haystack.svg)](https://pypi.org/project/milvus-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/milvus-haystack.svg)](https://pypi.org/project/milvus-haystack)

---

### Installation

```shell
pip install --upgrade pymilvus milvus-haystack
```

*If you are using Google Colab, you may need to restart the runtime to enable dependencies just installed.*

### Usage

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

### Dive deep usage

Prepare an OpenAI API key and set it as an environment variable:

```shell
export OPENAI_API_KEY=<your_api_key>
```

Here are the ways to

- Create the indexing Pipeline
- Create the retrieval pipeline
- Create the RAG pipeline

#### Create the indexing Pipeline and index some documents

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

#### Create the retrieval pipeline and try a query

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

#### Create the RAG pipeline and try a query

```python
from haystack.utils import Secret
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


## Haystack 1.x



An integration of [Milvus](https://milvus.io/) vector database with [Haystack](https://haystack.deepset.ai/).

Milvus is a flexible, reliable, and fast cloud-native, open-source vector database. It powers embedding similarity search and AI applications and strives to make vector databases accessible to every organization. Milvus can store, index, and manage a billion+ embedding vectors generated by deep neural networks and other machine learning (ML) models. This level of scale is vital to handling the volumes of unstructured data generated to help organizations to analyze and act on it to provide better service, reduce fraud, avoid downtime, and make decisions faster.
Milvus is a graduated-stage project of the LF AI & Data Foundation.

Use Milvus as storage for Haystack pipelines as `MilvusDocumentStore`.

🚀 See an example application that uses the `MilvusDocumentStore` to do Milvus documentation QA [here](https://github.com/TuanaCelik/milvus-documentation-qa).

### Installation

```bash
pip install milvus-haystack==0.0.2
```

### Usage

Once installed and running, you can start using Milvus with Haystack by initializing it: 

```python
from milvus_haystack import MilvusDocumentStore

document_store = MilvusDocumentStore()
```

#### Writing Documents to MilvusDocumentStore

To write documents to your `MilvusDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/v1.25/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/v1.25/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources. Below is the example indexing pipeline used in the Milvus Documentation QA demo, which makes use of the `Crawler` component.

##### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.nodes import Crawler, PreProcessor, EmbeddingRetriever
from milvus_haystack import MilvusDocumentStore

document_store = MilvusDocumentStore(recreate_index=True, return_embedding=True, similarity="cosine")
crawler = Crawler(urls=["https://milvus.io/docs/"], crawler_depth=1, overwrite_existing_files=True, output_dir="crawled_files")
preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=False,
    clean_header_footer=True,
    split_by="word",
    split_length=500,
    split_respect_sentence_boundary=True,
)
retriever = EmbeddingRetriever(document_store=document_store, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=crawler, name="crawler", inputs=['File'])
indexing_pipeline.add_node(component=preprocessor, name="preprocessor", inputs=['crawler'])
indexing_pipeline.add_node(component=retriever, name="retriever", inputs=['preprocessor'])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=['retriever'])

indexing_pipeline.run()
```

#### Using Milvus in a Retrieval Augmented Generative Pipeline

Once you have documents in your `MilvusDocumentStore`, it's ready to be used in any Haystack pipeline. For example, below is a pipeline that makes use of the ["deepset/question-answering"](https://prompthub.deepset.ai/?prompt=deepset%2Fquestion-answering) prompt that is designed to generate answers for the retrieved documents. Below is the example pipeline used in the Milvus Documentation QA deme that generates replies to queries using GPT-4:

```python
from haystack import Pipeline
from haystack.nodes import EmbeddingRetriever, PromptNode, PromptTemplate, AnswerParser
from milvus_haystack import MilvusDocumentStore

document_store = MilvusDocumentStore()

retriever = EmbeddingRetriever(document_store=document_store, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
template = PromptTemplate(prompt="deepset/question-answering", output_parser=AnswerParser())
prompt_node = PromptNode(model_name_or_path="gpt-4", default_prompt_template=template, api_key=YOUR_OPENAI_API_KEY, max_length=200)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
```
