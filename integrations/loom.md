---
layout: integration
name: Loom
description: Store Haystack documents and retrieve them through a self-hosted Loom deployment.
authors:
  - name: ClickHouse
    socials:
      github: ClickHouse
repo: https://github.com/ClickHouse/loom
type: Document Store
report_issue: https://github.com/ClickHouse/loom/issues/new/choose
version: Haystack 3.5
toc: true
---

## Overview

Loom provides `LoomDocumentStore`, a Haystack document store, and `LoomRetriever`,
a retrieval component that returns native Haystack documents. Document content,
metadata and embeddings stay in the configured Loom deployment.

This integration is maintained by ClickHouse.

## Installation

Use Python 3.11 or later. The adapter requires `haystack-ai>=3.5,<3.6`.
Install this source revision of the SDK:

```bash
python -m pip install "clickhouse-loom[haystack] @ git+https://github.com/ClickHouse/loom.git@5135c7f13444fa01fce58169f2631bf26f28cec8#subdirectory=sdk/python"
```

This command installs a Git revision. The published `clickhouse-loom` 1.2.0
package does not contain this adapter.

Use a Loom server built from the same source revision. The pinned
[local development guide](https://github.com/ClickHouse/loom/blob/5135c7f13444fa01fce58169f2631bf26f28cec8/docs/development/local-development.md)
describes running that source. Create a namespace-scoped token with access to the
knowledge operations.
Set `LOOM_BASE_URL` to the deployment URL and `LOOM_API_KEY` to that token.
The deployment must have its document indexing and search providers configured.
Writes and searches use that deployment's configured providers and may incur costs.

## Usage

This example writes one document and retrieves matching documents:

```python
from haystack import Document, Pipeline
from haystack.components.writers import DocumentWriter
from loom.integrations.haystack import LoomDocumentStore, LoomRetriever

store = LoomDocumentStore("acme", "support")
DocumentWriter(store).run(
    documents=[Document(id="travel", content="Boarding starts 30 minutes before departure.")]
)
pipeline = Pipeline()
pipeline.add_component("recall", LoomRetriever(store, top_k=5))
result = pipeline.run({"recall": {"query": "When does boarding start?"}})
for document in result["recall"]["documents"]:
    print(document.content)
```

Replace `acme` and `support` with the token's organization and namespace. Use
separate namespaces and scoped tokens for mutually untrusted applications.
Documents in one namespace are shared within that namespace.

The store supports document counting, filtering, writes, duplicate policies and
deletion. Filtering and counting hydrate the full store, so they incur a full read.
The retriever supports hybrid, semantic and lexical search. It ranks full documents
by matching chunks among at most 100 search candidates; duplicate chunks can leave
fewer than `top_k` documents.

The default credential is a Haystack `Secret` that names `LOOM_API_KEY`.
Serialization retains that environment-variable reference. Loading a serialized
pipeline requires the application to trust `loom.integrations.haystack` under
Haystack's normal module policy; the adapter does not register that trust.

See the [adapter reference](https://github.com/ClickHouse/loom/blob/5135c7f13444fa01fce58169f2631bf26f28cec8/docs/features/integrations/frameworks.md#haystack)
for scope, partial-write behavior and configuration.

## License

The SDK is licensed under Apache-2.0.
