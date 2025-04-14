---
layout: integration
name: OPEA
description: Use the OPEA framework for hardware abstraction and orchestration
authors:
  - name: OPEA-Project
    socials:
      github: opea-project
pypi: 
repo: https://github.com/opea-project/Haystack-OPEA
type: Distributed Computing
report_issue: https://github.com/opea-project/Haystack-OPEA/issues
logo: /logos/opea.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Embeddings](#embeddings)
  - [LLM Generation](#llm-generation)

## Overview

The `haystack-opea` integration connects Haystack to [OPEA](https://opea.dev/)—a collection of containerized microservices for LLMs, embedding, retrieval and reranking. By delegating heavy compute to OPEA services, you can build flexible Retrieval-Augmented Generation (RAG) pipelines that scale across cloud, on-prem and edge deployments.  

Key features:  
- Hardware-agnostic LLM & embedding services.
- Easy orchestration of LLM, embedder, retriever, ranker, among others.
- Support for local development via Docker Compose or production clusters.

## Installation

Install from source:

```bash
git clone https://github.com/opea-project/Haystack-OPEA.git
cd Haystack-OPEA
pip install poetry
poetry install --with test
```

## Usage

Below are quickstart examples for embeddings and LLM generation. Make sure your OPEA backend is running (e.g. via the provided Docker Compose in `samples/`).

### Embeddings

```python
from haystack import Document
from haystack_opea import OPEATextEmbedder, OPEADocumentEmbedder

# Text embedding example
text_embedder = OPEATextEmbedder(api_url="http://localhost:6006")
text_embedder.warm_up()
result = text_embedder.run("I love pizza!")
print("Text embedding:", result["vectors"][0])

# Document embedding example
doc = Document(content="I love pizza!")
doc_embedder = OPEADocumentEmbedder(api_url="http://localhost:6006")
doc_embedder.warm_up()
out = doc_embedder.run([doc])
print("Document embedding:", out["documents"][0].embedding)
```

### LLM Generation

```python
from haystack_opea import OPEAGenerator

# Initialize the OPEA LLM service
generator = OPEAGenerator(
    api_url="http://localhost:9009",
    model_arguments={
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 512,
    },
)
generator.warm_up()

# Run a simple prompt
response = generator.run(prompt="What is the capital of France?")
print("LLM reply:", response["replies"][0])
```

For more examples, see the `samples/` folder and the [official OPEA documentation](https://opea.dev/), as well as the [Components Library](https://github.com/opea-project/GenAIComps).
