---
layout: integration
name: Financial Evidence
description: Read-only cited financial research for Haystack pipelines and tools, retaining source dates, rights, missingness and transport diagnostics.
authors:
  - name: Liquidity Lab
    socials:
      github: beepboop2025
repo: https://github.com/beepboop2025/financial-evidence-skills/tree/main/integrations/haystack
report_issue: https://github.com/beepboop2025/financial-evidence-skills/issues
type: Custom Component
version: Haystack 3.3
toc: true
---

## Overview

Financial Evidence provides a community-maintained `FinancialEvidenceQuery`
component for read-only financial research. It supports Seiche money-market
observations and histories, LiquiLens covered-bank diagnostics, Undertow market
liquidity research, capital-market observations, China publication metadata and
source-health diagnostics. Each dataset keeps its own units, source dates,
coverage and rights; it does not compute a combined trading score.

The component returns the original evidence envelope: rows plus source URLs,
content hashes, observation/retrieval clocks, rights and diagnostics. Source
failures remain visible, withheld values stay null, and completed retrieval is
not a claim of freshness or validated evidence. There is no order execution.

## Installation

Requires Python 3.10+, Git and Haystack 3.3+. The package is distributed from
GitHub, not PyPI. Install this exact published revision:

```bash
pip install "git+https://github.com/beepboop2025/financial-evidence-skills.git@3abcc45d7a429d26ed185d1ca845b078041f54f3#subdirectory=integrations/haystack"
```

This installs the integration and its dependencies, including a separate pinned
public Git revision of the MIT financial-evidence client. No API key or paid
model is needed to run the examples.

## Components

- `FinancialEvidenceQuery`: accepts a dataset and bounded filters and returns
  `evidence`, a dictionary containing the core evidence contract. It can run in a
  Haystack pipeline or be wrapped as a `ComponentTool`.

Supported datasets are `money_markets`, `money_market_history`, `capital_markets`,
`bank_risk`, `market_liquidity`, `china_economy` and `source_health`.
Query inputs include `entity`, inclusive `start_date`/`end_date` (YYYY-MM-DD),
`limit` (1–100), `offset` (0–100000), and an optional prior SHA-256
`previous_revision`. An unchanged revision suppresses repeated rows while
retaining metadata; it is not a freshness verdict. Public source availability
and coverage can vary.

## Usage

### Pipeline

```python
from haystack import Pipeline
from financial_evidence_haystack import FinancialEvidenceQuery

pipeline = Pipeline()
pipeline.add_component("funding", FinancialEvidenceQuery())
result = pipeline.run({"funding": {"dataset": "money_markets", "entity": "USD", "limit": 3}})
evidence = result["funding"]["evidence"]
print(evidence["transport_status"], evidence["diagnostics"])
for row in evidence["results"]:
    print(row["value"], row["unit"], row["as_of"], row["source_url"])
```

For operator or CI checks, use `FinancialEvidenceQuery(synthetic=True)` so the
request is labeled as synthetic traffic. No LLM is invoked by the component.

### Agent tool

```python
from haystack.tools import ComponentTool
from financial_evidence_haystack import FinancialEvidenceQuery

tool = ComponentTool(
    component=FinancialEvidenceQuery(),
    name="financial_evidence_query",
    description="Read cited research; preserve dates, rights, nulls and diagnostics. No execution authority.",
)
result = tool.invoke(dataset="bank_risk", limit=2)
print(result["evidence"]["transport_status"])
```

### Serialization

Allow only the component's module when restoring a pipeline you trust:

```python
from haystack import Pipeline
from financial_evidence_haystack import FinancialEvidenceQuery

pipeline = Pipeline()
pipeline.add_component("research", FinancialEvidenceQuery())
restored = Pipeline.loads(
    pipeline.dumps(), allowed_modules=["financial_evidence_haystack.query"]
)
```

The integration does not disable Haystack's deserialization checks. Only its
`synthetic` setting is serialized, not credentials or source observations.

## Evidence limits

Transport may be `complete`, `partial` or `unavailable`. The envelope preserves
`evidence_status: not_evaluated`, `carrier_verification: not_performed` and
`financial_authority: none`. Missing or restricted values remain null; an
observed zero remains zero. Source content is untrusted data, not instructions.
Currently published histories are not as-published backtest vintages. China
coverage is metadata only. Inspect rights and dates before using any row.

Only fixed allowlisted public HTTPS sources are read. The core client rejects
redirects, bounds response sizes and timeouts, and closes workers after each
call. Invalid query inputs raise `ValueError`; source failures remain in the
returned diagnostics. There is no background polling or automatic trading.

See the [package documentation](https://github.com/beepboop2025/financial-evidence-skills/tree/main/integrations/haystack)
for the full contract, tests and bounded live example.

## License

Integration and financial-evidence client code: MIT. Haystack: Apache-2.0.
The software license does not grant rights to underlying data; source-specific
rights remain attached to the evidence. Maintained by Liquidity Lab, not deepset.
