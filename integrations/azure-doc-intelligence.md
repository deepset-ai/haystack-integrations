---
layout: integration
name: Azure Document Intelligence
description: Use Azure Document Intelligence with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/azure-doc-intelligence-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/azure_doc_intelligence
type: Converter
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

`AzureDocumentIntelligenceConverter` provides an integration of [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/) (formerly Form Recognizer) with [Haystack](https://haystack.deepset.ai/) by [deepset](https://www.deepset.ai).

This component uses Azure's Document Intelligence service to convert various file formats into Haystack Documents with markdown content. It supports advanced document analysis including layout detection, table extraction, and structured content recognition.

**Supported file formats**: PDF, JPEG, PNG, BMP, TIFF, DOCX, XLSX, PPTX, HTML.

**Key features**:
- Markdown output with preserved structure (headings, tables, lists)
- Inline table integration (tables rendered as markdown tables)
- Improved layout analysis and reading order
- Support for section headings
- Multiple model options for different use cases

## Installation

Install the Azure Document Intelligence integration:

```bash
pip install "azure-doc-intelligence-haystack"
```

## Usage

To use the `AzureDocumentIntelligenceConverter`, you need an active [Azure subscription](https://azure.microsoft.com/en-us/products/ai-services/document-intelligence) with a deployed Document Intelligence or Cognitive Services resource. You need to provide a service endpoint as `AZURE_DI_ENDPOINT` and an API key as `AZURE_DI_API_KEY` for authentication.

```python
import os
from haystack_integrations.components.converters.azure_doc_intelligence import (
    AzureDocumentIntelligenceConverter,
)
from haystack.utils import Secret

converter = AzureDocumentIntelligenceConverter(
    endpoint=os.environ["AZURE_DI_ENDPOINT"],
    api_key=Secret.from_env_var("AZURE_DI_API_KEY"),
)

results = converter.run(sources=["invoice.pdf", "contract.docx"])
documents = results["documents"]

# Documents contain markdown with inline tables
print(documents[0].content)
```

### Model Options

The converter supports different Azure Document Intelligence models depending on your needs:

- **`prebuilt-document`** (default): General document analysis with markdown output
- **`prebuilt-read`**: Fast OCR for text extraction
- **`prebuilt-layout`**: Enhanced layout analysis with better table and structure detection
- **Custom models**: Use your own trained models by providing the model ID

```python
# Use a specific model
converter = AzureDocumentIntelligenceConverter(
    endpoint=os.environ["AZURE_DI_ENDPOINT"],
    api_key=Secret.from_env_var("AZURE_DI_API_KEY"),
    model_id="prebuilt-layout",  # Enhanced layout analysis
)
```

### Metadata

The converter automatically adds metadata to each Document:
- `model_id`: The Azure model used for analysis
- `page_count`: Number of pages in the document
- `file_path`: The source file path (filename only by default, or full path if `store_full_path=True`)

You can also provide custom metadata:

```python
results = converter.run(
    sources=["document.pdf"],
    meta={"category": "legal", "priority": "high"}
)
```

For more details on Azure Document Intelligence capabilities and setup, refer to the [Azure documentation](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api).
