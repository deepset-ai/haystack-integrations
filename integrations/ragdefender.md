---
layout: integration
name: RAGDefender
description: Filter poisoned passages out of retrieved documents before they reach the LLM (ACSAC 2025)
authors:
    - name: Minseok Kim
      socials:
        github: DenisKimskku
pypi: https://pypi.org/project/ragdefender
repo: https://github.com/SecAI-Lab/RAGDefender
type: Custom Component
report_issue: https://github.com/SecAI-Lab/RAGDefender/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Standalone](#standalone)
  - [In a RAG pipeline](#in-a-rag-pipeline)
  - [Parameters](#parameters)
- [License](#license)

## Overview

[RAGDefender](https://github.com/SecAI-Lab/RAGDefender) defends RAG pipelines against knowledge-corruption attacks (PoisonedRAG, GARAG and similar), where an attacker plants passages in the corpus that are crafted to be retrieved for a target question and to steer the answer. It is the official implementation of *Rescuing the Unpoisoned: Efficient Defense against Knowledge Corruption Attacks on RAG Systems* (ACSAC 2025, [paper](https://doi.org/10.1109/ACSAC67867.2025.00093), [arXiv](https://arxiv.org/abs/2511.01268)).

The defense is purely post-retrieval. It embeds the retrieved passages, clusters them and drops the group that is abnormally concentrated around the query, which is the footprint of injected passages. There are no LLM calls, no training and no changes to your document store or retriever.

This integration provides `RAGDefenderFilter`, a Haystack component that sits between a retriever and a prompt builder. It takes `documents` and `query` and outputs the filtered `documents` plus the `removed_documents` it flagged. Document metadata, scores and order are preserved.

## Installation

```bash
pip install "ragdefender[haystack]"
```

The first run downloads the default sentence-embedding model (MiniLM).

## Usage

### Standalone

```python
from haystack import Document
from ragdefender.integrations import RAGDefenderFilter

defender = RAGDefenderFilter(task_type="single_hop")
defender.warm_up()

docs = [Document(content=text) for text in retrieved_texts]
result = defender.run(documents=docs, query="What is the capital of France?")

result["documents"]          # passages kept for the generator
result["removed_documents"]  # passages flagged as adversarial
```

### In a RAG pipeline

```python
from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from ragdefender.integrations import RAGDefenderFilter

document_store = InMemoryDocumentStore()
document_store.write_documents([Document(content=text) for text in corpus])

template = """Answer the question using only the passages below.
{% for doc in documents %}
{{ doc.content }}
{% endfor %}
Question: {{ question }}"""

pipe = Pipeline()
pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store, top_k=10))
pipe.add_component("defender", RAGDefenderFilter(task_type="single_hop"))
pipe.add_component("prompt", PromptBuilder(template=template, required_variables=["documents", "question"]))
pipe.add_component("llm", OpenAIGenerator())

pipe.connect("retriever.documents", "defender.documents")
pipe.connect("defender.documents", "prompt.documents")
pipe.connect("prompt.prompt", "llm.prompt")

question = "What is the capital of France?"
result = pipe.run({
    "retriever": {"query": question},
    "defender": {"query": question},
    "prompt": {"question": question},
})
print(result["llm"]["replies"][0])
```

`RAGDefenderFilter` implements `to_dict()` / `from_dict()`, so pipelines that include it serialize like any other.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `task_type` | required | `"single_hop"` for questions answered by one passage, `"multi_hop"` for questions that need several |
| `embedder` | `"minilm-all"` | sentence-embedding model used to compare passages |
| `device` | `"auto"` | `"cpu"`, `"cuda"` or `"auto"` |
| `min_passages` | `3` | retrieval sets smaller than this pass through unfiltered |
| `defender` | `None` | a pre-built `ragdefender.RAGDefender` to share one embedder across components |

The full parameter list and the adapters for other frameworks are documented in [docs/integrations.md](https://github.com/SecAI-Lab/RAGDefender/blob/main/docs/integrations.md#haystack-2x).

## License

RAGDefender is released under the MIT License.
