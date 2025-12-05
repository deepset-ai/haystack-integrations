---
layout: integration
name: Valkey
description: Use a Valkey database with Haystack
authors:
    - name: Daria Korenieva
      socials:
        github: daric93
        linkedin: https://www.linkedin.com/in/daria-korenieva/
pypi: https://pypi.org/project/valkey-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/valkey
type: Document Store
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/valkey.svg
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Valkey](https://valkey.io/) is a high-performance, in-memory data structure store that you can use in Haystack pipelines with the [ValkeyDocumentStore](https://docs.haystack.deepset.ai/docs/valkey-document-store). Valkey operates in-memory by default for maximum performance, but can be configured with persistence options for data durability.

For a detailed overview of all the available methods and settings for the `ValkeyDocumentStore`, visit the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/integrations-valkey#valkeydocumentstore).

## Installation

```bash
pip install valkey-haystack
```

## Usage

To use Valkey as your data storage for your Haystack LLM pipelines, you must have a Valkey server with search module running. Once you have that, you can initialize a `ValkeyDocumentStore` for Haystack:

```python
from haystack_integrations.document_stores.valkey import ValkeyDocumentStore

document_store = ValkeyDocumentStore(
    nodes_list=[("localhost", 6379)],
    index_name="my_documents",
    embedding_dim=768,
    distance_metric="cosine"
)
```

### Writing Documents to ValkeyDocumentStore

To write documents to your `ValkeyDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [Converters](https://docs.haystack.deepset.ai/docs/converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessors), as well as other [Integrations](/integrations) that might help you fetch data from other resources. Below is an example indexing pipeline that indexes your Markdown files into a Valkey database.

### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.converters import MarkdownToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack_integrations.document_stores.valkey import ValkeyDocumentStore

document_store = ValkeyDocumentStore(
    nodes_list=[("localhost", 6379)],
    index_name="my_documents",
    embedding_dim=768,
    distance_metric="cosine"
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

### Using Valkey in a RAG Pipeline

Once you have documents in your `ValkeyDocumentStore`, they can be used in any Haystack pipeline. Then, you can use [`ValkeyEmbeddingRetriever`](https://docs.haystack.deepset.ai/docs/valkeyembeddingretriever) to retrieve data from your ValkeyDocumentStore. For example, below is a pipeline that uses a custom prompt designed to answer questions for the retrieved documents.

```python
from haystack.utils import Secret
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.document_stores.valkey import ValkeyDocumentStore
from haystack_integrations.components.retrievers.valkey import ValkeyEmbeddingRetriever

document_store = ValkeyDocumentStore(
    nodes_list=[("localhost", 6379)],
    index_name="my_documents",
    embedding_dim=768,
    distance_metric="cosine"
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
query_pipeline.add_component("retriever", ValkeyEmbeddingRetriever(document_store=document_store))
query_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
query_pipeline.add_component("generator", OpenAIGenerator(api_key=Secret.from_token("YOUR_OPENAI_API_KEY"), model="gpt-4"))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "prompt_builder.documents")
query_pipeline.connect("prompt_builder", "generator")

query = "What is Valkey?"
results = query_pipeline.run(
    {
        "text_embedder": {"text": query},
        "prompt_builder": {"query": query},
    }
)
```

For more examples, see the [examples folder](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/valkey/examples) in the repository.

For more advanced configurations and clustering setups, refer to the [Valkey documentation](https://valkey.io/docs/).

### Running Valkey-Haystack Locally

To set up Valkey for development and testing with haystack-valkey:

1. **Start Valkey server**:
```bash
docker run -d -p 6379:6379 valkey/valkey-bundle:latest
```

2. **Set up development environment**:
```bash
git clone https://github.com/deepset-ai/haystack-core-integrations
cd integrations/valkey
uv sync
```

3. **Run tests**:
```bash
uv sync --group test

# Run unit tests only
hatch run test:unit

# Run integration tests (requires Valkey instance)
hatch run test:integration

# Run all tests
hatch run test:all
```

4. **Run examples**:
```bash
uv sync --group examples

# Basic usage example
hatch run python examples/basic_usage.py

# Pipeline example
hatch run python examples/example.py
```

## Performance Benefits

- **In-Memory Storage**: Lightning-fast read/write operations
- **High Throughput**: Handles thousands of operations per second
- **Low Latency**: Minimal response times for document operations
- **Scalability**: Supports clustering for horizontal scaling

## Requirements

- Valkey server with search module running and accessible
- Python 3.9+
- Haystack 2.11+

## License

`valkey-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
