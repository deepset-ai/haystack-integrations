---
layout: integration
name: Amazon Textract
description: Use Amazon Textract with Haystack to extract text, tables, forms, and answers to queries from documents
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/amazon-textract-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/amazon_textract
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aws.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[`AmazonTextractConverter`](https://docs.haystack.deepset.ai/docs/amazontextractconverter) provides an integration of [Amazon Textract](https://aws.amazon.com/textract/) with [Haystack](https://haystack.deepset.ai/).

This component uses Amazon Textract's synchronous API to convert images and single-page PDFs into Haystack `Document` objects using OCR. It supports plain text extraction, structural analysis for tables and forms, and natural-language queries on documents.

**Supported file formats**: JPEG, PNG, TIFF, BMP, and single-page PDF (up to 10 MB).

**Key features**:
- Plain text extraction with `DetectDocumentText`
- Table, form, signature, and layout detection with `AnalyzeDocument`
- Natural-language queries to extract specific answers from documents
- Access to the raw Textract response for downstream processing

## Installation

Install the Amazon Textract integration:

```bash
pip install amazon-textract-haystack
```

## Usage

The component uses the standard boto3 credential chain. You can set AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`) as environment variables, configure them via `~/.aws/credentials` and `~/.aws/config`, rely on an IAM role when running on AWS infrastructure, or pass them explicitly as [Secret](https://docs.haystack.deepset.ai/docs/secret-management) arguments.

### Basic text extraction

Extract plain text from a document using `DetectDocumentText`:

```python
from haystack_integrations.components.converters.amazon_textract import AmazonTextractConverter

converter = AmazonTextractConverter()
results = converter.run(sources=["document.png"])
documents = results["documents"]

print(documents[0].content)
```

### Table and form analysis

Use `AnalyzeDocument` to detect tables and forms by setting `feature_types`:

```python
from haystack_integrations.components.converters.amazon_textract import AmazonTextractConverter

converter = AmazonTextractConverter(feature_types=["TABLES", "FORMS"])
results = converter.run(sources=["invoice.png"])

documents = results["documents"]
raw_responses = results["raw_textract_response"]
```

Valid `feature_types` values: `"TABLES"`, `"FORMS"`, `"SIGNATURES"`, `"LAYOUT"`.

### Natural-language queries

Ask questions about a document and get extracted answers. The `QUERIES` feature type is enabled automatically when you pass the `queries` parameter at runtime:

```python
from haystack_integrations.components.converters.amazon_textract import AmazonTextractConverter

converter = AmazonTextractConverter()
results = converter.run(
    sources=["medical_form.png"],
    queries=["What is the patient name?", "What is the date of birth?"],
)

documents = results["documents"]
raw_responses = results["raw_textract_response"]
```

Queries can be combined with `feature_types` for both structural and question-based extraction:

```python
converter = AmazonTextractConverter(feature_types=["TABLES", "FORMS"])
results = converter.run(
    sources=["invoice.png"],
    queries=["What is the total amount due?"],
)
```

### In a Haystack pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentCleaner
from haystack_integrations.components.converters.amazon_textract import AmazonTextractConverter

pipeline = Pipeline()
pipeline.add_component("converter", AmazonTextractConverter())
pipeline.add_component("cleaner", DocumentCleaner())
pipeline.connect("converter.documents", "cleaner.documents")

result = pipeline.run({"converter": {"sources": ["scan.png"]}})
```

### Explicit credentials

```python
from haystack.utils import Secret
from haystack_integrations.components.converters.amazon_textract import AmazonTextractConverter

converter = AmazonTextractConverter(
    aws_access_key_id=Secret.from_env_var("MY_AWS_KEY"),
    aws_secret_access_key=Secret.from_env_var("MY_AWS_SECRET"),
    aws_region_name=Secret.from_token("us-east-1"),
)
```

For more details on Amazon Textract capabilities and setup, refer to the [Amazon Textract documentation](https://docs.aws.amazon.com/textract/latest/dg/what-is.html).
