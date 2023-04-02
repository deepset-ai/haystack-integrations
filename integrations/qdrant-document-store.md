---
name: Qdrant Document Store
description: Use the Qdrant vector database with Haystack
authors:
    - name: Qdrant 
      socials:
        github: qdrant
        twitter: qdrant_engine
pypi: https://pypi.org/project/qdrant-haystack/
repo: https://github.com/qdrant/qdrant-haystack
type: Document Store
report_issue: https://github.com/qdrant/qdrant-haystack/issues
---

An integration of [Qdrant](https://qdrant.tech) vector database with [Haystack](https://haystack.deepset.ai/)
by [deepset](https://www.deepset.ai).

The library finally allows using Qdrant as a document store, and provides an in-place replacement
for any other vector embeddings store. Thus, you should expect any kind of application to be working
smoothly just by changing the provider to `QdrantDocumentStore`.

## Installation

`qdrant-haystack` might be installed as any other Python library, using pip or poetry:

```bash
pip install qdrant-haystack
```

```bash
poetry add qdrant-haystack
```

## Usage

Once installed, you can already start using `QdrantDocumentStore` as any other store that supports
embeddings.

```python
from qdrant_haystack import QdrantDocumentStore

document_store = QdrantDocumentStore(
    url="localhost",
    index="Document",
    embedding_dim=512,
    recreate_index=True,
    hnsw_config={"m": 16, "ef_construct": 64}  # Optional
)
```

The list of parameters accepted by `QdrantDocumentStore` is complementary to those used in the
official [Python Qdrant client](https://github.com/qdrant/qdrant_client).

### Connecting to Qdrant Cloud cluster

If you prefer not to manage your own Qdrant instance, [Qdrant Cloud](https://cloud.qdrant.io/)
might be a better option.

```python
from qdrant_haystack import QdrantDocumentStore

document_store = QdrantDocumentStore(
    url="https://YOUR-CLUSTER-URL.aws.cloud.qdrant.io",
    index="Document",
    api_key="<< YOUR QDRANT CLOUD API KEY >>",
    embedding_dim=512,
    recreate_index=True,
)
```

There is no difference in terms of functionality between local instances and cloud clusters.