---
layout: integration
name: Jina AI
description: Use the latest Jina AI embedding models
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/jina-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/jina
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/jina.png
version: Haystack 2.0
toc: true
---

This integration allows users of Haystack to seamlessly use Jina AI's `jina-embeddings`and [reranking models](https://jina.ai/reranker/) in their pipelines. Haystack also integrates the [Jina Reader API](https://jina.ai/reader/).

[Jina AI](https://jina.ai/embeddings/) is a multimodal AI company, with a vision to revolutionize the way we interpret and interact with information with its prompt and model technologies.

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

Include `task` in your request to tailor the model for your specific application:

- **retrieval.query**: Used to encode user queries or questions in retrieval tasks.
- **retrieval.passage**: Used to encode large documents in retrieval tasks at indexing time.
- **classification**: Used to encode text for text classification tasks.
- **text-matching**: Used to encode text for similarity matching, such as measuring similarity between two sentences.
- **separation**: Used for clustering or reranking tasks.

**Matryoshka Representation Learning**:

`jina-embeddings-v3` supports Matryoshka Representation Learning, allowing users to control embedding dimensions with minimal performance impact. Specify `dimensions` in your request to select the desired dimension.

> **Note:** The default dimension is 1024, with recommended values ranging from 256 to 1024.

You can reference the table below for hints on dimension vs. performance:

|                Dimension                |  32   |  64   |  128  |  256  |  512  | 768  | 1024  |
| :-------------------------------------: | :---: | :---: | :---: | :---: | :---: | :--: | :---: |
| Average Retrieval Performance (nDCG@10) | 52.54 | 58.54 | 61.64 | 62.72 | 63.16 | 63.3 | 63.35 |

**Late Chunking in Long-Context Embedding Models**

`jina-embeddings-v3` supports [Late Chunking](https://jina.ai/news/late-chunking-in-long-context-embedding-models/), the technique to leverage the model's long-context capabilities for generating contextual chunk embeddings. Include `late_chunking=True` in your request to enable contextual chunked representation. When set to true, Jina AI API will concatenate all sentences in the input field and feed them as a single string to the model. Internally, the model embeds this long concatenated string and then performs late chunking, returning a list of embeddings that matches the size of the input list.

### **Table of Contents**

- [Overview](#overview)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Embedding Models](#embedding-models)
    - [Jina Reader API](#jina-reader-api)

## Overview

You can use [Jina embedding Models](https://jina.ai/embeddings) and [Jina Rerankers](https://jina.ai/reranker/) in your Haystack pipelines with the Jina [Embedders](https://docs.haystack.deepset.ai/docs/embedders) and Jina [Ranker](https://docs.haystack.deepset.ai/docs/jinaranker).

## Installation

```bash
pip install jina-haystack
```

## Usage

### Embedding Models

You can use Jina Embedding models with three components: [`JinaTextEmbedder`](https://docs.haystack.deepset.ai/docs/jinatextembedder), [`JinaDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/jinadocumentembedder), and [`JinaDocumentImageEmbedder`](https://docs.haystack.deepset.ai/docs/jinadocumentimageembedder).

You can use the Jina Reranker models with one component: [`JinaRanker`](https://docs.haystack.deepset.ai/docs/jinaranker).

To create semantic embeddings for documents, use `JinaDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `JinaTextEmbedder`. For image-based embeddings, use `JinaDocumentImageEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and Jina API key. You can also
set the environment variable `JINA_API_KEY` instead of passing the api key as an argument.

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
indexing_pipeline.add_component(
  "embedder",
  JinaDocumentEmbedder(
    api_key=Secret.from_token("<your-api-key>"),
    model="jina-embeddings-v3",
    dimensions=1024,
    task="retrieval.passage",
    late_chunking=True,
  )
)
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

#### Image Embedding

  For embedding images, you can use `JinaDocumentImageEmbedder` with Jina's multimodal models that support both text and image
   inputs:

  **Supported Models:**
  - `jina-clip-v1`: Basic multimodal model for text-image tasks
  - `jina-clip-v2`: Advanced model with higher resolution support (512×512) and improved performance
  - `jina-embeddings-v4`: Unified embeddings for text, images, and visual documents

  **Key Features:**
  - **Image resizing**: Automatically resize images to optimal dimensions
  - **Batch processing**: Process multiple images efficiently with configurable batch sizes
  - **PDF support**: Extract and embed images from PDF documents
  - **Multiple formats**: Support for JPEG, PNG, and PDF files

  Below is an example indexing pipeline for images using `JinaDocumentImageEmbedder`:

  ```python
  import os
  from haystack import Document, Pipeline
  from haystack.document_stores.in_memory import InMemoryDocumentStore
  from haystack.components.writers import DocumentWriter
  from haystack.utils import Secret
  from haystack_integrations.components.embedders.jina import JinaDocumentImageEmbedder

  os.environ["JINA_API_KEY"] = "your-jina-api-key"

  document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

  # Documents with image file paths
  documents = [
      Document(content="A cat sitting on a chair", meta={"file_path": "cat.jpg"}),
      Document(content="A dog running in the park", meta={"file_path": "dog.png"}),
      Document(content="City skyline at sunset", meta={"file_path": "city.jpeg"}),
  ]

  indexing_pipeline = Pipeline()
  indexing_pipeline.add_component(
      "image_embedder",
      JinaDocumentImageEmbedder(
          api_key=Secret.from_token("<your-api-key>"),
          model="jina-clip-v2",  # Recommended for image tasks
          embedding_dimension=768,
          image_size=(512, 512),  # Optional: resize images
          batch_size=5,  # Process 5 images per API call
      )
  )
  indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
  indexing_pipeline.connect("image_embedder", "writer")

  indexing_pipeline.run({"image_embedder": {"documents": documents}})

  The JinaDocumentImageEmbedder automatically:
  - Loads images from the file paths specified in document metadata
  - Converts images to the appropriate format for the Jina API
  - Resizes images if image_size is specified
  - Processes multiple images in batches for optimal performance
  - Supports PDF documents by extracting individual pages as images
```


### Jina Reader API

The Jina Reader API converts a URL/query into a LLM-friendly format.
It supports three modes of operation:
- `read`: process a URL and return the textual content of the page.
- `search`: search the web and return textual content of the most relevant pages.
- `ground`: call the grounding engine to perform fact checking.

In Haystack, you can use the Jina Reader API with the [`JinaReaderConnector`](https://docs.haystack.deepset.ai/reference/integrations-jina#jinareaderconnector) component.

Below is an example of using the `JinaReaderConnector` in `read` mode:

```python
import os
from haystack_integrations.components.connectors.jina import JinaReaderConnector

os.environ["JINA_API_KEY"]="your-jina-api-key"

reader = JinaReaderConnector(mode="read")
query = "https://example.com"
result = reader.run(query=query)
document = result["documents"][0]
print(document.content)

>>> "This domain is for use in illustrative examples..."
```

You can find more examples [here](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/jina/examples/jina_reader_connector.py).
