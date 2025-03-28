---
layout: integration
name: Voyage AI
description: Use text embeddings and rerankers from Voyage AI
authors:
  - name: Ashwin Mathur
    socials:
      github: awinml
      twitter: awinml
      linkedin: https://www.linkedin.com/in/ashwin-mathur-ds
pypi: https://pypi.org/project/voyage-embedders-haystack/
repo: https://github.com/awinml/voyage-embedders-haystack/tree/main
type: Model Provider
report_issue: https://github.com/awinml/voyage-embedders-haystack/issues
logo: /logos/voyage_ai.jpg
version: Haystack 2.0
toc: true
---

[![PyPI](https://img.shields.io/pypi/v/voyage-embedders-haystack)](https://pypi.org/project/voyage-embedders-haystack/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/voyage-embedders-haystack?logo=python&logoColor=gold)

### **Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)

[Voyage AI](https://voyageai.com/)’s embedding and ranking models, such as `voyage-2` and `voyage-large-2`, are state-of-the-art in retrieval accuracy. These models outperform top performing embedding models like `intfloat/e5-mistral-7b-instruct` and `OpenAI/text-embedding-3-large` on the [MTEB Benchmark](https://github.com/embeddings-benchmark/mteb). `voyage-2` is current ranked second on the [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard).

The available models can be found on the [Embeddings Documentation](https://docs.voyageai.com/embeddings/).

## Installation

```bash
pip install voyage-embedders-haystack
```

## Usage

You can use Voyage models with three components: [VoyageTextEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/haystack_integrations/components/embedders/voyage_embedders/voyage_text_embedder.py), [VoyageDocumentEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/haystack_integrations/components/embedders/voyage_embedders/voyage_document_embedder.py) and [VoyageRanker](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/haystack_integrations/components/rankers/voyage/ranker.py)

To create semantic embeddings for documents, use `VoyageDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `VoyageTextEmbedder`. For reranking, use `VoyageRanker` with [Voyage Rerankers](https://docs.voyageai.com/docs/reranker)

Once you've selected the suitable component for your specific use case, initialize the component with the model name and VoyageAI API key. You can also set the environment variable `VOYAGE_API_KEY` instead of passing the API key as an argument.

Information about the supported models, can be found on the [Embeddings Documentation](https://docs.voyageai.com/embeddings/).

To get an API key, please see the [Voyage AI website.](https://www.voyageai.com/)

## Example

Below is the example Semantic Search pipeline that uses the [Simple Wikipedia](https://huggingface.co/datasets/pszemraj/simple_wikipedia) Dataset from HuggingFace. You can find more examples in the [`examples`](https://github.com/awinml/voyage-embedders-haystack/tree/main/examples) folder.

Load the dataset:

```python
# Install HuggingFace Datasets using "pip install datasets"
from datasets import load_dataset
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore

# Import Voyage Embedders
from haystack_integrations.components.embedders.voyage_embedders import VoyageDocumentEmbedder, VoyageTextEmbedder

# Load first 100 rows of the Simple Wikipedia Dataset from HuggingFace
dataset = load_dataset("pszemraj/simple_wikipedia", split="validation[:100]")

docs = [
    Document(
        content=doc["text"],
        meta={
            "title": doc["title"],
            "url": doc["url"],
        },
    )
    for doc in dataset
]
```

Index the documents to the `InMemoryDocumentStore` using the `VoyageDocumentEmbedder` and `DocumentWriter`:

```python
doc_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
retriever = InMemoryEmbeddingRetriever(document_store=doc_store)
doc_writer = DocumentWriter(document_store=doc_store)

doc_embedder = VoyageDocumentEmbedder(
    model="voyage-law-2",
    input_type="document",
)
text_embedder = VoyageTextEmbedder(model="voyage-law-2", input_type="query")

# Indexing Pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=doc_embedder, name="DocEmbedder")
indexing_pipeline.add_component(instance=doc_writer, name="DocWriter")
indexing_pipeline.connect("DocEmbedder", "DocWriter")

indexing_pipeline.run({"DocEmbedder": {"documents": docs}})

print(f"Number of documents in Document Store: {len(doc_store.filter_documents())}")
print(f"First Document: {doc_store.filter_documents()[0]}")
print(f"Embedding of first Document: {doc_store.filter_documents()[0].embedding}")
```

Query the Semantic Search Pipeline using the `InMemoryEmbeddingRetriever` and `VoyageTextEmbedder`:

```python
text_embedder = VoyageTextEmbedder(model="voyage-law-2", input_type="query")

# Query Pipeline
query_pipeline = Pipeline()
query_pipeline.add_component(instance=text_embedder, name="TextEmbedder")
query_pipeline.add_component(instance=retriever, name="Retriever")
query_pipeline.connect("TextEmbedder.embedding", "Retriever.query_embedding")

# Search
results = query_pipeline.run({"TextEmbedder": {"text": "Which year did the Joker movie release?"}})

# Print text from top result
top_result = results["Retriever"]["documents"][0].content
print("The top search result is:")
print(top_result)
```

## License

`voyage-embedders-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/awinml/voyage-embedders-haystack/blob/main/LICENSE).
