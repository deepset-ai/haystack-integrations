---
layout: integration
name: Pinecone
description: Use a Pinecone database with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Ashwin Mathur
      socials:
        github: awinml
        twitter: awinml
        linkedin: https://www.linkedin.com/in/ashwin-mathur-ds
    - name: Varun Mathur
      socials:
        github: vrunm
        twitter: vrunmnlp
        linkedin: https://www.linkedin.com/in/varun-mathur-ds        
pypi: https://pypi.org/project/pinecone_haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/pinecone
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/pinecone.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Pinecone](https://www.pinecone.io/) is a fast and scalable vector database that you can use in Haystack pipelines with the [PineconeDocumentStore](https://docs.haystack.deepset.ai/docs/pinecone-document-store).

For a detailed overview of all the available methods and settings for the `PineconeDocumentStore`, visit the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/integrations-pinecone#pineconedocumentstore).

## Installation

```bash
pip install pinecone-haystack
```

## Usage

To use Pinecone as your data storage for your Haystack LLM pipelines, you must have an account with Pinecone and an API Key. Once you have those, you can initialize a `PineconeDocumentStore` for Haystack:

```python
from haystack_integrations.document_stores.pinecone import PineconeDocumentStore

# Make sure you have the PINECONE_API_KEY environment variable set
document_store = PineconeDocumentStore(
  index="YOUR_INDEX_NAME",
  metric="cosine",
  dimension=768,
  spec={"serverless": {"region": "us-east-1", "cloud": "aws"}},
  )
```

### Writing Documents to PineconeDocumentStore

To write documents to your `PineconeDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [Converters](https://docs.haystack.deepset.ai/docs/converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessors), as well as other [Integrations](/integrations) that might help you fetch data from other resources. Below is an example indexing pipeline that indexes your Markdown files into a Pinecone database.

### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.converters import MarkdownToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack_integrations.document_stores.pinecone import PineconeDocumentStore

# Make sure you have the PINECONE_API_KEY environment variable set
document_store = PineconeDocumentStore(
  index="YOUR_INDEX_NAME",
  metric="cosine",
  dimension=768,
  spec={"serverless": {"region": "us-east-1", "cloud": "aws"}},
  )

indexing = Pipeline()
indexing.add_component("converter", MarkdownToDocument())
indexing.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=2))
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "splitter")
indexing.connect("splitter", "embedder")
indexing.connect("embedder", "writer")

indexing.run({"converter": {"sources": ["filename.md"]}})
```

### Using Pinecone in a RAG Pipeline

Once you have documents in your `PineconeDocumentStore`, they can be used in any Haystack pipeline. Then, you can use [`PineconeEmbeddingRetriever`](https://docs.haystack.deepset.ai/docs/pineconedenseretriever) to retrieve data from your PineconeDocumentStore. For example, below is a pipeline that uses a custom prompt designed to answer questions for the retrieved documents.

```python
from haystack.utils import Secret
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.document_stores.pinecone import PineconeDocumentStore
from haystack_integrations.components.retrievers.pinecone import PineconeEmbeddingRetriever

# Make sure you have the PINECONE_API_KEY environment variable set
document_store = PineconeDocumentStore(
  index="YOUR_INDEX_NAME",
  metric="cosine",
  dimension=768,
  spec={"serverless": {"region": "us-east-1", "cloud": "aws"}},
  )
              
prompt_template = """Answer the following query based on the provided context. If the context does
                     not include an answer, reply with 'I don't know'.\n
                     Query: {{query}}
                     Documents:
                     {% for doc in documents %}
                        {{ doc.content }}
                     {% endfor %}
                     Answer: 
                  """

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
query_pipeline.add_component("retriever", PineconeEmbeddingRetriever(document_store=document_store))
query_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
query_pipeline.add_component("generator", OpenAIGenerator(api_key=Secret.from_token("YOUR_OPENAI_API_KEY"), model="gpt-4"))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "prompt_builder.documents")
query_pipeline.connect("prompt_builder", "generator")

query = "What is Pinecone?"
results = query_pipeline.run(
    {
        "text_embedder": {"text": query},
        "prompt_builder": {"query": query},
    }
)
```
