---
layout: integration
name: Jina AI
description: Use the latest Jina AI embedding models
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: https://pypi.org/project/jina-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/jina
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/jina.png
version: Haystack 2.0
toc: true
---

This integration allows users of Haystack to seamlessly use Jina AI's`jina-embeddings`and [reranking models](https://jina.ai/reranker/) in their pipelines. [Jina AI](https://jina.ai/embeddings/) is a multimodal AI company, with a vision to revolutionize the way we interpret and interact with information with its prompt and model technologies.

Jina AI offers several models so people can use and chose whatever fits best to their needs:

|           Model            | Dimension |          Language           | MRL (matryoshka) | Context |
| :------------------------: | :-------: | :-------------------------: | :--------------: | :-----: |
|     jina-embeddings-v3     |   1024    | Multilingual (89 languages) |       Yes        |  8192   |
| jina-embeddings-v2-base-en |    768    |           English           |        No        |  8192   |
| jina-embeddings-v2-base-de |    768    |      German & English       |        No        |  8192   |
| jina-embeddings-v2-base-es |    768    |      Spanish & English      |        No        |  8192   |
| jina-embeddings-v2-base-zh |    768    |      Chinese & English      |        No        |  8192   |

**Recommended Model: jina-embeddings-v3 :**

We recommend `jina-embeddings-v3` as the latest and most performant embedding model from Jina AI. This model features 5 task-specific adapters trained on top of its backbone, optimizing various embedding use cases.

**Task-Specific Adapters:**

Include `task_type` in your request to tailor the model for your specific application:

- **retrieval.query**: Used to encode user queries or questions in retrieval tasks.
- **retrieval.passage**: Used to encode large documents in retrieval tasks at indexing time.
- **classification**: Used to encode text for text classification tasks.
- **text-matching**: Used to encode text for similarity matching, such as measuring similarity between two sentences.
- **separation**: Used for clustering or reranking tasks.

**Matryoshka Representation Learning**:

`jina-embeddings-v3` supports Matryoshka Representation Learning, allowing users to control embedding dimensions with minimal performance impact. Specify `dimensions` in your request to select the desired dimension.

> **Note:** The default dimension is 1024, with recommended values ranging from 256 to 1024.

### **Table of Contents**

- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)

## Haystack 2.0

You can use [Jina embedding Models](https://jina.ai/embeddings) and [Jina Rerankers](https://jina.ai/reranker/) in your Haystack 2.0 pipelines with the Jina [Embedders](https://docs.haystack.deepset.ai/docs/embedders) and Jina [Rankers](https://docs.haystack.deepset.ai/docs/rankers)

### Installation

```bash
pip install jina-haystack
```

### Usage

You can use Jina Embedding models with two components: [`JinaTextEmbedder`](https://docs.haystack.deepset.ai/docs/jinatextembedder) and [`JinaDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/jinadocumentembedder).

You can use the Jina Reranker models with one component: [`JinaRanker`](https://docs.haystack.deepset.ai/docs/jinaranker)

To create semantic embeddings for documents, use `JinaDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `JinaTextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and Jina API key. You can also
set the environment variable JINA_API_KEY instead of passing the api key as an argument.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `JinaDocumentEmbedder` and `DocumentWriter`:

```python
import os
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.jina import JinaDocumentEmbedder

os.environ["JINA_API_KEY"]="your-jina-api-key"

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="I enjoy programming in Python"),
             Document(content="My city does not get snow in winter"),
             Document(content="Japanese diet is well known for being good for your health"),
             Document(content="Thomas is injured and can't play sports")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", JinaDocumentEmbedder(model="jina-embeddings-v3", dimensions=1024, task_type="retrieval.passage")
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```
