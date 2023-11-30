---
layout: integration
name: OpenSearch Document Store
description: A Document Store for storing and retrieval from OpenSearch - built for Haystack 2.0.
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
        linkedin: deepset-ai
pypi: https://pypi.org/project/opensearch-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opensearch
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/opensearch.png
version: Haystack 2.0
---
# OpenSearch Document Store for Haystack

[![PyPI - Version](https://img.shields.io/pypi/v/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opensearch-haystack.svg)](https://pypi.org/project/opensearch-haystack)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/opensearch.yml)

-----

**Table of Contents**

- [OpenSearch Document Store for Haystack](#opensearch-document-store-for-haystack)
  - [Installation](#installation)
  - [License](#license)

## Installation
Use `pip` to install OpenSearch:

```console
pip install opensearch-haystack
```
## Usage
Once installed, initialize your OpenSearch database to use it with Haystack 2.0:

```python
from opensearch_haystack import OpenSearchDocumentStore

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

## License

`opensearch-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
