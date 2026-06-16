---
layout: integration
name: langdetect
description: Detect the language of documents and route text by language with langdetect
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/langdetect-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Custom Component
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `langdetect-haystack` integration provides two components for language detection in Haystack pipelines, built on top of the [`langdetect`](https://github.com/Mimino666/langdetect) library:

- [`DocumentLanguageClassifier`](https://docs.haystack.deepset.ai/docs/documentlanguageclassifier): classifies the language of each document and stores the detected language in the document's metadata.
- [`TextLanguageRouter`](https://docs.haystack.deepset.ai/docs/textlanguagerouter): routes a text string to a different output connection depending on its detected language.

Both components take a list of ISO language codes during initialization. If the detected language is not in that list, the document or text is labeled or routed as `"unmatched"`.

These components were previously part of Haystack core and now live in the `langdetect-haystack` integration package, maintained in [haystack-core-integrations](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/langdetect).

## Installation

Install the `langdetect-haystack` package:

```bash
pip install langdetect-haystack
```

## Usage

### DocumentLanguageClassifier

`DocumentLanguageClassifier` adds a `language` field to the metadata of each document. Combine it with the `MetadataRouter` to send documents to different branches of a pipeline based on their language:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.classifiers.langdetect import DocumentLanguageClassifier
from haystack.components.routers import MetadataRouter
from haystack.components.writers import DocumentWriter

docs = [
    Document(id="1", content="This is an English document"),
    Document(id="2", content="Este es un documento en español"),
]

document_store = InMemoryDocumentStore()

p = Pipeline()
p.add_component(instance=DocumentLanguageClassifier(languages=["en"]), name="language_classifier")
p.add_component(
    instance=MetadataRouter(rules={"en": {"field": "meta.language", "operator": "==", "value": "en"}}),
    name="router",
)
p.add_component(instance=DocumentWriter(document_store=document_store), name="writer")
p.connect("language_classifier.documents", "router.documents")
p.connect("router.en", "writer.documents")

p.run({"language_classifier": {"documents": docs}})

written_docs = document_store.filter_documents()
assert len(written_docs) == 1
assert written_docs[0].content == "This is an English document"
```

### TextLanguageRouter

`TextLanguageRouter` routes a query string to the output named after its detected language. Use it as the first component of a query pipeline to only forward queries in supported languages:

```python
from haystack import Pipeline, Document
from haystack_integrations.components.routers.langdetect import TextLanguageRouter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

document_store = InMemoryDocumentStore()
document_store.write_documents([Document(content="Elvis Presley was an American singer and actor.")])

p = Pipeline()
p.add_component(instance=TextLanguageRouter(languages=["en"]), name="text_language_router")
p.add_component(instance=InMemoryBM25Retriever(document_store=document_store), name="retriever")
p.connect("text_language_router.en", "retriever.query")

result = p.run({"text_language_router": {"text": "Who was Elvis Presley?"}})
assert result["retriever"]["documents"][0].content == "Elvis Presley was an American singer and actor."

result = p.run({"text_language_router": {"text": "ένα ελληνικό κείμενο"}})
assert result["text_language_router"]["unmatched"] == "ένα ελληνικό κείμενο"
```

## License

`langdetect-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
