---
layout: integration
name: Salesforce NPSP
description: Ingest Salesforce Nonprofit Success Pack (NPSP) donor records, gift histories, and engagement metrics as Documents for RAG.
authors:
  - name: Shivam Ashokbhai Lalakiya
    socials:
      github: shivamlalakiya
pypi: https://pypi.org/project/haystack-salesforce-npsp
repo: https://github.com/PhilanthroPy-Project/salesforce-npsp-integrations
type: Data Ingestion
report_issue: https://github.com/PhilanthroPy-Project/salesforce-npsp-integrations/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`haystack-salesforce-npsp` provides a Haystack 2.x component,
`SalesforceNPSPFetcher`, that ingests donor data from Salesforce
[Nonprofit Success Pack (NPSP)](https://www.salesforce.org/nonprofit/nonprofit-success-pack/)
organizations as Haystack `Document`s — no Airbyte and no CDK required.

Unlike a generic Salesforce connector that returns raw JSON, this component is
**NPSP-aware**: it understands the `npo02__` and `npsp__` field prefixes and
produces human-readable donor profiles (lifetime giving, gift history, soft
credits, planned giving, engagement) that an LLM can reason over directly. An
optional `affinity_score_fn` injects an ML-derived donor propensity score into
each document's metadata at fetch time.

## Installation

```bash
pip install haystack-salesforce-npsp
```

Set your Salesforce credentials as environment variables:

```bash
export SF_USERNAME="you@yourorg.org"
export SF_PASSWORD="your_password"
export SF_TOKEN="your_security_token"
```

## Usage

Fetch donors on their own:

```python
from haystack_salesforce_npsp import SalesforceNPSPFetcher

fetcher = SalesforceNPSPFetcher(
    soql_filter="npo02__TotalOppAmount__c > 5000",
    limit=500,
)
documents = fetcher.run()["documents"]
# documents[0].content -> narrative donor profile
# documents[0].meta    -> {"donor_id": ..., "total_gift_amount": ..., "source": "salesforce_npsp", ...}
```

In an indexing pipeline:

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_salesforce_npsp import SalesforceNPSPFetcher

store = InMemoryDocumentStore()
p = Pipeline()
p.add_component("fetch", SalesforceNPSPFetcher(soql_filter="npo02__TotalOppAmount__c > 5000"))
p.add_component("embed", SentenceTransformersDocumentEmbedder())
p.add_component("write", DocumentWriter(document_store=store))
p.connect("fetch.documents", "embed.documents")
p.connect("embed.documents", "write.documents")
p.run({})
```

## License

`haystack-salesforce-npsp` is distributed under the terms of the MIT license.
