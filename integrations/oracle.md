---
layout: integration
name: Oracle
description: Use Oracle AI Vector Search as a Document Store with Haystack
authors:
    - name: Federico Kamelhar
      socials:
        github: fede-kamel
        linkedin: https://www.linkedin.com/in/fedekamelhar/
pypi: https://pypi.org/project/oracle-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/oracle
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/oracle.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Oracle AI Vector Search](https://www.oracle.com/database/ai-vector-search/) is a feature of Oracle Database 23ai and 26ai that provides native vector storage and similarity search using the `VECTOR` data type — no extensions or plugins required.

This integration provides an `OracleDocumentStore` and an `OracleEmbeddingRetriever` that you can use in Haystack pipelines. It supports HNSW indexing for fast approximate search, metadata filtering with the full Haystack filter grammar, wallet-based TLS connections to Oracle Autonomous Database, and async variants for all public methods.

For a detailed overview of all available methods and settings, visit the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/integrations-oracle).

## Installation

```bash
pip install oracle-haystack
```

No separate Oracle Client install is required — the underlying [python-oracledb](https://python-oracledb.readthedocs.io/) driver runs in thin mode by default.

## Usage

Once installed, initialize an `OracleDocumentStore`. For a local Oracle Database:

```python
from haystack.utils import Secret
from haystack_integrations.document_stores.oracle import OracleDocumentStore, OracleConnectionConfig

document_store = OracleDocumentStore(
    connection_config=OracleConnectionConfig(
        user="scott",
        password=Secret.from_env_var("ORACLE_PASSWORD"),
        dsn="localhost:1521/freepdb1",
    ),
    embedding_dim=768,
)
```

For Oracle Autonomous Database on OCI, provide the wallet location for TLS authentication:

```python
document_store = OracleDocumentStore(
    connection_config=OracleConnectionConfig(
        user="admin",
        password=Secret.from_env_var("ORACLE_PASSWORD"),
        dsn="mydb_low",
        wallet_location="/path/to/wallet",
        wallet_password=Secret.from_env_var("ORACLE_WALLET_PASSWORD"),
    ),
    embedding_dim=768,
    distance_metric="COSINE",
)
```

### Writing Documents to OracleDocumentStore

To write documents to your `OracleDocumentStore`, create an indexing pipeline with a [DocumentWriter](https://docs.haystack.deepset.ai/docs/documentwriter), or use the `write_documents()` function. You can use the available [Converters](https://docs.haystack.deepset.ai/docs/converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessors), as well as other [Integrations](/integrations) that might help you fetch data from other resources.

### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("converter", TextFileToDocument())
indexing_pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=2))
indexing_pipeline.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing_pipeline.add_component("writer", DocumentWriter(document_store))

indexing_pipeline.connect("converter", "splitter")
indexing_pipeline.connect("splitter", "embedder")
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"converter": {"sources": ["filename.txt"]}})
```

For faster approximate nearest-neighbor search on large collections, create an HNSW index once after the first batch of writes — Oracle maintains it incrementally as new documents are added, so you don't need to rebuild it after each ingestion:

```python
document_store.create_hnsw_index()
```

The call is idempotent (`CREATE VECTOR INDEX IF NOT EXISTS`), so re-running it is safe. You can also pass `create_index=True` to `OracleDocumentStore(...)` to have the index created automatically on initialization.

### Using Oracle in a RAG Pipeline

Once you have documents in your `OracleDocumentStore`, you can use the `OracleEmbeddingRetriever` in any Haystack pipeline. Below is a pipeline that retrieves relevant documents and generates an answer using an LLM.

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.retrievers.oracle import OracleEmbeddingRetriever

prompt_template = """Answer the following query based on the provided context. If the context does
                     not include an answer, reply with 'I don't know'.\n
                     Query: {{query}}
                     Documents:
                     {% for doc in documents %}
                        {{ doc.content }}
                     {% endfor %}
                     Answer:
                  """

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
query_pipeline.add_component("retriever", OracleEmbeddingRetriever(document_store=document_store, top_k=5))
query_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
query_pipeline.add_component("generator", OpenAIGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"), model="gpt-4o"))

query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "prompt_builder.documents")
query_pipeline.connect("prompt_builder", "generator")

query = "What is Oracle AI Vector Search?"
results = query_pipeline.run(
    {
        "text_embedder": {"text": query},
        "prompt_builder": {"query": query},
    }
)
```

## License

`oracle-haystack` is distributed under the terms of the [Apache-2.0 license](https://spdx.org/licenses/Apache-2.0.html).
