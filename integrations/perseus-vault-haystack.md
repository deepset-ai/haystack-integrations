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

```bash
pip install perseus-vault-haystack
```

## Usage

```python
from haystack import Pipeline, Document
from perseus_vault_haystack import (
    PerseusVaultMemoryStore,
    PerseusVaultMemoryWriter,
    PerseusVaultMemoryRetriever,
)

store = PerseusVaultMemoryStore(db_path="~/.mimir/haystack.db")

write_pipe = Pipeline()
write_pipe.add_component("writer", PerseusVaultMemoryWriter(memory_store=store))
write_pipe.run({"writer": {"documents": [Document(content="Sample text.")]}})

read_pipe = Pipeline()
read_pipe.add_component("retriever", PerseusVaultMemoryRetriever(memory_store=store))
result = read_pipe.run({"retriever": {"query": "What is stored?"}})
```

## License

`perseus-vault-haystack` is distributed under the terms of the MIT license.
