---
layout: integration
name: AstraDB Document Store
description: A Document Store for storing and retrieval from AstraDB - built for Haystack 2.0.
authors:
  - name: Nicholas Brackley
    socials:
      github: hc33brackles
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: TODO
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/astra
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/astradb.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Note](#note)
- [License](#license)

## Overview

This integration allows you to use [AstraDB](https://docs.datastax.com/en/astra-serverless/docs/) as the document store for your Haystack pipelines. This page provides simple instructions on how to start it up and how to initialize an `AstraDocumentStore` that can be used in any Haystack 2.0 pipeline.

## Installation

```console
pip install haystack-ai astra-store
```
## Usage

This package includes Astra Document Store and Astra Retriever classes that integrate with Haystack 2.0, allowing you to easily perform document retrieval or RAG with AstraDB, and include those functions in Haystack pipelines.

### In order to use the Document Store directly:

```python
import os

from haystack import Document, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import GPTGenerator
from haystack.document_stores import DuplicatePolicy
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.writers import DocumentWriter

from astra_store.document_store import AstraDocumentStore
from astra_store.retriever import AstraRetriever

# Create a RAG query pipeline
prompt_template = """
                Given these documents, answer the question.
                Documents:
                {% for doc in documents[0] %}
                    {{ doc.content }}
                {% endfor %}
                Question: {{question}}
                Answer:
                """

# Load in environment variables:
astra_id = os.getenv("ASTRA_DB_ID", "")
astra_region = os.getenv("ASTRA_DB_REGION", "us-east1")

astra_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN", "")
collection_name = os.getenv("COLLECTION_NAME", "haystack_vector_search")
keyspace_name = os.getenv("KEYSPACE_NAME", "recommender_demo")

# Instantiate the Document Store class.
# We support many different databases. Here, we load a simple and lightweight in-memory database.
document_store = AstraDocumentStore(
    astra_id=astra_id,
    astra_region=astra_region,
    astra_collection=collection_name,
    astra_keyspace=keyspace_name,
    astra_application_token=astra_application_token,
    duplicates_policy=DuplicatePolicy.SKIP,
    embedding_dim=384,
)


# Add Documents
documents = [
    Document(content="There are over 7,000 languages spoken around the world today."),
    Document(
        content="Elephants have been observed to behave in a way that indicates a high level of self-awareness, such as recognizing themselves in mirrors."
    ),
    Document(
        content="In certain parts of the world, like the Maldives, Puerto Rico, and San Diego, you can witness the phenomenon of bioluminescent waves."
    ),
]
p = Pipeline()
p.add_component(
    instance=SentenceTransformersDocumentEmbedder(model_name_or_path="sentence-transformers/all-MiniLM-L6-v2"),
    name="embedder",
)
p.add_component(instance=DocumentWriter(document_store=document_store, policy=DuplicatePolicy.SKIP), name="writer")
p.connect("embedder.documents", "writer.documents")

p.run({"embedder": {"documents": documents}})


# Construct rag pipeline
rag_pipeline = Pipeline()
rag_pipeline.add_component(
    instance=SentenceTransformersTextEmbedder(model_name_or_path="sentence-transformers/all-MiniLM-L6-v2"),
    name="embedder",
)
rag_pipeline.add_component(instance=AstraRetriever(document_store=document_store), name="retriever")
rag_pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
rag_pipeline.add_component(instance=GPTGenerator(api_key=os.environ.get("OPENAI_API_KEY")), name="llm")
rag_pipeline.add_component(instance=AnswerBuilder(), name="answer_builder")
rag_pipeline.connect("embedder", "retriever")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("llm.metadata", "answer_builder.metadata")
rag_pipeline.connect("retriever", "answer_builder.documents")


# Draw the pipeline
rag_pipeline.draw("./rag_pipeline.png")


# Run the pipeline
question = "How many languages are there in the world today?"
result = rag_pipeline.run(
    {
        "embedder": {"text": question},
        "retriever": {"top_k": 2},
        "prompt_builder": {"question": question},
        "answer_builder": {"query": question},
    }
)
print(result)
```

### Note:
Please note that the current version of Astra JSON API does not support the following operators:
$lt, $lte, $gt, $gte, $nin, $not, $neq 
As well as filtering with none values (these won't be inserted as the result is stored as json document, and it doesn't store nones)

### License

`astra-store` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.