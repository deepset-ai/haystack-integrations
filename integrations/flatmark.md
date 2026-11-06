---
layout: integration
name: flatmark
description: "Document to Markdown API and MCP server for PDF, Word, PowerPoint, Excel and HTML. OCR queue for large files. Hosted in Germany."
authors:
    - name: flatmark
      socials:
        github: flatmark-dev
pypi: https://pypi.org/project/flatmark/
repo: https://github.com/flatmark-dev/flatmark-integrations
type: Data Ingestion
report_issue: https://github.com/flatmark-dev/flatmark-integrations/issues
logo: /logos/flatmark.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

flatmark converts PDF, Word, PowerPoint, Excel and HTML to Markdown over a REST API and an MCP server. Files up to 8 MB convert in one call with MarkItDown. Files up to 25 MB and 200 pages go through a queue that runs Docling with OCR and table detection. The queue returns Markdown and a JSON structure file, by polling or a signed webhook. The servers are in Germany. The free plan has 100 credits a month and needs no card.

This page shows `FlatmarkConverter`, a small Haystack component built on the
[`flatmark`](https://pypi.org/project/flatmark/) Python SDK: it sends local files to the
[flatmark API](https://flatmark.dev) and returns one Haystack `Document` per
file, with the Markdown as its content. Copy it into your project to feed
PDF, Word, PowerPoint, Excel and HTML files into indexing and RAG pipelines
without running a converter yourself.

## Installation

```bash
pip install flatmark haystack-ai
```

The component works without an API key, at the anonymous rate limit. For
more, [create a key](https://flatmark.dev/go/haystack?to=/app/api-keys) and set it as
`FLATMARK_API_KEY`.

## Usage

### Components

`FlatmarkConverter` reads file paths and outputs `documents`. Each file is
converted in one call; the file name decides its content type.

```python
import mimetypes
from pathlib import Path

from flatmark import AuthenticatedClient
from flatmark.api.convert import convert_document
from flatmark.models import BodyConvertDocument, Problem
from flatmark.types import File
from haystack import Document, component
from haystack.utils import Secret


@component
class FlatmarkConverter:
    """Converts files to Markdown Documents with the flatmark API."""

    def __init__(
        self, api_key: Secret = Secret.from_env_var("FLATMARK_API_KEY", strict=False)
    ):
        self.client = AuthenticatedClient(
            base_url="https://api.flatmark.dev",
            token=api_key.resolve_value() or "",  # no key: the anonymous rate limit
            auth_header_name="X-API-Key",
            prefix="",
            timeout=120.0,
        )

    @component.output_types(documents=list[Document])
    def run(self, sources: list[str | Path]):
        documents = []
        for source in sources:
            path = Path(source)
            mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            with path.open("rb") as payload:
                file = File(payload=payload, file_name=path.name, mime_type=mime_type)
                result = convert_document.sync(
                    client=self.client, body=BodyConvertDocument(file=file)
                )
            if isinstance(result, Problem):
                raise RuntimeError(f"{path.name}: {result.title}: {result.detail}")
            documents.append(
                Document(content=result.markdown, meta={"file_path": str(path)})
            )
        return {"documents": documents}
```

### Standalone

```python
converter = FlatmarkConverter()
documents = converter.run(sources=["report.pdf"])["documents"]
print(documents[0].content)
```

### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", FlatmarkConverter())
pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=200))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("converter", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["report.pdf"]}})
print(document_store.count_documents())
```

For scans, tables and larger files, the same SDK queues a conversion
(`submit_conversion_job`, then `get_job` and `get_conversion_result`); see the
[API reference](https://flatmark.dev/docs).

## License

The `flatmark` SDK is distributed under the terms of the
[MIT license](https://github.com/flatmark-dev/flatmark-integrations/blob/main/LICENSE).
