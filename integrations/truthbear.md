---
layout: integration
name: Truth Bear (GAUGE)
description: Verify official facts with Bitcoin-anchored proof for Haystack pipelines.
authors:
  - name: changchinfu
    socials:
      github: CHANGCHINFU
pypi: https://pypi.org/project/mcp-gauge-x402
repo: https://github.com/CHANGCHINFU/mcp-gauge
type: Data Ingestion
report_issue: https://github.com/CHANGCHINFU/mcp-gauge/issues
logo: /logos/truthbear.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Usage](#usage)
- [License](#license)

## Overview

[Truth Bear (GAUGE)](https://truthbear.co) returns verifiable official-source records for AI pipelines.
Every record carries:

- The **official source URL** (FRED, USGS, SEC EDGAR, NOAA, EPA, and 180+ signals)
- A **SHA-256 record_hash** anchored to Bitcoin via daily Merkle tree + OpenTimestamps
- A **freshness stamp** and Ed25519 signature

Bundle tiers cross-check 3 independent official sources against each other.

Screening-level factual grounding, not decision-grade advice. If the data cannot be found, you do not pay.

## Usage

Truth Bear is available as an MCP server ([mcp-gauge-x402](https://www.npmjs.com/package/mcp-gauge-x402))
and via REST API at `https://api.truthbear.co`.

### REST API in a Haystack pipeline

```python
import requests
from haystack import Document

def get_verified_fact(query: str) -> Document:
    resp = requests.get(
        "https://api.truthbear.co/trust/preview",
        params={"q": query}
    )
    data = resp.json()
    return Document(
        content=f"{data.get('value', '')} (source: {data.get('source_url', '')})",
        meta={
            "record_hash": data.get("record_hash"),
            "source_url": data.get("source_url"),
            "freshness": data.get("freshness"),
        }
    )

fact = get_verified_fact("US unemployment rate")
print(fact.content)
print(f"record_hash: {fact.meta['record_hash']}")
```

### MCP Server

Install and run the MCP server for full x402-paid access:

```bash
npx mcp-gauge-x402
```

Free tools (catalog, preview, sample, anchor verification) require no wallet.
Paid tools settle per call via x402 (USDC on Base) with no API key or signup.

### Key features

- **180+ signals** from official government sources
- **Bitcoin-anchored proof**: every record hash is independently re-verifiable
- **3-source cross-validation** in bundle tiers
- **No prediction, no advice**: descriptive only

## License

MIT
