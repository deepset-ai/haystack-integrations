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
pypi: https://pypi.org/project/mongodb-atlas-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mongodb_atlas
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/mongodb.png
toc: true
version: Haystack 2.0
---

### Table of Contents

- [Overview](#overview)
- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)
- [Haystack 1.x](#haystack-1x)
  - [Installation (1.x)](#installation-1x)
  - [Usage (1.x)](#usage-1x)
  - [Writing Documents to MongoDBAtlasDocumentStore](#writing-documents-to-mongodbstlasdocumentstore)
  - [Indexing Pipeline](#indexing-pipeline)
  - [Query Pipeline](#query-pipeline)

## Overview

[MongoDB](https://www.mongodb.com/) is a document database designed for ease of application development and scaling. [MongoDB Atlas](https://www.mongodb.com/atlas) is a multi-cloud database service built by people behind MongoDB. MongoDB Atlas simplifies deploying and managing your databases while offering the versatility you need to build resilient and performant global applications on the cloud providers of your choice.

For a detailed overview of all the available methods and settings for the `MongoDBAtlasDocumentStore`, visit the Haystack [Documentation](https://docs.haystack.deepset.ai/v2.0/docs/mongodbatlasdocumentstore).

## Haystack 2.0


### Installation

```bash
pip install mongodb-atlas-haystack
```

### Usage

To use the `MongoDBAtlasDocumentStore`, you must have a running MongoDB Atlas database.
For details, see [Get Started with Atlas](https://www.mongodb.com/docs/atlas/getting-started/).  

Once your database is set, set the environment variable `MONGO_CONNECTION_STRING` with the connection string to your MongoDB Atlas database.
The format should be similar to the following:
`"mongodb+srv://{mongo_atlas_username}:{mongo_atlas_password}@{mongo_atlas_host}/?{mongo_atlas_params_string}"`

And then you can initialize a [`MongoDBAtlasDocumentStore`](https://docs.haystack.deepset.ai/v2.0/docs/mongodbatlasdocumentstore) for Haystack with the required configurations:

```python
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore

document_store = MongoDBAtlasDocumentStore(
    database_name="haystack_test",
    collection_name="test_collection",
    vector_search_index="test_vector_search_index",
)
```

### Example pipelines

Here is some example code of an end-to-end RAG app built on MongoDB Atlas: one indexing pipeline that embeds the documents,
and a generative pipeline that can be used for question answering.

```python
from haystack import Pipeline, Document
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.writers import DocumentWriter
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack_integrations.components.embedders.mongodb_atlas import MongoDBAtlasEmbeddingRetriever

# Create some example documents
documents = [
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome."),
]

document_store = MongoDBAtlasDocumentStore(
    database_name="haystack_test",
    collection_name="test_collection",
    vector_search_index="test_vector_search_index",
)

# Define some more components
doc_writer = DocumentWriter(document_store=document_store, policy=DuplicatePolicy.SKIP)
doc_embedder = SentenceTransformersDocumentEmbedder(model="intfloat/e5-base-v2")
query_embedder = SentenceTransformersTextEmbedder(model="intfloat/e5-base-v2")

# Pipeline that ingests document for retrieval
indexing_pipe = Pipeline()
indexing_pipe.add_component(instance=doc_embedder, name="doc_embedder")
indexing_pipe.add_component(instance=doc_writer, name="doc_writer")

indexing_pipe.connect("doc_embedder.documents", "doc_writer.documents")
indexing_pipe.run({"doc_embedder": {"documents": documents}})

# Build a RAG pipeline with a Retriever to get documents relevant to 
# the query, a PromptBuilder to create a custom prompt and the OpenAIGenerator (LLM)
prompt_template = """
Given these documents, answer the question.\nDocuments:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

\nQuestion: {{question}}
\nAnswer:
"""
rag_pipeline = Pipeline()
rag_pipeline.add_component(instance=query_embedder, name="query_embedder")
rag_pipeline.add_component(instance=MongoDBAtlasEmbeddingRetriever(document_store=document_store), name="retriever")
rag_pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
rag_pipeline.add_component(instance=OpenAIGenerator(), name="llm")
rag_pipeline.connect("query_embedder", "retriever.query_embedding")
rag_pipeline.connect("embedding_retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")

# Ask a question on the data you just added.
question = "Where does Mark live?"
result = rag_pipeline.run(
    {
        "query_embedder": {"text": question},
        "prompt_builder": {"question": question},
    }
)
print(result)
```

## Haystack 1.x

### Installation

```bash
pip install farm-haystack[mongodb]
```

### Usage

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

### Indexing Pipeline

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
