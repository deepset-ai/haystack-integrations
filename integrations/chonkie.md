---
layout: integration
name: Chonkie
description: Fast, lightweight text chunking for Haystack indexing pipelines, powered by Chonkie.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/chonkie-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/chonkie
type: Data Ingestion
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/chonkie.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Token-based splitting](#token-based-splitting)
  - [Sentence-based splitting](#sentence-based-splitting)
  - [Recursive splitting](#recursive-splitting)
  - [Semantic splitting](#semantic-splitting)
  - [In a pipeline](#in-a-pipeline)
- [License](#license)

## Overview

[Chonkie](https://docs.chonkie.ai/) is a fast, lightweight chunking library designed for RAG applications. This integration provides four Haystack document splitter components backed by Chonkie's chunkers:

| Component | Chunking strategy |
|-----------|-------------------|
| `ChonkieTokenDocumentSplitter` | Fixed-size token-based chunks with configurable overlap |
| `ChonkieSentenceDocumentSplitter` | Chunks that respect sentence boundaries |
| `ChonkieRecursiveDocumentSplitter` | Hierarchical recursive splitting using a rule set |
| `ChonkieSemanticDocumentSplitter` | Embedding-based splitting at semantic topic boundaries |

All components accept a `list[Document]` and return a `list[Document]`. Each output document carries `source_id`, `page_number`, `split_id`, `split_idx_start`, `split_idx_end`, and `token_count` in its metadata.

## Installation

```bash
pip install chonkie-haystack
```

## Usage

### Token-based splitting

Split documents into fixed-size token chunks:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.chonkie import ChonkieTokenDocumentSplitter

chunker = ChonkieTokenDocumentSplitter(tokenizer="gpt2", chunk_size=10, chunk_overlap=2)
result = chunker.run(documents=[Document(content=(
    "Haystack is an open-source framework for building LLM applications. "
    "It supports retrieval-augmented generation and custom components. "
    "Developers can connect models, databases, and tools in a pipeline."
))])
print(result["documents"])
```

### Sentence-based splitting

Split documents while keeping sentence boundaries intact:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.chonkie import ChonkieSentenceDocumentSplitter

chunker = ChonkieSentenceDocumentSplitter(tokenizer="gpt2", chunk_size=10)
result = chunker.run(documents=[Document(content=(
    "Haystack is an open-source framework for building LLM applications. "
    "It supports retrieval-augmented generation and custom components. "
    "Developers can connect models, databases, and tools in a pipeline."
))])
print(result["documents"])
```

### Recursive splitting

Apply a hierarchy of splitting rules — useful for structured text like Markdown or code:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.chonkie import ChonkieRecursiveDocumentSplitter

chunker = ChonkieRecursiveDocumentSplitter(chunk_size=30)
result = chunker.run(documents=[Document(content=(
    "# Introduction\n\n"
    "Haystack is an open-source framework for building LLM applications.\n\n"
    "## Features\n\n"
    "It supports retrieval-augmented generation, custom components, and production pipelines.\n\n"
    "## Installation\n\n"
    "Install Haystack with pip and start building your first pipeline today."
))])
print(result["documents"])
```

### Semantic splitting

Split documents at topic boundaries detected via embedding similarity:

```python
from haystack import Document
from haystack_integrations.components.preprocessors.chonkie import ChonkieSemanticDocumentSplitter

chunker = ChonkieSemanticDocumentSplitter(chunk_size=512, threshold=0.5)
result = chunker.run(documents=[
    Document(content=(
        "Haystack is an open-source framework for building LLM applications. "
        "It supports retrieval-augmented generation and custom components. "
        "The Eiffel Tower is a wrought-iron landmark on the Champ de Mars in Paris. "
        "It was constructed between 1887 and 1889 as the centrepiece of the World's Fair."
    ))
])
print(result["documents"])
```

The embedding model is loaded lazily on the first `run()` call. No explicit `warm_up()` is needed.

### In a pipeline

All four components fit directly into a standard indexing pipeline:

```python
from pathlib import Path

from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.preprocessors.chonkie import ChonkieTokenDocumentSplitter

document_store = InMemoryDocumentStore()

p = Pipeline()
p.add_component("converter", TextFileToDocument())
p.add_component("cleaner", DocumentCleaner())
p.add_component("splitter", ChonkieTokenDocumentSplitter(tokenizer="gpt2", chunk_size=512))
p.add_component("writer", DocumentWriter(document_store=document_store))

p.connect("converter.documents", "cleaner.documents")
p.connect("cleaner.documents", "splitter.documents")
p.connect("splitter.documents", "writer.documents")

files = list(Path("path/to/your/files").glob("*.txt"))
p.run({"converter": {"sources": files}})
```

## License

`chonkie-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
