---
layout: integration
name: switchfile
description: Convert PDFs into Markdown documents with tables through the switchfile API, with optional table-only documents
authors:
    - name: switchfile
      socials:
        github: switchfile
pypi: https://pypi.org/project/switchfile-haystack/
repo: https://github.com/switchfile/switchfile-haystack
type: Data Ingestion
report_issue: https://github.com/switchfile/switchfile-haystack/issues
logo: /logos/switchfile.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[switchfile](https://switchfile.io) converts PDFs into Markdown and JSON through an HTTP API. The
`switchfile-haystack` package provides `SwitchfileConverter`, a component that sends PDF files to the API and returns
Haystack `Document` objects whose content is the API's Markdown output: headings, paragraphs, lists and tables as pipe
tables, in reading order, with a `<!-- page N -->` line where each page starts.

- Accepts file paths and `ByteStream` objects, and returns one `Document` per file.
- With `split_pages=True`, pages are separated by a form feed (`\f`), so `DocumentSplitter(split_by="page")` keeps
  page numbers.
- With `table_documents=True`, every table is also returned as a `Document` of its own, with its page number.
- Both options use the API's structured JSON result and render the Markdown from it. Each file is converted once.
- Scanned pages go through text recognition.
- Word, Excel and PowerPoint files are converted the same way.
- With `store=False`, the file and the result are not stored on the server.

In the open [pdf-table-bench](https://github.com/switchfile/pdf-table-bench) benchmark, 97.2 % of the number cells in
switchfile's output are exact, summed over all test PDFs. Documents, outputs and scoring code are public.

The API key is read from the `SWITCHFILE_API_KEY` environment variable through Haystack's `Secret`. Create one in the
[switchfile dashboard](https://switchfile.io/dashboard/keys). Keys that start with `sf_test_` are sandbox keys and
never use credits.

## Installation

```bash
pip install switchfile-haystack
```

## Usage

### Components

This integration introduces one component:

- `SwitchfileConverter`: converts PDF files and `ByteStream` objects into Markdown `Document` objects.

Its main initialization parameters:

- `split_pages`: separate pages by a form feed for page-wise splitting. `False` by default.
- `table_documents`: also return every table as a separate document. `False` by default.
- `pages`: pages to convert, for example `"1-3,5"`. All pages by default.
- `ocr_language`: language of scanned pages, for example `"eng"` or `"deu+eng"`. Detected by default.
- `store`: set to `False` to convert without storing the file or the result.
- `timeout`: seconds to wait for one file. `300` by default.
- `raise_on_failure`: raise on a file that cannot be converted instead of skipping it with a warning.

### Use the converter on its own

```python
from haystack_integrations.components.converters.switchfile import SwitchfileConverter

converter = SwitchfileConverter()
result = converter.run(sources=["report.pdf"], meta={"collection": "annual-reports"})

document = result["documents"][0]
print(document.content)
print(document.meta["page_count"], document.meta["file_path"])
```

### Use it in an indexing pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.switchfile import SwitchfileConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", SwitchfileConverter(split_pages=True))
pipeline.add_component("splitter", DocumentSplitter(split_by="page", split_length=1))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("converter", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["report.pdf"]}})
print(document_store.count_documents())
```

### Get tables as separate documents

```python
from haystack_integrations.components.converters.switchfile import SwitchfileConverter

converter = SwitchfileConverter(table_documents=True)
documents = converter.run(sources=["report.pdf"])["documents"]

for table in documents[1:]:
    print(table.meta["page_number"], table.meta["table_rows"], table.meta["table_cols"])
    print(table.content)
```

The first document holds the whole file; every table follows as its own document with `source_document_id`,
`page_number`, `table_index`, `table_rows` and `table_cols` in its metadata.

### Errors

A file that cannot be converted is skipped with a warning by default. With `raise_on_failure=True`, it raises
`SwitchfileError`, whose `code` is the error code from the [switchfile API documentation](https://switchfile.io/docs/errors),
for example `PASSWORD_PROTECTED` or `UNSUPPORTED_PAIR`. An invalid API key or missing credits always raise.

## License

`switchfile-haystack` is distributed under the terms of the [MIT](https://github.com/switchfile/switchfile-haystack/blob/main/LICENSE) license.
