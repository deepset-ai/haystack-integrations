---
layout: integration
name: TealTiger
description: Deterministic governance, cost tracking, and PII detection for Haystack pipelines. No LLM in the governance path.
authors:
  - name: TealTiger
    socials:
      github: agentguard-ai
      twitter: TealtigerAI
      linkedin: https://www.linkedin.com/company/tealtiger
pypi: https://pypi.org/project/tealtiger-haystack
repo: https://github.com/agentguard-ai/tealtiger
type: Custom Component
report_issue: https://github.com/agentguard-ai/tealtiger/issues
logo: /logos/tealtiger.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Support](#support)
- [License](#license)

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/tealtiger-haystack.svg)](https://pypi.org/project/tealtiger-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tealtiger-haystack.svg)](https://pypi.org/project/tealtiger-haystack)

Add deterministic governance to any Haystack pipeline. No LLM in the governance path — all policy evaluation is deterministic, adding <2ms latency.

## Installation

```bash
pip install tealtiger-haystack
```

## Usage

### Zero-Config Mode (Observe)

No policies needed — just add the component and get instant visibility into cost, PII, and tool usage:

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.connectors.tealtiger import TealTigerGovernanceComponent

pipeline = Pipeline()
pipeline.add_component("governance", TealTigerGovernanceComponent())
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("governance.text", "llm.prompt")

result = pipeline.run({"governance": {"text": "What is the capital of France?"}})

# Access governance decision
decision = result["governance"]["decision"]
print(decision["action"])         # "ALLOW"
print(decision["cost_tracked"])   # 0.0023
print(decision["pii_detected"])   # []
```

### Policy Mode (Enforce)

Add a TealEngine with policies for full governance enforcement:

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from tealtiger import TealEngine
from haystack_integrations.components.connectors.tealtiger import TealTigerGovernanceComponent

engine = TealEngine(policies=[
    {"type": "cost_limit", "max_per_session": 5.00},
    {"type": "pii_block", "categories": ["ssn", "credit_card"]},
])

pipeline = Pipeline()
pipeline.add_component(
    "governance",
    TealTigerGovernanceComponent(engine=engine, mode="ENFORCE"),
)
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("governance.text", "llm.prompt")

result = pipeline.run({"governance": {"text": "Process payment for card 4111-1111-1111-1111"}})
# PII detected → action: "DENY"
```

## Features

- **Deterministic** — Same input + same policy = same decision, every time
- **<2ms overhead** — No LLM in the governance path
- **Zero-config mode** — Observe cost, PII, and behavior without writing policies
- **Policy enforcement** — ALLOW, DENY, REQUIRE_APPROVAL, REVISE decisions
- **Cost tracking** — Per-request and cumulative session cost
- **PII detection** — Email, phone, SSN, credit card, IP address patterns
- **Audit trail** — Every decision produces a structured evidence record
- **TEEC receipts** — Compliance-grade execution receipts with correlation IDs

## Support

- [GitHub Issues](https://github.com/agentguard-ai/tealtiger/issues)
- [TealTiger Documentation](https://tealtiger.ai)
- [OWASP ASI Coverage](https://github.com/agentguard-ai/tealtiger) — 8/10 Agentic Security Index categories

## License

`tealtiger-haystack` is distributed under the [Apache 2.0 License](https://opensource.org/licenses/Apache-2.0).
