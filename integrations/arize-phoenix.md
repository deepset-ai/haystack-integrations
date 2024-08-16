---
layout: integration
name: Arize Phoenix
description: Trace your Haystack pipelines with Arize Phoenix
authors:
  - name: Arize AI
    socials:
      github: Arize-ai
      twitter: ArizePhoenix
      linkedin: arizeai
pypi: https://pypi.org/project/openinference-instrumentation-haystack/
repo: https://github.com/Arize-ai/openinference
type: Monitoring Tool
report_issue: https://github.com/Arize-ai/openinference/issues
logo: /logos/arize.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

**Arize Phoenix** is Arize's open-source platform that offers developers the quickest way to troubleshoot, evaluate, and experiment with LLM applications.

You can bring your Haystack pipelines to either a [hosted Phoenix](https://phoenix.arize.com) or opting for a [self-hosted version](https://docs.arize.com/phoenix/deployment).

For a detailed integration guide, see the [documentation for Phoenix + Haystack](https://docs.arize.com/phoenix/tracing/integrations-tracing/haystack)

## Installation

```bash
pip install openinference-instrumentation-haystack haystack-ai opentelemetry-sdk opentelemetry-exporter-otlp
```

## Usage

To trace any Haystack pipeline with Phoenix, simply initialize OpenTelemetry and the `HaystackInstrumentor`. Haystack pipelines that run within the same environment send traces to Phoenix.

You have 2 options:

- The easiest option is to [launch a hosted phoenix instance](https://phoenix.arize.com/) for free and to use the provided API key to [connect to it](https://docs.arize.com/phoenix/hosted-phoenix).
- There are also options to [self-host](https://docs.arize.com/phoenix/deployment/deploying-phoenix) or simply run Phoenix in [local environments](https://docs.arize.com/phoenix/setup/environments)

```python
import os
from openinference.instrumentation.haystack import HaystackInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GRPCSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPSpanExporter,
)

# Add Phoenix API Key for tracing if using hosted Phoenix
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}"

# Add Phoenix as the target for your traces
endpoint = "https://app.phoenix.arize.com/v1/traces" # Or your own phoenix instance
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

HaystackInstrumentor().instrument(tracer_provider=tracer_provider)
```

Now, you can run a Haystack pipeline within the same environment, resulting in the following trace:

> To run the example below, export your OpenAI Key to the `OPENAI_API_KEY` environment variable.

![Arize Phoenix Demo](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/arize-demo.gif)

```python
import os
from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder

document_store = InMemoryDocumentStore()
document_store.write_documents([
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome.")
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

retriever = InMemoryBM25Retriever(document_store=document_store)
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator()

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")

question = "Who lives in Paris?"
results = rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)

```
