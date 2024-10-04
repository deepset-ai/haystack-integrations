---
layout: integration
name: FAISS
description: Use a FAISS vector database with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/farm-haystack
repo: https://github.com/deepset-ai/haystack
type: Document Store
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/meta.png
---

[Faiss](https://github.com/facebookresearch/faiss#readme) is a project by Meta, for efficient vector search. You can use it in your Haystack pipelines with the [FAISSDocumentStore](https://docs.haystack.deepset.ai/v1.25/docs/document_store#initialization)

For a detailed explanation on different initialization options of the `FAISSDocumentStore`, please visit the [Haystack Documentation](https://docs.haystack.deepset.ai/v1.25/docs/document_store#initialization) and [API Reference](https://docs.haystack.deepset.ai/v1.25/reference/document-store-api#faissdocumentstore). Below are some examples of how you might use it within a Haystack Pipeline.

## Installation

```bash
pip install farm-haystack[faiss]
```

or to install `FAISSDocumentStore` with GPU support, you may install:
```bash
pip install farm-haystack[faiss-gpu]
```

## Usage

Once installed, you can start using FAISS with Haystack by initializing it: 

```python
from haystack.document_stores import FAISSDocumentStore

document_store = FAISSDocumentStore()
```

### Writing Documents to FAISSDocumentStore

To write documents to your `FAISSDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/v1.25/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/v1.25/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources.

#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import PDFToTextConverter, PreProcessor

document_store = FAISSDocumentStore()
converter = PDFToTextConverter()
preprocessor = PreProcessor()

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

indexing_pipeline.run(file_paths=["filename.pdf"])
```

### Using Faiss in a Query Pipeline

Once you have documents in your `FAISSDocumentStore`, it's ready to be used in any Haystack pipeline. Such as a Retrieval Augmented Generation (RAG) pipeline. Learn more about [Retrievers](https://docs.haystack.deepset.ai/v1.25/docs/retriever) to make use of vector search within your LLM pipelines.

```python
from haystack import Pipeline
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever, PromptNode

document_store = FAISSDocumentStore()
retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
prompt_node = PromptNode(model_name_or_path = "gpt-4",
                         api_key = "YOUR_OPENAI_KEY",
                         default_prompt_template = "deepset/question-answering-with-references")

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "What is Haystack?")
```