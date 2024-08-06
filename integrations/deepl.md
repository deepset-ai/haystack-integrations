---
layout: integration
name: DeepL
description: Use DeepL translation services with Haystack
authors:
    - name: Dribia Data Research
      socials:
        github: dribia
        linkedin: https://www.linkedin.com/company/dribia
pypi: https://pypi.org/project/deepl-haystack/
repo: https://github.com/dribia/deepl-haystack
type: Custom Component
report_issue: https://github.com/dribia/deepl-haystack/issues
logo: /logos/deepl.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
- [Examples](#examples)
  - [Standalone](#standalone)
  - [Pipeline](#pipeline)
- [License](#license)

## Overview

[DeepL](https://www.deepl.com/) is a powerful translation services provider, offering high-quality translations 
in multiple languages. This integration allows you to use DeepL's translation services with Haystack. 

## Installation

```console
pip install deepl-haystack
```

## Usage

### Components

The DeepL Haystack integration introduces two components that can be used to
obtain translations using the [DeepL API](https://www.deepl.com/en/pro-api).

- The `DeepLTextTranslator` to translate plain text (Python strings).
- The `DeepLDocumentTranslator` to translate Haystack `Document` objects.

### API Key

To use the DeepL Haystack integration, you'll need to provide a DeepL API key.
You can get one by signing up at the [DeepL API website](https://www.deepl.com/en/pro#developer).

Once obtained, **make sure to export it as an environment variable named `DEEPL_API_KEY`**
in you working environment before running the examples below. Both the `DeepLTextTranslator`
and the `DeepLDocumentTranslator` component constructors will expect this variable to be set.

An alternative way to provide the API key, although not recommended, would be to pass it through the
`api_key` parameter of the components' constructor, using the Haystack
[Secret](https://docs.haystack.deepset.ai/reference/utils-api#secret) utility.

## Examples

### Standalone

The following example shows how to translate a simple text:

```python
from deepl_haystack import DeepLTextTranslator

translator = DeepLTextTranslator(source_lang="EN", target_lang="ES")

translated_text = translator.run("Hello, world!")
print(translated_text)
# {'translation': '¡Hola, mundo!', 'meta': {'source_lang': 'EN', 'target_lang': 'ES'}}
```

Here, instead, we show how to translate a list of `Document` objects:

```python
from haystack.dataclasses import Document

from deepl_haystack import DeepLDocumentTranslator

translator = DeepLDocumentTranslator(source_lang="EN", target_lang="ES")

documents_to_translate = [
    Document(content="Hello, world!"),
    Document(content="Goodbye, Joe!", meta={"name": "Joe"}),
]

translated_documents = translator.run(documents_to_translate)
print(
    "\n".join(
        [f"{doc.content}, {doc.meta}" for doc in translated_documents["documents"]]
    )
)
# ¡Hola, mundo!, {'source_lang': 'EN', 'target_lang': 'ES'}
# ¡Adiós, Joe!, {'name': 'Joe', 'source_lang': 'EN', 'target_lang': 'ES'}
```

### Pipeline

To use the DeepL components in a Haystack pipeline, 
you can use them as any other Haystack component.

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.dataclasses.byte_stream import ByteStream
from haystack.document_stores.in_memory import InMemoryDocumentStore

from deepl_haystack import DeepLDocumentTranslator

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component(instance=TextFileToDocument(), name="converter")
pipeline.add_component(
    instance=DeepLDocumentTranslator(target_lang="ES"),
    name="translator",
)
pipeline.add_component(
    instance=DocumentWriter(document_store=document_store), name="document_store"
)
pipeline.connect("converter", "translator")
pipeline.connect("translator", "document_store")
pipeline.run({"converter": {"sources": [ByteStream.from_string("Hello world!")]}})
print(document_store.filter_documents())
# [Document(id=..., content: '¡Hola, mundo!', meta: {'source_lang': 'EN', 'language': 'ES'})]
```

### License

`deepl-haystack` is distributed under the terms of the
[MIT](https://opensource.org/license/mit) license.
