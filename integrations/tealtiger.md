---
layout: integration
name: TealTiger
description: Deterministic governance component for Haystack pipelines — policy enforcement, PII detection, cost tracking, and structured audit evidence.
authors:
    - name: TealTiger Team
      socials:
        github: https://github.com/agentguard-ai/tealtiger
        twitter: https://x.com/TealtigerAI
pypi: https://pypi.org/project/tealtiger-haystack
repo: https://github.com/agentguard-ai/tealtiger/tree/main/packages/haystack-tealtiger
type: Custom Component
report_issue: https://github.com/agentguard-ai/tealtiger/issues
logo: /logos/tealtiger.png
version: Haystack 2.0
---


# TealTiger Governance for Haystack

[![PyPI - Version](https://img.shields.io/pypi/v/tealtiger-haystack.svg)](https://pypi.org/project/tealtiger-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tealtiger-haystack.svg)](https://pypi.org/project/tealtiger-haystack)

Add deterministic governance to any Haystack pipeline. No LLM in the governance path — all policy evaluation is deterministic, adding <2ms latency.

## Installation

```bash
pip install tealtiger-haystack
```

## Usage ⚡️

### Zero-Config Mode (Observe)

Add governance with zero configuration. TealTiger observes all traffic, tracks cost, detects PII, and allows everything through — producing structured audit entries for observability.

```python
from haystack import Pipeline
from haystack_integrations.components.connectors.tealtiger import (
    TealTigerGovernanceComponent,
)

pipeline = Pipeline()
pipeline.add_component("governance", TealTigerGovernanceComponent())
pipeline.add_component("llm", your_generator)
pipeline.connect("governance.text", "llm.prompt")

result = pipeline.run({"governance": {"text": "What is the capital of France?"}})
# result["governance"]["decision"] contains:
# - correlation_id: UUID v4 for tracing
# - action: "ALLOW"
# - pii_detected: []
# - cost_tracked: estimated cost
# - evaluation_time_ms: <2ms
```

### Policy Mode (Enforce)

When you provide a `TealEngine` instance, the component evaluates configured policies and blocks requests that violate governance rules.

```python
from tealtiger import TealEngine
from haystack_integrations.components.connectors.tealtiger import (
    TealTigerGovernanceComponent,
)

engine = TealEngine(policies=[
    {"type": "cost_limit", "max_per_session": 5.00},
    {"type": "pii_block", "categories": ["ssn", "credit_card"]},
])

pipeline = Pipeline()
pipeline.add_component(
    "governance",
    TealTigerGovernanceComponent(engine=engine, mode="ENFORCE"),
)
pipeline.add_component("llm", your_generator)
pipeline.connect("governance.text", "llm.prompt")

# Raises GovernanceDenyError if policy violated
result = pipeline.run({"governance": {"text": "Process this request"}})
```

## Features

- **Zero-config**: Observe, track cost, detect PII — no setup required
- **Policy enforcement**: Block requests that violate governance rules (ENFORCE mode)
- **PII detection**: Email, SSN, credit card, phone, IP address
- **Cost tracking**: Per-evaluation and cumulative with budget enforcement
- **Structured audit**: UUID v4 correlation IDs, risk scoring, timing
- **Fail-closed**: Engine errors result in DENY in ENFORCE mode
- **<2ms latency**: Deterministic, in-process, no external service

## Support 📞

- [GitHub Issues](https://github.com/agentguard-ai/tealtiger/issues)
- [TealTiger Documentation](https://tealtiger.ai)
- [OWASP ASI Coverage](https://github.com/agentguard-ai/tealtiger) — 8/10 Agentic Security Index categories
