---
layout: integration
name: Arize AI
description: Trace and Monitor your Haystack pipelines with Arize AI
authors:
  - name: Arize AI
    socials:
      github: Arize-ai
      twitter: arizeai
      linkedin: https://www.linkedin.com/company/arizeai/
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

Arize is AI Observability and Evaluation platform designed to help you troubleshoot, evaluate, and experiment on LLM and ML applications. Developers use Arize to get applications working quickly, evaluate performance, detect and prevent production issues, and curate datasets.

- [Documentation for Arize AI + Haystack](https://docs.arize.com/arize/large-language-models/tracing/auto-instrumentation/haystack)

## Installation

```bash
pip install openinference-instrumentation-haystack haystack-ai arize-otel opentelemetry-sdk opentelemetry-exporter-otlp
```

## Usage

To trace any Haystack pipeline with Arize, simply initialize OpenTelemetry and the `HaystackInstrumentor`. Haystack pipelines that run within the same environment send traces to Arize.

```python
from openinference.instrumentation.haystack import HaystackInstrumentor
# Import open-telemetry dependencies
from arize_otel import register_otel, Endpoints

# Setup OTEL via our convenience function
register_otel(
    endpoints = Endpoints.ARIZE,
    space_id = "<your-space-id>", # from the space settings page
    api_key = "<your-api-key>", # from the space settings page
    model_id = "<your-haystack-app-name>", # name this to whatever you would like
)
```

Now, you can run a Haystack pipeline within the same environment, resulting in the following trace:

> To run the example below, export your OpenAI Key to the `OPENAI_API_KEY` environment variable.

![Arize Demo](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/arize-demo.gif)

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
