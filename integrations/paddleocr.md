---
layout: integration
name: PaddleOCR
description: Use PaddleOCR’s text-recognition and document-parsing capabilities with Haystack
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/paddleocr-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/paddleocr
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/paddleocr.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Note](#note)
- [License](#license)

## Overview

[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) converts documents and images into structured, AI-friendly data (like JSON and Markdown) with industry-leading accuracy—powering AI applications for everyone from indie developers and startups to large enterprises worldwide.

This integration allows you to use PaddleOCR’s text-recognition and document-parsing capabilities with Haystack.

## Components

- [`PaddleOCRVLDocumentConverter`](https://docs.haystack.deepset.ai/docs/paddleocrvldocumentconverter). This component extracts text from documents using PaddleOCR's large model document parsing API.

## Initialization

Every component of the PaddleOCR integration requires an access token from PaddlePaddle AI Studio. By default, authentication uses the `AISTUDIO_ACCESS_TOKEN` environment variable. You can also provide an `access_token` when initializing each component. The AI Studio access token can be obtained from [this page](https://aistudio.baidu.com/account/accessToken).

## Installation

```shell
pip install paddleocr-haystack
```

## Usage

### How to use the `PaddleOCRVLDocumentConverter`

To start, visit the [PaddleOCR official website](https://aistudio.baidu.com/paddleocr/task), click the **API** button in the upper-left corner, choose the example code for **Large Model document parsing(PaddleOCR-VL)**, and copy the `API_URL`.

Basic usage with a local file:

```python
from pathlib import Path
from haystack.utils import Secret
from haystack_integrations.components.converters.paddleocr import PaddleOCRVLDocumentConverter

converter = PaddleOCRVLDocumentConverter(
    api_url="<your-api-url>",
    access_token=Secret.from_env_var("AISTUDIO_ACCESS_TOKEN"),
)

result = converter.run(sources=[Path("my_document.pdf")])
documents = result["documents"]
```

Here's an example of an indexing pipeline that processes PDFs with OCR and writes them to a Document Store:

```python
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret
from haystack_integrations.components.converters.paddleocr import PaddleOCRVLDocumentConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component(
    "converter",
    PaddleOCRVLDocumentConverter(
        api_url="<your-api-url>",
        access_token=Secret.from_env_var("AISTUDIO_ACCESS_TOKEN"),
    )
)
pipeline.add_component("cleaner", DocumentCleaner())
pipeline.add_component("splitter", DocumentSplitter(split_by="page", split_length=1))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter", "cleaner")
pipeline.connect("cleaner", "splitter")
pipeline.connect("splitter", "writer")

file_paths = ["invoice.pdf", "receipt.jpg", "contract.pdf"]
pipeline.run({"converter": {"sources": file_paths}})
```


### License

`paddleocr-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
