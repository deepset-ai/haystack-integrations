---
layout: integration
name: OpenSearch
description: A Document Store for storing and retrieval from OpenSearch
authors:
    - name: Thomas Stadelmann
      socials:
        github: tstadel
    - name: Julian Risch
      socials:
        github: julian-risch
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/opensearch-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opensearch
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/opensearch.png
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

[![PyPI - Version](https://img.shields.io/pypi/v/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml)

-----

## Installation
Use `pip` to install OpenSearch:

```console
pip install opensearch-haystack
```
## Usage
Once installed, initialize your OpenSearch database to use it with Haystack 2.0:

```python
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore

document_store = OpenSearchDocumentStore()
```

### Writing Documents to OpenSearchDocumentStore
To write documents to `OpenSearchDocumentStore`, create an indexing pipeline.

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

`opensearch-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

## Haystack 1.x
You can use [OpenSearch](https://opensearch.org/docs/latest/#docker-quickstart) in your Haystack pipelines with the [OpenSearchDocumentStore](https://docs.haystack.deepset.ai/docs/document_store#initialization)

For a detailed overview of all the available methods and settings for the `OpenSearchDocumentStore`, visit the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/document-store-api#opensearchdocumentstore)

## Installation (1.x)

```bash
pip install farm-haystack[opensearch]
```

## Usage (1.x)

Once installed and running, you can start using OpenSearch with Haystack by initializing it: 

```python
from haystack.document_stores import OpenSearchDocumentStore

document_store = OpenSearchDocumentStore()
```

### Writing Documents to OpenSearchDocumentStore

To write documents to your `OpenSearchDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources.

#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.document_stores import OpenSearchDocumentStore
from haystack.nodes import PDFToTextConverter, PreProcessor

document_store = OpenSearchDocumentStore()
converter = PDFToTextConverter()
preprocessor = PreProcessor()

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

indexing_pipeline.run(file_paths=["filename.pdf"])
```

### Using OpenSearch in a Query Pipeline

Once you have documents in your `OpenSearchDocumentStore`, it's ready to be used in any Haystack pipeline. For example, below is a pipeline that makes use of the ["deepset/question-generation"](https://prompthub.deepset.ai/?prompt=deepset%2Fquestion-generation) prompt that is designed to generate questions for the retrieved documents. If our `OpenSearchDocumentStore` had documents about food in it, you could generate questions about "Pizzas" in the following way:

```python
from haystack import Pipeline
from haystack.document_stores import OpenSearchDocumentStore
from haystack.nodes import BM25Retriever, PromptNode

document_store = OpenSearchDocumentStore()
retriever = BM25Retriever(document_sotre = document_store)
prompt_node = PromptNode(model_name_or_path = "gpt-4",
                         api_key = "YOUR_OPENAI_KEY",
                         default_prompt_template = "deepset/question-generation")

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "Pizzas")
```
