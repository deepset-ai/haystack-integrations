---
layout: integration
name: SingleStore
description: Use SingleStore with Haystack
authors:
    - name: SingleStore
      socials:
        github: singlestore-labs
        twitter: SingleStoreDB
        linkedin: https://www.linkedin.com/company/singlestore/
pypi: https://pypi.org/project/singlestore-haystack/
repo: https://github.com/singlestore-labs/singlestore-haystack
report_issue: https://github.com/singlestore-labs/singlestore-haystack/issues
type: Document Store
logo: /logos/singlestore.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [Running SingleStore](#running-singlestore)
    - [Writing Documents](#writing-documents)
    - [Index configuration](#index-configuration)
    - [Retrieving documents](#retrieving-documents)
    - [More examples](#more-examples)
- [License](#license)

## Overview

An integration of the [SingleStore](https://www.singlestore.com/) database
with [Haystack](https://docs.haystack.deepset.ai/docs/intro) by [deepset](https://www.deepset.ai). In SingleStore,
a [vector index](https://docs.singlestore.com/cloud/reference/sql-reference/vector-functions/vector-indexing/) is used
to store document embeddings and support efficient approximate nearest neighbor (ANN)–based dense retrieval for semantic
use cases such as RAG and similarity search. In contrast,
a [full-text search index](https://docs.singlestore.com/cloud/developer-resources/functional-extensions/working-with-full-text-search/) (
`VERSION 2`) is used to perform Lucene-compatible, BM25-scored keyword and phrase searches over text and JSON content
for traditional text-based retrieval.

The `singlestore-haystack` library enables SingleStore as
a [DocumentStore](https://docs.haystack.deepset.ai/docs/document-store) by implementing the
Haystack [DocumentStore protocol](https://docs.haystack.deepset.ai/docs/document-store#documentstore-protocol) methods.
Import the `SingleStoreDocumentStore` implementation from the `singlestore_haystack` package:

```python
from singlestore_haystack import SingleStoreDocumentStore
```

In addition to `SingleStoreDocumentStore`, the library includes the following haystack components which can be used in a
pipeline:

- SingleStoreEmbeddingRetriever - is a typical [retriever component](https://docs.haystack.deepset.ai/docs/retrievers)
  which can be used to query SingleStore vector index and find semantically related Documents. This component uses
  `SingleStoreDocumentStore` to perform vector similarity search over stored embeddings.

- SingleStoreBM25Retriever - is a retriever component that performs sparse retrieval using the BM25 ranking algorithm.
  It leverages SingleStore full-text search capabilities to retrieve Documents based on keyword relevance, rather than
  vector similarity (embeddings). This component uses `SingleStoreDocumentStore` to execute BM25 queries and is well
  suited for keyword-based and hybrid search scenarios.

The `singlestore-haystack` library uses [Python Client](https://pypi.org/project/singlestoredb/) to interact with a
SingleStore database and hide all complexities under the hood.

`SingleStoreDocumentStore` stores Documents as rows in a SingleStore table. Embeddings are stored as
a [VECTOR](https://docs.singlestore.com/cloud/reference/sql-reference/data-types/vector-type/) type column.

```text
                                         +-----------------------------------+
                                         |       SingleStore Database        |
                                         +-----------------------------------+
                                         |                                   |
                write_documents          |      +----------------------+     |
          +------------------------------+----->|    Haystack table    |     |
          |                              |      +----------------------+     |
+---------+----------------+             |      |  * embedding         |     |
|                          |             |      |  * content           |     |
| SingleStoreDocumentStore |             |      |  * other attributes  |     |
|                          |             |      |                      |     |
+---------+----------------+             |      |  - vector indexes    |     |
          |                              |      |  - fulltext index    |     |
          +------------------------------+----->|                      |     |
                retrieve_documents       |      +----------------------+     |
                                         |                                   |
                                         +-----------------------------------+
```

In this diagram:

- `Haystack table` is a SingleStore table used by `SingleStoreDocumentStore` to persist Haystack Document objects as
  rows.
- `embedding` is a property of the Document (shown separately in the diagram for clarity) which is stored as a vector of
  type `VECTOR(n, F32)`.
- `content` is a property of the Document (shown separately in the diagram for clarity).
- `vector indexes` are SingleStore vector indexes created on the `embedding` column to enable efficient search for dense
  retrieval.
- `fulltext index` is a SingleStore full-text index created on the `content` column to support BM25-based sparse
  retrieval.
- `write_documents` represents the operation where Documents are inserted into the table by `SingleStoreDocumentStore`.
- `retrieve_documents` represents retrieval operations executed by retrievers, such as `SingleStoreEmbeddingRetriever` (
  vector search) and `SingleStoreBM25Retriever` (full-text search).

`SingleStoreDocumentStore` automatically creates the required vector and full-text indexes if they do not already exist.
When using `SingleStoreEmbeddingRetriever`, Documents must be embedded before they are written to the database. You can
use one of the available [Haystack embedders](https://docs.haystack.deepset.ai/docs/embedders) to generate these
embeddings.
For example,
the [SentenceTransformersDocumentEmbedder](https://docs.haystack.deepset.ai/docs/sentencetransformersdocumentembedder)
can be used in an indexing pipeline to generate document embeddings prior to persisting them in SingleStore.

## Installation

`singlestore-haystack` can be installed with `pip` like any other Python library:

```bash
pip install --upgrade pip # optional
pip install sentence-transformers  # required to run pipeline examples given below
pip install singlestore-haystack
```

## Usage

### Running SingleStore

You must have an active SingleStore deployment to use the components from this package.
The [SingleStore Dev Image](https://github.com/singlestore-labs/singlestoredb-dev-image) enables you to easily deploy a
SingleStore instance locally using a Docker container:

```bash
docker run \
    -d --name singlestoredb-dev \
    -e ROOT_PASSWORD="YOUR SINGLESTORE ROOT PASSWORD" \
    -p 3306:3306 -p 8080:8080 -p 9000:9000 \
    ghcr.io/singlestore-labs/singlestoredb-dev:latest
```

Refer to the [SingleStore Dev Image](https://github.com/singlestore-labs/singlestoredb-dev-image) GitHub repository for
more information.

### Writing documents

Once the package is installed and the SingleStore database is running, you can start using `SingleStoreDocumentStore`
just like any other document store that supports embeddings.

Set the `S2_CONN_STR` environment variable to your connection string to avoid hardcoding credentials in the code:

```bash
export S2_CONN_STR="singlestoredb://USER:PASSWORD@HOST:PORT"
```

```python
from singlestore_haystack import SingleStoreDocumentStore

document_store = SingleStoreDocumentStore(
    database_name="haystack_db",  # The name of the database in SingleStore
    table_name="haystack_documents",  # The name of the table to store Documents
    embedding_dimension=384  # The dimension of the embeddings being stored
)
```

Assuming that you have a list of documents available and an active SingleStore database, you can write the documents to
SingleStore. For example:

```python
from haystack import Document

documents = [Document(content="My name is Morgan and I live in Paris.")]

document_store.write_documents(documents)
```

If you intend to obtain embeddings before writing documents, use the following code:

```python
from haystack import Document

# import one of the available document embedders
from haystack.components.embedders import SentenceTransformersDocumentEmbedder

documents = [Document(content="My name is Morgan and I live in Paris.")]

document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))
```

Ensure that the embedding model produces vectors of same size as configured on `SingleStoreDocumentStore`, e.g., setting
`embedding_dimension=384` will comply with the "sentence-transformers/all-MiniLM-L6-v2" model.

> **Note**
> In most cases, you will use [Haystack Pipelines](https://docs.haystack.deepset.ai/docs/pipelines) to build both
> indexing and querying RAG workflows.

It is important to understand how Haystack Documents are stored in SingleStore after you call `write_documents`.

```python
from random import random
from haystack import Document

sample_embedding = [random() for _ in range(384)]  # using fake/random embedding for brevity here to simplify example
document = Document(
    content="My name is Morgan and I live in Paris.", embedding=sample_embedding, meta={"num_of_years": 3}
)
print(document.to_dict())
```

This code converts a Document to a dictionary and renders the following output:

```bash
>>> output:
{
    "id": "945a32e1d4532f8506fc812d5a77b0812cafdd289d6c1af468ee0626129d6ab4",
    "content": "My name is Morgan and I live in Paris.",
    "blob": None,
    "score": None,
    "embedding": [0.814127326,0.327150941,0.166730702, ...], # vector of size 384
    "sparse_embedding": None,
    "num_of_years": 3,
}
```

The data from the dictionary will be used to add a row in SingleStore after you write the document with
`document_store.write_documents([document])`. The following is a representation of the row in SingleStore:

```bash
singlestore> SET vector_type_project_format = JSON;        
Query OK, 0 rows affected (0.00 sec)

singlestore> select * from haystack_db.haystack_documents\G
*************************** 1. row ***************************
            id: 945a32e1d4532f8506fc812d5a77b0812cafdd289d6c1af468ee0626129d6ab4
     embedding: [0.814127326,0.327150941,0.166730702,... ]  # vector of size 384
       content: My name is Morgan and I live in Paris.
     blob_data: NULL
     blob_meta: NULL
blob_mime_type: NULL
          meta: {"num_of_years":3}
1 row in set (0.06 sec)

```

With Haystack, you can use the [DocumentWriter](https://docs.haystack.deepset.ai/docs/documentwriter) component to write
Documents into a Document Store. In the following example, we construct a pipeline to write documents to SingleStore
using
`SingleStoreDocumentStore`:

```python
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter

from singlestore_haystack import SingleStoreDocumentStore

documents = [Document(content="This is document 1"), Document(content="This is document 2")]

document_store = SingleStoreDocumentStore(
    database_name="haystack_db",  # The name of the database in SingleStore
    table_name="haystack_documents",  # The name of the table to store Documents
    embedding_dimension=384,  # The dimension of the embeddings being stored
    recreate_table=True,  # recreate the table if it already exists
)
embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
document_writer = DocumentWriter(document_store=document_store)

pipeline = Pipeline()
pipeline.add_component(instance=embedder, name="embedder")
pipeline.add_component(instance=document_writer, name="writer")

pipeline.connect("embedder", "writer")
print(pipeline.run({"embedder": {"documents": documents}}))
```

```bash
>>> output:
`{'writer': {'documents_written': 2}}`
```

### Index configuration

`SingleStoreDocumentStore` allows you to control which indexes are created and used in the database. Depending on your
retrieval strategy, you can enable or disable specific index types and customize their creation options.

#### Dot product vector index

- `use_dot_product_vector_index`
  Whether to create and use a vector index optimized for **dot product similarity**. Dot product similarity is typically
  used with **normalized embeddings**.

- `dot_product_vector_index_options` Optional dictionary containing additional options to pass to the dot product vector
  index during creation. These options are forwarded directly to SingleStore. Refer
  to [Vector Index Options](https://docs.singlestore.com/cloud/reference/sql-reference/vector-functions/vector-indexing/#index-options)
  for information on supported options.

#### Euclidean (L2) distance vector index

- `use_euclidian_distance_vector_index`
  Whether to create and use a vector index optimized for **Euclidean (L2) distance**.
  This metric is commonly used when embeddings are **not normalized**.

- `euclidian_distance_vector_index_options`  
  Optional dictionary containing additional options to pass to the Euclidean distance vector index during
  creation. These options are forwarded directly to SingleStore. Refer
  to [Vector Index Options](https://docs.singlestore.com/cloud/reference/sql-reference/vector-functions/vector-indexing/#index-options)
  for information on supported options.

#### Full-text index

- `use_fulltext_index`  
  Whether to create and use a **full-text index** for keyword-based retrieval.

- `fulltext_index_options`  
  Optional dictionary containing additional options to pass to the full-text index during creation, such as
  custom analyzers or tokenization settings.  
  Refer
  to [Full-Text Custom Analyzers](https://docs.singlestore.com/db/v9.0/developer-resources/functional-extensions/full-text-version-2-custom-analyzers)
  for more information.

The full-text index is required for keyword-based retrieval using `SingleStoreBM25Retriever`.

#### Hybrid retrieval

Both vector and full-text indexes can be enabled at the same time to support **hybrid retrieval** scenarios, where dense (semantic) and sparse (keyword-based) search techniques are combined within the same Haystack pipeline.
Find the example in [hybrid_retrieval.py](https://github.com/singlestore-labs/singlestore-haystack/tree/main/examples/hybrid_retrieval.py)

### Retrieving documents

`SingleStoreEmbeddingRetriever` component can be used to retrieve documents from SingleStore by using vector index. The
following pipeline finds documents using vector index as well
as [metadata filtering](https://docs.haystack.deepset.ai/docs/metadata-filtering):

```python
from typing import List

from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder

from singlestore_haystack import SingleStoreDocumentStore, SingleStoreEmbeddingRetriever

document_store = SingleStoreDocumentStore(
    database_name="haystack_db",  # The name of the database in SingleStore
    table_name="haystack_documents",  # The name of the table to store Documents
    embedding_dimension=384,  # The dimension of the embeddings being stored
    recreate_table=True,
)

documents = [
    Document(content="My name is Morgan and I live in Paris.", meta={"num_of_years": 3}),
    Document(content="I am Susan and I live in Berlin.", meta={"num_of_years": 7}),
]

# The same model is used for both query and Document embeddings
model_name = "sentence-transformers/all-MiniLM-L6-v2"

document_embedder = SentenceTransformersDocumentEmbedder(model=model_name)
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))

print("Number of documents written: ", document_store.count_documents())

pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model=model_name))
pipeline.add_component("retriever", SingleStoreEmbeddingRetriever(document_store=document_store))
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = pipeline.run(
    data={
        "text_embedder": {"text": "What cities do people live in?"},
        "retriever": {
            "top_k": 5,
            "filters": {"field": "meta.num_of_years", "operator": "==", "value": 3},
        },
    }
)

documents: List[Document] = result["retriever"]["documents"]
print(documents)
```

```bash
>>> output:
[Document(id=4014455c3be5d88151ba12d734a16754d7af75c691dfc3a5f364f81772471bd2, content: 'My name is Morgan and I live in Paris.', meta: {'num_of_years': 3}, score: 0.33934953808784485, embedding: vector of size 384)]
```

### More examples

You can find more examples in the
implementation [repository](https://github.com/singlestore-labs/singlestore-haystack/tree/main/examples):

- [embedding_retrieval.py](https://github.com/singlestore-labs/singlestore-haystack/tree/main/examples/embedding_retrieval.py)
- [hybrid_retrieval.py](https://github.com/singlestore-labs/singlestore-haystack/tree/main/examples/hybrid_retrieval.py)

## License

`singlestore-haystack` is distributed under the terms of
the [Apache-2.0](https://github.com/singlestore-labs/singlestore-haystack/blob/main/LICENSE) license.
