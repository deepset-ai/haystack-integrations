---
layout: integration
name: Neo4j
description: Use the Neo4j database with Haystack
authors:
  - name: Sergey Bondarenco
    socials:
      github: prosto
pypi: https://pypi.org/project/neo4j-haystack/
repo: https://github.com/prosto/neo4j-haystack
type: Document Store
report_issue: https://github.com/prosto/neo4j-haystack/issues
logo: /logos/neo4j.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

An integration of [Neo4j](https://neo4j.com/) graph database with [Haystack v2.0](https://docs.haystack.deepset.ai/docs/intro)
by [deepset](https://www.deepset.ai). In Neo4j [Vector search index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/)
is being used for storing document embeddings and dense retrievals.

The library allows using Neo4j as a [DocumentStore](https://docs.haystack.deepset.ai/docs/document-store), and implements the required [Protocol](https://docs.haystack.deepset.ai/docs/document-store#documentstore-protocol) methods. You can start working with the implementation by importing it from `neo4j_haystack` package:

```python
from neo4j_haystack import Neo4jDocumentStore
```

In addition to the `Neo4jDocumentStore` the library includes the following haystack components which can be used in a pipeline:

- [Neo4jEmbeddingRetriever](https://prosto.github.io/neo4j-haystack/reference/neo4j_retriever/#neo4j_haystack.components.neo4j_retriever.Neo4jEmbeddingRetriever) - a typical [retriever component](https://docs.haystack.deepset.ai/docs/retrievers) which can be used to query vector store index and find related Documents. The component uses `Neo4jDocumentStore` to query embeddings.
- [Neo4jDynamicDocumentRetriever](https://prosto.github.io/neo4j-haystack/reference/neo4j_retriever/#neo4j_haystack.components.neo4j_retriever.Neo4jDynamicDocumentRetriever) is also a retriever component in a sense that it can be used to query Documents in Neo4j. However it is decoupled from `Neo4jDocumentStore` and allows to run arbitrary [Cypher query](https://neo4j.com/docs/cypher-manual/current/queries/) to extract documents. Practically it is possible to query Neo4j same way `Neo4jDocumentStore` does, including vector search.

The `neo4j-haystack` library uses [Python Driver](https://neo4j.com/docs/api/python-driver/current/api.html#api-documentation) and
[Cypher Queries](https://neo4j.com/docs/cypher-manual/current/introduction/) to interact with Neo4j database and hide all complexities under the hood.

`Neo4jDocumentStore` will store Documents as Graph nodes in Neo4j. Embeddings are stored as part of the node, but indexing and querying of vector embeddings using ANN is managed by a dedicated [Vector Index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/).

```text
                                   +-----------------------------+
                                   |       Neo4j Database        |
                                   +-----------------------------+
                                   |                             |
                                   |      +----------------+     |
                                   |      |    Document    |     |
                write_documents    |      +----------------+     |
          +------------------------+----->|   properties   |     |
          |                        |      |                |     |
+---------+----------+             |      |   embedding    |     |
|                    |             |      +--------+-------+     |
| Neo4jDocumentStore |             |               |             |
|                    |             |               |index/query  |
+---------+----------+             |               |             |
          |                        |      +--------+--------+    |
          |                        |      |  Vector Index   |    |
          +----------------------->|      |                 |    |
               query_embeddings    |      | (for embedding) |    |
                                   |      +-----------------+    |
                                   |                             |
                                   +-----------------------------+
```

In the above diagram:

- `Document` is a Neo4j node (with "Document" label)
- `properties` are Document [attributes](https://docs.haystack.deepset.ai/docs/data-classes#document) stored as part of the node.
- `embedding` is also a property of the Document node (just shown separately in the diagram for clarity) which is a vector of type `LIST[FLOAT]`.
- `Vector Index` is where embeddings are getting indexed by Neo4j as soon as those are updated in Document nodes.

## Installation

`neo4j-haystack` can be installed as any other Python library, using pip:

```bash
pip install --upgrade pip # optional
pip install sentence-transformers # required in order to run pipeline examples given below
pip install neo4j-haystack
```

## Usage

Once installed, you can start using `Neo4jDocumentStore` as any other document stores that support embeddings.

```python
from neo4j_haystack import Neo4jDocumentStore

document_store = Neo4jDocumentStore(
    url="bolt://localhost:7687",
    username="neo4j",
    password="passw0rd",
    database="neo4j",
    embedding_dim=384,
    embedding_field="embedding",
    index="document-embeddings", # The name of the Vector Index in Neo4j
    node_label="Document", # Providing a label to Neo4j nodes which store Documents
)
```

Assuming there is a list of documents available you can write/index those in Neo4j, e.g.:

```python
documents: List[Document] = ...
document_store.write_documents(documents)
```

The full list of parameters accepted by `Neo4jDocumentStore` can be found in
[API documentation](https://prosto.github.io/neo4j-haystack/reference/neo4j_store/#neo4j_haystack.document_stores.neo4j_store.Neo4jDocumentStore.__init__).

Please notice you will need to have a running instance of Neo4j database (in-memory version of Neo4j is not supported). There are several options available:

- [Docker](https://neo4j.com/docs/operations-manual/5/docker/), other options available in the same Operations Manual
- [AuraDB](https://neo4j.com/cloud/platform/aura-graph-database/) - a fully managed Cloud Instance of Neo4j
- [Neo4j Desktop](https://neo4j.com/docs/desktop-manual/current/) client application

The simplest way to start database locally will be with Docker container:

```bash
docker run \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/passw0rd \
    neo4j:5.15.0
```

### Retrieving documents

`Neo4jEmbeddingRetriever` component can be used to retrieve documents from Neo4j by querying vector index using an embedded query. Below is a pipeline which finds documents using query embedding as well as [metadata filtering](https://docs.haystack.deepset.ai/docs/metadata-filtering):

```python
from typing import List

from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from neo4j_haystack import Neo4jEmbeddingRetriever, Neo4jDocumentStore

document_store = Neo4jDocumentStore(
    url="bolt://localhost:7687",
    username="neo4j",
    password="passw0rd",
    database="neo4j",
    embedding_dim=384,
    index="document-embeddings",
)
documents = [
    Document(content="My name is Morgan and I live in Paris.", meta={"release_date": "2018-12-09"})]

document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")  
document_embedder.warm_up()
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))

print(document_store.count_documents())
pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
pipeline.add_component("retriever", Neo4jEmbeddingRetriever(document_store=document_store))
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = pipeline.run(
    data={
        "text_embedder": {"text": "What cities do people live in?"},
        "retriever": {
            "top_k": 5,
            "filters": {"field": "release_date", "operator": "==", "value": "2018-12-09"},
        },
    }
)

documents: List[Document] = result["retriever"]["documents"]
```

```bash
>>> output:
`[Document(id=e765764ab700b231db1eeae208d6a59047b4b93712d1a9e379ae9599128ffdbd, content: 'My name is Morgan and I live in Paris.', meta: {'release_date': '2018-12-09'}, score: 0.8416308164596558)]`
```

### Retrieving documents using Cypher

`Neo4jDynamicDocumentRetriever` is a flexible retriever component which can run a Cypher query to obtain documents. The above example of `Neo4jEmbeddingRetriever` could be rewritten without usage of `Neo4jDocumentStore`:

```python
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder

from neo4j_haystack import Neo4jClientConfig, Neo4jDynamicDocumentRetriever

client_config = Neo4jClientConfig(
    url="bolt://localhost:7687",
    username="neo4j",
    password="passw0rd",
    database="neo4j",
)

cypher_query = """
            CALL db.index.vector.queryNodes($index, $top_k, $query_embedding)
            YIELD node as doc, score
            MATCH (doc) WHERE doc.release_date = $release_date
            RETURN doc{.*, score}, score
            ORDER BY score DESC LIMIT $top_k
        """

embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
retriever = Neo4jDynamicDocumentRetriever(
    client_config=client_config, runtime_parameters=["query_embedding"], doc_node_name="doc"
)

pipeline = Pipeline()
pipeline.add_component("text_embedder", embedder)
pipeline.add_component("retriever", retriever)
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = pipeline.run(
    data={
        "text_embedder": {"text": "What cities do people live in?"},
        "retriever": {
            "query": cypher_query,
            "parameters": {"index": "document-embeddings", "top_k": 5, "release_date": "2018-12-09"},
        },
    }
)

documents: List[Document] = result["retriever"]["documents"]
```

Please notice how query parameters are being used in the `cypher_query`:

- `runtime_parameters` is a list of parameter names which are going to be input slots when connecting components
    in a pipeline. In our case `query_embedding` input is connected to the `text_embedder.embedding` output.
- `pipeline.run` specifies additional parameters to the `retriever` component which can be referenced in the
    `cypher_query`, e.g. `top_k`.

### More examples

You can find more examples in the implementation [repository](https://github.com/prosto/neo4j-haystack/tree/main/examples):

- [indexing_pipeline.py](https://github.com/prosto/neo4j-haystack/blob/main/examples/indexing_pipeline.py) - Indexing text files (documents) from a remote http location.
- [rag_pipeline.py](https://github.com/prosto/neo4j-haystack/blob/main/examples/rag_pipeline.py) - Generative question answering RAG pipeline using `Neo4jEmbeddingRetriever` to fetch documents from Neo4j document store and answer question using [HuggingFaceTGIGenerator](https://docs.haystack.deepset.ai/docs/huggingfacetgigenerator).
- [rag_pipeline_cypher.py](https://github.com/prosto/neo4j-haystack/blob/main/examples/rag_pipeline_cypher.py) - Same as `rag_pipeline.py` but using `Neo4jDynamicDocumentRetriever`.

You might find more technical details in the [Code Reference](https://prosto.github.io/neo4j-haystack/reference/neo4j_store/) documentation. For example, in real world scenarios there could be requirements to tune connection settings to Neo4j database (e.g. request timeout). [Neo4jDocumentStore](https://prosto.github.io/neo4j-haystack/reference/neo4j_store/#neo4j_haystack.document_stores.Neo4jDocumentStore.__init__) accepts an extended client configuration using [Neo4jClientConfig](https://prosto.github.io/neo4j-haystack/reference/neo4j_client/#neo4j_haystack.client.neo4j_client.Neo4jClientConfig) class.

## License

`neo4j-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
