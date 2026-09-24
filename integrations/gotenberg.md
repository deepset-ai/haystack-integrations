---
layout: integration
name: Gotenberg File Converter
description: Convert documents, HTML, Markdown, and web pages to PDF using Gotenberg in Haystack pipelines.
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

`GotenbergFileConverter` is a Haystack component that uses a [Gotenberg](https://gotenberg.dev/) service to convert files and web pages to PDF. It automatically routes office documents through LibreOffice, HTML and Markdown through Chromium, and HTTP or HTTPS URLs through Chromium's URL conversion route.

Sources can be local file paths (`str` or `Path`), URLs, or `ByteStream` objects with a MIME type. The converter returns one PDF `ByteStream` per source and supports both synchronous (`run`) and asynchronous (`run_async`) execution.

## Installation

Install the Python package:

```bash
pip install gotenberg-haystack
```

The component requires a running Gotenberg 8 service. For local use, start one with Docker:

```bash
docker run --rm -p 3000:3000 gotenberg/gotenberg:8
```

By default, the component connects to `http://localhost:3000`. Pass a different service URL to `GotenbergFileConverter` when Gotenberg runs elsewhere.

## Usage

### Standalone

Convert a local office document and a web page in one batch:

```python
from pathlib import Path

from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter

converter = GotenbergFileConverter()
result = converter.run(sources=[Path("report.docx"), "https://haystack.deepset.ai"])
pdfs = result["output"]  # [ByteStream(data=b'...')]
```

The component also accepts HTML and Markdown `ByteStream` objects and routes them by MIME type:

```python
from haystack.dataclasses import ByteStream
from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter

source = ByteStream(data=b"# Quarterly report", mime_type="text/markdown")
result = GotenbergFileConverter().run(sources=[source])
```

### In a Haystack Pipeline

`GotenbergFileConverter` outputs `list[ByteStream]`, which can be connected directly to a PDF converter to create Haystack `Document` objects:

```python
from pathlib import Path

from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter

pipeline = Pipeline()
pipeline.add_component("gotenberg", GotenbergFileConverter())
pipeline.add_component("pdf_converter", PyPDFToDocument())
pipeline.connect("gotenberg.output", "pdf_converter.sources")

result = pipeline.run({"gotenberg": {"sources": [Path("report.docx")]}})
print(result["pdf_converter"]["documents"])
```

### Async Usage

`run_async` converts sources concurrently while preserving their input order. Use `concurrency_limit` to control the maximum number of requests in flight:

```python
import asyncio
from pathlib import Path

from haystack_integrations.components.converters.gotenberg import GotenbergFileConverter


async def main():
    converter = GotenbergFileConverter(concurrency_limit=3)
    result = await converter.run_async(
        sources=[Path("report.docx"), "https://haystack.deepset.ai"]
    )
    print(result["output"])


asyncio.run(main())
```

## License

`gotenberg-haystack` is distributed under the [Apache-2.0 License](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/gotenberg/LICENSE.txt).
