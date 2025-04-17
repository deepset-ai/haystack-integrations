---
layout: integration
name: Arize Phoenix
description: Trace your Haystack pipelines with Arize Phoenix
authors:
  - name: Arize AI
    socials:
      github: Arize-ai
      twitter: ArizePhoenix
      linkedin: https://www.linkedin.com/company/arizeai/
pypi: https://pypi.org/project/openinference-instrumentation-haystack/
repo: https://github.com/Arize-ai/phoenix
type: Monitoring Tool
report_issue: https://github.com/Arize-ai/openinference/issues
logo: /logos/arize-phoenix.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Resources](#resources)

## Overview

**Arize Phoenix** is Arize's open-source platform that offers developers the quickest way to troubleshoot, evaluate, and experiment with LLM applications.

For a detailed integration guide, see the [documentation for Phoenix + Haystack](https://docs.arize.com/phoenix/tracing/integrations-tracing/haystack)

## Installation

```bash
pip install openinference-instrumentation-haystack haystack-ai opentelemetry-sdk opentelemetry-exporter-otlp arize-phoenix
```

## Usage

To trace any Haystack pipeline with Phoenix, simply initialize OpenTelemetry and the `HaystackInstrumentor`. Haystack pipelines that run within the same environment send traces to Phoenix.

First, start a Phoenix instance to send traces to.

```sh
python -m phoenix.server.main serve
```

Now let's connect our Haystack pipeline to Phoenix using OpenTelemetry.

```python
from openinference.instrumentation.haystack import HaystackInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

endpoint = "http://localhost:6006/v1/traces" # The URL to your Phoenix instance
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

HaystackInstrumentor().instrument(tracer_provider=tracer_provider)
```

Now, you can run a Haystack pipeline within the same environment, resulting in the following trace:

> To run the example below, export your OpenAI Key to the `OPENAI_API_KEY` environment variable.

![Arize Phoenix Demo](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/arize-demo.gif)

```python
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

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

## Resources

- Check out the Phoenix [GitHub repository](https://github.com/Arize-ai/phoenix)
- For an in-depth guide on how to host your own Phoenix instance, see the [Phoenix documentation](https://docs.arize.com/phoenix/deployment)
- Try out free hosted Phoenix instances at [phoenix.arize.com](https://phoenix.arize.com/)
- Check out the [Phoenix documentation](https://docs.arize.com/phoenix)
