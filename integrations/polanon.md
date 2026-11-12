---
layout: integration
name: polanon
description: Reversible PII masking for RAG, Polish-first, with stable tokens so that masked questions find masked documents
authors:
    - name: boromat
      socials:
        github: boromat
pypi: https://pypi.org/project/polanon/
repo: https://github.com/boromat/polanon
type: Custom Component
report_issue: https://github.com/boromat/polanon/issues
version: Haystack 3.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[polanon](https://github.com/boromat/polanon) replaces personal data with tokens such as
`<OSOBA_482193047556>` before text reaches an embedder, a document store or a model, and puts the
originals back into the answer, also while it streams. It validates the checksums of Polish
identifiers (PESEL, NIP, REGON, ID card, IBAN, payment cards) and reads Polish first names with
their surnames in all seven grammatical cases, without a language model; foreign invoices, e-mail
addresses, phone numbers and secrets are covered too.

For retrieval, tokens are computed with HMAC-SHA256 under a secret key: the same person gets the
same token in every document and in every question, also when the name stands in another case
("Jan Kowalski", "Jana Kowalskiego"). A masked question therefore finds the masked passages, while
the document store, the embeddings and the prompt hold no names, numbers or addresses. What each
token stands for is kept in a mapping store of the application's own, never in a document's
`meta`.

## Installation

```bash
pip install "polanon[haystack]"
```

Set the key, 32 random bytes in hexadecimal, in the `POLANON_KEY` environment variable:
`python -c "import secrets; print(secrets.token_hex(32))"`.

## Usage

### Components

- `PolanonDocumentMasker`: masks documents before the splitter and the embedder of an indexing
  pipeline, and writes what the tokens stand for to the mapping store.
- `PolanonQueryMasker`: masks a question with the tokens of the documents; its `query` goes to the
  text embedder and the prompt builder, its `mapping` to the restorer.
- `PolanonRestorer`: restores the generator's replies and the documents found, for the reader.
- `PolanonStreamRestorer`: a streaming callback that restores a streamed answer, holding back a
  token cut between chunks.

### Use polanon in a RAG pipeline

```python
from haystack import Pipeline
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from polanon import InMemoryMappingStore
from polanon.integrations.haystack import PolanonDocumentMasker

document_store = InMemoryDocumentStore()
mappings = InMemoryMappingStore()  # in production, an encrypted table of your own

indexing = Pipeline()
indexing.add_component("mask", PolanonDocumentMasker(store=mappings))
indexing.add_component("split", DocumentSplitter(split_by="period"))
indexing.add_component("embed", OpenAIDocumentEmbedder())
indexing.add_component("write", DocumentWriter(document_store))
indexing.connect("mask", "split")
indexing.connect("split", "embed")
indexing.connect("embed", "write")
```

The query pipeline puts `PolanonQueryMasker` first and `PolanonRestorer` after the generator. A
complete example, which runs offline with Haystack's mock embedders and chat generator, is
[examples/haystack_rag.py](https://github.com/boromat/polanon/blob/main/examples/haystack_rag.py).
To load a saved pipeline, allow this module and the module of your mapping store:
`Pipeline.loads(text, allowed_modules=["polanon.integrations.haystack", "myapp.vault"])`.

### License

`polanon` is distributed under the terms of the
[MIT](https://github.com/boromat/polanon/blob/main/LICENSE) license.
