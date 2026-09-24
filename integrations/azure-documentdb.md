---
layout: integration
name: Azure DocumentDB
description: Use Azure DocumentDB as a Document Store with vector and full-text retrieval in Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/azure-documentdb-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/azure_documentdb
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/azure.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/azure-documentdb-haystack.svg)](https://pypi.org/project/azure-documentdb-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/azure-documentdb-haystack.svg)](https://pypi.org/project/azure-documentdb-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/azure_documentdb.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/azure_documentdb.yml)

[Azure DocumentDB](https://learn.microsoft.com/azure/documentdb/overview) is a fully managed, MongoDB-compatible document database on Azure, built on the open source [DocumentDB](https://documentdb.io/) engine. Its integrated vector search keeps documents, metadata, and embeddings in the same collection, so a RAG application doesn't need a separate vector database.

The integration provides:

- `AzureDocumentDBDocumentStore`, with sync and async support for all operations
- `AzureDocumentDBEmbeddingRetriever`, which runs `cosmosSearch` vector search with metadata filters applied before the nearest neighbors are ranked
- `AzureDocumentDBFullTextRetriever`, which runs BM25 full-text search (currently a gated preview in Azure DocumentDB)
- Passwordless authentication with Microsoft Entra ID and managed identity

## Installation

```bash
pip install azure-documentdb-haystack
```

## Usage

### Authentication

By default, the Document Store authenticates with Microsoft Entra ID through `DefaultAzureCredential`: your Azure CLI login during local development, and a managed identity or workload identity in production. New clusters only allow native authentication, so first [enable Microsoft Entra ID on your cluster](https://learn.microsoft.com/azure/documentdb/how-to-connect-role-based-access-control) and assign your identity a role. Then set the cluster name:

```bash
export AZURE_DOCUMENTDB_CLUSTER_NAME="my-cluster"
```

For local development and testing, you can instead set a connection string in `AZURE_DOCUMENTDB_CONNECTION_STRING`. When it's set, the Document Store uses it instead of Microsoft Entra ID and logs a warning.

### Writing documents

The database and collection must exist before you use the Document Store. To use embedding retrieval, create a vector index once per collection. `dimensions` must match your embedding model:

```python
from haystack import Document
from haystack_integrations.document_stores.azure_documentdb import AzureDocumentDBDocumentStore

document_store = AzureDocumentDBDocumentStore(database_name="haystack", collection_name="documents")

# The default HNSW index needs an M30 or higher tier; on smaller tiers, pass kind="vector-ivf".
document_store.create_vector_index(dimensions=1536)

document_store.write_documents([Document(content="This is first"), Document(content="This is second")])
print(document_store.count_documents())
```

`create_vector_index` supports the `vector-hnsw`, `vector-diskann`, and `vector-ivf` index kinds, the `COS`, `L2`, and `IP` similarity metrics, and algorithm-specific options such as `m` and `efConstruction` for HNSW. To filter vector search on a metadata field, the collection also needs a regular index on that field, such as `meta.category`.

### Retrieval

The integration supports different retrieval types through different retriever components:

- [`AzureDocumentDBEmbeddingRetriever`](https://docs.haystack.deepset.ai/docs/azuredocumentdbembeddingretriever): Compares the query and document embeddings and fetches the documents most relevant to the query.
- [`AzureDocumentDBFullTextRetriever`](https://docs.haystack.deepset.ai/docs/azuredocumentdbfulltextretriever): A keyword-based retriever that uses Azure DocumentDB BM25 full-text search. Full-text search is a [gated preview](https://learn.microsoft.com/azure/documentdb/full-text-search-overview) that must be enabled on your cluster, and it needs a full-text search index, which you name with the Document Store's `full_text_search_index` parameter.

Here is a RAG pipeline that uses the embedding retriever with the vector index created above. It uses OpenAI models, so set the `OPENAI_API_KEY` environment variable before running it:

```python
from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import ChatMessage
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.components.retrievers.azure_documentdb import AzureDocumentDBEmbeddingRetriever
from haystack_integrations.document_stores.azure_documentdb import AzureDocumentDBDocumentStore

document_store = AzureDocumentDBDocumentStore(database_name="haystack", collection_name="documents")

documents = [
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome."),
]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", OpenAIDocumentEmbedder())
indexing_pipeline.add_component(
    "writer", DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE)
)
indexing_pipeline.connect("embedder", "writer")
indexing_pipeline.run({"embedder": {"documents": documents}})

prompt_template = [
    ChatMessage.from_user(
        """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

rag_pipeline = Pipeline()
rag_pipeline.add_component("text_embedder", OpenAITextEmbedder())
rag_pipeline.add_component("retriever", AzureDocumentDBEmbeddingRetriever(document_store=document_store))
rag_pipeline.add_component("prompt_builder", ChatPromptBuilder(template=prompt_template, required_variables="*"))
rag_pipeline.add_component("llm", OpenAIChatGenerator())
rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "Where does Mark live?"
result = rag_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
print(result["llm"]["replies"][0].text)
```

For more details, including full-text and hybrid retrieval, see the [`AzureDocumentDBDocumentStore` documentation](https://docs.haystack.deepset.ai/docs/azuredocumentdbdocumentstore).

## License

`azure-documentdb-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/azure_documentdb/LICENSE.txt).
