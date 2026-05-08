---
layout: integration
name: Docling Serve
description: Use DoclingServe to convert PDF, DOCX, HTML, and other document types to Haystack Documents via a remote HTTP server, with no local ML dependencies
authors:
    - name: deepset
      socials:
        github: deepset-ai
pypi: https://pypi.org/project/docling-serve-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/docling_serve
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/docling.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[DoclingServe](https://github.com/docling-project/docling-serve) hosts [Docling](https://github.com/DS4SD/docling)
as a scalable HTTP server, supporting PDFs, Office documents, HTML, and many other formats.

This integration introduces `DoclingServeConverter`, a Haystack component that sends documents to a running
DoclingServe instance and returns Haystack `Document` objects. Unlike the local `DoclingConverter`, this
component has no heavy ML dependencies — all document parsing happens on the remote server.

## Installation

```bash
pip install docling-serve-haystack
```

Start a DoclingServe instance locally (requires Docker):

```bash
docker run -p 5001:5001 ghcr.io/docling-project/docling-serve-cpu:latest
```

## Usage

### Components

This integration introduces `DoclingServeConverter`, a component which converts documents by sending them
to a DoclingServe HTTP server and returns Haystack `Document` objects.

Local files and `ByteStream` objects are uploaded via the `/v1/convert/file` endpoint. URL strings are
sent to `/v1/convert/source`.

The component supports three export modes via the `export_type` parameter:

- `ExportType.MARKDOWN` (default): Returns document content as a Markdown string.
- `ExportType.TEXT`: Returns plain text extracted from the document.
- `ExportType.JSON`: Returns the full Docling document representation as a JSON string.

### Standalone

```python
from haystack_integrations.components.converters.docling_serve import (
    DoclingServeConverter,
)

# Default: Markdown output
converter = DoclingServeConverter(base_url="http://localhost:5001")
result = converter.run(sources=["https://arxiv.org/pdf/2206.01062"])
documents = result["documents"]
print(documents[0].content[:200])
```

### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.docling_serve import (
    DoclingServeConverter,
)

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component(
    "converter",
    DoclingServeConverter(base_url="http://localhost:5001"),
)
pipeline.add_component("splitter", DocumentSplitter())
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("converter", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["report.pdf", "manual.docx"]}})
```

### License

`docling-serve-haystack` is distributed under the terms of the Apache-2.0 license.
