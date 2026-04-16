---
layout: integration
name: Dewey
description: Connect Haystack pipelines to Dewey — a managed document intelligence backend that handles PDF conversion, chunking, embedding, and hybrid retrieval behind a single API.
authors:
    - name: Dewey
      socials:
        github: meetdewey
pypi: https://pypi.org/project/dewey-haystack
repo: https://github.com/meetdewey/dewey-haystack
type: Document Store
report_issue: https://github.com/meetdewey/dewey-haystack/issues
logo: /logos/dewey.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Dewey](https://meetdewey.com) is a managed document intelligence backend for AI applications. Upload PDFs, Word docs, and other files — Dewey handles conversion, section extraction, chunking, embedding, and hybrid semantic + BM25 retrieval automatically.

This integration provides three Haystack 2.0 components:

- **`DeweyDocumentStore`** — implements the Haystack `DocumentStore` protocol, backed by a Dewey collection
- **`DeweyRetriever`** — a `@component` that runs hybrid search against a collection and returns ranked `Document` objects
- **`DeweyResearchComponent`** — a `@component` that runs Dewey's full agentic research loop (multi-step search, synthesis, citations) and returns a grounded Markdown answer

## Installation

```bash
pip install dewey-haystack
```

Requires a free Dewey account at [meetdewey.com](https://meetdewey.com). Set your API key:

```bash
export DEWEY_API_KEY="dwy_live_..."
```

## Usage

### Components

This integration introduces three components:

- **`DeweyDocumentStore`** (`haystack_integrations.document_stores.dewey`)
- **`DeweyRetriever`** (`haystack_integrations.components.retrievers.dewey`)
- **`DeweyResearchComponent`** (`haystack_integrations.components.retrievers.dewey`)

### RAG pipeline with DeweyRetriever

```python
import os
from haystack import Pipeline
from haystack_integrations.document_stores.dewey import DeweyDocumentStore
from haystack_integrations.components.retrievers.dewey import DeweyRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

store = DeweyDocumentStore(
    api_key=Secret.from_env_var("DEWEY_API_KEY"),
    collection_id="3f7a1b2c-...",  # your collection ID
)

prompt_template = """
Answer the question using only the provided context.
Context: {% for doc in documents %}{{ doc.content }}{% endfor %}
Question: {{ query }}
"""

pipeline = Pipeline()
pipeline.add_component("retriever", DeweyRetriever(document_store=store, top_k=5))
pipeline.add_component("prompt", PromptBuilder(template=prompt_template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))

pipeline.connect("retriever.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.prompt")

result = pipeline.run({
    "retriever": {"query": "What are the key findings?"},
    "prompt": {"query": "What are the key findings?"},
})
print(result["llm"]["replies"][0])
```

### Agentic research with DeweyResearchComponent

`DeweyResearchComponent` is a drop-in replacement for an LLM generator when you want Dewey to handle both retrieval *and* generation. It runs a multi-step research loop internally and returns a grounded answer with cited sources.

```python
import os
from haystack import Pipeline
from haystack_integrations.components.retrievers.dewey import DeweyResearchComponent
from haystack.utils import Secret

pipeline = Pipeline()
pipeline.add_component(
    "research",
    DeweyResearchComponent(
        api_key=Secret.from_env_var("DEWEY_API_KEY"),
        collection_id="3f7a1b2c-...",
        depth="balanced",  # "quick" | "balanced" | "deep" | "exhaustive"
    ),
)

result = pipeline.run({"research": {"query": "What were the key findings across all studies?"}})
print(result["research"]["answer"])

for source in result["research"]["sources"]:
    print(f"  [{source.meta['filename']}] {source.content[:80]}...")
```

### Writing documents

Upload content to Dewey directly from a Haystack pipeline using `DeweyDocumentStore.write_documents`:

```python
from haystack import Document
from haystack_integrations.document_stores.dewey import DeweyDocumentStore
from haystack.utils import Secret

store = DeweyDocumentStore(
    api_key=Secret.from_env_var("DEWEY_API_KEY"),
    collection_id="3f7a1b2c-...",
)

store.write_documents([
    Document(content="Neural networks learn via backpropagation.", meta={"source": "ml-intro.txt"}),
    Document(content="Transformers use self-attention mechanisms.", meta={"source": "transformers.txt"}),
])
```

## License

`dewey-haystack` is released under the [MIT License](https://github.com/meetdewey/dewey-haystack/blob/main/LICENSE).
