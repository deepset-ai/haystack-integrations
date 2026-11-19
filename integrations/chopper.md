---
layout: integration
name: Chopper
description: Rerank retrieved documents and cut the exact quotes that answer the query out of them, in one pass of a local mmBERT model
authors:
    - name: wiiiktor
      socials:
        github: wiiiktor
pypi: https://pypi.org/project/chopper-rag
repo: https://github.com/wiiiktor/chopper_demo
type: Custom Component
report_issue: https://github.com/wiiiktor/chopper_demo/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`ChopperDocumentCompressor` goes after a retriever or ranker. It replaces the retrieved documents with **chops**: the exact
quotes that answer the query, never rewritten, typically 2–5% of the retrieved text. Each chop keeps its source document's
metadata plus character offsets into it. The component also outputs an `ANSWER` / `SEARCH` decision: whether the documents
seem to contain the answer, or the pipeline should search again.

It runs locally on CPU or GPU with a fine-tuned mmBERT encoder:
[wiiiktor/chopper_mmbert](https://huggingface.co/wiiiktor/chopper_mmbert) (`base` 0.31B or `small` 0.14B, MIT).
On multi-hop MuSiQue questions, Qwen3-14B answers 4-hop questions correctly 29% of the time from the chops, against 12% from
all 20 retrieved snippets, with about 11× fewer tokens.

**It can also replace a ranker.** With `mode="rerank"` the component outputs the input documents, most relevant first
(`top_k` of them), with the model's relevance as their `score`, computed in the same single pass. On an 8-language
held-out set (400 queries, 16 documents each) it ranks with nDCG@10 0.973, against 0.984 for bge-reranker-v2-m3 and 0.986
for Qwen3-Reranker-4B, at the speed of bge-reranker-v2-m3 (0.20 s per query on an RTX 3090).

## Installation

```bash
pip install "chopper-rag[haystack]"
```

## Usage

```python
from haystack import Pipeline
from chopper_rag.haystack import ChopperDocumentCompressor

pipe = Pipeline()
pipe.add_component("retriever", retriever)                          # any retriever, top_k=16
pipe.add_component("chopper", ChopperDocumentCompressor(variant="base"))
pipe.connect("retriever.documents", "chopper.documents")
out = pipe.run({"retriever": {"query": q}, "chopper": {"query": q}})
print([d.content for d in out["chopper"]["documents"]], out["chopper"]["decision"])
```

As a ranker (whole documents, most relevant first), e.g. in place of a cross-encoder ranker:

```python
pipe.add_component("ranker", ChopperDocumentCompressor(variant="base", mode="rerank", top_k=5))
```

Requires `chopper-rag` 0.1.4 or later.

## License

`chopper-rag` and the model weights are released under the MIT license.
