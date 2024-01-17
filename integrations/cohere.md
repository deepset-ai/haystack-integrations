---
layout: integration
name: Cohere
description: Use Cohere models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/cohere-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/cohere
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/cohere.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)
- [Haystack 1.x](#haystack-1x)
  - [Installation (1.x)](#installation-1x)
  - [Usage (1.x)](#usage-1x)

## Haystack 2.0

You can use [Cohere Models](https://cohere.com/) in your Haystack 2.0 pipelines with the [Generators](https://docs.haystack.deepset.ai/v2.0/docs/generators) and [Embedders](https://docs.haystack.deepset.ai/v2.0/docs/embedders).

### Installation

```bash
pip install cohere-haystack
```

### Usage

You can use Cohere models in various ways:

#### Embedding Models

You can leverage `/embed` models from Cohere through two components: [CohereTextEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/coheretextembedder) and [CohereDocumentEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/coheredocumentembedder). These components support both **Embed v2** and **Embed v3** models.

To create semantic embeddings for documents, use `CohereDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `CohereTextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with the model name and Cohere API key.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `CohereDocumentEmbedder` and  `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from cohere_haystack.embedders.document_embedder import CohereDocumentEmbedder

document_store = InMemoryDocumentStore()

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="People speak French in France"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", CohereDocumentEmbedder(api_key="COHERE_API_KEY", model="embed-multilingual-v3.0", input_type="search_document"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

#### Generative Models (LLMs) 

To use `/generate` models from Cohere, initialize a [CohereGenerator](https://docs.haystack.deepset.ai/v2.0/docs/coheregenerator) with the model name and Cohere API key. You can then use this `CohereGenerator` in a question answering pipeline after the `PromptBuilder`.   

Below is the example of generative questions answering pipeline using RAG with `PromptBuilder` and  `CohereGenerator`:

```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.builders.prompt_builder import PromptBuilder
from cohere_haystack.embedders.text_embedder import CohereTextEmbedder
from cohere_haystack.generator import CohereGenerator

template = """
Given the following information, answer the question.

Context: 
{% for document in documents %}
    {{ document.text }}
{% endfor %}

Question: What's the official language of {{ country }}?
"""
pipe = Pipeline()
pipe.add_component("embedder", CohereTextEmbedder(api_key=api_key, model="embed-multilingual-v3.0"))
pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", CohereGenerator(api_key=api_key, model="command-light"))
pipe.connect("embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

pipe.run({
    "embedder": {"text": "France"},
    "prompt_builder": {"country": "France"}
})  
```

## Haystack 1.x  

You can use [Cohere Models](https://cohere.com/) in your Haystack pipelines with the [EmbeddingRetriever](https://docs.haystack.deepset.ai/docs/retriever#embedding-retrieval-recommended), [PromptNode](https://docs.haystack.deepset.ai/docs/prompt_node), and [CohereRanker](https://docs.haystack.deepset.ai/docs/ranker#cohereranker).

### Installation (1.x)

```bash
pip install farm-haystack
```

### Usage (1.x)

You can use Cohere models in various ways:

#### Embedding Models

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

#### Generative Models (LLMs) 

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

#### Ranker Models

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
