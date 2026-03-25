---
layout: integration
name: Kreuzberg
description: Locally convert 91+ document formats into Haystack Documents using Kreuzberg's Rust-core engine
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/kreuzberg-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/kreuzberg
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/kreuzberg.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Additional Features](#additional-features)
- [License](#license)

## Overview

[Kreuzberg](https://docs.kreuzberg.dev/) is a document intelligence framework with a Rust core that extracts text, tables, and metadata from 91+ file formats — entirely locally with no external API calls.

This integration provides `KreuzbergConverter`, a Haystack component that converts files into Haystack `Document` objects with rich metadata. It supports parallel batch extraction using Rust's rayon thread pool for high throughput.

**Supported format categories:**
- **Documents**: PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS, ODT, ODS, ODP, RTF, Pages, Keynote, Numbers, and more
- **Images (via OCR)**: PNG, JPEG, TIFF, GIF, BMP, WebP, JPEG 2000, SVG
- **Text/Markup**: Markdown, HTML, XML, LaTeX, Typst, JSON, YAML, reStructuredText, Jupyter notebooks
- **Email**: EML, MSG (with attachment extraction)
- **Archives**: ZIP, TAR, GZIP, 7Z (extracts and processes contents recursively)
- **eBooks & Academic**: EPUB, BibTeX, DocBook, JATS

## Installation

```bash
pip install kreuzberg-haystack
```

## Usage

### Components

This integration introduces one component:

- **`KreuzbergConverter`**: Converts files and directories into Haystack `Document` objects. Accepts file paths, directory paths, and `ByteStream` objects as input.

### Basic Usage

```python
from haystack_integrations.components.converters.kreuzberg import KreuzbergConverter

converter = KreuzbergConverter()
result = converter.run(sources=["report.pdf", "notes.docx"])
documents = result["documents"]
```

### Markdown Output with OCR

Use `ExtractionConfig` to customize output format, OCR backend, and other extraction settings:

```python
from haystack_integrations.components.converters.kreuzberg import KreuzbergConverter
from kreuzberg import ExtractionConfig, OcrConfig

converter = KreuzbergConverter(
    config=ExtractionConfig(
        output_format="markdown",
        ocr=OcrConfig(backend="tesseract", language="eng"),
    ),
)
result = converter.run(sources=["scanned_document.pdf"])
documents = result["documents"]
```

### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.kreuzberg import KreuzbergConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", KreuzbergConverter())
pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["report.pdf", "presentation.pptx"]}})
```

## Additional Features

- **Per-page extraction**: Create one `Document` per page using `PageConfig(extract_pages=True)`
- **Chunking**: Split documents by token count with configurable overlap via `ChunkingConfig`
- **Token reduction**: Reduce token count with modes from `"light"` to `"maximum"` via `TokenReductionConfig`
- **Rich metadata**: Quality scores, detected languages, extracted keywords, table data, and PDF annotations
- **Batch processing**: Parallel extraction enabled by default; set `batch=False` for sequential mode
- **Config from file**: Load extraction settings from a TOML, YAML, or JSON file via `config_path`

For the full configuration reference and format support matrix, see the [Kreuzberg documentation](https://docs.kreuzberg.dev/).

### License

`kreuzberg-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
