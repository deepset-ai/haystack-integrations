---
layout: integration
name: TwelveLabs
description: Use TwelveLabs Marengo multimodal embeddings and Pegasus video understanding with Haystack
authors:
    - name: Mohit Varikuti
      socials:
        github: mohit-twelvelabs
    - name: TwelveLabs
      socials:
        github: twelvelabs-io
        twitter: twelve_labs
        linkedin: https://www.linkedin.com/company/twelve-labs/
pypi: https://pypi.org/project/twelvelabs-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/twelvelabs
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/twelvelabs.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Video Understanding (Pegasus)](#video-understanding-pegasus)
  - [Embeddings (Marengo)](#embeddings-marengo)
  - [Indexing and retrieval pipeline](#indexing-and-retrieval-pipeline)
- [License](#license)

## Overview

[TwelveLabs](https://twelvelabs.io) builds video-native foundation models. This integration brings two of them to Haystack:

- **Marengo** — a multimodal embedding model that maps text, images, audio, and video into a single shared vector space. Embeddings produced from text are directly comparable (cosine similarity) with embeddings of images, audio, and video, which enables cross-modal retrieval (for example, searching a video collection with a text query).
- **Pegasus** — a video-language model that analyzes a video on the fly (its visuals **and** its own audio via ASR) and returns text, so a video becomes a `Document` whose content is the analysis — no frame extraction or separate transcription step.

Get a free API key at [playground.twelvelabs.io](https://playground.twelvelabs.io) and set it as the `TWELVELABS_API_KEY` environment variable.

## Installation

```bash
pip install twelvelabs-haystack
```

## Usage

This integration introduces three components:

- [`TwelveLabsVideoConverter`](https://docs.haystack.deepset.ai/docs/twelvelabsvideoconverter): turns videos into `Document`s using Pegasus.
- [`TwelveLabsTextEmbedder`](https://docs.haystack.deepset.ai/docs/twelvelabstextembedder): embeds a query string with Marengo.
- [`TwelveLabsDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/twelvelabsdocumentembedder): embeds the content of `Document`s with Marengo.

All components read the API key from the `TWELVELABS_API_KEY` environment variable by default, or you can pass it explicitly with `api_key=Secret.from_token("...")`.

### Video Understanding (Pegasus)

`TwelveLabsVideoConverter` analyzes each source video and returns a `Document` whose content is Pegasus's analysis. Sources may be publicly accessible direct video URLs or local file paths (uploaded to TwelveLabs, up to 200 MB).

```python
import os
from haystack_integrations.components.converters.twelvelabs import TwelveLabsVideoConverter

os.environ["TWELVELABS_API_KEY"] = "your-twelvelabs-api-key"

converter = TwelveLabsVideoConverter()
result = converter.run(sources=["https://example.com/clip.mp4"])

document = result["documents"][0]
print(document.content)   # Pegasus's description + transcript of the video
print(document.meta)      # includes asset_id, analysis_id, model, provider
```

You can steer the analysis with a custom `prompt`, and tune `temperature` and `max_tokens`:

```python
converter = TwelveLabsVideoConverter(
    prompt="Summarize this video in three bullet points and list any products shown.",
    temperature=0.2,
    max_tokens=1024,
)
```

### Embeddings (Marengo)

Use `TwelveLabsTextEmbedder` to embed a query, and `TwelveLabsDocumentEmbedder` to embed `Document`s. Because Marengo embeds into one shared space, these embeddings support cross-modal retrieval.

```python
import os
from haystack import Document
from haystack_integrations.components.embedders.twelvelabs import (
    TwelveLabsTextEmbedder,
    TwelveLabsDocumentEmbedder,
)

os.environ["TWELVELABS_API_KEY"] = "your-twelvelabs-api-key"

text_embedder = TwelveLabsTextEmbedder()
print(text_embedder.run(text="a cat playing piano")["embedding"])

doc_embedder = TwelveLabsDocumentEmbedder()
documents = [Document(content="a cat playing piano")]
documents = doc_embedder.run(documents=documents)["documents"]
print(documents[0].embedding)
```

### Indexing and retrieval pipeline

Below is an example that indexes `Document`s with `TwelveLabsDocumentEmbedder` and retrieves them with a text query embedded by `TwelveLabsTextEmbedder`:

```python
import os
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack_integrations.components.embedders.twelvelabs import (
    TwelveLabsTextEmbedder,
    TwelveLabsDocumentEmbedder,
)

os.environ["TWELVELABS_API_KEY"] = "your-twelvelabs-api-key"

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [
    Document(content="a cat playing piano"),
    Document(content="a dog catching a frisbee at the beach"),
    Document(content="a timelapse of a city skyline at night"),
]

# Indexing
indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", TwelveLabsDocumentEmbedder())
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")
indexing_pipeline.run({"embedder": {"documents": documents}})

# Retrieval
query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", TwelveLabsTextEmbedder())
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run({"text_embedder": {"text": "feline making music"}})
print(result["retriever"]["documents"][0].content)
```

## License

`twelvelabs-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
</content>
