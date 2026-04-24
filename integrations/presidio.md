---
layout: integration
name: Presidio
description: PII detection and anonymization for Haystack Documents and text strings, powered by Microsoft Presidio.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Shahmeer Ali
      socials:
        github: SyedShahmeerAli12
pypi: https://pypi.org/project/presidio-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/presidio
type: Custom Component
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/microsoft.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Document Cleaning](#document-cleaning)
  - [Text Cleaning](#text-cleaning)
  - [Entity Extraction](#entity-extraction)
- [License](#license)

## Overview

[Microsoft Presidio](https://microsoft.github.io/presidio/) is an open-source library for PII detection and anonymization using NLP-based entity recognition.

`presidio-haystack` provides three Haystack components:

| Component | Input | Purpose |
|-----------|-------|---------|
| `PresidioDocumentCleaner` | `list[Document]` | Replace PII in document text with entity type placeholders |
| `PresidioTextCleaner` | `list[str]` | Replace PII in plain strings — useful for sanitizing user queries |
| `PresidioEntityExtractor` | `list[Document]` | Detect PII and store entities as structured document metadata |

All components run locally — no external API required. Presidio uses spaCy NLP models under the hood.

## Installation

```bash
pip install presidio-haystack
```

`en_core_web_lg` is the recommended English model for best accuracy. For a lighter footprint, `en_core_web_sm` works too — see the [full list of spaCy models](https://spacy.io/models/en) for options.

Each component accepts a `language` parameter (default `"en"`). To use a non-English language, specify the language code, and provide a model mapping, unless you want to use the large one.


## Usage

### Document Cleaning

Replace PII in document content before indexing:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.presidio import PresidioDocumentCleaner

cleaner = PresidioDocumentCleaner()
result = cleaner.run(documents=[
    Document(content="Contact Alice Smith at alice@example.com or 212-555-1234.")
])
print(result["documents"][0].content)
# Contact <PERSON> at <EMAIL_ADDRESS> or <PHONE_NUMBER>.
```

Original documents are not mutated. Documents with no text content pass through unchanged.

### Text Cleaning

Sanitize user queries before they reach your LLM:

```python
from haystack_integrations.components.preprocessors.presidio import PresidioTextCleaner

cleaner = PresidioTextCleaner()
result = cleaner.run(texts=["My name is John Doe, my SSN is 123-45-6789"])
print(result["texts"][0])
# My name is <PERSON>, my SSN is <US_SSN>
```

### Entity Extraction

Detect PII and attach it as structured metadata without modifying the document text:

```python
from haystack import Document
from haystack_integrations.components.extractors.presidio import PresidioEntityExtractor

extractor = PresidioEntityExtractor()
result = extractor.run(documents=[
    Document(content="Contact Alice at alice@example.com")
])
print(result["documents"][0].meta["entities"])
# [{"entity_type": "PERSON", "start": 8, "end": 13, "score": 0.85},
#  {"entity_type": "EMAIL_ADDRESS", "start": 17, "end": 34, "score": 1.0}]
```

All three components accept `language`, `entities`, and `score_threshold` parameters at init time. See [Presidio supported entities](https://microsoft.github.io/presidio/supported_entities/) for the full list of detectable PII types.

## License

`presidio-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
