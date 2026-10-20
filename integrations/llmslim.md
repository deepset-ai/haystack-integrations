---
layout: integration
name: LLMSlim
description: Compress retrieved documents to a token budget before the prompt, locally, with an optional 22M cross-encoder
authors:
    - name: Yashvardhan Thanvi
      socials:
        github: Thanatos9404
        twitter: yashvt9404
pypi: https://pypi.org/project/llmslim/
repo: https://github.com/Thanatos9404/llmslim
report_issue: https://github.com/Thanatos9404/llmslim/issues
type: Custom Component
toc: true
version: Haystack 2.0
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[LLMSlim](https://github.com/Thanatos9404/llmslim) is an MIT-licensed Python library that selects the query-relevant parts of retrieved documents so they fit a token budget before they reach the prompt. It ranks text units lexically by default (no model, no API call) or with an optional 22M-parameter MS MARCO cross-encoder (`relevance="semantic"`), and keeps the best units that fit, in their original order.

`LLMSlimDocumentCompressor` is a Haystack component (Haystack 2.x and 3) that sits between a retriever and the prompt builder: it takes `documents` and an optional `query` and returns `{"documents": [...]}`. Kept documents keep their order, `id`, `score` and `meta`; documents that compress to nothing are dropped.

## Installation

```bash
pip install "llmslim[haystack]"
# optional cross-encoder reranker:
pip install "llmslim[haystack,semantic]"
```

## Usage

```python
from haystack import Document, Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from llmslim.integrations.haystack import LLMSlimDocumentCompressor

store = InMemoryDocumentStore()
store.write_documents(
    [
        Document(
            content="Standard shipping takes three to seven business days within the country. "
            "Express shipping arrives in one or two business days and costs fifteen dollars. "
            "We ship to forty countries, and international orders clear customs in about a week. "
            "Tracking numbers are emailed as soon as the parcel leaves the warehouse.",
            meta={"source": "shipping.md"},
        ),
        Document(
            content="You can return any item within 30 days of delivery for a full refund. "
            "Refunds go back to the original payment method within five business days. "
            "Items must be unused and in their original packaging. "
            "Gift cards and final-sale items cannot be returned.",
            meta={"source": "refunds.md"},
        ),
        Document(
            content="The company was founded in 2015 by two engineers in Pune. "
            "Our team of eighty people works across design, engineering and support. "
            "The office has a rooftop garden and a small library of design books. "
            "Every Friday afternoon the team hosts an open demo for customers.",
            meta={"source": "about.md"},
        ),
    ]
)

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=store, top_k=3))
pipeline.add_component("compressor", LLMSlimDocumentCompressor(target_ratio=0.25))
pipeline.connect("retriever.documents", "compressor.documents")

query = "How many days do I have to return an item for a refund?"
result = pipeline.run({"retriever": {"query": query}, "compressor": {"query": query}})
for doc in result["compressor"]["documents"]:
    print(round(doc.score, 3), doc.meta)
    print(doc.content)
```

Output (Python 3.12, haystack-ai 3.3.0, token counts from tiktoken):

```text
5.838 {'source': 'refunds.md', 'llmslim_original_tokens': 50, 'llmslim_compressed_tokens': 40}
You can return any item within 30 days of delivery for a full refund. Refunds go back to the original payment method within five business days. Items must be unused and in their original packaging.
```

The three retrieved documents share one budget of 25% of their 158 tokens (40
tokens). The shipping and company pages do not answer the question and are
dropped; the refund page keeps the answer and loses its sentence about gift
cards. The score is the BM25 retriever's.

To compress before a prompt builder, connect
`"compressor.documents"` to `"prompt_builder.documents"`.

Options: `target_ratio` (default 0.25), `relevance` (`"lexical"`, `"semantic"` or a callable), `selection`, `context_role`, `additional_compress_kwargs`. With Haystack 3, load saved pipelines with `allowed_modules=["llmslim.integrations.haystack"]`. Full guide: [docs/integrations/HAYSTACK.md](https://github.com/Thanatos9404/llmslim/blob/main/docs/integrations/HAYSTACK.md).

## License

`llmslim` is distributed under the terms of the [MIT](https://github.com/Thanatos9404/llmslim/blob/main/LICENSE) license.
