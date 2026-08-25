---
layout: integration
name: OpenDataLoader PDF
description: Convert PDFs into Haystack Documents locally with OpenDataLoader PDF, a layout-aware PDF parser
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/opendataloader-pdf-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opendataloader_pdf
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/opendataloader-pdf.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `opendataloader-pdf-haystack` integration provides [`OpenDataLoaderConverter`](https://docs.haystack.deepset.ai/docs/opendataloaderconverter), a component that converts PDF files into Haystack `Document` objects using [OpenDataLoader PDF](https://opendataloader.org/).

OpenDataLoader PDF analyzes the layout of a PDF – headings, paragraphs, lists, and tables – and serializes it into Markdown, plain text, HTML, or a full structured JSON representation. Everything runs locally, with no external API calls.

The converter accepts PDF file paths and Haystack `ByteStream` objects, and returns one `Document` per source. Each document's metadata contains the `file_path` of the source and the `output_format` that produced its content, along with any metadata you pass through the `meta` run parameter. Metadata attached to a `ByteStream` is preserved as well.

Only PDFs are supported: a file path with another extension, or a `ByteStream` whose MIME type is not `application/pdf`, raises a `ValueError`.

**OpenDataLoader PDF runs on a Java engine, so Java 11 or newer must be installed and `java` must be available on your `PATH`.** The component checks for this at run time and raises a `RuntimeError` if no usable Java runtime is found.

For more details, see the [OpenDataLoaderConverter documentation](https://docs.haystack.deepset.ai/docs/opendataloaderconverter) and the [OpenDataLoader PDF docs](https://opendataloader.org/docs/quick-start-python).

## Installation

```bash
pip install opendataloader-pdf-haystack
```

## Usage

### Components

This integration introduces one component:

- The [`OpenDataLoaderConverter`](https://docs.haystack.deepset.ai/docs/opendataloaderconverter): converts PDF file paths and `ByteStream` objects into Haystack `Document` objects.

It takes two initialization parameters:

- `output_format`: the format OpenDataLoader produces – `"markdown"` (default), `"text"`, `"html"`, or `"json"`. The chosen format ends up in the `output_format` metadata field of every returned document.
- `convert_kwargs`: additional arguments forwarded to `opendataloader_pdf.convert`. See the [OpenDataLoader PDF convert options](https://opendataloader.org/docs/quick-start-python#convert-options) for the full list. Image extraction is turned off by default so that documents contain text only; pass `image_output` here to turn it back on.

### Use the Converter standalone

```python
from haystack_integrations.components.converters.opendataloader_pdf import OpenDataLoaderConverter

converter = OpenDataLoaderConverter()
result = converter.run(sources=["report.pdf"], meta={"source": "annual-report"})

document = result["documents"][0]
print(document.meta)
# {'file_path': 'report.pdf', 'source': 'annual-report', 'output_format': 'markdown'}
print(document.content)
```

### Use it in an indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.opendataloader_pdf import OpenDataLoaderConverter

document_store = InMemoryDocumentStore()

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("converter", OpenDataLoaderConverter())
indexing_pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))

indexing_pipeline.connect("converter", "splitter")
indexing_pipeline.connect("splitter", "writer")

indexing_pipeline.run({"converter": {"sources": ["report.pdf"]}})
```

### Choose an output format

```python
from haystack_integrations.components.converters.opendataloader_pdf import OpenDataLoaderConverter

# The full structured representation, including layout information
converter = OpenDataLoaderConverter(output_format="json")
documents = converter.run(sources=["report.pdf"])["documents"]
```

### Customize the extraction

Any [OpenDataLoader PDF option](https://opendataloader.org/docs/quick-start-python#convert-options) can be passed through `convert_kwargs`. For example, to convert a page range of an encrypted PDF, keep page separators in the Markdown output, and redact sensitive data:

```python
from haystack_integrations.components.converters.opendataloader_pdf import OpenDataLoaderConverter

converter = OpenDataLoaderConverter(
    output_format="markdown",
    convert_kwargs={
        "pages": "1,3,5-7",
        "password": "secret",
        "markdown_page_separator": "--- page %page-number% ---",
        "sanitize": True,
    },
)
documents = converter.run(sources=["report.pdf"])["documents"]
```

Other frequently used options are `table_method="cluster"` for table-heavy PDFs, `use_struct_tree=True` to follow the structure tree of a tagged PDF, and `include_header_footer=True` to keep page headers and footers.

### Convert ByteStreams

PDFs that never touch disk – uploads, or objects fetched from blob storage – can be passed as `ByteStream` objects:

```python
from pathlib import Path

from haystack.dataclasses import ByteStream
from haystack_integrations.components.converters.opendataloader_pdf import OpenDataLoaderConverter

stream = ByteStream.from_file_path(
    Path("report.pdf"), mime_type="application/pdf", meta={"file_path": "report.pdf"}
)

converter = OpenDataLoaderConverter()
documents = converter.run(sources=[stream], meta={"source": "internal-reports"})["documents"]
```

### License

`opendataloader-pdf-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/opendataloader_pdf/LICENSE.txt).
