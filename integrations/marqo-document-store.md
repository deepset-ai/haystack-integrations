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

Once installed, you can start using your Marqo database with Haystack 2.0 by first starting a Marqo Docker container, and then initializing a `MarqoDocumentStore`

### Starting a Marqo Docker Container

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

### Initializing a MarqoDocumetStore in Haystack

```python
from marqo_haystack import MarqoDocumentStore
 
document_store = MarqoDocumentStore()

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
