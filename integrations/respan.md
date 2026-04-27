---
layout: integration
name: Respan
description: Trace and monitor your Haystack pipelines with Respan
authors:
    - name: Respan
      socials:
        github: respanai
        twitter: respanai
        linkedin: https://www.linkedin.com/company/respanai/
pypi: https://pypi.org/project/respan-exporter-haystack/
repo: https://github.com/respanai/respan
type: Monitoring Tool
report_issue: https://github.com/respanai/respan/issues
logo: /logos/respan.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Resources](#resources)

## Overview

[Respan](https://respan.ai/) is an observability platform for monitoring and tracing LLM applications. The `respan-exporter-haystack` package provides components that integrate into Haystack pipelines to automatically capture traces, including API calls, latency, token usage, cost, and tool invocations.

For a detailed integration guide, see the [Respan Haystack Tracing Guide](https://respan.ai/docs/integrations/tracing/haystack).

## Installation

```bash
pip install respan-exporter-haystack haystack-ai
```

## Usage

This integration provides the following components:

- **`RespanConnector`**: A pass-through component that connects to your pipeline's generator to trace operations and data flow. It forwards the prompt to the connected component while sending trace data to Respan.
- **`RespanTracer`**: An alternative tracing integration for Haystack pipeline execution.
- **`RespanGenerator`**: Routes LLM calls through the Respan gateway, providing observability without needing a separate provider API key.
- **`RespanChatGenerator`**: Chat-specific gateway component for routing chat completions through Respan.

### Set up your API key

Sign up at [platform.respan.ai](https://platform.respan.ai), generate an API key from the [API keys page](https://platform.respan.ai/platform/api/api-keys), and set it as an environment variable:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
```

### Trace a pipeline with `RespanConnector`

Add `RespanConnector` to your pipeline and connect it to the generator component. The connector accepts the prompt, forwards it to the generator, and sends trace data to Respan.

> This example uses `OpenAIGenerator` and requires an `OPENAI_API_KEY` environment variable. When using `RespanGenerator` or `RespanChatGenerator` instead, only `RESPAN_API_KEY` is needed.

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from respan_exporter_haystack import RespanConnector

pipeline = Pipeline()
pipeline.add_component("respan", RespanConnector(api_key="your-api-key"))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("respan", "llm")

result = pipeline.run({"respan": {"prompt": "Tell me a joke about AI"}})
print(result)
```

Once you run this, open the [Traces page](https://platform.respan.ai/platform/traces) to see your pipeline trace.

### Use `RespanGenerator` as a gateway

Instead of tracing with a connector, you can route LLM calls directly through Respan as a gateway. This means you only need your Respan API key — no separate provider key required.

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from respan_exporter_haystack import RespanGenerator

pipeline = Pipeline()
pipeline.add_component("prompt_builder", PromptBuilder(template="Tell me about {{topic}}"))
pipeline.add_component("llm", RespanGenerator(api_key="your-api-key", model="gpt-4o-mini"))

pipeline.connect("prompt_builder", "llm")

result = pipeline.run({"prompt_builder": {"topic": "Haystack pipelines"}})
print(result["llm"]["replies"][0])
```

### Use Respan-managed prompts

You can use prompts managed in the Respan platform by passing a `prompt_id` and `prompt_version` to `RespanGenerator`:

```python
from respan_exporter_haystack import RespanGenerator

generator = RespanGenerator(
    api_key="your-api-key",
    model="gpt-4o-mini",
    prompt_id="your-prompt-id",
    prompt_version=1,
)
```

## Configuration

### `RespanConnector`

- `api_key` (optional) — Your Respan API key. Falls back to the `RESPAN_API_KEY` environment variable.
- `base_url` (optional) — API base URL. Falls back to the `RESPAN_BASE_URL` environment variable.

### `RespanGenerator` / `RespanChatGenerator`

- `api_key` (optional) — Your Respan API key. Falls back to `RESPAN_API_KEY`.
- `model` (required) — Model to use (e.g., `"gpt-4o-mini"`).
- `base_url` (optional) — Gateway base URL. Defaults to `https://api.respan.ai/api`.

### Custom attributes

Pass Respan attributes through the connector to filter and group traces in the dashboard:

```python
result = pipeline.run({
    "respan": {
        "prompt": "Tell me a joke",
        "customer_identifier": "user-123",
        "metadata": {"team": "ml"},
    }
})
```

- `customer_identifier` — User or customer ID for filtering traces in the dashboard.
- `metadata` — Custom key-value pairs attached to trace data.

See the [Haystack Exporter SDK Reference](https://respan.ai/docs/sdks/python/exporters/haystack) for the full API.

## Resources

- [Respan Haystack Tracing Guide](https://respan.ai/docs/integrations/tracing/haystack)
- [Respan Haystack Gateway Guide](https://respan.ai/docs/integrations/gateway/haystack)
- [Haystack Exporter SDK Reference](https://respan.ai/docs/sdks/python/exporters/haystack)
- [Respan Documentation](https://respan.ai/docs)
