---
layout: integration
name: Supabase
description: Use Supabase Postgres (with pgvector) as a Document Store for Haystack
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
- [License](#license)

## Overview

[Supabase](https://supabase.com/) is an open-source Postgres platform with the `pgvector` extension pre-installed. The `supabase-haystack` package lets you use a Supabase database as a [Document Store](https://docs.haystack.deepset.ai/docs/document-store) in a Haystack pipeline, with both dense embedding retrieval and keyword retrieval.

It's a thin wrapper around [`pgvector-haystack`](https://haystack.deepset.ai/integrations/pgvector-documentstore), so it inherits all of its functionality: three vector similarity functions (`cosine_similarity`, `inner_product`, `l2_distance`), exact or HNSW search, metadata filtering, and keyword retrieval via PostgreSQL's `ts_rank_cd`. The two Supabase-specific defaults are that the connection string is read from `SUPABASE_DB_URL` and that `create_extension` is `False` (Supabase enables pgvector for you).

## Installation

```bash
pip install supabase-haystack
```

```bash
export SUPABASE_DB_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres"
```

For local development, the [`docker-compose.yml`](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/supabase/docker-compose.yml) in the repo spins up a pgvector Postgres on `localhost:5432`.

## Usage

### Components

- `SupabasePgvectorDocumentStore`: stores Haystack `Document` objects (content, embedding, metadata, optional blob) in a Postgres table, and handles writes, filtering, and both sync and async retrieval.
- `SupabasePgvectorEmbeddingRetriever`: dense Retriever that compares a query embedding against stored embeddings using the configured `vector_function`.
- `SupabasePgvectorKeywordRetriever`: keyword Retriever that scores documents with PostgreSQL's `ts_rank_cd`, considering term frequency, proximity, and section weight.

### Example

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

## License

`supabase-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.