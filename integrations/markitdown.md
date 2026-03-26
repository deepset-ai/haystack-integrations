---
layout: integration
name: MarkItDown
description: Use Microsoft's MarkItDown to locally convert PDF, DOCX, PPTX, XLSX, HTML, images, and more into Markdown in Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/markitdown-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/markitdown
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[MarkItDown](https://github.com/microsoft/markitdown) is a Python library by Microsoft for converting various file formats into Markdown. It supports a wide range of formats including PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), HTML, images, and more — all processed locally.

This integration provides a `MarkItDownConverter` component that wraps Microsoft's MarkItDown library, enabling Haystack users to convert files into Haystack `Document` objects with Markdown content.

## Installation

```bash
pip install markitdown-haystack
```

## Usage

### Standalone

```python
from haystack_integrations.components.converters.markitdown import MarkItDownConverter

converter = MarkItDownConverter()
result = converter.run(sources=["document.pdf", "report.docx"])
documents = result["documents"]
```

You can also pass metadata to attach to the resulting documents:

```python
from haystack_integrations.components.converters.markitdown import MarkItDownConverter

converter = MarkItDownConverter()
result = converter.run(
    sources=["document.pdf", "report.docx"],
    meta=[{"author": "Alice"}, {"author": "Bob"}]
)
documents = result["documents"]
```

To convert `ByteStream` objects:

```python
from haystack.dataclasses import ByteStream
from haystack_integrations.components.converters.markitdown import MarkItDownConverter

converter = MarkItDownConverter()
bytestream = ByteStream(data=file_bytes, meta={"file_path": "document.pdf"})
result = converter.run(sources=[bytestream])
documents = result["documents"]
```

### In a Haystack Pipeline

```python
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.markitdown import MarkItDownConverter

document_store = InMemoryDocumentStore()

indexing = Pipeline()
indexing.add_component("converter", MarkItDownConverter())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")

indexing.run({"converter": {"sources": ["a/file/path.pdf", "another/file.docx"]}})
```

## License

`markitdown-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
