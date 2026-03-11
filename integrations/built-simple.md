---
layout: integration
name: Built Simple
description: Search PubMed and ArXiv scientific literature in Haystack pipelines
authors:
    - name: Built-Simple
      socials:
        github: Built-Simple
        twitter: BuiltSimpleAI
        linkedin: https://www.linkedin.com/company/built-simple-ai/
pypi: https://pypi.org/project/haystack-builtsimple/
repo: https://github.com/Built-Simple/haystack-builtsimple
type: Data Ingestion
report_issue: https://github.com/Built-Simple/haystack-builtsimple/issues
logo: /logos/built-simple.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

This integration provides retrievers for [Built-Simple](https://built-simple.ai) research APIs, enabling you to search scientific literature directly in your Haystack pipelines:

- **PubMed Retriever** - Hybrid search over 35M+ biomedical articles
- **ArXiv Retriever** - Search preprints in physics, math, CS, and more
- **Combined Retriever** - Search both sources simultaneously

No API key required. The APIs use hybrid semantic + keyword search for high-quality results.

## Installation

```bash
pip install haystack-builtsimple
```

## Usage

### Basic Retrieval

```python
from haystack_builtsimple import BuiltSimplePubMedRetriever, BuiltSimpleArxivRetriever

# Search PubMed
pubmed = BuiltSimplePubMedRetriever(top_k=5)
results = pubmed.run(query="CRISPR gene therapy clinical trials")
for doc in results["documents"]:
    print(f"[PMID {doc.meta['pmid']}] {doc.meta['title']}")

# Search ArXiv
arxiv = BuiltSimpleArxivRetriever(top_k=5)
results = arxiv.run(query="large language models reasoning")
for doc in results["documents"]:
    print(f"[{doc.meta['arxiv_id']}] {doc.meta['title']}")
```

### RAG Pipeline

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_builtsimple import BuiltSimplePubMedRetriever

pipeline = Pipeline()
pipeline.add_component("retriever", BuiltSimplePubMedRetriever(top_k=5))
pipeline.add_component("prompt", PromptBuilder(template="""
Based on these research papers:
{% for doc in documents %}
- {{ doc.meta.title }} (PMID: {{ doc.meta.pmid }})
  {{ doc.content[:500] }}
{% endfor %}

Answer: {{ query }}
"""))
pipeline.add_component("llm", OpenAIGenerator())

pipeline.connect("retriever.documents", "prompt.documents")
pipeline.connect("prompt", "llm")

result = pipeline.run({
    "retriever": {"query": "mRNA vaccine efficacy"},
    "prompt": {"query": "What factors affect mRNA vaccine efficacy?"}
})
print(result["llm"]["replies"][0])
```

### Combined Search

Search both PubMed and ArXiv simultaneously:

```python
from haystack_builtsimple import BuiltSimpleCombinedRetriever

retriever = BuiltSimpleCombinedRetriever(
    top_k=10,
    merge_strategy="score"  # or "interleave", "pubmed_first", "arxiv_first"
)

results = retriever.run(query="machine learning drug discovery")
for doc in results["documents"]:
    source = doc.meta["source"]  # "pubmed" or "arxiv"
    print(f"[{source}] {doc.meta['title']}")
```

### Full Text Retrieval

For PubMed articles, optionally fetch full text:

```python
pubmed = BuiltSimplePubMedRetriever(
    top_k=3,
    fetch_full_text=True
)
```
