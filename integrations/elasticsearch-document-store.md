---
layout: integration
name: Elasticsearch
description: Use an Elasticsearch database with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/elasticsearch-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opensearch
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/elastic.png
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

The `ElasticsearchDocumentStore` is maintained in [haystack-core-integrations](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/elasticsearch) repo. It allows you to use [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/elasticsearch-intro.html) as data storage for your Haystack pipelines.

For a details on available methods, visit the [API Reference](https://docs.haystack.deepset.ai/v1.25/reference/document-store-api#elasticsearchdocumentstore-1)

### Installation

To run an Elasticsearch instance locally, first follow the [installation](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) and [start up](https://www.elastic.co/guide/en/elasticsearch/reference/current/starting-elasticsearch.html) guides. 

```bash
pip install elasticsearch-haystack
```

### Usage

Once installed, you can start using your Elasticsearch database with Haystack by initializing it: 

```python
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(hosts = "http://localhost:9200")
```

#### Writing Documents to ElasticsearchDocumentStore

To write documents to your `ElasticsearchDocumentStore`, create an indexing pipeline with a [DocumentWriter](https://docs.haystack.deepset.ai/docs/documentwriter), or use the `write_documents()` function.
For this step, you can use the available [TextFileToDocument](https://docs.haystack.deepset.ai/docs/textfiletodocument) and [DocumentSplitter](https://docs.haystack.deepset.ai/docs/documentsplitter), as well as other [Integrations](/integrations) that might help you fetch data from other resources.

#### Indexing Pipeline

```python
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter 

document_store = ElasticsearchDocumentStore(hosts = "http://localhost:9200")
converter = TextFileToDocument()
splitter = DocumentSplitter()
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
writer = DocumentWriter(document_store)

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("converter", converter)
indexing_pipeline.add_component("splitter", splitter)
indexing_pipeline.add_component("doc_embedder", doc_embedder)
indexing_pipeline.add_component("writer", writer)

indexing_pipeline.connect("converter", "splitter")
indexing_pipeline.connect("splitter", "doc_embedder")
indexing_pipeline.connect("doc_embedder", "writer")

indexing_pipeline.run({
    "converter":{"sources":["filename.txt"]}
    })
```

### Using Elasticsearch in a Query Pipeline

Once you have documents in your `ElasticsearchDocumentStore`, it's ready to be used with with [ElasticsearchEmbeddingRetriever](https://docs.haystack.deepset.ai/docs/elasticsearchembeddingretriever) in the retrieval step of any Haystack pipeline such as a Retrieval Augmented Generation (RAG) pipelines. Learn more about [Retrievers](https://docs.haystack.deepset.ai/docs/retrievers) to make use of vector search within your LLM pipelines.

```python
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder 
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever

model = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

document_store = ElasticsearchDocumentStore(hosts = "http://localhost:9200")


retriever = ElasticsearchEmbeddingRetriever(document_store=document_store)
text_embedder = SentenceTransformersTextEmbedder(model=model)

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", text_embedder)
query_pipeline.add_component("retriever", retriever)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"text_embedder": {"text": "historical places in Instanbul"}})

print(result)
```

## Haystack 1.x

The `ElasticsearchDocumentStore` is maintained within the core Haystack project. It allows you to use [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/elasticsearch-intro.html) as data storage for your Haystack pipelines.

For a details on available methods, visit the [API Reference](https://docs.haystack.deepset.ai/v1.25/reference/document-store-api#elasticsearchdocumentstore-1)

### Installation (1.x)

To run an Elasticsearch instance locally, first follow the [installation](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) and [start up](https://www.elastic.co/guide/en/elasticsearch/reference/current/starting-elasticsearch.html) guides. 

```bash
pip install farm-haystack[elasticsearch]
```

To install Elasticsearch 7, you can run `pip install farm-haystac[elasticsearch7]`.

### Usage (1.x)

Once installed, you can start using your Elasticsearch database with Haystack by initializing it: 

```python
from haystack.document_stores import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(host = "localhost",
                                            port = 9200,
                                            embedding_dim = 768)
```

#### Writing Documents to ElasticsearchDocumentStore

To write documents to your `ElasticsearchDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/v1.25/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/v1.25/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources.

#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import TextConverter, PreProcessor

document_store = ElasticsearchDocumentStore(host = "localhost", port = 9200)
converter = TextConverter()
preprocessor = PreProcessor()

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="TextConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["TextConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

indexing_pipeline.run(file_paths=["filename.txt"])
```

### Using Elasticsearch in a Query Pipeline

Once you have documents in your `ElasitsearchDocumentStore`, it's ready to be used in any Haystack pipeline. Such as a Retrieval Augmented Generation (RAG) pipeline. Learn more about [Retrievers](https://docs.haystack.deepset.ai/v1.25/docs/retriever) to make use of vector search within your LLM pipelines.

```python
from haystack import Pipeline
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import EmbeddingRetriever, PromptNode

document_store = ElasticsearchDocumentStore()
retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
prompt_node = PromptNode(model_name_or_path = "google/flan-t5-xl", default_prompt_template = "deepset/question-answering")

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "Where is Istanbul?")
```
