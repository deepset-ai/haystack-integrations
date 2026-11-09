---
layout: integration
name: wardowl
description: Permission-aware retrieval for Haystack. Returns only the documents the current user may read, using OpenFGA, SpiceDB, OPA, Cerbos, Cedar or access lists
authors:
  - name: Syed Muzakkir Hussain
    socials:
      github: muzakkirhussain011
pypi: https://pypi.org/project/wardowl/
repo: https://github.com/muzakkirhussain011/wardowl
type: Custom Component
report_issue: https://github.com/muzakkirhussain011/wardowl/issues
logo: /logos/wardowl.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

A RAG pipeline can pass the LLM a document the asking user is not allowed to read, because
retrieval ranks by similarity, not by permission. wardowl's `WardowlRetriever` retrieves through
a permission check: where the permission system can describe what a user may read as a filter,
the filter runs inside the store's search; every hit is checked again; and an error from the
permission service stops the run instead of returning unfiltered documents.

It works with any wardowl backend (pgvector, Qdrant, Milvus, Weaviate, Elasticsearch, OpenSearch,
Redis, LanceDB, Chroma, FAISS, Pinecone, MongoDB Atlas, Vespa, Cassandra) and permission system
(OpenFGA, SpiceDB, OPA, Cerbos, Cedar, Casbin, Ory Keto, or access lists stored on the chunks).

## Installation

```bash
pip install "wardowl[haystack]"
```

## Usage

### Components

- `WardowlRetriever`: inputs `query`, `subject` (the authenticated user), and optional `top_k` and
  `query_embedding`; outputs `documents` and `complete`. One pipeline serves every user.
- `BoundWardowlRetriever`: the same, with the user taken from a function you pass (for example one
  reading your web framework's request context), so neither a caller nor a model can name another
  user.

### Use wardowl in a pipeline

```python
from haystack import Pipeline

from wardowl import Document, InMemoryBackend, MetadataACLAuthorizer, PermissionedRetriever, Subject
from wardowl.haystack import WardowlRetriever

backend = InMemoryBackend(
    [
        Document("handbook", "Annual leave is 25 days.", {"allowed_groups": ["*"]}),
        Document("salaries", "Salary bands for 2026 ...", {"allowed_groups": ["hr"]}),
    ]
)
pipeline = Pipeline()
pipeline.add_component("retriever", WardowlRetriever(PermissionedRetriever(backend, MetadataACLAuthorizer())))

result = pipeline.run({"retriever": {"query": "leave salary bands", "subject": Subject("bob", groups=["engineering"])}})
print([doc.id for doc in result["retriever"]["documents"]])  # ['handbook']
```

`InMemoryBackend` and `MetadataACLAuthorizer` keep the example self-contained; in production they
are your vector store and permission system. Building the subject from your session, and using the
component as an agent tool, are covered in the
[Haystack guide](https://muzakkirhussain011.github.io/wardowl/integrations/haystack.html).

### License

`wardowl` is distributed under the terms of the
[MIT](https://github.com/muzakkirhussain011/wardowl/blob/main/LICENSE) license.
