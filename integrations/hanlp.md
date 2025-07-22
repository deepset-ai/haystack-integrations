---
layout: integration
name: HanLP
description: Use HanLP for Chinese text processing with Haystack
authors:
  - name: MaChi
    socials:
      github: mc112611
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/hanlp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/hanlp
type: Preprocessor
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/hanlp.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Configuration](#basic-configuration)
  - [Advanced Configuration](#advanced-configuration)
  - [Sentence Boundary Respect](#sentence-boundary-respect)
  - [Custom Splitting Functions](#custom-splitting-functions)

## Overview

You can use [HanLP (Han Language Processing)](https://github.com/hankcs/HanLP) in your Haystack pipelines or as a standalone component for Chinese text processing. HanLP is a comprehensive NLP library for Chinese language processing that provides advanced tokenization, sentence segmentation, and other linguistic analysis capabilities.

The integration provides a specialized `ChineseDocumentSplitter` component that understands the unique characteristics of Chinese text, such as the lack of spaces between words and the multi-character nature of Chinese words.

## Installation

```bash
pip install hanlp-haystack
```

## Usage

### Basic Configuration

Here's a simple example of how to use the `ChineseDocumentSplitter`:

```python
from haystack import Document, Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.preprocessors.hanlp import ChineseDocumentSplitter

# Create a document with Chinese text
doc = Document(content=
    "这是第一句话，这是第二句话，这是第三句话。"
    "这是第四句话，这是第五句话，这是第六句话！"
    "这是第七句话，这是第八句话，这是第九句话？"
)

# Initialize the splitter
splitter = ChineseDocumentSplitter(
    split_by="word",
    split_length=10,
    split_overlap=3,
    respect_sentence_boundary=True
)

# Warm up the component (loads the necessary models)
splitter.warm_up()

result = splitter.run(documents=[doc])
print(result["documents"])
```

### Advanced Configuration

The `ChineseDocumentSplitter` supports various configuration options:

```python
from haystack_integrations.components.preprocessors.hanlp import ChineseDocumentSplitter

splitter = ChineseDocumentSplitter(
    split_by="sentence",
    split_length=1000,
    split_overlap=200,
    split_threshold=0,
    respect_sentence_boundary=True,
    granularity="coarse"
)
```

**Available `split_by` options:**
- `word`: Split by Chinese words (default)
- `sentence`: Split by sentences using HanLP sentence tokenizer
- `passage`: Split by double line breaks (`\n\n`)
- `page`: Split by form feed (`\f`)
- `line`: Split by line breaks (`\n`)
- `period`: Split by periods (`.`)
- `function`: Use a custom splitting function

**Granularity options:**
- `coarse`: Coarse granularity Chinese word segmentation (default)
- `fine`: Fine granularity word segmentation

### Sentence Boundary Respect

When splitting by words, you can ensure that splits respect sentence boundaries:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.hanlp import ChineseDocumentSplitter

doc = Document(content=
    "这是第一句话，这是第二句话，这是第三句话。"
    "这是第四句话，这是第五句话，这是第六句话！"
    "这是第七句话，这是第八句话，这是第九句话？"
)

splitter = ChineseDocumentSplitter(
    split_by="word",
    split_length=10,
    split_overlap=3,
    respect_sentence_boundary=True
)
splitter.warm_up()
result = splitter.run(documents=[doc])
```

### Custom Splitting Functions

You can also use custom splitting functions for specialized text processing:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.hanlp import ChineseDocumentSplitter

def custom_chinese_split(text: str) -> list[str]:
    return text.split("。")

doc = Document(content="这是第一句话。这是第二句话。这是第三句话。")

splitter = ChineseDocumentSplitter(
    split_by="function",
    splitting_function=custom_chinese_split
)
splitter.warm_up()
result = splitter.run(documents=[doc])
```

### Integration with Haystack Pipelines

The `ChineseDocumentSplitter` integrates seamlessly with Haystack pipelines:

```python
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.preprocessors.hanlp import ChineseDocumentSplitter

document_store = InMemoryDocumentStore()

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("splitter", ChineseDocumentSplitter(
    split_by="word",
    split_length=1000,
    split_overlap=200,
    respect_sentence_boundary=True
))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("splitter", "writer")

chinese_documents = [
    Document(content="这是第一个文档的内容。"),
    Document(content="这是第二个文档的内容。"),
]

indexing_pipeline.run({"splitter": {"documents": chinese_documents}})
```

## License

`hanlp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. 
