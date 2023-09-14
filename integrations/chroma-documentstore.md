---
layout: integration
name: Chroma Document Store
description: A Document Store for storing and retrieval from Chroma - built for Haystack 2.0
authors:
  - name: Massimiliano Pippi
    socials:
      github: masci
pypi: https://pypi.org/project/chroma-store
repo: https://github.com/masci/chroma-haystack
type: Document Store
report_issue: https://github.com/masci/chroma-haystack/issues
logo: /logos/chroma.png
version: Haystack 2.0
---
# Chroma Document Store for Haystack

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

```console
pip install chroma-haystack
```
## Usage
Once installed, you can start using your Chroma database with Haystack 2.0 by initializing it:

```python
from chroma_haystack import ChromaDocumentStore

# Chroma is used in-memory so we use the same instances in the two pipelines below
document_store = ChromaDocumentStore()
```

### Writing Documents to ChromaDocumentStore
To write documents to `ChromaDocumentStore`, create an indexing pipeline.

```python
from haystack.preview.components.file_converters import TextFileToDocument
from haystack.preview.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"paths": file_paths}})
```

## Examples
You can find a code example showing how to use the Document Store and the Retriever under the `example/` folder of this repo or in [this Colab](https://colab.research.google.com/drive/1YpDetI8BRbObPDEVdfqUcwhEX9UUXP-m?usp=sharing).

## License

`chroma-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
