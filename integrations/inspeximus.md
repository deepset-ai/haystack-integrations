---
layout: integration
name: Inspeximus
description: A persistent DocumentStore with a correction channel — supersede, revert, and receipted erasure
authors:
    - name: Inspeximus
      socials:
        github: DanceNitra
pypi: https://pypi.org/project/inspeximus/
repo: https://github.com/DanceNitra/inspeximus
type: Document Store
report_issue: https://github.com/DanceNitra/inspeximus/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Inspeximus](https://github.com/DanceNitra/inspeximus) is an MIT-licensed, zero-dependency agent-memory
library. `InspeximusDocumentStore` implements Haystack's `DocumentStore` protocol, so it slots into any
Haystack pipeline the way `InMemoryDocumentStore` does — with two differences that matter for long-running
or regulated systems:

- **It persists.** The store is a file on disk; reopening it returns the same documents, rather than
  starting empty each process.
- **Its delete leaves nothing behind.** `delete_documents` removes the value from the bytes on disk, and
  with receipts enabled it writes a signed, content-free tombstone — so a deletion made for a data-subject
  request is provable, not merely done.

It is a faithful drop-in: duplicate policies (`SKIP`, `OVERWRITE`, `NONE`, `FAIL`) behave exactly as they
do in `InMemoryDocumentStore`, and filtering reuses Haystack's own `document_matches_filter`, so a
`FilterRetriever` and pipeline serialization work unchanged. That parity is verified in CI, operation by
operation, against `InMemoryDocumentStore`, with a falsification control that must fail.

## Installation

```bash
pip install "inspeximus[haystack]"
```

## Usage

### Components

This integration provides one component:

- `InspeximusDocumentStore`: a persistent `DocumentStore` you can pass to any store-agnostic retriever
  (for example `FilterRetriever`) or to indexing components (`DocumentWriter`).

### Write and retrieve

```python
from haystack import Pipeline
from haystack.dataclasses import Document
from haystack.components.retrievers import FilterRetriever
from haystack.components.writers import DocumentWriter
from inspeximus.integrations.haystack import InspeximusDocumentStore

store = InspeximusDocumentStore(path="documents.json")

# Index some documents.
indexing = Pipeline()
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.run({"writer": {"documents": [
    Document(content="the invoice is due in March", meta={"kind": "invoice"}),
    Document(content="the manager is Rachel Tseng", meta={"kind": "person"}),
]}})

# Retrieve with a metadata filter.
retrieval = Pipeline()
retrieval.add_component("retriever", FilterRetriever(document_store=store))
result = retrieval.run({"retriever": {
    "filters": {"field": "meta.kind", "operator": "==", "value": "invoice"}
}})
print([d.content for d in result["retriever"]["documents"]])
# ['the invoice is due in March']
```

### Provable erasure

```python
# Remove a document and get back the erasure record; with receipts enabled it is a signed tombstone.
store.erase_documents(["<document-id>"], request_id="dsr-2026-04-01")
```

## License

`inspeximus` is distributed under the MIT license.
