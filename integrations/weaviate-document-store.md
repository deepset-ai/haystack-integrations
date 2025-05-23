---
layout: integration
name: Weaviate
description: Use a Weaviate database with Haystack
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/weaviate-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/weaviate
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/weaviate.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/weaviate-haystack.svg)](https://pypi.org/project/weaviate-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/weaviate-haystack.svg)](https://pypi.org/project/weaviate-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/weaviate.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/weaviate.yml)

---

## Installation

Use `pip` to install Weaviate:

```console
pip install weaviate-haystack
```

## Usage

Once installed, initialize your Weaviate database to use it with Haystack.

In this example, we use the temporary embedded version for simplicity.
To use a self-hosted Docker container or Weaviate Cloud Service, take a look at the [docs](https://docs.haystack.deepset.ai/docs/weaviatedocumentstore).

```python
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from weaviate.embedded import EmbeddedOptions

document_store = WeaviateDocumentStore(embedded_options=EmbeddedOptions())
```

### Writing Documents to WeaviateDocumentStore

To write documents to `WeaviateDocumentStore`, create an indexing pipeline.

```python
from haystack.components.file_converters import TextFileToDocument
from haystack.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"paths": file_paths}})
```

### License

`weaviate-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
