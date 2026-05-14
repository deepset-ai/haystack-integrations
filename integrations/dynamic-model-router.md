---
layout: integration
name: Dynamic Model Router
description: Pre-call task classifier that routes each Haystack generator call to the cheapest model tier that can handle the task — no proxy, no extra network hop.
authors:
    - name: Manthan Vaghela
      socials:
        github: manthan9891994
        linkedin: https://www.linkedin.com/in/manthansinhvaghela/
pypi: https://pypi.org/project/dynamic-model-router/
repo: https://github.com/manthan9891994/agents-multi-model-support
type: Model Provider
report_issue: https://github.com/manthan9891994/agents-multi-model-support/issues
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [How routing works](#how-routing-works)
- [Cost reduction](#cost-reduction)

## Overview

[Dynamic Model Router](https://github.com/manthan9891994/agents-multi-model-support) is a pre-call task classifier. It analyzes each prompt and routes it to the cheapest model tier (low / medium / high) that can produce a correct response — *before* the API call is made.

For Haystack users, it returns a routed generator pinned to the right model, so you can keep your existing pipelines intact and just swap the generator construction step.

- **3-layer cascade** — L1 keywords (<1ms) → L3 frozen MiniLM ML head (~15ms) → L2 LLM fallback (~500ms)
- **No proxy** — runs in-process, no extra network hop, no vendor lock-in
- **Pluggable telemetry** — SQLite / Postgres / BigQuery / DynamoDB / GCS / your own backend, or just Python logging
- **Configurable** — tune the keyword packs, complexity thresholds, and tier definitions to your domain

## Installation

```bash
pip install dynamic-model-router haystack-ai
```

With the optional ML head (recommended for better classification on ambiguous tasks):

```bash
pip install 'dynamic-model-router[ml]' haystack-ai
```

## Usage

The integration provides a single helper, `get_generator`, that classifies the task and returns a Haystack generator pinned to the routed model:

```python
from classifier.integrations.haystack import get_generator
from haystack import Pipeline
from haystack.components.builders import PromptBuilder

# Simple task -> routes to a low-tier model
gen_simple = get_generator("What is the capital of France?")

# Complex task -> routes to a high-tier model
gen_complex = get_generator(
    "Compare CQRS and event sourcing for a healthcare records system "
    "under HIPAA constraints. Discuss trade-offs in 2 paragraphs."
)

# Use either generator in a Haystack pipeline as usual
pipe = Pipeline()
pipe.add_component("prompt", PromptBuilder(template="{{ task }}"))
pipe.add_component("llm", gen_complex)
pipe.connect("prompt", "llm")

result = pipe.run({"prompt": {"task": "..."}})
```

You can pin a provider, attach a fallback model, and pass through any generator kwargs:

```python
gen = get_generator(
    "summarize this contract clause",
    provider="openai",
    fallback_model="gpt-4o-mini",
    generation_kwargs={"max_tokens": 200},
)
```

## How routing works

```
                   ┌────────────────────────────────────────┐
   prompt  ───────▶│  L1: keyword packs           (<1 ms)   │──▶ tier
                   └────────────────────────────────────────┘
                              │  unsure?
                              ▼
                   ┌────────────────────────────────────────┐
                   │  L3: frozen MiniLM ML head   (~15 ms)  │──▶ tier
                   └────────────────────────────────────────┘
                              │  still unsure?
                              ▼
                   ┌────────────────────────────────────────┐
                   │  L2: small-model LLM         (~500 ms) │──▶ tier
                   └────────────────────────────────────────┘
```

Each layer can short-circuit. Most prompts never reach the LLM fallback — the keyword layer alone resolves typical FAQ / lookup / code / translation tasks.

## Cost reduction

Cost reduction depends entirely on your traffic mix and how you tune the cascade for your domain. On mixed-complexity workloads (FAQs + lookups + occasional analytical questions), typical savings are **60–80%** versus sending everything to a frontier reasoning model. The cascade is fully configurable: tune the keyword packs, complexity thresholds, and tier definitions to your own data to maximize savings.

## Telemetry

Every routing decision and outcome can be emitted to a pluggable backend:

```python
from classifier import Router
from classifier.logger_backends import StdoutLoggerBackend  # or SQLite, Postgres, BigQuery, ...

router = Router(decision_logger=StdoutLoggerBackend())
```

See the [backends examples](https://github.com/manthan9891994/agents-multi-model-support/tree/master/examples/custom_backends) for SQLite / Postgres / BigQuery / DynamoDB / GCS templates.

## Links

- **PyPI**: [pypi.org/project/dynamic-model-router](https://pypi.org/project/dynamic-model-router/)
- **GitHub**: [manthan9891994/agents-multi-model-support](https://github.com/manthan9891994/agents-multi-model-support)
- **License**: MIT
