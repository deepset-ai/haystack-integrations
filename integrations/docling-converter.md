---
layout: integration
name: Docling Converter
description: Use Docling to locally parse and chunk PDF, DOCX, and other document types in Haystack
authors:
    - name: DS4SD
      socials:
        github: DS4SD
pypi: https://pypi.org/project/docling-haystack
repo: https://github.com/DS4SD/docling-haystack
type: Data Ingestion
report_issue: https://github.com/DS4SD/docling/issues
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

[Docling](https://github.com/DS4SD/docling) locally parses PDF, DOCX, HTML, and other
document formats into a rich standardized representation (incl. layout, tables etc.),
which it can then export to Markdown, JSON, and others.

Check out the [Docling docs](https://ds4sd.github.io/docling/) for more details.

This integration introduces Docling support, enabling Haystack users to:
- use various document types in LLM applications with ease and speed, and
- leverage Docling's rich format for advanced, document-native grounding.

## Installation

```bash
pip install docling-haystack
```

## Usage

### Components

This integration introduces `DoclingConverter`, a component which reads document
file paths (local or URL) and outputs Haystack `Document` objects.

`DoclingConverter` supports two different export modes, see `export_type` initialization
argument further below.

### Use Docling Converter

#### Docling Converter Initialization

`DoclingConverter` creation can be parametrized via the following `__init__()`
arguments, most of which refer to the initialization and usage of the underlying Docling
[`DocumentConverter`](https://ds4sd.github.io/docling/usage/) and
[chunker](https://ds4sd.github.io/docling/concepts/chunking/) instances:

- `converter`: The Docling `DocumentConverter` to use; if not set, a system default is
  used.
- `convert_kwargs`: Any parameters to pass to Docling conversion; if not set, a system
  default is used.
- `export_type`: The export mode to use: `ExportType.DOC_CHUNKS` (default) chunks each
  input document (see `chunker`) and captures each individual chunk as a separate
  Haystack `Document`, while `ExportType.MARKDOWN` captures each input document as a
  separate Haystack `Document` (in which case splitting is likely required downstream).
- `md_export_kwargs`: Any parameters to pass to Markdown export (in case of
  `ExportType.MARKDOWN`).
- `chunker`: The Docling chunker instance to use; if not set, a system default is used
  (in case of `ExportType.DOC_CHUNKS`).
- `meta_extractor`: The extractor instance to use for populating the output document
  metadata; if not set, a system default is used.

#### Standalone

```python
from docling_haystack.converter import DoclingConverter

converter = DoclingConverter()
documents = converter.run(paths=["https://arxiv.org/pdf/2408.09869"])["documents"]

print(repr(documents[2].content))
# -> Abstract\nThis technical report introduces Docling [...]
```

#### In a Pipeline

Check out [this notebook](https://ds4sd.github.io/docling/examples/rag_haystack/)
illustrating usage in a complete example with indexing and RAG pipelines.

### License

MIT License.
