---
layout: integration
name: Pyversity
description: A Ranker component for result diversification in retrieval pipelines
authors:
  - name: Kacper Łukawski
    socials:
      github: kacperlukawski
      twitter: LukawskiKacper
      linkedin: https://www.linkedin.com/in/kacperlukawski/
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/pyversity-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/pyversity
type: Ranker
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

[Pyversity](https://github.com/Pringled/pyversity) is a library for result diversification in retrieval pipelines. This integration wraps pyversity's diversification algorithms as a Haystack component, making it easy to balance relevance and diversity in your search results.

The `PyversityRanker` reranks documents by trading off between relevance scores and embedding-based diversity using strategies such as Maximal Marginal Relevance (MMR) or Determinantal Point Processes (DPP).

## Installation

```bash
pip install pyversity-haystack
```

## Usage

### Components

This integration introduces one component:

- `PyversityRanker`: Reranks documents using pyversity's diversification algorithms. Documents must have both `score` and `embedding` populated (e.g. as returned by a dense retriever with `return_embedding=True`).

The ranker accepts the following parameters:

- `top_k`: Number of documents to return. If `None`, all documents are returned in diversified order.
- `strategy`: Diversification strategy (`Strategy.MMR` or `Strategy.DPP`). Defaults to `Strategy.DPP`.
- `diversity`: Trade-off between relevance and diversity in `[0, 1]`. `0.0` keeps only the most relevant documents; `1.0` maximises diversity. Defaults to `0.5`.

### Standalone

```python
from haystack import Document
from haystack_integrations.components.rankers.pyversity import PyversityRanker
from pyversity import Strategy

ranker = PyversityRanker(top_k=5, strategy=Strategy.MMR, diversity=0.5)

docs = [
    Document(content="Paris is the capital of France.", score=0.9, embedding=[0.1, 0.2]),
    Document(content="Berlin is the capital of Germany.", score=0.8, embedding=[0.3, 0.4]),
    Document(content="The Eiffel Tower is in Paris.", score=0.7, embedding=[0.15, 0.25]),
]
output = ranker.run(documents=docs)
reranked_docs = output["documents"]
```

### Pipeline

```python
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from pyversity import Strategy

from haystack_integrations.components.rankers.pyversity import PyversityRanker

# Index documents
document_store = InMemoryDocumentStore()

raw_documents = [
    Document(content="Paris is the capital of France."),
    Document(content="The Eiffel Tower is located in Paris."),
    Document(content="Berlin is the capital of Germany."),
    Document(content="The Brandenburg Gate is in Berlin."),
    Document(content="France borders Spain to the south."),
    Document(content="The Louvre is the world's largest art museum and is in Paris."),
]

doc_embedder = SentenceTransformersDocumentEmbedder()
documents_with_embeddings = doc_embedder.run(raw_documents)["documents"]
document_store.write_documents(documents_with_embeddings)

# Build pipeline
pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
pipeline.add_component(
    "retriever",
    InMemoryEmbeddingRetriever(document_store=document_store, top_k=6, return_embedding=True),
)
pipeline.add_component("reranker", PyversityRanker(top_k=3, strategy=Strategy.MMR, diversity=0.7))

pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
pipeline.connect("retriever.documents", "reranker.documents")

# Run
result = pipeline.run({"text_embedder": {"text": "What are the famous landmarks in France?"}})

for doc in result["reranker"]["documents"]:
    print(f"{doc.score:.4f}  {doc.content}")
```

## License

`pyversity-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
