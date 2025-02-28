---
layout: integration
name: OpenSearch
description: A Document Store for storing and retrieval from OpenSearch
authors:
    - name: Thomas Stadelmann
      socials:
        github: tstadel
    - name: Julian Risch
      socials:
        github: julian-risch
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/opensearch-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opensearch
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/opensearch.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml)

-----

## Installation
Use `pip` to install OpenSearch:

```console
pip install opensearch-haystack
```
## Usage
Once installed, initialize your OpenSearch database to use it with Haystack:

```python
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore

document_store = OpenSearchDocumentStore()
```

### Writing Documents to OpenSearchDocumentStore
To write documents to `OpenSearchDocumentStore`, create an indexing pipeline.

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

`opensearch-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
