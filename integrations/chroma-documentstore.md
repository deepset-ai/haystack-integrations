---
layout: integration
name: Chroma
description: A Document Store for storing and retrieval from Chroma
authors:
  - name: Massimiliano Pippi
    socials:
      github: masci
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: https://pypi.org/project/chroma-store
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/chroma
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/chroma.png
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/chroma-haystack.svg)](https://pypi.org/project/chroma-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/chroma-haystack.svg)](https://pypi.org/project/chroma-haystack)
[![test](https://github.com/masci/chroma-haystack/actions/workflows/test.yml/badge.svg)](https://github.com/masci/chroma-haystack/actions/workflows/test.yml)

-----

**Table of Contents**

- [Chroma Document Store for Haystack](#chroma-document-store-for-haystack)
  - [Installation](#installation)
  - [Examples](#examples)
  - [License](#license)

## Installation
Use `pip` to install Chroma:

```console
pip install chroma-haystack
```
## Usage
Once installed, initialize your Chroma database to use it with Haystack 2.0:

```python
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

# Chroma is used in-memory so we use the same instances in the two pipelines below
document_store = ChromaDocumentStore()
```

### Writing Documents to ChromaDocumentStore
To write documents to `ChromaDocumentStore`, create an indexing pipeline.

```python
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"sources": file_paths}})
```

## Examples
You can find a code example showing how to use the Document Store and the Retriever under the `example/` folder of [this repo](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/chroma).

## License

`chroma-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
