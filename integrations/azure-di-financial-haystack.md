---
layout: integration
name: Azure DI Financial Document Extractor
description: Real-time structured KV extraction, field normalisation, and delta reconciliation for financial PDFs (IRS 1040, W-2, and more) using Azure Document Intelligence.
authors:
  - name: Ambreen Zaver, Callisto Tech
    socials:
      github: zavera
      linkedin: https://www.linkedin.com/in/ambreenzaver/
pypi: https://pypi.org/project/azure-di-financial-haystack
repo: https://github.com/zavera/haystack-financial-doc-extractor
type: Data Ingestion
report_issue: https://github.com/zavera/haystack-financial-doc-extractor/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Why structured extraction over RAG](#why-structured-extraction-over-rag)
- [Installation](#installation)
- [Components](#components)
- [Usage](#usage)
  - [Single endpoint](#single-endpoint)
  - [Multi-endpoint pool](#multi-endpoint-pool)
  - [Running the pipeline](#running-the-pipeline)
  - [Persisting and retrieving payload per user](#persisting-and-retrieving-payload-per-user)
- [PDF preprocessing stages](#pdf-preprocessing-stages)
- [Field map normalisation](#field-map-normalisation)
- [License](#license)

## Overview

`azure-di-financial-haystack` provides a pre-wired Haystack pipeline for extracting
and reconciling key-value fields from financial PDFs — IRS Form 1040, W-2, Schedule C,
and similar documents — using
[Azure Document Intelligence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence).

**Key capabilities:**

- **Real-time processing with FIFO queue semantics** — documents are submitted and
  processed as they arrive. Parallelism is controlled via `max_workers`; ordering
  within a batch is FIFO. No polling loops or manual orchestration required.
- **Multi-endpoint pool** — provision multiple Azure DI resources and distribute
  load across them with thread-safe round-robin. Each additional endpoint multiplies
  your effective TPS quota linearly.
- **4-stage PDF preprocessing chain** — handles documents that fail standard
  submission: full document → page-chunk split → DPI reduction → rotation sweep.
  Each stage runs automatically before falling back to the next.
- **Structured payload** — output is a typed list of `ExtractedField` objects with
  `field_name`, `extracted_value` (`Decimal`), `confidence`, `raw_value`, and
  `section`. Deterministic, debuggable, and persistable.
- **Delta reconciliation** — compares extracted values against reference values you
  supply and scores each field `HIGH / MEDIUM / LOW` by the magnitude of the
  discrepancy.

## Why structured extraction over RAG

Most document Q&A pipelines embed the full document and retrieve by semantic
similarity. For financial documents that approach has two practical problems:

**Precision.** A similarity search for "what is the AGI?" may return a passage
containing the right line — or a nearby line that looks similar. Structured
extraction retrieves the exact key from Azure DI's KV output and maps it to a
canonical name. There is no ambiguity: `agi = 83200` or it is not found.

**Debuggability.** When a downstream system flags a discrepancy, you can trace it
to the exact extracted key, its raw Azure DI value, and the confidence score. With
embedding-based retrieval you are debugging a similarity score, not a field value.

**Persistence and reuse.** The structured payload — a list of typed `ExtractedField`
objects — can be serialised and stored per user (see
[Persisting and retrieving payload per user](#persisting-and-retrieving-payload-per-user)).
On the next request you load the stored payload rather than re-running Azure DI.
RAG pipelines have no natural unit of persistence at this granularity.

## Installation

```bash
pip install azure-di-financial-haystack
```

Set your Azure DI credentials:

```bash
export AZURE_DI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
export AZURE_DI_KEY=<your-api-key>
```

## Components

| Component | Role |
|---|---|
| `BytesIngestionComponent` | Accepts raw PDF bytes + document IDs; emits `DocumentPayload` objects |
| `AzureDiExtractor` | Calls Azure DI with 4-stage recovery; supports single or multi-endpoint pool; FIFO within batch |
| `KvNormalizer` | Maps raw Azure DI keys to canonical field names; parses financial values to `Decimal` |
| `DeltaCalculator` | Compares extracted values against reference values; assigns `HIGH / MEDIUM / LOW` severity |
| `build_pipeline()` | Convenience function — wires all four components into a ready-to-run `Pipeline` |

## Usage

### Single endpoint

```python
import os
from haystack_integrations.components.azure_di_financial import build_pipeline

FIELD_MAP_W2 = {
    "wages, tips, other compensation":  "wages_w2",
    "federal income tax withheld":      "federal_tax_withheld",
    "social security wages":            "ss_wages",
    "social security tax withheld":     "ss_tax_withheld",
    "medicare wages and tips":          "medicare_wages",
    "medicare tax withheld":            "medicare_tax_withheld",
    "dependent care benefits":          "dependent_care",
    "state wages, tips, etc.":          "state_wages",
    "state income tax":                 "state_income_tax",
}

pipeline = build_pipeline(
    azure_endpoint=os.environ["AZURE_DI_ENDPOINT"],
    azure_api_key=os.environ["AZURE_DI_KEY"],
    field_map=FIELD_MAP_W2,
    section="INCOME",
    source_doc_type="IRS Form W-2",
)
```

### Multi-endpoint pool

Provision multiple Azure DI resources to scale TPS linearly. The extractor
distributes documents across the pool using thread-safe round-robin — each
document is pinned to one endpoint for the duration of its processing, including
any page-chunk retries.

```python
pipeline = build_pipeline(
    azure_endpoints=[
        # East US — primary quota
        {"endpoint": "https://resource-eastus.cognitiveservices.azure.com/", "api_key": "key1"},
        # West Europe — additional quota, doubles effective TPS
        {"endpoint": "https://resource-westeu.cognitiveservices.azure.com/", "api_key": "key2"},
        # South East Asia — optional third tier
        {"endpoint": "https://resource-sea.cognitiveservices.azure.com/",    "api_key": "key3"},
    ],
    field_map=FIELD_MAP_W2,
    section="INCOME",
    source_doc_type="IRS Form W-2",
    max_workers=12,   # recommended: len(endpoints) * 4
)
```

**Sizing guidance:**

| Endpoints | `max_workers` | Effective TPS (Standard tier) |
|---|---|---|
| 1 | 4 | ~15 req/s |
| 2 | 8 | ~30 req/s |
| 3 | 12 | ~45 req/s |

### Running the pipeline

Documents in a batch are processed in submission order (FIFO). Results are
returned as a flat list of `ExtractedField` objects — one list covering all
documents in the batch.

```python
from pathlib import Path

pdf_bytes = Path("w2-2024.pdf").read_bytes()

result = pipeline.run({
    "ingest": {
        "bytes_list":   [pdf_bytes],
        "document_ids": ["w2-001"],
        "source_names": ["w2-2024.pdf"],
    },
    "delta": {
        # Reference values from your authoritative system (HR, aid application, etc.)
        # Delta = |reference − extracted|. Omit a field to skip delta scoring for it.
        "reference_values": {
            "wages_w2":            88450,
            "federal_tax_withheld": 6912,
            "ss_wages":            88450,
        },
    },
})

for field in result["delta"]["fields"]:
    if field.extracted_value is not None:
        delta_str = f"  delta={field.delta:+,.2f}  [{field.severity.name}]" if field.delta is not None else ""
        print(f"{field.field_name:<25} {field.extracted_value:>12}   conf={float(field.confidence):.2f}{delta_str}")
```

Example output:

```
wages_w2                    88450.00   conf=0.68  delta=+0.00  [LOW]
federal_tax_withheld         6912.34   conf=0.64  delta=-0.34  [LOW]
ss_wages                    88450.00   conf=0.53  delta=+0.00  [LOW]
ss_tax_withheld              5485.90   conf=0.63
medicare_wages              88450.00   conf=0.68
medicare_tax_withheld        1282.53   conf=0.88
dependent_care              12000.00   conf=0.62
state_wages                 88450.00   conf=0.87
state_income_tax             1845.67   conf=0.68
```

### Persisting and retrieving payload per user

The structured payload is a plain list of `ExtractedField` dataclasses — easy to
serialise and store against a user or document ID in any persistence layer. On
subsequent requests, load the stored payload and skip re-running Azure DI entirely.

```python
import json
from dataclasses import asdict
from haystack_integrations.components.azure_di_financial import KvNormalizer
from haystack_integrations.components.azure_di_financial.models.extracted_field import ExtractedField

# --- After pipeline.run() ---
fields = result["delta"]["fields"]

# Serialise to JSON and store against user_id + document_id in your DB / cache
payload = [asdict(f) for f in fields]
store(user_id="u-001", doc_id="w2-2024", payload=json.dumps(payload))

# --- On next request: load from store, skip Azure DI ---
raw = load(user_id="u-001", doc_id="w2-2024")
cached_fields = [ExtractedField(**item) for item in json.loads(raw)]

# Feed directly into DeltaCalculator for re-scoring with updated reference values
from haystack_integrations.components.azure_di_financial import DeltaCalculator
delta = DeltaCalculator()
rescored = delta.run(fields=cached_fields, reference_values={"wages_w2": 90000})
```

This pattern keeps Azure DI calls to one per document version. Re-scoring,
threshold changes, and reference value updates are all handled in-process
against the cached payload — no network round-trip required.

## PDF preprocessing stages

The extractor runs up to four stages automatically, moving to the next only if
the current stage returns no KV pairs:

| Stage | What it does | When it triggers |
|---|---|---|
| **Stage 0** | Submit raw PDF bytes to Azure DI | Always — first attempt |
| **Stage 1** | Split PDF into page chunks, submit in parallel | Stage 0 returns empty |
| **Stage 2** | Re-compress PDF stream to reduce file size | Stage 1 returns empty |
| **Stage 3** | Rotate PDF (0° / 90° / 180° / 270°), try each | Stage 2 returns empty |

All stages use the same exponential backoff with ±20% jitter on 429 rate-limit
responses. Chunk size and retry count are configurable:

```python
build_pipeline(
    ...,
    page_chunk_size=5,    # pages per Stage-1 chunk (default: 10)
    max_retries=3,        # retry attempts on 429 (default: 5)
    poll_timeout_seconds=60,  # per-call timeout (default: 120)
)
```

## Field map normalisation

Field map keys are matched with full whitespace and punctuation tolerance — write
them in whichever form is readable to you:

| You write | Azure DI returns | Resolved |
|---|---|---|
| `"wages, tips, other compensation"` | `"Wages, tips, other compensation"` | ✓ exact |
| `"statutory employee"` | `"Statutory\nemployee"` | ✓ whitespace-normalised |
| `"wages tips other compensation"` | `"Wages, tips, other compensation"` | ✓ simplified |

Three resolution stages run in order:
1. Whitespace-normalised exact match (collapses `\n`/`\t`, preserves punctuation)
2. Simplified match (strips special chars from both sides)
3. Snake-case fallback — unmatched fields are still emitted, never dropped

Checkbox values (`:selected:`, `:unselected:`) are parsed as `None` automatically.

## License

`azure-di-financial-haystack` is distributed under the terms of the
[Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
