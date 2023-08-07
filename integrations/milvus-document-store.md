---
layout: integration
name: Milvus Document Store
description: Use the Milvus vector database with Haystack
authors:
    - name: Zilliz 
      socials:
        github: zilliztech
        twitter: zilliz_universe
pypi: https://pypi.org/project/milvus-haystack/
repo: https://github.com/deepset-ai/milvus-haystack
type: Document Store
report_issue: https://github.com/deepset-ai/milvus-haystack/issues
logo: /logos/milvus.png
---

An integration of [Milvus](https://milvus.io/) vector database with [Haystack](https://haystack.deepset.ai/).

Use Milvus as storage for Haystack pipelines as `MilvusDocumentStore`.

## Installation

```bash
pip install milvus-haystack
```

## Usage

Once installed, you can import and use the `MilvusDocumentStore` as follows

```python
from milvus_haystack import MilvusDocumentStore
from haystack import Document

document_store = MilvusDocumentStore()
document_store.write_documents([Document("Some Content")])
document_store.get_all_documents()  # prints [<Document: {'content': 'foo', 'content_type': 'text', ...>]
```