---
layout: integration
name: Hugging Face
description: Use Models on Hugging Face with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/farm-haystack
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/huggingface.png
---

You can use models on [Hugging Face](https://huggingface.co/) in your Haystack pipelines with the [PromptNode](https://docs.haystack.deepset.ai/docs/prompt_node), [EmbeddingRetriever](https://docs.haystack.deepset.ai/docs/retriever#embedding-retrieval-recommended), [Ranker](https://docs.haystack.deepset.ai/docs/ranker), [Reader](https://docs.haystack.deepset.ai/docs/reader) and more!

## Installation

```bash
pip install farm-haystack
```

## Usage

You can use models on Hugging Face in various ways:

### Embedding Models

To use embedding models on Hugging Face, initialize an `EmbeddingRetriever` with the model name. You can then use this `EmbeddingRetriever` in an indexing pipeline to create semantic embeddings for documents and index them to a document store. 

Below is the example indexing pipeline with `PreProcessor`, `InMemoryDocumentStore` and  `EmbeddingRetriever`:

```python
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import Pipeline
from haystack.schema import Document

document_store = InMemoryDocumentStore(embedding_dim=384)
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2", document_store=document_store
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=preprocessor, name="Preprocessor", inputs=["File"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["Preprocessor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=["Retriever"])
indexing_pipeline.run(documents=[Document("This is my document")])
```

### Generative Models (LLMs) 

To use text generation models on Hugging Face, initialize a `PromptNode` with the model name and the prompt template. You can then use this `PromptNode` to generate questions from the given context.  

Below is the example of question generation pipeline using RAG with `EmbeddingRetriever` and  `PromptNode`:

```python
from haystack import Pipeline
from haystack.nodes import BM25Retriever, PromptNode

retriever = EmbeddingRetriever(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2", document_store=document_store
)
prompt_node = PromptNode(model_name_or_path = "mistralai/Mistral-7B-Instruct-v0.1",
                         api_key = "HF_API_KEY",
                         default_prompt_template = "deepset/question-generation")
query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "Berlin")
```

> If you would like to use the [Inference API](https://huggingface.co/inference-api), you need pass your Hugging Face token to PromptNode.


### Ranker Models

To use cross encoder models on Hugging Face, initialize a `SentenceTransformersRanker` with the model name. You can then use this `SentenceTransformersRanker` to sort documents based on their relevancy to the query.

Below is the example of document retrieval pipeline with `BM25Retriever` and  `SentenceTransformersRanker`:

```python
from haystack.nodes import SentenceTransformersRanker, BM25Retriever
from haystack.pipelines import Pipeline

retriever = BM25Retriever(document_store=document_store)
ranker = SentenceTransformersRanker(model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2")

document_retrieval_pipeline = Pipeline()
document_retrieval_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
document_retrieval_pipeline.add_node(component=ranker, name="Ranker", inputs=["Retriever"])
document_retrieval_pipeline.run("YOUR_QUERY")
```

### Reader Models

To use question answering models on Hugging Face, initialize a `FarmReader` with the model name. You can then use this `FarmReader` to extract answers from the relevant context.

Below is the example of extractive question answering pipeline with `BM25Retriever` and  `FARMReader`:

```python
from haystack.nodes import BM25Retriever, FARMReader
from haystack.pipelines import Pipeline

retriever = BM25Retriever(document_store=document_store)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

querying_pipeline = Pipeline()
querying_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
querying_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])
querying_pipeline.run("YOUR_QUERY")
```