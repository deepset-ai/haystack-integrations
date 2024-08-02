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
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/unstructured.svg
version: Haystack 2.0
toc: true
---
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Connecting to the Unstructured API](#connecting-to-the-unstructured-api)
    - [Hosted API](#hosted-api)
    - [Local API (Docker)](#local-api-docker)
  - [Running Unstructured File Converter](#running-unstructured-file-converter)
    - [In isolation](#in-isolation)
    - [In a Haystack Pipeline](#in-a-haystack-pipeline)



## Overview
Component for the Haystack (2.x) LLM framework to convert files and directories into Documents using the Unstructured API.

**[Unstructured](https://unstructured-io.github.io/unstructured/index.html)** provides ETL tools for LLMs, extracting text and other information from various file formats. See [supported file types](https://docs.unstructured.io/api-reference/api-services/overview#supported-file-types) for more details.

## Installation
To install the [Unstructured File Converter](https://docs.haystack.deepset.ai/docs/unstructuredfileconverter), run:

```bash
pip install unstructured-fileconverter-haystack
```

## Usage

### Connecting to the Unstructured API
#### Hosted API

The Unstructured API is available in both free and paid versions: Unstructured Serverless API or Free Unstructured API.

For the Free Unstructured API, the API URL is `https://api.unstructured.io/general/v0/general`. For the Unstructured Serverless API, find your unique API URL in your Unstructured account.

Note that the API keys for free and paid versions are not interchangeable.

Set the Unstructured API key as an environment variable:
```bash
export UNSTRUCTURED_API_KEY=your_api_key
```

#### Local API (Docker)
You can run a local instance of the Unstructured API using Docker:

```bash
docker run -p 8000:8000 -d --rm --name unstructured-api quay.io/unstructured-io/unstructured-api:latest --port 8000 --host 0.0.0.0
```

When initializing the component, specify the localhost URL:
```python
from haystack_integrations.components.converters.unstructured import UnstructuredFileConverter

converter = UnstructuredFileConverter(api_url="http://localhost:8000/general/v0/general")
```

### Running Unstructured File Converter
#### In isolation
```python
import os
from haystack_integrations.components.converters.unstructured import UnstructuredFileConverter

converter = UnstructuredFileConverter()
documents = converter.run(paths = ["a/file/path.pdf", "a/directory/path"])["documents"]
```

#### In a Haystack Pipeline
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