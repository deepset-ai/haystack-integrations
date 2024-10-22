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
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/azure-cosmos-db.png
toc: true
version: Haystack 2.0
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage (MongoDB)](#usage-mongodb)
- [Usage (PostgreSQL)](#usage-postgresql)

## Overview

[Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction) is a fully managed NoSQL, relational, and vector database for modern app development. It offers single-digit millisecond response times, automatic and instant scalability, and guaranteed speed at any scale. It is the database that ChatGPT relies on to dynamically scale with high reliability and low maintenance. Haystack supports **MongoDB** and **PostgreSQL** clusters running on Azure Cosmos DB.

[Azure Cosmos DB for MongoDB](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/introduction) makes it easy to use Azure Cosmos DB as if it were a MongoDB database. You can use your existing MongoDB skills and continue to use your favorite MongoDB drivers, SDKs, and tools by pointing your application to the connection string for your account using the API for MongoDB. Learn more in the [Azure Cosmos DB for MongoDB documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/).

[Azure Cosmos DB for PostgreSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/postgresql/introduction) is a managed service for PostgreSQL extended with the Citus open source superpower of distributed tables. This superpower enables you to build highly scalable relational apps. You can start building apps on a single node cluster, the same way you would with PostgreSQL. As your app's scalability and performance requirements grow, you can seamlessly scale to multiple nodes by transparently distributing your tables. Learn more in the [Azure Cosmos DB for PostgreSQL documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/postgresql/).

## Installation

It's possible to connect to your **MongoDB** cluster on Azure Cosmos DB through the `MongoDBAtlasDocumentStore`. For that, install the `mongo-atlas-haystack` integration.
```bash
pip install mongodb-atlas-haystack
```

If you want to connect to the **PostgreSQL** cluster on Azure Cosmos DB, install the `pgvector-haystack` integration.
```bash
pip install pgvector-haystack
```

## Usage (MongoDB)

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

## Usage (PostgreSQL)

To use Azure Cosmos DB for PostgreSQL with `PgvectorDocumentStore`, you'll need to set up a PostgreSQL cluster through the Azure portal. For a step-by-step guide, refer to [Quickstart: Azure Cosmos DB for PostgreSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/postgresql/quickstart-create-portal).

After setting up your cluster, configure the `PG_CONN_STR` environment variable using the connection string for your cluster. You can find the connection string by following the instructions [here](https://learn.microsoft.com/en-us/azure/cosmos-db/postgresql/quickstart-connect-psql). The format should look like this:

```python
import os 

os.environ['PG_CONN_STR'] = "host=c-<cluster>.<uniqueID>.postgres.cosmos.azure.com port=5432 dbname=citus user=citus password={your_password} sslmode=require"
```

Once this is done, you can initialize the [`PgvectorDocumentStore`](https://docs.haystack.deepset.ai/docs/pgvectordocumentstore) in Haystack with the appropriate configuration.

```python
document_store = PgvectorDocumentStore(
    table_name="haystack_documents",
    embedding_dimension=1024,
    vector_function="cosine_similarity",
    search_strategy="hnsw",
    recreate_table=True,
)
```
