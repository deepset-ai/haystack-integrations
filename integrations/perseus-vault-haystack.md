---
layout: integration
name: Perseus Vault
description: Local-first, encrypted, persistent memory for Haystack 2.x pipelines and agents — backed by Perseus Vault.
authors:
    - name: Perseus Computing LLC
      socials:
        github: Perseus-Computing-LLC
pypi: https://pypi.org/project/perseus-vault-haystack/
repo: https://github.com/Perseus-Computing-LLC/mimir-haystack
type: Memory Store
report_issue: https://github.com/Perseus-Computing-LLC/mimir-haystack/issues
logo: /logos/perseus-vault.svg
version: Haystack 2.0
toc: true
---

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Perseus Vault](https://github.com/Perseus-Computing-LLC/perseus-vault) is a local-first,
single-binary memory engine for AI agents. It stores data in an encrypted (AES-256-GCM)
SQLite database with FTS5 full-text and vector search, runs fully offline, and requires no
external vector database or API keys.

`perseus-vault-haystack` brings that persistent memory into Haystack 2.x pipelines and agents
through three components:

- **`PerseusVaultMemoryStore`** — the encrypted document/memory store.
- **`PerseusVaultMemoryWriter`** — a pipeline component that persists documents to the store.
- **`PerseusVaultMemoryRetriever`** — a pipeline component that retrieves documents from the store.

## Installation

Install the Python components from PyPI:

```bash
pip install perseus-vault-haystack
```

The components talk to a local `perseus-vault` executable over stdio, so the binary is a
separate, language-agnostic dependency. Download a pre-built binary from the
[Perseus Vault releases page](https://github.com/Perseus-Computing-LLC/perseus-vault/releases)
(or build from source) and either put it on your `$PATH` (so `perseus-vault` resolves) or pass
its absolute path via `perseus_vault_binary=`.

## Usage

The example below writes a document into persistent memory and retrieves it back in a
separate pipeline. Because Perseus Vault persists to an encrypted SQLite file, documents
written in one run are available in any future run pointed at the same `db_path`.

```python
from pathlib import Path

from haystack import Pipeline, Document
from perseus_vault_haystack import (
    PerseusVaultMemoryStore,
    PerseusVaultMemoryWriter,
    PerseusVaultMemoryRetriever,
)

db_path = Path("~/.perseus-vault/haystack.db").expanduser()
db_path.parent.mkdir(parents=True, exist_ok=True)
store = PerseusVaultMemoryStore(db_path=str(db_path))

write_pipe = Pipeline()
write_pipe.add_component("writer", PerseusVaultMemoryWriter(memory_store=store))
write_pipe.run(
    {"writer": {"documents": [
        Document(content="Perseus Vault stores encrypted memory for Haystack agents."),
    ]}}
)

read_pipe = Pipeline()
read_pipe.add_component("retriever", PerseusVaultMemoryRetriever(memory_store=store))
result = read_pipe.run({"retriever": {"query": "encrypted memory"}})
print(result["retriever"]["documents"])
```

## License

`perseus-vault-haystack` is distributed under the terms of the MIT license.
