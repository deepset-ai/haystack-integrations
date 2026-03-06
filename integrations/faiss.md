---
layout: integration
name: FAISS
description: A Document Store for vector search using FAISS
authors:
  - name: Guna Palanivel
    socials:
      github: GunaPalanivel
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/faiss-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/faiss
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/meta.png
version: Haystack 2.0
toc: true
---

The integration provides `FAISSDocumentStore`, which uses [FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search) for vector search and a simple JSON file for metadata storage. It is suitable for small to medium-sized datasets where simplicity is preferred over scalability, and supports optional persistence by saving the FAISS index to a `.faiss` file and documents to a `.json` file. Use `FAISSEmbeddingRetriever` for semantic retrieval in your pipelines.

## Installation

Install the package with pip:

```bash
pip install faiss-haystack
```

For GPU-accelerated FAISS, install `faiss-gpu` separately and use it in place of the default `faiss-cpu` dependency where applicable.

The examples below use [Sentence Transformers](https://www.sbert.net/) for embeddings. Install with: `pip install "sentence-transformers>=5.0.0"`.

## Usage

### In-memory document store

Create an in-memory document store (no persistence):

```python
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

document_store = FAISSDocumentStore(embedding_dim=768)
```

### Persisted document store

To save and load the index and documents from disk, pass `index_path`:

```python
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

document_store = FAISSDocumentStore(
    index_path="./my_faiss_index",
    index_string="Flat",
    embedding_dim=768,
)
# After writing documents, persist with:
# document_store.save("./my_faiss_index")
# Later, create the store with the same index_path to load from disk.
```

### Writing documents

Use an indexing pipeline to write documents (with embeddings) to the store.
This example uses Sentence Transformers (768 dimensions).

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

document_store = FAISSDocumentStore(
    index_path="./my_faiss_index",
    index_string="Flat",
    embedding_dim=768,
)

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "embedder")
indexing.connect("embedder", "writer")
indexing.run({"converter": {"sources": file_paths}})

# If using persistence, save after indexing
# document_store.save("./my_faiss_index")
```

### Retrieval with FAISSEmbeddingRetriever

Build a query pipeline using `FAISSEmbeddingRetriever` for semantic search:

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.faiss import FAISSEmbeddingRetriever

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
query_pipeline.add_component(
    "retriever",
    FAISSEmbeddingRetriever(document_store=document_store, top_k=10),
)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

results = query_pipeline.run({"text_embedder": {"text": "your query"}})
documents = results["retriever"]["documents"]
```

### Fixing OpenMP Runtime Conflicts on macOS 

#### Symptoms

You may encounter one or both of the following errors at runtime:

```
OMP: Error #15: Initializing libomp.dylib, but found libomp.dylib already initialized.
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program.
```

```
resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown
```

If setting `OMP_NUM_THREADS=1` prevents the crash, the root cause is **multiple OpenMP runtimes loaded simultaneously**. Each runtime maintains its own thread pool and thread-local storage (TLS). When two runtimes spin up worker threads at the same time, they corrupt each other's memory — causing segfaults at `N > 1` threads.

---

#### Diagnosis

First, find how many copies of `libomp.dylib` exist in your virtual environment:

```bash
find /path/to/your/.venv -name "libomp.dylib" 2>/dev/null
```

If you see more than one, e.g.:

```
.venv/lib/pythonX.Y/site-packages/torch/lib/libomp.dylib
.venv/lib/pythonX.Y/site-packages/sklearn/.dylibs/libomp.dylib
.venv/lib/pythonX.Y/site-packages/faiss/.dylibs/libomp.dylib
```

you need to consolidate them into a single runtime.

---

#### Fix

The solution is to pick one canonical `libomp.dylib` (torch's is a good choice) and replace all other copies with symlinks pointing to it.

For each duplicate, delete the copy and replace it with a symlink:

```bash
# Delete the duplicate
rm /path/to/.venv/lib/pythonX.Y/site-packages/<package>/.dylibs/libomp.dylib

# Replace with a symlink to the canonical copy
ln -s /path/to/.venv/lib/pythonX.Y/site-packages/torch/lib/libomp.dylib \
      /path/to/.venv/lib/pythonX.Y/site-packages/<package>/.dylibs/libomp.dylib
```

Repeat for every duplicate found. Because these packages use `@loader_path`-relative references to load `libomp.dylib`, the symlink will be transparently resolved to the single canonical runtime at load time.

---

#### Verify

After applying the fix, confirm only one unique `libomp.dylib` is being referenced:

```bash
find /path/to/your/.venv -name "*.so" | xargs otool -L 2>/dev/null | grep libomp | sort -u
```

All entries should resolve to the same canonical path. You should now be able to run without `OMP_NUM_THREADS=1`.



## License

`faiss-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
