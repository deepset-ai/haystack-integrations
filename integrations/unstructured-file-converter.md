---
layout: integration
name: Unstructured File Converter
description: Component to easily convert files and directories into Documents using the Unstructured API
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/unstructured-fileconverter-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/unstructured
type: Custom Node
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/unstructured.svg
version: Haystack 2.0
---

Component for the Haystack (2.x) LLM framework to easily convert files and directories into Documents using the Unstructured API.

**[Unstructured](https://unstructured-io.github.io/unstructured/index.html)** provides a series of tools to do **ETL for LLMs**. This component calls the Unstructured API that simply extracts text and other information from a vast range of file formats. See [supported file types](https://unstructured-io.github.io/unstructured/api.html#supported-file-types).

## Installation

```bash
pip install unstructured-fileconverter-haystack
```

### Hosted API
If you plan to use the hosted version of the Unstructured API, you just need the **(free) Unsctructured API key**. You can get it by signing up [here](https://unstructured.io/api-key-free).

### Local API (Docker)
If you want to run your own local instance of the Unstructured API, you need Docker and you can find instructions [here](https://unstructured-io.github.io/unstructured/api.html#using-docker-images).

In short, this should work:
```bash
docker run -p 8000:8000 -d --rm --name unstructured-api quay.io/unstructured-io/unstructured-api:latest --port 8000 --host 0.0.0.0
```

## Usage

Set the Unstructured API key as an environment variable `UNSTRUCTURED_API_KEY`:
```bash
export UNSTRUCTURED_API_KEY=your_api_key
```

### In isolation
```python
import os
from haystack_integrations.components.converters.unstructured import UnstructuredFileConverter

converter = UnstructuredFileConverter()
documents = converter.run(paths = ["a/file/path.pdf", "a/directory/path"])["documents"]
```

### In a Haystack Pipeline
```python
import os
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.unstructured import UnstructuredFileConverter

document_store = InMemoryDocumentStore()

indexing = Pipeline()
indexing.add_component("converter", UnstructuredFileConverter())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")

indexing.run({"converter": {"paths": ["a/file/path.pdf", "a/directory/path"]}})
```