---
layout: integration
name: Jina
description: Use Jina embedding models with Haystack
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

### **Table of Contents**

- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)

## Haystack 2.0

You can use [Jina embedding Models](https://jina.ai/embeddings) in your Haystack 2.0 pipelines with the Jina [Embedders](https://docs.haystack.deepset.ai/v2.0/docs/embedders).

### Installation

```bash
pip install jina-haystack
```

### Usage

You can use Jina Embedding models with two components: [JinaTextEmbedder](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/jina/src/jina_haystack/text_embedder.py) and [JinaDocumentEmbedder](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/jina/src/jina_haystack/document_embedder.py).

To create semantic embeddings for documents, use `JinaDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `JinaTextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and Jina API key. You can also
set the environment variable JINA_API_KEY instead of passing the api key as an argument.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `JinaDocumentEmbedder` and  `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from jina_haystack import JinaDocumentEmbedder

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="I enjoy programming in Python"),
             Document(content="My city does not get snow in winter"),
             Document(content="Japanese diet is well known for being good for your health"),
             Document(content="Thomas is injured and can't play sports")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", JinaDocumentEmbedder(api_key="JINA_API_KEY", model_name="jina-embeddings-v2-base-en"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

