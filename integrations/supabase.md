---
layout: integration
name: Supabase
description: Use Supabase as a Document Store for Haystack — pgvector for embedding search, PGroonga for full-text BM25 search, and Supabase Storage for file downloads
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/supabase-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/supabase
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/supabase.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [pgvector Components](#pgvector-components)
  - [PGroonga Components](#pgroonga-components)
  - [Supabase Storage](#supabase-storage)
- [License](#license)

## Overview

[Supabase](https://supabase.com/) is an open-source Postgres platform. The `supabase-haystack` package provides three sets of components for building Haystack pipelines:

1. **pgvector** — dense embedding and keyword retrieval via the `pgvector` extension (pre-installed on Supabase).
2. **PGroonga** — full-text BM25 search via the `pgroonga` extension (no embeddings required).
3. **Supabase Storage** — download files from a Supabase Storage bucket into `ByteStream` objects ready for indexing.

The pgvector components are a thin wrapper around [`pgvector-haystack`](https://haystack.deepset.ai/integrations/pgvector-documentstore), inheriting all of its functionality: three vector similarity functions (`cosine_similarity`, `inner_product`, `l2_distance`), exact or HNSW search, metadata filtering, and keyword retrieval via PostgreSQL's `ts_rank_cd`. The two Supabase-specific defaults are that the connection string is read from `SUPABASE_DB_URL` and that `create_extension` is `False` (Supabase enables pgvector for you).

## Installation

```bash
pip install supabase-haystack
```

For the pgvector components, set the database connection string:

```bash
export SUPABASE_DB_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres"
```

For the PGroonga and Storage components, set the project URL and service role key:

```bash
export SUPABASE_SERVICE_KEY="<your-service-role-key>"
```

For local development, the [`docker-compose.yml`](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/supabase/docker-compose.yml) in the repo spins up a pgvector Postgres on `localhost:5432`.

## Usage

### pgvector Components

These components use Supabase Postgres with the `pgvector` extension for embedding-based and keyword retrieval.

- `SupabasePgvectorDocumentStore`: stores Haystack `Document` objects (content, embedding, metadata, optional blob) in a Postgres table, and handles writes, filtering, and both sync and async retrieval.
- `SupabasePgvectorEmbeddingRetriever`: dense Retriever that compares a query embedding against stored embeddings using the configured `vector_function` (`cosine_similarity`, `inner_product`, or `l2_distance`).
- `SupabasePgvectorKeywordRetriever`: keyword Retriever that scores documents with PostgreSQL's `ts_rank_cd`, considering term frequency, proximity, and section weight.

```python
from haystack import Document, Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy

from haystack_integrations.document_stores.supabase import SupabasePgvectorDocumentStore
from haystack_integrations.components.retrievers.supabase import SupabasePgvectorEmbeddingRetriever

document_store = SupabasePgvectorDocumentStore(
    table_name="haystack_documents",
    embedding_dimension=384,
    vector_function="cosine_similarity",
    recreate_table=True,
    search_strategy="hnsw",
)

documents = [
    Document(content="There are over 7,000 languages spoken around the world today."),
    Document(content="Elephants have been observed to recognize themselves in mirrors."),
    Document(content="Bioluminescent waves can be seen in the Maldives and Puerto Rico."),
]

indexing = Pipeline()
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"))
indexing.add_component("writer", DocumentWriter(
    document_store=document_store, policy=DuplicatePolicy.OVERWRITE))
indexing.connect("embedder", "writer")
indexing.run({"embedder": {"documents": documents}})

querying = Pipeline()
querying.add_component("text_embedder", SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"))
querying.add_component("retriever",
    SupabasePgvectorEmbeddingRetriever(document_store=document_store, top_k=3))
querying.connect("text_embedder.embedding", "retriever.query_embedding")

result = querying.run({"text_embedder": {"text": "How many languages are there?"}})
for doc in result["retriever"]["documents"]:
    print(doc.score, "—", doc.content)
```

For keyword or hybrid (dense + keyword) retrieval, swap in or combine `SupabasePgvectorKeywordRetriever` — it takes a `query` string directly and can be joined with the embedding retriever via `DocumentJoiner` using reciprocal rank fusion.

### PGroonga Components

These components use the [PGroonga](https://pgroonga.github.io/) PostgreSQL extension for fast, multilingual full-text BM25 search. No embeddings are required — retrieval works on plain text queries.

**Prerequisites:** enable the PGroonga extension in your Supabase project:

```sql
CREATE EXTENSION IF NOT EXISTS pgroonga;
```

- `SupabaseGroongaDocumentStore`: stores `Document` objects in a Postgres table with a PGroonga index on the content column. Supports both sync and async operations. Authenticates via `SUPABASE_SERVICE_KEY` and a project URL rather than a raw connection string.
- `SupabaseGroongaBM25Retriever`: full-text Retriever backed by `SupabaseGroongaDocumentStore`. Accepts a plain text `query` and returns ranked documents using PGroonga BM25 scoring. Supports both `run()` (sync) and `run_async()` (async).

```python
from haystack import Document, Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils import Secret

from haystack_integrations.document_stores.supabase import SupabaseGroongaDocumentStore
from haystack_integrations.components.retrievers.supabase import SupabaseGroongaBM25Retriever

document_store = SupabaseGroongaDocumentStore(
    supabase_url="https://<project-ref>.supabase.co",
    supabase_key=Secret.from_env_var("SUPABASE_SERVICE_KEY"),
    table_name="haystack_fts_documents",
    recreate_table=True,
)
document_store.warm_up()

documents = [
    Document(content="There are over 7,000 languages spoken around the world today."),
    Document(content="Elephants have been observed to recognize themselves in mirrors."),
    Document(content="Bioluminescent waves can be seen in the Maldives and Puerto Rico."),
]
document_store.write_documents(documents, policy=DuplicatePolicy.OVERWRITE)

retriever = SupabaseGroongaBM25Retriever(document_store=document_store, top_k=3)
result = retriever.run(query="languages spoken around the world")
for doc in result["documents"]:
    print(doc.score, "—", doc.content)
```

### Supabase Storage

- `SupabaseBucketDownloader`: downloads files from a Supabase Storage bucket and returns them as `ByteStream` objects. Each stream carries `meta["file_path"]` and `meta["bucket_name"]`. Supports optional extension filtering (e.g. `[".pdf", ".txt"]`). Designed to feed directly into document converters in indexing pipelines.

```python
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret

from haystack_integrations.components.downloaders.supabase import SupabaseBucketDownloader
from haystack_integrations.document_stores.supabase import SupabasePgvectorDocumentStore

document_store = SupabasePgvectorDocumentStore(
    table_name="haystack_documents",
    embedding_dimension=384,
)

indexing = Pipeline()
indexing.add_component("downloader", SupabaseBucketDownloader(
    supabase_url="https://<project-ref>.supabase.co",
    supabase_key=Secret.from_env_var("SUPABASE_SERVICE_KEY"),
    bucket_name="my-documents",
    file_extensions=[".pdf"],
))
indexing.add_component("converter", PyPDFToDocument())
indexing.add_component("writer", DocumentWriter(document_store=document_store))
indexing.connect("downloader.streams", "converter.sources")
indexing.connect("converter.documents", "writer.documents")

indexing.run({"downloader": {"sources": ["reports/q1.pdf", "reports/q2.pdf"]}})
```

## License

`supabase-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
