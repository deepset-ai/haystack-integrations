---
layout: integration
name: NeedToKnow
description: Permission-aware retrieval that drops documents a user is not allowed to see
authors:
    - name: Sanoer Soni
      socials:
        github: Sanoer11
repo: https://github.com/Sanoer11/needtoknow-haystack
type: Custom Component
report_issue: https://github.com/Sanoer11/needtoknow-haystack/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

RAG pipelines usually retrieve from one shared index, and retrieval ranks by relevance, not by who is asking. Without access control, a user who asks "What are the salary bands?" can get HR documents back, and whatever the retriever returns reaches the LLM prompt.

`needtoknow-haystack` adds `AccessFilter`, a component that sits after any retriever and removes documents the requesting user may not read, based on per-document metadata:

- `allowed_users`: user IDs that may read the document
- `allowed_groups`: groups that may read the document
- an optional public flag for documents everyone may read

It is store-agnostic and fails closed: documents without access metadata are denied by default, and an empty `user_id` raises an error.

On the package's offline benchmark (5 users × 10 probing queries, BM25 top-5, Haystack 3.4.1), 58% of retrieved documents leaked across departments without the filter and none leaked with it.

## Installation

```bash
pip install git+https://github.com/Sanoer11/needtoknow-haystack.git
```

## Usage

### Components

This integration introduces one component:

- `AccessFilter`: keeps only the documents the requesting user (or one of their groups) may read, and reports how many were removed.

### Filter retrieved documents per user

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from needtoknow_haystack import AccessFilter

store = InMemoryDocumentStore()
store.write_documents(
    [
        Document(content="Q3 salary bands for engineering", meta={"allowed_groups": ["hr"]}),
        Document(content="Engineering onboarding guide", meta={"allowed_groups": ["engineering"]}),
        Document(content="Company holiday calendar", meta={"public": True}),
        Document(content="Alice's performance review", meta={"allowed_users": ["alice"]}),
    ]
)

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=store, top_k=20))
pipeline.add_component("access_filter", AccessFilter(public_field="public", top_k=5))
pipeline.connect("retriever.documents", "access_filter.documents")

result = pipeline.run(
    {
        "retriever": {"query": "salary bands, onboarding guide, holiday calendar and performance review"},
        "access_filter": {"user_id": "bob", "groups": ["engineering"]},
    }
)

for doc in result["access_filter"]["documents"]:
    print(doc.content)
print("denied:", result["access_filter"]["denied_count"])
```

Bob is in `engineering`, so he gets the onboarding guide and the public calendar, and the HR salary document and Alice's review are removed.

Filtering happens after retrieval, so ask the retriever for more candidates than you need (`top_k=20`) and let `AccessFilter(top_k=5)` trim the allowed ones.

When loading a saved pipeline in Haystack 3, allow the module: `Pipeline.loads(yaml_text, allowed_modules=["needtoknow_haystack"])`.

### License

`needtoknow-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
