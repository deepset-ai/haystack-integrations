---
layout: integration
name: LibreOffice File Converter
description: Convert office documents, spreadsheets, and presentations between formats using LibreOffice in Haystack pipelines.
authors:
    - name: Max Swain
      socials:
        github: maxdswain
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/libreoffice-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/libreoffice
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/libreoffice.png
version: Haystack 2.0
toc: true
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

`LibreOfficeFileConverter` is a Haystack component that uses [LibreOffice](https://www.libreoffice.org/)'s command-line utility (`soffice`) to convert office files between formats. It supports documents, spreadsheets, and presentations, and can output `ByteStream` objects that plug directly into other Haystack components.

Sources can be file paths (`str` or `Path`) or `ByteStream` objects. Both synchronous (`run`) and asynchronous (`run_async`) execution modes are supported.

## Installation

First, install LibreOffice on your system:

- **macOS:** `brew install --cask libreoffice`
- **Ubuntu/Debian:** `sudo apt-get install libreoffice`
- **Windows:** Download from [libreoffice.org](https://www.libreoffice.org/download/download/)

Then install the Python package:

```bash
pip install libreoffice-haystack
```

## Usage

### Standalone

```python
from pathlib import Path
from haystack_integrations.components.converters.libreoffice import LibreOfficeFileConverter

converter = LibreOfficeFileConverter()
result = converter.run(sources=[Path("report.doc")], output_file_type="docx")
print(result["output"])  # [ByteStream(data=b'...')]
```

The `output_file_type` can be set at initialization or passed per `run()` call (the latter takes precedence):

```python
# Set at init
converter = LibreOfficeFileConverter(output_file_type="pdf")
result = converter.run(sources=[Path("report.docx")])

# Override per call
result = converter.run(sources=[Path("slides.pptx")], output_file_type="png")
```

### In a Haystack Pipeline

`LibreOfficeFileConverter` outputs `list[ByteStream]`, which connects directly to Haystack's built-in converters. Here is an example that converts a legacy `.doc` file to `.docx` and then extracts its text as Haystack `Document` objects:

```python
from pathlib import Path
from haystack import Pipeline
from haystack.components.converters import DOCXToDocument
from haystack_integrations.components.converters.libreoffice import LibreOfficeFileConverter

pipeline = Pipeline()
pipeline.add_component("libreoffice_converter", LibreOfficeFileConverter())
pipeline.add_component("docx_converter", DOCXToDocument())
pipeline.connect("libreoffice_converter.output", "docx_converter.sources")

result = pipeline.run({
    "libreoffice_converter": {
        "sources": [Path("legacy_report.doc")],
        "output_file_type": "docx",
    }
})
print(result["docx_converter"]["documents"])
```

### Async Usage

`LibreOfficeFileConverter` also exposes a `run_async` method with the same signature as `run`, for use in async Haystack pipelines:

```python
import asyncio
from pathlib import Path
from haystack_integrations.components.converters.libreoffice import LibreOfficeFileConverter

async def main():
    converter = LibreOfficeFileConverter()
    result = await converter.run_async(
        sources=[Path("presentation.pptx")],
        output_file_type="pdf",
    )
    print(result["output"])

asyncio.run(main())
```

> **Note:** LibreOffice only supports one running `soffice` instance at a time. Conversions within a single `run_async` call are executed sequentially.

## License

`libreoffice-haystack` is distributed under the [Apache-2.0 License](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/libreoffice/LICENSE.txt).
