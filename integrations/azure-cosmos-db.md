---
layout: integration
name: Azure CosmosDB
description: Use Azure CosmosDB with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/mongodb-atlas-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/mongodb_atlas
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/azure-cosmos-db.png
toc: true
version: Haystack 2.0
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction) is a fully managed NoSQL, relational, and vector database for modern app development. It offers single-digit millisecond response times, automatic and instant scalability, and guaranteed speed at any scale. It is the database that ChatGPT relies on to dynamically scale with high reliability and low maintenance.

[Azure Cosmos DB for MongoDB](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/introduction) makes it easy to use Azure Cosmos DB as if it were a MongoDB database. You can use your existing MongoDB skills and continue to use your favorite MongoDB drivers, SDKs, and tools by pointing your application to the connection string for your account using the API for MongoDB. Learn more in the [Azure Cosmos DB for MongoDB documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/).

## Installation

It's possible to connect to your MongoDB cluster in Azure Cosmos DB through the `MongoDBAtlasDocumentStore`. For that, install the `mongo-atlas-haystack` integration.
```bash
pip install mongodb-atlas-haystack
```

## Usage

To use Azure Cosmos DB for MongoDB with `MongoDBAtlasDocumentStore`, you'll need to set up an Azure Cosmos DB for MongoDB vCore cluster through the Azure portal. For a step-by-step guide, refer to [Quickstart: Azure Cosmos DB for MongoDB vCore](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/quickstart-portal).

After setting up your cluster, configure the `MONGO_CONNECTION_STRING` environment variable using the connection string for your cluster. You can find the connection string by following the instructions [here](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/quickstart-portal#get-cluster-credentials). The format should look like this:

```python
import os

os.environ["MONGO_CONNECTION_STRING"] = "mongodb+srv://<username>:<password>@<clustername>.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
```

Next, navigate to the Quickstart page of your cluster and click "Launch Quickstart."

![Azure CosmosDB cluster quickstart](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/azure-cosmosdb-quickstart.png)

This will start the Quickstart guide, which will walk you through creating a database and a collection.

![Azure CosmosDB collection](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/azure-cosmosdb-collection.png)

Once this is done, you can initialize the [`MongoDBAtlasDocumentStore`](https://docs.haystack.deepset.ai/docs/mongodbatlasdocumentstore) in Haystack with the appropriate configuration.

```python
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack import Document

document_store = MongoDBAtlasDocumentStore(
    database_name="quickstartDB", # your db name
    collection_name="sampleCollection", # your collection name
    vector_search_index="haystack-test", # your cluster name
)

document_store.write_documents([Document(content="this is my first doc")])
```

### Example pipelines

Here is some example code of an end-to-end RAG app built on Azure Cosmos DB: one indexing pipeline that embeds the documents,
and a generative pipeline that can be used for question answering.

```python
from haystack import Pipeline, Document
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.writers import DocumentWriter
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack_integrations.components.retrievers.mongodb_atlas import MongoDBAtlasEmbeddingRetriever

# Create some example documents
documents = [
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome."),
]

document_store = MongoDBAtlasDocumentStore(
    database_name="quickstartDB", # your db name
    collection_name="sampleCollection", # your collection name
    vector_search_index="haystack-test", # your cluster name
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
