---
layout: integration
name: Weaviate
description: Use a Weaviate database with Haystack
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: https://pypi.org/project/weaviate-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/weaviate_haystack
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/weaviate.png
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

[![PyPI - Version](https://img.shields.io/pypi/v/weaviate-haystack.svg)](https://pypi.org/project/weaviate-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/weaviate-haystack.svg)](https://pypi.org/project/weaviate-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/weaviate.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/weaviate.yml)

---

## Installation

Use `pip` to install Weaviate:

```console
pip install weaviate-haystack
```

## Usage

Once installed, initialize your Weaviate database to use it with Haystack 2.0:

```python
from haystack.utils.auth import Secret
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore, AuthApiKey


auth_client_secret = AuthApiKey(Secret.from_token("MY_WEAVIATE_API_KEY"))
document_store = WeaviateDocumentStore(auth_client_secret=auth_client_secret)
```

### Writing Documents to WeaviateDocumentStore

To write documents to `WeaviateDocumentStore`, create an indexing pipeline.

```python
from haystack.components.file_converters import TextFileToDocument
from haystack.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"paths": file_paths}})
```

### License

`weaviate-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

## Haystack 1.x

Haystack supports the use of [Weaviate](https://weaviate.io/) as data storage for LLM pipelines, with the `WeaviateDocumentStore`. You can choose to run Weaviate locally youself, or use a hosted Weaviate database.

For details on the available methods and parameters of the `WeaviateDocumentStore`, check out the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/document-store-api#weaviatedocumentstore) and [Documentation](https://docs.haystack.deepset.ai/docs/document_store#initialization)

## Installation

```bash
pip install farm-haystack[weaviate]
```

## Usage

To use Weaviate as your data storage for your Haystack LLM pipelines, you should have it running locally or have a hosted instance. Then, you can initialize a `WeaviateDocumentStore`:

```python
from haystack.document_stores import WeaviateDocumentStore

document_store = WeaviateDocumentStore(host='http://localhost",
                                       port=8080,
                                       embedding_dim=768)
```

### Writing Documents to WeaviateDocumentStore

To write documents to your `WeaviateDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources. Below is an example indexing pipeline that indexes your Markdown files into a Weaviate database. The example pipeline below not only indexes the contents of the files, but also the embeddings. This way, we can do vector search on our files.

#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.document_stores import WeaviateDocumentStore
from haystack.nodes import EmbeddingRetriever, MarkdownConverter, PreProcessor

document_store = WeaviateDocumentStore(host="http://localhost",
                                       port=8080,
                                       embedding_dim=768)
converter = MarkdownConverter()
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["PreProcessor"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["Retriever"])

indexing_pipeline.run(file_paths=["filename.pdf"])
```

### Using Weaviate in a Query Pipeline

Once you have documents in your `WeaviateDocumentStore`, it's ready to be used in any Haystack pipeline. For example, below is a pipeline that makes use of a custom prompt that, given a query, is designed to generate long answers based on the retrieved documents.

```python
from haystack import Pipeline
from haystack.document_stores import WeaviateDocumentStore
from haystack.nodes import AnswerParser, EmbeddingRetriever, PromptNode, PromptTemplate

document_store = WeaviateDocumentStore(host='http://localhost",
                                       port=8080,
                                       embedding_dim=768)

retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
prompt_template = PromptTemplate(prompt = """"Given the provided Documents, answer the Query. Make your answer detailed and long\n
                                              Query: {query}\n
                                              Documents: {join(documents)}
                                              Answer:
                                          """,
                                          output_parser=AnswerParser())
prompt_node = PromptNode(model_name_or_path = "gpt-4",
                         api_key = "YOUR_OPENAI_KEY",
                         default_prompt_template = prompt_template)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "What is Weaviate", params={"Retriever" : {"top_k": 5}})
```
