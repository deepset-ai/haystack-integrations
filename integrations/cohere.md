---
layout: integration
name: Cohere
description: Use Cohere with Haystack
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
logo: /logos/cohere.png
---

You can use [Cohere Models](https://cohere.com/) in your Haystack pipelines with the [EmbeddingRetriever](https://docs.haystack.deepset.ai/docs/retriever#embedding-retrieval-recommended), [PromptNode](https://docs.haystack.deepset.ai/docs/prompt_node), and [CohereRanker](https://docs.haystack.deepset.ai/docs/ranker#cohereranker).

## Installation

```bash
pip install farm-haystack
```

## Usage

You can use Cohere models in various ways:

### Embedding Models

To use `/embed` models from Cohere, initialize an `EmbeddingRetriever` with the model name and Cohere API key. You can then use this `EmbeddingRetriever` in an indexing pipeline to create Cohere embeddings for documents and index them to a document store. 

Below is the example indexing pipeline with `PreProcessor`, `InMemoryDocumentStore` and  `EmbeddingRetriever`:

```python
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import Pipeline
from haystack.schema import Document

document_store = InMemoryDocumentStore(embedding_dim=768)
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(
    embedding_model="embed-multilingual-v2.0", document_store=document_store, api_key=COHERE_API_KEY
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=preprocessor, name="Preprocessor", inputs=["File"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["Preprocessor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=["Retriever"])
indexing_pipeline.run(documents=[Document("This is my document")])
```

### Generative Models (LLMs) 

To use `/generate` models from Cohere, initialize a `PromptNode` with the model name, Cohere API key and the prompt template. You can then use this `PromptNode` in a question answering pipeline to generate answers based on the given context.  

Below is the example of generative questions answering pipeline using RAG with `EmbeddingRetriever` and  `PromptNode`:

```python
from haystack.nodes import PromptNode, EmbeddingRetriever
from haystack.pipelines import Pipeline

retriever = EmbeddingRetriever(
    embedding_model="embed-english-v2.0", document_store=document_store, api_key=COHERE_API_KEY
)
prompt_node = PromptNode(model_name_or_path="command", api_key=COHERE_API_KEY, default_prompt_template="deepset/question-answering")

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
query_pipeline.run("YOUR_QUERY")
```

### Ranker Models

To use `/rerank` models from Cohere, initialize a `CohereRanker` with the model name, and Cohere API key. You can then use this `CohereRanker` to sort documents based on their relevancy to the query.

Below is the example of document retrieval pipeline with `BM25Retriever` and  `CohereRanker`:

```python
from haystack.nodes import CohereRanker, BM25Retriever
from haystack.pipelines import Pipeline

retriever = BM25Retriever(document_store=document_store)
ranker = CohereRanker(api_key=COHERE_API_KEY, model_name_or_path="rerank-english-v2.0")

document_retrieval_pipeline = Pipeline()
document_retrieval_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
document_retrieval_pipeline.add_node(component=ranker, name="Ranker", inputs=["Retriever"])
document_retrieval_pipeline.run("YOUR_QUERY")
```