---
layout: integration
name: oxidize-pdf
description: Convert PDFs into Haystack Documents with a fast Rust engine and element-disjoint RAG chunking; accepts paths and ByteStreams
authors:
    - name: Santiago Fernández Muñoz
      socials:
        github: bzsanti
pypi: https://pypi.org/project/haystack-oxidize-pdf
repo: https://github.com/bzsanti/oxidize-pdf-integrations/tree/main/haystack
type: Data Ingestion
report_issue: https://github.com/bzsanti/oxidize-pdf-integrations/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[`haystack-oxidize-pdf`](https://pypi.org/project/haystack-oxidize-pdf/) is a Haystack
converter backed by [oxidize-pdf](https://github.com/bzsanti/oxidize-python), a
Rust-powered PDF engine with first-class RAG primitives. The parser runs natively (no
system dependencies — it ships as a wheel for Linux, macOS and Windows) and exposes
element-disjoint semantic chunking, so PDFs become retrieval-ready `Document` objects
without any post-processing.

The chunking contract is enforced by regression tests: no chunk's text is a substring of
another's, and every source element appears in exactly one chunk. This guarantees no
duplicated context leaks into a vector store during ingestion.

## Installation

```bash
pip install haystack-oxidize-pdf
```

The package depends on `haystack-ai>=2.0,<3` and `oxidize-pdf>=0.4.3`.

## Usage

### Components

This integration introduces `OxidizePdfConverter`, a `@component` that reads PDF sources
and outputs Haystack `Document` objects. Sources may be file paths (`str` /
`pathlib.Path`) or `ByteStream` instances, interchangeably.

The converter has a single `__init__` argument, `mode`, controlling how each source is
turned into documents:

- `mode="rag"` (default): one `Document` per semantic chunk produced by oxidize-pdf's
  chunker. Per-chunk metadata exposes `chunk_index` (0-based, resets per source),
  `page_numbers` (1-indexed), `element_types`, `heading_context`, and `token_estimate`.
- `mode="pages"`: one `Document` per page (plain text); metadata carries `page_number`
  (1-indexed).
- `mode="markdown"`: a single `Document` per source containing the whole PDF as markdown;
  no `page_number` is emitted.

### Use the Converter standalone

```python
from haystack_oxidize_pdf import OxidizePdfConverter

converter = OxidizePdfConverter()  # mode="rag" by default
result = converter.run(sources=["paper.pdf"])

for doc in result["documents"]:
    print(doc.meta["chunk_index"], doc.meta["heading_context"])
    print(doc.content[:200])
```

### Use it in a Pipeline

```python
from haystack import Pipeline
from haystack_oxidize_pdf import OxidizePdfConverter

pipeline = Pipeline()
pipeline.add_component("converter", OxidizePdfConverter(mode="rag"))
# ...add an embedder, a document writer, etc.

result = pipeline.run({"converter": {"sources": ["paper.pdf"]}})
documents = result["converter"]["documents"]
```

### ByteStream input

The converter accepts `ByteStream` objects natively (via oxidize-pdf's
`PdfReader.from_bytes`), so PDFs that never touch disk — uploads, objects fetched from
blob storage — can be ingested directly. `ByteStream.meta` is merged into each output
`Document.meta`:

```python
from haystack.dataclasses import ByteStream
from haystack_oxidize_pdf import OxidizePdfConverter

with open("paper.pdf", "rb") as f:
    stream = ByteStream(
        data=f.read(),
        mime_type="application/pdf",
        meta={"upstream_origin": "s3://bucket/key"},
    )

docs = OxidizePdfConverter().run(sources=[stream])["documents"]
# each doc.meta carries upstream_origin == "s3://bucket/key"
```

### Batch sources with per-source metadata

`meta` may be a single dict (broadcast to every output document) or a list of dicts (one
per source, lengths must match):

```python
docs = OxidizePdfConverter(mode="markdown").run(
    sources=["doc-a.pdf", "doc-b.pdf"],
    meta=[{"tag": "first"}, {"tag": "second"}],
)["documents"]
# docs[0].meta["tag"] == "first"; docs[1].meta["tag"] == "second"
```

Caller-supplied `meta` overrides base file-level fields (`file_path`, `file_name`,
`total_pages`, `pdf_version`), but per-document fields (`chunk_index`, `page_numbers`,
`page_number`) are applied last and are never overwritten.

## License

`haystack-oxidize-pdf` is distributed under the terms of the
[MIT license](https://github.com/bzsanti/oxidize-pdf-integrations/blob/main/LICENSE).
