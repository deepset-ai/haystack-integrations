---
layout: integration
name: ocr-software.com
description: Read PDFs and scans with the ocr-software.com OCR API and get one Haystack Document per page, as text or Markdown.
authors:
    - name: ocr-software.com
      socials:
        github: ocr-software
pypi: https://pypi.org/project/ocr-software-haystack/
repo: https://github.com/ocr-software/ocr-software-haystack
type: Data Ingestion
report_issue: https://github.com/ocr-software/ocr-software-haystack/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`OcrSoftwareConverter` sends PDF, PNG, JPEG or TIFF files to the paid [ocr-software.com](https://ocr-software.com/integrations/haystack/) OCR API and returns one `Document` per page, as text or Markdown. Each `Document` carries `meta["page"]` (counted from 1), so an answer can cite its page. The component is MIT-licensed; the OCR service behind it is a paid API and needs an API key. The files leave your machine for the API (Helsinki, EU), or for your own server if you set `base_url`.

- `pipeline`: optional, `name@version`. Without it the cheapest available pipeline is used and named in the log and in `meta["pipeline"]`.
- `format`: `"text"` (default) or `"md"`.
- `split_pages`: `True` (default) gives one `Document` per page, `False` one per file.
- Files are read one after the other, so at most one job is open at the API. A page that failed does not stop the run; its `Document` carries `meta["incomplete"]` with the reason. With `on_error="raise"` an invalid file raises `OcrError` instead of being skipped.

Tested with `haystack-ai` 3.5.0.

## Installation

```bash
pip install ocr-software-haystack
export OCR_SOFTWARE_API_KEY=ocr_...
```

Get a key at [ocr-software.com/order](https://ocr-software.com/order/).

## Usage

```python
from ocr_software_haystack import OcrSoftwareConverter

converter = OcrSoftwareConverter()
documents = converter.run(sources=["scan.pdf"])["documents"]
print(documents[0].content, documents[0].meta)
```

The component also runs inside a `Pipeline`. `to_dict` and `from_dict` keep the key out of the file; it is read from the environment. Haystack 3 loads only trusted modules from YAML: `Pipeline.loads(text, allowed_modules=["ocr_software_haystack"])`.

### License

The `ocr-software-haystack` package is released under the MIT license. The ocr-software.com API is a paid service operated by Helm & Nagel GmbH; see its [terms](https://ocr-software.com/legal/saas-terms/).
