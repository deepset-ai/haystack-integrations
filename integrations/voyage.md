---
layout: integration
name: Voyage AI
description: A component for computing embeddings using Voyage AI embedding models - built for Haystack 2.0.
authors:
    - name: Ashwin Mathur
      socials:
        github: awinml
        twitter: awinml
        linkedin: ashwin-mathur-ds
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

Custom component for [Haystack](https://github.com/deepset-ai/haystack) (2.x) for creating embeddings using the [VoyageAI Embedding Models](https://voyageai.com/).

Voyage’s embedding models, `voyage-01` and `voyage-lite-01`, are state-of-the-art in retrieval accuracy. These models outperform top performing embedding models like `BAAI-bge` and `OpenAI text-embedding-ada-002` on the [MTEB Benchmark](https://github.com/embeddings-benchmark/mteb).


## Installation

```bash
pip install voyage-embedders-haystack
```

## Usage

You can use Voyage Embedding models with two components: [VoyageTextEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/voyage_embedders/voyage_text_embedder.py) and [VoyageDocumentEmbedder](https://github.com/awinml/voyage-embedders-haystack/blob/main/src/voyage_embedders/voyage_document_embedder.py).

To create semantic embeddings for documents, use `VoyageDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `VoyageTextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and Voyage AI API key. You can also
set the environment variable "VOYAGE_API_KEY" instead of passing the api key as an argument.

Information about the supported models, can be found on the [Embeddings Documentation.](https://docs.voyageai.com/embeddings/)

To get an API key, please see the [Voyage AI website.](https://www.voyageai.com/)


## Example

Below is the example Semantic Search pipeline that uses the [Simple Wikipedia](https://huggingface.co/datasets/pszemraj/simple_wikipedia) Dataset from HuggingFace. You can find more examples in the [`examples`](https://github.com/awinml/voyage-embedders-haystack/tree/main/examples) folder.  

Load the dataset:

```python
# Install HuggingFace Datasets using "pip install datasets"
from datasets import load_dataset
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import Document
from haystack.document_stores import InMemoryDocumentStore

# Import Voyage Embedders
from voyage_embedders.voyage_document_embedder import VoyageDocumentEmbedder
from voyage_embedders.voyage_text_embedder import VoyageTextEmbedder

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
doc_embedder = VoyageDocumentEmbedder(
    model_name="voyage-01",
    input_type="document",
    batch_size=8,
    api_key="VOYAGE_API_KEY",
)

# Indexing Pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=doc_embedder, name="DocEmbedder")
indexing_pipeline.add_component(instance=DocumentWriter(document_store=doc_store), name="DocWriter")
indexing_pipeline.connect(connect_from="DocEmbedder", connect_to="DocWriter")

indexing_pipeline.run({"DocEmbedder": {"documents": docs}})

print(f"Number of documents in Document Store: {len(doc_store.filter_documents())}")
print(f"First Document: {doc_store.filter_documents()[0]}")
print(f"Embedding of first Document: {doc_store.filter_documents()[0].embedding}")
```

Query the Semantic Search Pipeline using the `InMemoryEmbeddingRetriever` and `VoyageTextEmbedder`:
```python
text_embedder = VoyageTextEmbedder(model_name="voyage-01", input_type="query", api_key="VOYAGE_API_KEY)

# Query Pipeline
query_pipeline = Pipeline()
query_pipeline.add_component("TextEmbedder", text_embedder)
query_pipeline.add_component("Retriever", InMemoryEmbeddingRetriever(document_store=doc_store))
query_pipeline.connect("TextEmbedder", "Retriever")


# Search
results = query_pipeline.run({"TextEmbedder": {"text": "Which year did the Joker movie release?"}})

# Print text from top result
top_result = results["Retriever"]["documents"][0].content
print("The top search result is:")
print(top_result)
```

## License

`voyage-embedders-haystack` is distributed under the terms of the [Apache-2.0 license](https://github.com/awinml/voyage-embedders-haystack/blob/main/LICENSE).
