---
layout: integration
name: Lara
description: Translate Haystack documents using translated's Lara adaptive translation API
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/lara-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/lara
type: Custom Component
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/lara.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [API Keys](#api-keys)
- [Examples](#examples)
  - [Standalone](#standalone)
  - [Pipeline](#pipeline)
- [License](#license)

## Overview

[Lara](https://laratranslate.com/) is an adaptive translation API by [translated](https://translated.com/) that combines the fluency and context handling of LLMs with low hallucination and latency. It adapts to domains at inference time using optional context, instructions, translation memories, and glossaries.

Key features:

- **Translation styles**: Choose between `faithful`, `fluid`, or `creative` styles to control the balance between accuracy and natural flow.
- **Context-aware translation**: Provide surrounding text as context to improve translation quality without translating it.
- **Instruction-guided translation**: Use natural-language instructions to guide translations (e.g. "Be formal", "Use a professional tone").
- **Translation memories**: Adapt translations to the style and terminology of existing translation memories.
- **Glossaries**: Enforce consistent terminology (e.g. brand names, product terms) across translations.
- **Reasoning (Lara Think)**: Enable multi-step linguistic analysis for higher-quality translations.

For more details, see the [Lara SDK documentation](https://developers.laratranslate.com/docs/introduction) and the [Lara support documentation](https://support.laratranslate.com/en).

## Installation

```bash
pip install lara-haystack
```

## Usage

### Components

This integration provides one component:

- The `LaraDocumentTranslator`: translates the text content of Haystack `Document` objects using the Lara API.

### API Keys

To use the Lara integration, you need a Lara API access key ID and secret. You can obtain them from [Lara](https://laratranslate.com/).

Once obtained, export them as environment variables:

```bash
export LARA_ACCESS_KEY_ID="your-access-key-id"
export LARA_ACCESS_KEY_SECRET="your-access-key-secret"
```

By default, `LaraDocumentTranslator` reads the API credentials from these environment variables. You can also pass them explicitly using the Haystack [Secret](https://docs.haystack.deepset.ai/reference/utils-api#secret) utility.

## Examples

### Standalone

The following example translates a list of Documents from English to German:

```python
from haystack import Document
from haystack_integrations.components.translators.lara import LaraDocumentTranslator

translator = LaraDocumentTranslator(
    source_lang="en-US",
    target_lang="de-DE",
)

documents = [
    Document(content="Hello, world!"),
    Document(content="Goodbye, world!"),
]

result = translator.run(documents=documents)
for doc in result["documents"]:
    print(doc.content)
```

### Pipeline

You can use `LaraDocumentTranslator` in a Haystack pipeline. The following example converts text files to Documents, translates them, and writes them to an `InMemoryDocumentStore`:

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

from haystack_integrations.components.translators.lara import LaraDocumentTranslator

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", TextFileToDocument())
pipeline.add_component(
    "translator",
    LaraDocumentTranslator(source_lang="en-US", target_lang="es-ES"),
)
pipeline.add_component("writer", DocumentWriter(document_store=document_store))

pipeline.connect("converter", "translator")
pipeline.connect("translator", "writer")

pipeline.run({"converter": {"sources": ["filename.txt"]}})
print(document_store.filter_documents())
```

### License

`lara-haystack` is distributed under the terms of the
[Apache-2.0](https://opensource.org/license/apache-2-0) license.
