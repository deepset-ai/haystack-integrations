---
name: fastRAG
description: A research framework designed to facilitate the building of retrieval augmented generative pipelines.
authors:
    - name: Intel Labs
      socials:
        github: IntelLabs
pypi:
repo: https://github.com/IntelLabs/fastRAG
type: Custom Node
report_issue: https://github.com/IntelLabs/fastRAG/issues
---

fast**RAG** is a research framework designed to facilitate the building of retrieval augmented generative pipelines. Its main goal is to make retrieval augmented generation as efficient as possible through the use of state-of-the-art and efficient retrieval and generative models. The framework includes a variety of sparse and dense retrieval models, as well as different extractive and generative information processing models. fastRAG aims to provide researchers and developers with a comprehensive tool-set for exploring and advancing the field of retrieval augmented generation.

It includes custom nodes such as:
- Image Generators
- Knoweldge Graph Creator
- Document Shapers 

## 📍 Installation

Preliminary requirements:

- Python 3.8+
- PyTorch

In a new virtual environment, run:

```bash
pip install .
```

There are various dependencies, based on usage:

```bash
# Additional engines/components
pip install .[faiss-cpu]           # CPU-based Faiss
pip install .[faiss-gpu]           # GPU-based Faiss
pip install .[qdrant]              # Qdrant support
pip install libs/colbert           # ColBERT/PLAID indexing engine
pip install .[image-generation]    # Stable diffusion library
pip install .[knowledge_graph]     # spacy and KG libraries

# REST API + UI
pip install .[ui]

# Benchmarking
pip install .[benchmark]

# Dev tools
pip install .[dev]
```