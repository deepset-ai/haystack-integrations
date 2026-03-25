---
layout: integration
name: Tonic Textual
description: PII detection, transformation, and entity extraction for Haystack pipelines, powered by Tonic Textual.
authors:
    - name: Tonic AI
      socials:
        github: tonicai
pypi: https://pypi.org/project/textual-haystack/
repo: https://github.com/tonicai/textual-haystack
type: Custom Component
report_issue: https://github.com/tonicai/textual-haystack/issues
logo: /logos/tonic-textual.png
version: Haystack 2.0
toc: true
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Document Cleaning](#document-cleaning)
  - [Entity Extraction](#entity-extraction)
  - [Pipeline Usage](#pipeline-usage)
  - [Configuration](#configuration)
- [License](#license)

## Overview

[Tonic Textual](https://docs.tonic.ai/textual) is a PII detection and transformation platform powered by transformer-based NER models that identify 46+ entity types across 50+ languages.

`textual-haystack` provides two Haystack components:

| Component | Purpose |
|-----------|---------|
| `TonicTextualDocumentCleaner` | Synthesize or tokenize PII in document content before ingestion |
| `TonicTextualEntityExtractor` | Extract PII entities and store them as structured document metadata |

Use the document cleaner to sanitize documents before they enter your RAG pipeline — replacing real PII with realistic synthetic data or reversible placeholder tokens. Use the entity extractor to detect PII and attach structured metadata (entity type, value, location, confidence) to documents for hybrid retrieval, auditing, or compliance workflows.

## Installation

```bash
pip install textual-haystack
```

You will need a [Tonic Textual](https://textual.tonic.ai) API key:

```bash
export TONIC_TEXTUAL_API_KEY="your-api-key"
```

## Usage

### Document Cleaning

Sanitize documents before ingestion by synthesizing PII with realistic fake data:

```python
from haystack.dataclasses import Document
from haystack_integrations.components.tonic_textual import TonicTextualDocumentCleaner

cleaner = TonicTextualDocumentCleaner(generator_default="Synthesis")
result = cleaner.run(documents=[
    Document(content="Patient John Smith, DOB 03/15/1982, was admitted for chest pain.")
])
print(result["documents"][0].content)
# "Patient Maria Chen, DOB 07/22/1975, was admitted for chest pain."
```

Or tokenize PII with reversible placeholder tokens:

```python
cleaner = TonicTextualDocumentCleaner(generator_default="Redaction")
result = cleaner.run(documents=[
    Document(content="Contact Jane Doe at jane@example.com.")
])
print(result["documents"][0].content)
# "Contact [NAME_GIVEN_xxxx] [NAME_FAMILY_xxxx] at [EMAIL_ADDRESS_xxxx]."
```

### Entity Extraction

Detect PII entities and store them as structured metadata on documents:

```python
from haystack.dataclasses import Document
from haystack_integrations.components.tonic_textual import TonicTextualEntityExtractor

extractor = TonicTextualEntityExtractor()
result = extractor.run(documents=[
    Document(content="My name is John Smith and my email is john@example.com.")
])

for entity in TonicTextualEntityExtractor.get_stored_annotations(result["documents"][0]):
    print(f"{entity.entity}: {entity.text} (confidence: {entity.score:.2f})")
# NAME_GIVEN: John (confidence: 0.90)
# NAME_FAMILY: Smith (confidence: 0.90)
# EMAIL_ADDRESS: john@example.com (confidence: 0.95)
```

Annotations are stored in `doc.meta["named_entities"]` as `PiiEntityAnnotation` dataclass instances with `entity`, `text`, `start`, `end`, and `score` fields.

### Pipeline Usage

Both components accept and return `list[Document]`, so they slot directly into any Haystack pipeline. Here they are chained together — clean PII first, then extract entities from the cleaned text:

```python
from haystack import Pipeline
from haystack.dataclasses import Document
from haystack_integrations.components.tonic_textual import (
    TonicTextualDocumentCleaner,
    TonicTextualEntityExtractor,
)

pipeline = Pipeline()
pipeline.add_component("cleaner", TonicTextualDocumentCleaner(generator_default="Synthesis"))
pipeline.add_component("extractor", TonicTextualEntityExtractor())
pipeline.connect("cleaner", "extractor")

result = pipeline.run({
    "cleaner": {
        "documents": [
            Document(content="Contact Jane Doe at jane@example.com or (555) 867-5309."),
        ]
    }
})

for doc in result["extractor"]["documents"]:
    entities = TonicTextualEntityExtractor.get_stored_annotations(doc)
    print(f"Cleaned: {doc.content}")
    print(f"Entities: {[(e.entity, e.text) for e in entities]}")
```

### Configuration

**Per-entity control** — mix synthesis and tokenization per PII type:

```python
cleaner = TonicTextualDocumentCleaner(
    generator_default="Off",
    generator_config={
        "NAME_GIVEN": "Synthesis",
        "NAME_FAMILY": "Synthesis",
        "EMAIL_ADDRESS": "Redaction",
        "US_SSN": "Redaction",
    },
)
```

**Self-hosted deployment:**

```python
cleaner = TonicTextualDocumentCleaner(
    base_url="https://textual.your-company.com"
)
```

**Explicit API key:**

```python
from haystack.utils.auth import Secret

cleaner = TonicTextualDocumentCleaner(
    api_key=Secret.from_token("your-api-key")
)
```

## License

`textual-haystack` is licensed under the [MIT License](https://github.com/tonicai/textual-haystack/blob/main/LICENSE).
