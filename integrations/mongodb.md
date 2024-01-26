---
layout: integration
name: MongoDB
description: Use a MongoDB Atlas database with Haystack
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
logo: /logos/mongodb.png
toc: true
---

[MongoDB](https://www.mongodb.com/) is a document database designed for ease of application development and scaling. [MongoDB Atlas](https://www.mongodb.com/atlas) is a multi-cloud database service built by people behind MongoDB. MongoDB Atlas simplifies deploying and managing your databases while offering the versatility you need to build resilient and performant global applications on the cloud providers of your choice.

For a detailed overview of all the available methods and settings for the `MongoDBAtlasDocumentStore`, visit the Haystack [Documentation](https://docs.haystack.deepset.ai/docs/document_store#initialization).

## Installation

```bash
pip install farm-haystack[mongodb]
```

## Usage

To use MongoDB Atlas as your data storage for your Haystack LLM pipelines, you must have a running database at MongoDB Atlas. For details, see [Get Started with Atlas](https://www.mongodb.com/docs/atlas/getting-started/).  

Once your database is set, you can initialize a `MongoDBAtlasDocumentStore` for Haystack with required configurations:

```python
from haystack.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore

ds=MongoDBAtlasDocumentStore(
    mongo_connection_string="mongodb+srv://{mongo_atlas_username}:{mongo_atlas_password}@{mongo_atlas_host}/?{mongo_atlas_params_string}",
    database_name="database_name",
    collection_name="collection_name",
    vector_search_index="vector_search_index"
)
```

### Writing Documents to MongoDBAtlasDocumentStore

To write documents to your `MongoDBAtlasDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources. Below is an example indexing pipeline that indexes your Markdown files into a MongoDB Atlas instance.

#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack.nodes import MarkdownConverter, PreProcessor

document_store=MongoDBAtlasDocumentStore(
    mongo_connection_string="mongodb+srv://{mongo_atlas_username}:{mongo_atlas_password}@{mongo_atlas_host}/?{mongo_atlas_params_string}",
    database_name="database_name",
    collection_name="collection_name",
    vector_search_index="vector_search_index",
    embedding_dim=1536
)
converter = MarkdownConverter()
preprocessor = PreProcessor()

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

indexing_pipeline.run(file_paths=["filename.pdf"])
```

### Query Pipeline

Once you have documents in your `MongoDBAtlasDocumentStore`, it's ready to be used in any Haystack pipeline. For example, below is a pipeline that makes use of a custom prompt that is designed to answer questions for the retrieved documents.

```python
from haystack import Pipeline
from haystack.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack.nodes import AnswerParser, EmbeddingRetriever, PromptNode, PromptTemplate

document_store=MongoDBAtlasDocumentStore(
    mongo_connection_string="mongodb+srv://{mongo_atlas_username}:{mongo_atlas_password}@{mongo_atlas_host}/?{mongo_atlas_params_string}",
    database_name="database_name",
    collection_name="collection_name",
    vector_search_index="vector_search_index"
)
              
retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
prompt_template = PromptTemplate(prompt = """"Answer the following query based on the provided context. If the context does
                                              not include an answer, reply with 'I don't know'.\n
                                              Query: {query}\n
                                              Documents: {join(documents)}
                                              Answer: 
                                          """,
                                          output_parser=AnswerParser())
prompt_node = PromptNode(model_name_or_path="gpt-4",
                         api_key="YOUR_OPENAI_KEY",
                         default_prompt_template=prompt_template)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "What is MongoDB Atlas?", params={"Retriever" : {"top_k": 5}})
```
