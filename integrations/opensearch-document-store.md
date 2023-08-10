---
layout: integration
name: OpenSearch Document Store
description: Use an OpenSearch database with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/farm-haystack
repo: https://github.com/deepset-ai/haystack
type: Document Store
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/opensearch.png
---

You can use [OpenSearch](https://opensearch.org/docs/latest/#docker-quickstart) in your Haystack pipelines with the [OpenSearchDocumentStore](https://docs.haystack.deepset.ai/docs/document_store#initialization)

For a detailed overview of all the available methods and settings for the `OpenSearchDocumentStore`, visit the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/document-store-api#opensearchdocumentstore)

## Installation

```bash
pip install farm-haystack[opensearch]
```

## Usage

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