---
layout: integration
name: Amazon S3 Vectors
description: Store documents and embeddings in Amazon S3 Vectors for semantic search with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/amazon-s3-vectors-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/amazon_s3_vectors
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aws.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Amazon S3 Vectors](https://aws.amazon.com/s3/features/vectors/) provides vector storage and similarity search without provisioning a database server. Use it with Haystack to build semantic search and RAG pipelines backed by dedicated S3 vector buckets.

The integration includes two components:

- [AmazonS3VectorsDocumentStore](https://docs.haystack.deepset.ai/docs/amazons3vectorsdocumentstore) stores documents, embeddings, and metadata in a vector index.
- [AmazonS3VectorsEmbeddingRetriever](https://docs.haystack.deepset.ai/docs/amazons3vectorsembeddingretriever) retrieves documents similar to a query embedding, with optional metadata filters.

## Installation

```bash
pip install amazon-s3-vectors-haystack
```

## Usage

Configure your AWS credentials through the AWS CLI or environment variables. Make sure your AWS identity has the required [S3 Vectors permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_s3vectors.html).

This example embeds documents with Sentence Transformers, stores them in S3 Vectors, and searches them using a Haystack pipeline. The vector bucket and index are created if they do not already exist.

Install the embedding integration:

```bash
pip install sentence-transformers-haystack
```

```python
from haystack import Document, Pipeline
from haystack_integrations.components.embedders.sentence_transformers import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack_integrations.components.retrievers.amazon_s3_vectors import (
    AmazonS3VectorsEmbeddingRetriever,
)
from haystack_integrations.document_stores.amazon_s3_vectors import (
    AmazonS3VectorsDocumentStore,
)

model = "sentence-transformers/all-MiniLM-L6-v2"
document_store = AmazonS3VectorsDocumentStore(
    vector_bucket_name="haystack-docs-example",
    index_name="semantic-search",
    dimension=384,
    region_name="us-east-1",
)
documents = [
    Document(
        id="languages",
        content="There are over 7,000 languages spoken around the world today.",
    ),
    Document(id="elephants", content="Elephants can recognize themselves in mirrors."),
    Document(id="waves", content="Bioluminescent waves can be seen in the Maldives."),
]
document_embedder = SentenceTransformersDocumentEmbedder(model=model)
embedded = document_embedder.run(documents=documents)
document_store.write_documents(embedded["documents"])

query_pipeline = Pipeline()
query_pipeline.add_component(
    "text_embedder", SentenceTransformersTextEmbedder(model=model)
)
query_pipeline.add_component(
    "retriever",
    AmazonS3VectorsEmbeddingRetriever(document_store=document_store, top_k=1),
)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = query_pipeline.run(
    {"text_embedder": {"text": "How many languages are there?"}}
)
print(result["retriever"]["documents"][0].content)
# >> There are over 7,000 languages spoken around the world today.
document_store.close()
```

## License

`amazon-s3-vectors-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
