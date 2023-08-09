---
layout: integration
name: Elasticsearch Document Store
description: Use an Elasticsearch database with Haystack
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
logo: /logos/elastic.png
---

The `ElasticsearchDocumentStore` is maintained within the core Haystack project. It allows you to use [Elasicsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/elasticsearch-intro.html) as data storage for your Haystack pipelines.

For a details on available methods, visit the [API Reference](https://docs.haystack.deepset.ai/reference/document-store-api#elasticsearchdocumentstore-1)

## Installation

To run an Elasticsearch instance locally, first follow the [installation](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) and [start up](https://www.elastic.co/guide/en/elasticsearch/reference/current/starting-elasticsearch.html) guides. 

```bash
pip install farm-haystack[elasticsearch]
```

To install Elasticsearch 7, you can run `pip install farm-haystac[elasticsearch7]`.

## Usage

Once installed, you can start using your Elasticsearch database with Haystack by initializing it: 

```python
from haystack.document_stores import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(host = "localhost",
                                            port = 9200,
                                            embedding_dim = 768)
```

### Writing Documents to ElasticsearchDocumentStore

To write documents to your `ElasticsearchDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources.

#### Indexing Pipleine

```python
from haystack import Pipeline
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import TextConverter, PreProcessor

document_store = ElasticsearchDocumentStore(host = "localhost",
                                            port = 9200)
converter = TextConverter()
preprocessor = PreProcessor()

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="TextConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["TextConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

indexing_pipeline.run(file_paths=["filename.txt"])
```

### Using Elasticsearch in a Query Pipeline

Once you have documents in your `ElasitsearchDocumentStore`, it's ready to be used in any Haystack pipeline. Such as a Retrieval Augmented Generation (RAG) pipeline. Learn more about [Retrievers](https://docs.haystack.deepset.ai/docs/retriever) to make use of vector search within your LLM pipelines.

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