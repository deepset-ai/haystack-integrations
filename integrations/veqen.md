---
layout: integration
name: Veqen
description: See what your Haystack AI requests cost and which customer or feature they served, without sending their content to Veqen.
authors:
  - name: Keyveve, Inc.
    socials:
      github: Keyveve
pypi: https://pypi.org/project/veqen/
repo: https://github.com/Keyveve/veqen-sdks
report_issue: https://github.com/Keyveve/veqen-sdks/issues
type: Monitoring Tool
version: Haystack 3.4
toc: true
---

## Overview

[Veqen](https://veqen-app.com/integrations/haystack?utm_source=haystack&utm_medium=integration&utm_campaign=launch-v1-5) helps you scale AI inference without losing track of the bill. See what your Haystack requests cost and who they were for, then check the totals against your provider bills in the optional dashboard.

The `VeqenOpenAICostTracker` component reads token counts from an OpenAI-compatible chat reply, calculates its cost and passes the reply through unchanged. Your prompt and response content are not sent to Veqen.

Local cost recording needs no Veqen account. Optional hosted reporting adds spending breakdowns, provider-bill reconciliation and shared budgets. The component sends usage and allocation tags only; it does not send message content to Veqen.

## Installation

Requires Python 3.11 or later and Haystack 3.4. The component is included in Veqen 1.2.0 and later:

```bash
pip install "veqen[haystack]>=1.2,<2"
```

## Usage

Set `OPENAI_API_KEY` in your environment for the generator. To send usage to the hosted ledger, also set `VEQEN_API_KEY` to a send-only key from your Veqen organization. Keep credentials out of source files.

```python
import veqen
from haystack import Pipeline
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from veqen.integrations.haystack import VeqenOpenAICostTracker

veqen.init(ledger_file=".veqen/ledger.jsonl")

pipeline = Pipeline()
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipeline.add_component("cost", VeqenOpenAICostTracker(tags={"feature": "support"}))
pipeline.connect("llm.replies", "cost.replies")

try:
    result = pipeline.run({
        "llm": {"messages": [ChatMessage.from_user("Explain a cost ledger in one sentence.")]},
        "cost": {"customer": "customer-123"},
    })
    print(result["cost"]["recorded"], result["cost"]["recording_status"])
finally:
    veqen.flush()
```

Use internal identifiers for tags, not personal information. For another OpenAI-compatible provider, pass its provider key to `VeqenOpenAICostTracker(provider="together")` so rates use the intended host. Do not also wrap or instrument the same generator through another Veqen recording path.

## Outputs and limitations

- `replies`: the original chat messages.
- `recorded`: whether usage was passed to the SDK, not a guarantee of remote delivery or a known price.
- `recording_status`: `recorded`, `missing_usage`, `invalid_usage`, `unsupported_usage` or `requires_one_reply`.

The component supports one reply per request (`n=1`) with OpenAI-shaped prompt, completion and cached-token usage. It rejects malformed or missing usage rather than fabricating a cost. Audio-token and cache-write metadata are not supported by this component. It runs **after** inference and cannot prevent a request or enforce a pre-call budget.

The repository includes [pipeline, serialization, usage and privacy tests](https://github.com/Keyveve/veqen-sdks/blob/main/python/tests/test_haystack.py) and a [standalone example](https://github.com/Keyveve/veqen-sdks/tree/main/examples/haystack). See the [integration guide](https://veqen-app.com/integrations/haystack) and [Python SDK](https://veqen-app.com/docs/python) for more detail.

## License

The SDK is [MIT licensed](https://github.com/Keyveve/veqen-sdks/blob/main/LICENSE). The price book preserves [upstream attribution](https://github.com/Keyveve/veqen-sdks/blob/main/python/THIRD_PARTY_NOTICES).
