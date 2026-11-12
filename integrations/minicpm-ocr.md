---
layout: integration
name: MiniCPM-OCR
description: Convert PDFs and images to Markdown with MiniCPM-OCR, an open-weight OCR model running on your own inference server
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/minicpm-ocr-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/minicpm_ocr
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/minicpm.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[MiniCPM-OCR](https://github.com/OpenBMB/MiniCPM-OCR) is a 1.3B open-weight OCR model by OpenBMB, specialized in document parsing. It recognizes text, tables, and formulas in Chinese and English documents and returns them as Markdown. You run the model on your own inference server, such as vLLM, llama.cpp, or Ollama, so documents never leave your infrastructure.

This integration lets you use MiniCPM-OCR to convert PDFs and images into Haystack documents.

## Components

- [`MiniCPMOCRDocumentConverter`](https://docs.haystack.deepset.ai/docs/minicpmocrdocumentconverter). This component detects the layout of each page locally and sends the detected blocks to a MiniCPM-OCR inference server. It returns one document per source, with pages separated by form feed characters (`\f`) so you can split them by page.

## Installation

```shell
pip install minicpm-ocr-haystack
```

The integration supports Python 3.11 to 3.13.

You also need a running MiniCPM-OCR inference server. With a GPU, you can use vLLM:

```shell
vllm serve openbmb/MiniCPM-OCR-1.0 --served-model-name minicpm-ocr --port 8000
```

Without a GPU, for example on a laptop or Apple Silicon, llama.cpp can serve the quantized weights:

```shell
llama-server -hf openbmb/MiniCPM-OCR-1.0-gguf:Q4_K_M --host 127.0.0.1 --port 8080
```

For llama.cpp, initialize the converter with `server_url="http://127.0.0.1:8080"` and `backend="llamacpp"`.

## Usage

### How to use the `MiniCPMOCRDocumentConverter`

Basic usage with a local file:

```python
from pathlib import Path

from haystack_integrations.components.converters.minicpm_ocr import MiniCPMOCRDocumentConverter

converter = MiniCPMOCRDocumentConverter(server_url="http://localhost:8000")
converter.warm_up()

result = converter.run(sources=[Path("my_document.pdf")])
documents = result["documents"]
```

The first call to `warm_up()` downloads the layout model into `~/.cache/minicpm-ocr/layout`.

Here's an example of an indexing pipeline that converts PDFs and images, splits them by page, and writes them to a Document Store:

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.converters.minicpm_ocr import MiniCPMOCRDocumentConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", MiniCPMOCRDocumentConverter(server_url="http://localhost:8000"))
pipeline.add_component("splitter", DocumentSplitter(split_by="page", split_length=1))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter", "splitter")
pipeline.connect("splitter", "writer")

file_paths = ["invoice.pdf", "receipt.jpg", "contract.pdf"]
pipeline.run({"converter": {"sources": file_paths}})
```

### License

`minicpm-ocr-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
