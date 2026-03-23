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

[Respan](https://respan.ai/) is an observability platform for monitoring and tracing LLM applications. The `respan-exporter-haystack` package provides a `RespanConnector` component that integrates directly into Haystack pipelines to automatically capture traces, including API calls, latency, token usage, cost, and tool invocations.

For a detailed integration guide, see the [Respan Haystack Tracing Guide](https://respan.ai/docs/integrations/tracing/haystack).

## Installation

```bash
pip install respan-exporter-haystack haystack-ai
```

## Usage

### Components

This integration provides the following components:

- **`RespanConnector`**: Connects Haystack pipelines to Respan for tracing. Add it to your pipeline and it will automatically trace all operations and data flow. It does not need to be connected to other components.

- **`RespanGenerator`**: Routes LLM calls through the Respan gateway, providing observability without needing a separate provider API key.

- **`RespanChatGenerator`**: Chat-specific gateway component for routing chat completions through Respan.

### Set up environment variables

Sign up at [platform.respan.ai](https://platform.respan.ai), generate an API key from the [API keys page](https://platform.respan.ai/platform/api/api-keys), and set it as an environment variable:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

### Trace a pipeline with `RespanConnector`

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

### Use `RespanConnector` in a RAG pipeline

```python
from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from respan_exporter_haystack import RespanConnector

document_store = InMemoryDocumentStore()
document_store.write_documents([
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome."),
])

prompt_template = """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{question}}
Answer:
"""

pipeline = Pipeline()
pipeline.add_component("tracer", RespanConnector(api_key="your-api-key"))
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
pipeline.add_component("llm", OpenAIGenerator())

pipeline.connect("retriever", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

question = "Who lives in Paris?"
result = pipeline.run({
    "retriever": {"query": question},
    "prompt_builder": {"question": question},
})

print(result["llm"]["replies"][0])
```

### Use `RespanGenerator` as a gateway

Instead of tracing with a connector, you can route LLM calls directly through Respan as a gateway:

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

## Configuration

### Connector options

| Parameter  | Type             | Default                  | Description          |
| ---------- | ---------------- | ------------------------ | -------------------- |
| `api_key`  | str \| None      | `RESPAN_API_KEY` env var | Your Respan API key  |
| `base_url` | str \| None      | `https://api.respan.ai`  | API endpoint         |

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

| Attribute             | Description                             |
| --------------------- | --------------------------------------- |
| `customer_identifier` | User or customer ID for filtering       |
| `metadata`            | Custom key-value pairs for trace data   |

## Resources

- [Respan Haystack Tracing Guide](https://respan.ai/docs/integrations/tracing/haystack)
- [Respan Haystack Gateway Guide](https://respan.ai/docs/integrations/gateway/haystack)
- [Haystack Exporter SDK Reference](https://respan.ai/docs/sdks/python/exporters/haystack)
- [Respan Documentation](https://respan.ai/docs)
