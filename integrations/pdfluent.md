---
layout: integration
name: PDFluent
description: Convert PDFs to structure-aware Documents with page, bounding box and kind in the metadata. Runs locally.
authors:
    - name: PDFluent
      socials:
        github: pdfluent
pypi: https://pypi.org/project/pdfluent-haystack
repo: https://github.com/pdfluent/pdfluent-sdk/tree/main/integrations/haystack-pdfluent
type: Data Ingestion
report_issue: https://github.com/pdfluent/pdfluent-sdk/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
`PDFluentConverter` reads a PDF into `Document` chunks in reading order. Each chunk carries `source`, `page` (counted from 0), `kind` and `bbox` in its `meta`, so an answer can cite where it came from. In local mode the engine runs on your machine and the PDF does not leave it.

## Installation
```bash
pip install pdfluent-haystack
```

## Usage
### Components
This integration introduces one component:

- `PDFluentConverter`: takes `sources` (paths or `ByteStream`) and returns `documents`.

### Convert a PDF
```python
from pdfluent_haystack import PDFluentConverter

converter = PDFluentConverter()
docs = converter.run(sources=["report.pdf"])["documents"]
print(docs[0].meta["page"], docs[0].meta["kind"], docs[0].content[:80])
```

### License
This integration is MIT licensed. The PDFluent engine it uses in local mode (`pdfluent` on PyPI) is licensed separately, under AGPL-3.0 or a commercial licence; see https://pdfluent.com/license.
