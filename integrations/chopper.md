---
layout: integration
name: Chopper
description: Cut the exact quotes that answer the query out of retrieved documents with a local mmBERT context compressor
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

## License

`chopper-rag` and the model weights are released under the MIT license.
