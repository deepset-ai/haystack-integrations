---
layout: integration
name: Gotenberg
description: Convert Office, OpenDocument, HTML, and Markdown files, and web pages to PDF with a Gotenberg server in Haystack pipelines.
authors:
    - name: Max Swain
      socials:
        github: maxdswain
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/gotenberg-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/gotenberg
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/gotenberg.png
version: Haystack 2.0
toc: true
enterprise: true
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Standalone](#standalone)
  - [In a Haystack Pipeline](#in-a-haystack-pipeline)
  - [Async Usage](#async-usage)
- [License](#license)

## Overview

`GotenbergFileConverter` is a Haystack component that converts files to PDF using [Gotenberg](https://gotenberg.dev/), a Docker-based API that wraps LibreOffice and Chromium. Because conversion runs in a separate service, you can deploy and scale it independently of your pipelines, with no need to install LibreOffice next to your Haystack application.

Each source is routed to the matching Gotenberg endpoint, so a single batch can mix source types:

- **Office and OpenDocument files** (`.docx`, `.xlsx`, `.pptx`, `.odt`, `.rtf`, and [many more](https://gotenberg.dev/docs/convert-with-libreoffice/convert-to-pdf)) are converted with LibreOffice.
- **HTML and Markdown files** are rendered with Chromium. Local assets such as images and stylesheets can be uploaded alongside them through the `resources` parameter.
- **HTTP(S) URLs** are fetched by Gotenberg and printed to PDF with Chromium.
- **`ByteStream` objects** are routed by their `mime_type`.

The component outputs one PDF `ByteStream` per source, which plugs directly into Haystack's PDF converters such as `PyPDFToDocument`. Both synchronous (`run`) and asynchronous (`run_async`) execution are supported.

For more details, see the [GotenbergFileConverter documentation](https://docs.haystack.deepset.ai/docs/gotenbergfileconverter).

## Installation

Start a Gotenberg server, for example with Docker:

```bash
docker run --rm -p 3000:3000 gotenberg/gotenberg:8
```

Then install the Python package:

```bash
pip install gotenberg-haystack
```

## Usage

### Standalone

By default, the converter connects to `http://localhost:3000`. Use the `url` parameter to point it to another Gotenberg server.

```python
from pathlib import Path
from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter

converter = GotenbergFileConverter(url="http://localhost:3000")
result = converter.run(
    sources=[Path("report.docx"), Path("notes.md"), "https://haystack.deepset.ai"],
)
print(result["output"])
# [ByteStream(data=b'%PDF-1.7...', meta={'file_path': 'report.docx'}, mime_type='application/pdf'), ...]
```

### In a Haystack Pipeline

`GotenbergFileConverter` outputs `list[ByteStream]`, which connects directly to Haystack's PDF converters. This example converts a Word document and a Markdown file to PDF, extracts their text, splits it, and writes the resulting Documents to a Document Store:

```python
from pathlib import Path
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("gotenberg", GotenbergFileConverter())
pipeline.add_component("pdf_converter", PyPDFToDocument())
pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("gotenberg.output", "pdf_converter.sources")
pipeline.connect("pdf_converter", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"gotenberg": {"sources": [Path("report.docx"), Path("notes.md")]}})
print(document_store.count_documents())
```

### Async Usage

`run_async` sends requests to Gotenberg concurrently. `concurrency_limit` sets how many requests are in flight at once:

```python
import asyncio
from pathlib import Path
from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter

async def main():
    converter = GotenbergFileConverter(concurrency_limit=10)
    result = await converter.run_async(sources=[Path("report.docx"), Path("notes.md")])
    print(result["output"])

asyncio.run(main())
```

## License

`gotenberg-haystack` is distributed under the [Apache-2.0 License](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/gotenberg/LICENSE.txt).
