---
layout: integration
name: Marqo Document Store
description: A Document Store for storing and retrieval from Marqo - built for Haystack 2.0
authors:
  - name: marqo-ai
    socials:
      github: marqo-ai
pypi: https://pypi.org/project/marqo-haystack/
repo: https://github.com/marqo-ai/marqo-haystack
type: Document Store
report_issue: https://github.com/marqo-ai/marqo-haystack/issues
logo: /logos/marqo.png
version: Haystack 2.0
---
# Marqo Document Store for Haystack
This integration allows you to use [Marqo DB](https://www.marqo.ai/) as the document store for your Haystack pipelines. This page provides simple instructions on how to start it up and how to initialize a `MarqoDocumentStore` that can be used in any Haystack 2.0 pipeline.

## Installation

```console
pip install marqo-haystack
```
## Usage

Once installed, you can start using your Marqo database with Haystack 2.0. The `MarqoDocumentStore` is compatible with the open-source Marqo Docker container and with the Marqo managed cloud offering.

### Getting Started Locally with the Marqo Docker Container

#### For x86 machines
```bash
docker pull marqoai/marqo:latest
docker rm -f marqo
docker run --name marqo -it --privileged -p 8882:8882 --add-host host.docker.internal:host-gateway marqoai/marqo:latest
```
#### For M1/M2 ARM machines
```bash
docker rm -f marqo-os; docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" marqoai/marqo-os:0.0.3-arm
```

Next, in a new terminal:
```bash
docker rm -f marqo; docker run --name marqo --privileged \
    -p 8882:8882 --add-host host.docker.internal:host-gateway \
    -e "OPENSEARCH_URL=https://localhost:9200" \
    marqoai/marqo:latest
```

### Getting started with Marqo Cloud

Log in or create an account at [https://cloud.marqo.ai](https://cloud.marqo.ai). Create a new index with the indexing mode set as "Text-optimised".

### Initializing a MarqoDocumetStore in Haystack

```python
from marqo_haystack import MarqoDocumentStore
 
document_store = MarqoDocumentStore()
```

If you are using the Docker container then this will use an index called `documents`, if it doesn't exist then it will be created.

If you are using Marqo cloud then you can connect to an existing index like so:

```python
from marqo_haystack import MarqoDocumentStore
 
document_store = MarqoDocumentStore(
    url="https://api.marqo.ai",
    api_key="XXXXXXXXXXXXX",
    collection_name="my-cloud-index"
)
```

### Writing Documents to MarqoDocumentStore
To write documents to `MarqoDocumentStore`, create an indexing pipeline.

```python
from haystack.preview.components.file_converters import TextFileToDocument
from haystack.preview.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"paths": file_paths}})
```

### Using the MarqoRetriever
To retrieve documents from your Marqo document store, create a querying pipeline.

To send a single query use the `MarqoSingleRetriever`:

```python
from marqo_haystack.retriever import MarqoSingleRetriever

querying = Pipeline()
querying.add_component("retriever", MarqoSingleRetriever(document_store))
results = querying.run({"retriever": {"query": "Who is Marco Polo?", "top_k": 3}})
```

To send a list of queries use the `MarqoRetriever`:

```python
from marqo_haystack.retriever import MarqoRetriever

querying = Pipeline()
querying.add_component("retriever", MarqoRetriever(document_store))
results = querying.run({"retriever": {"queries": ["Who is Marco Polo?", "Can Hippos swim?"], "top_k": 3}})
```

