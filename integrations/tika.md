---
layout: integration
name: Apache Tika
description: Convert files of different types (PDF, DOCX, HTML, and more) to Documents using Apache Tika
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/tika-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/tika
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/tika.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `tika-haystack` integration provides [`TikaDocumentConverter`](https://docs.haystack.deepset.ai/docs/tikadocumentconverter), a component that converts files of different types (PDF, DOCX, HTML, RTF, and many others) into Haystack `Document` objects using [Apache Tika](https://tika.apache.org/).

Apache Tika is a content analysis toolkit that detects and extracts metadata and text from many file formats. The component requires a running Tika server to parse documents.

This component was previously part of Haystack core and now lives in the `tika-haystack` integration package, maintained in [haystack-core-integrations](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/tika).

## Installation

Install the `tika-haystack` package:

```bash
pip install tika-haystack
```

This integration requires a running Tika server. The easiest way to start one is with Docker:

```bash
docker run -d -p 127.0.0.1:9998:9998 apache/tika:latest
```

For more options, see the [Tika Docker documentation](https://github.com/apache/tika-docker/blob/main/README.md#usage).

## Usage

### On its own

```python
from haystack_integrations.components.converters.tika import TikaDocumentConverter
from pathlib import Path

converter = TikaDocumentConverter()
result = converter.run(sources=[Path("sample.docx"), Path("report.pdf")])
documents = result["documents"]

print(documents[0].content)
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.converters.tika import TikaDocumentConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", TikaDocumentConverter())
pipeline.add_component("cleaner", DocumentCleaner())
pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("converter", "cleaner")
pipeline.connect("cleaner", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["document.pdf", "report.docx"]}})
```

By default, the component connects to a Tika server at `http://localhost:9998/tika`. Use the `tika_url` parameter to point to a different server:

```python
converter = TikaDocumentConverter(tika_url="http://my-tika-server:9998/tika")
```

## License

`tika-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
