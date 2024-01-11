---
layout: integration
name: Qdrant
description: Use the Qdrant vector database with Haystack
authors:
  - name: Qdrant
    socials:
      github: qdrant
      twitter: qdrant_engine
pypi: https://pypi.org/project/qdrant-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/qdrant
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/qdrant.png
version: Haystack 2.0
toc: true
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

## Installation (1.x)

Latest versions of `qdrant-haystack` are compatible only with Haystack 2.x.
If you're using Haystack 1.x you need to specify the version explicitly.

```bash
pip install "qdrant-haystack<2.0.0"
```

```bash
poetry add "qdrant-haystack<2.0.0"
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

### Using local in-memory / disk-persisted mode

Qdrant Python client, from version 1.1.1, supports local in-memory/disk-persisted mode. That's
a good choice for any test scenarios and quick experiments in which you do not plan to store
lots of vectors. In such a case spinning a Docker container might be even not required.

The local mode was also implemented in `qdrant-haystack` integration.

#### In-memory storage

In case you want to have a transient storage, for example in case of automated tests launched
during your CI/CD pipeline, using Qdrant Local mode with in-memory storage might be a preferred
option. It might be simply enabled by passing `:memory:` as first parameter, while creating an
instance of `QdrantDocumentStore`.

```python
from qdrant_haystack import QdrantDocumentStore

document_store = QdrantDocumentStore(
    ":memory:",
    index="Document",
    embedding_dim=512,
    recreate_index=True,
    hnsw_config={"m": 16, "ef_construct": 64}  # Optional
)
```

#### On disk storage

However, if you prefer to keep the vectors between different runs of your application, it
might be better to use on disk storage and pass the path that should be used to persist
the data.

```python
from qdrant_haystack import QdrantDocumentStore

document_store = QdrantDocumentStore(
    path="/home/qdrant/storage_local",
    index="Document",
    embedding_dim=512,
    recreate_index=True,
    hnsw_config={"m": 16, "ef_construct": 64}  # Optional
)
```

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
