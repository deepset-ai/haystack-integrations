---
layout: integration
name: Azure Form Recognizer
description: Convert files to Documents using Azure's Document Intelligence service (Form Recognizer SDK)
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/azure-form-recognizer-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/azure_form_recognizer
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/azure-ai.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[`AzureOCRDocumentConverter`](https://docs.haystack.deepset.ai/docs/azureocrdocumentconverter) converts files to Haystack Documents using [Azure's Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/) service through the [`azure-ai-formrecognizer`](https://pypi.org/project/azure-ai-formrecognizer/) SDK.

**Supported file formats**: PDF, JPEG, PNG, BMP, TIFF, DOCX, XLSX, PPTX, HTML.

Unlike the [`AzureDocumentIntelligenceConverter`](azure-doc-intelligence.md) (which produces Markdown), this component extracts tables as separate `Document` objects that preserve their two-dimensional (CSV) structure, and returns the remaining text with page breaks (`\f`) so it can be split per page by downstream preprocessors.

You need an active Azure account and a Document Intelligence or Cognitive Services resource. Follow the [Azure setup guide](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api) to create your resource.

## Installation

```bash
pip install azure-form-recognizer-haystack
```

## Usage

Provide your service endpoint and an API key. By default the component reads the key from the `AZURE_AI_API_KEY` environment variable.

```python
import os
from haystack_integrations.components.converters.azure_form_recognizer import AzureOCRDocumentConverter
from haystack.utils import Secret

converter = AzureOCRDocumentConverter(
    endpoint=os.environ["AZURE_AI_ENDPOINT"],
    api_key=Secret.from_env_var("AZURE_AI_API_KEY"),
)

results = converter.run(sources=["document.pdf"])
documents = results["documents"]
print(documents[0].content)
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret
from haystack_integrations.components.converters.azure_form_recognizer import AzureOCRDocumentConverter

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", AzureOCRDocumentConverter(endpoint="azure_resource_url", api_key=Secret.from_env_var("AZURE_AI_API_KEY")))
pipeline.add_component("cleaner", DocumentCleaner())
pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("converter", "cleaner")
pipeline.connect("cleaner", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["my_file.pdf"]}})
```
