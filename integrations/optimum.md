---
layout: integration
name: Optimum
description: High-performance inference using Hugging Face Optimum
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/optimum-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/optimum
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/huggingface.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
- [License](#license)

## Overview

[Hugging Face Optimum](https://huggingface.co/docs/optimum/index) is an extension of the
[Transformers](https://huggingface.co/docs/transformers/index) library that provides a set
of performance optimization tools to train and run models on targeted hardware with maximum
efficiency. Using Optimum, you can leverage the [ONNX Runtime](https://onnxruntime.ai/)
to automatically export models from the [Hugging Face Model Hub](https://huggingface.co/docs/hub/en/models-the-hub) and deploy them in pipelines to achieve significant improvements in performance.

## Installation

```bash
pip install optimum-haystack
```

## Usage

### Components

This integration introduces two components: [OptimumTextEmbedder](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/optimum/src/haystack_integrations/components/embedders/optimum/optimum_text_embedder.py) and [OptimumDocumentEmbedder](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/optimum/src/haystack_integrations/components/embedders/optimum/optimum_document_embedder.py).

To create semantic embeddings for documents, use `OptimumDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `OptimumTextEmbedder`.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `OptimumDocumentEmbedder` and `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.optimum import (
    OptimumDocumentEmbedder,
    OptimumEmbedderPooling,
)


document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="I enjoy programming in Python"),
             Document(content="My city does not get snow in winter"),
             Document(content="Japanese diet is well known for being good for your health"),
             Document(content="Thomas is injured and can't play sports")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", OptimumDocumentEmbedder(
    model="intfloat/e5-base-v2",
    normalize_embeddings=True,
    pooling_mode=OptimumEmbedderPooling.MEAN,
))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

## License

`optimum-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
