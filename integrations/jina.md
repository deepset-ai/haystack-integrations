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

This integration allows users of Haystack to seamlessly use Jina AI's `jina-embeddings-v2` and [reranking models](https://jina.ai/reranker/) in their pipelines. [Jina AI](https://jina.ai/embeddings/) is a multimodal AI company, with a vision to revolutionize the way we interpret and interact with information with its prompt and model technologies.
 
Jina Embeddings v2 are state-of-the-art models, trained to understand and process large volumes of text data efficiently. The unique selling points include:

1. Extended Document Handling: The ability to process and encode up to 8192 tokens is crucial for enterprises dealing with lengthy documents, such as legal documents, technical manuals, or comprehensive reports.
2. Enhanced Semantic Understanding: The extended context length allows for a richer and more nuanced understanding of text, improving applications like document summarization, topic extraction, and semantic search.
3. Efficient Information Retrieval and Clustering: For tasks requiring clustering or retrieval of large documents, the model's capability to handle extended texts ensures more accurate and relevant results.

Jina AI is paving the way towards the future of AI as a multimodal reality. We recognize that the existing machine learning and software ecosystems face challenges in handling multimodal AI. Our vision is to play a crucial role in helping the world harness the vast potential of multimodal AI and truly revolutionize the way we interpret and interact with information.

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

Below is the example indexing pipeline with `InMemoryDocumentStore`, `JinaDocumentEmbedder` and  `DocumentWriter`:

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
indexing_pipeline.add_component("embedder", JinaDocumentEmbedder(model="jina-embeddings-v2-base-en"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

