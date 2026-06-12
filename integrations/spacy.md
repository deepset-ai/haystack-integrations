---
layout: integration
name: spaCy
description: Annotate named entities in your Haystack pipelines with spaCy models
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/spacy-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/spacy
type: Custom Component
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [Standalone](#standalone)
  - [Pipeline](#pipeline)
- [License](#license)

## Overview

[spaCy](https://spacy.io/) is a popular open-source library for Natural Language Processing in Python. The `spacy-haystack` integration provides the `SpacyNamedEntityExtractor`, which uses spaCy models to recognize named entities — such as people, organizations, and locations — and attach them to your documents.

## Installation

Install the `spacy-haystack` package:

```bash
pip install spacy-haystack
```

## Usage

### Components

This integration provides one component:

- [`SpacyNamedEntityExtractor`](https://docs.haystack.deepset.ai/docs/spacynamedentityextractor): annotates named entities in documents using a spaCy model.

When initializing it, you must set a `model`. Optionally, you can pass `pipeline_kwargs` (forwarded to the spaCy pipeline) and a `device` to run the model on.

### Standalone

The component works with any [spaCy model](https://spacy.io/models) that contains an NER component. `SpacyNamedEntityExtractor` accepts a list of `Documents`, annotates the text, and stores the result in each document's `meta` under the `named_entities` key. Use the `get_stored_annotations` helper to read the annotations back, and the span offsets to recover the entity text:

```python
from haystack import Document
from haystack_integrations.components.extractors.spacy import SpacyNamedEntityExtractor

extractor = SpacyNamedEntityExtractor(model="en_core_web_sm")

documents = [
    Document(content="My name is Clara and I live in Berkeley, California."),
    Document(content="New York State is home to the Empire State Building."),
]

results = extractor.run(documents=documents)["documents"]

for doc in results:
    print(doc.content)
    for ann in SpacyNamedEntityExtractor.get_stored_annotations(doc):
        print(f"  {ann.entity}: {doc.content[ann.start:ann.end]}")

# My name is Clara and I live in Berkeley, California.
#   PERSON: Clara
#   GPE: Berkeley
#   GPE: California
# New York State is home to the Empire State Building.
#   GPE: New York State
#   ORG: the Empire State Building
```

### Pipeline

The most common place for the extractor is right after the preprocessing step of an indexing pipeline, so that the entities are stored alongside the documents you write to a Document Store:

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.extractors.spacy import SpacyNamedEntityExtractor

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", TextFileToDocument())
pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=200))
pipeline.add_component("extractor", SpacyNamedEntityExtractor(model="en_core_web_sm"))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter", "splitter")
pipeline.connect("splitter", "extractor")
pipeline.connect("extractor", "writer")

pipeline.run({"converter": {"sources": ["document.txt"]}})

# Each stored document now carries its named entities in meta["named_entities"].
print(document_store.filter_documents()[0].meta["named_entities"])
```

## License

`spacy-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
