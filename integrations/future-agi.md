---
layout: integration
name: Future AGI
description: OpenTelemetry tracing and evaluation for Haystack pipelines via traceAI.
authors:
    - name: Future AGI
      socials:
        github: future-agi
        linkedin: https://www.linkedin.com/company/futureagi/
pypi: https://pypi.org/project/traceAI-haystack/
repo: https://github.com/future-agi/traceAI/tree/main/python/frameworks/haystack
type: Monitoring Tool
report_issue: https://github.com/future-agi/traceAI/issues
logo: /logos/future-agi.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Resources](#resources)
- [License](#license)

## Overview

[Future AGI](https://futureagi.com) is an open-source e2e agent engineering and optimization platform that helps you ship self-improving AI agents. The `traceAI-haystack` package auto-instruments Haystack pipelines and exports spans to any OTLP-compatible backend (Future AGI, Jaeger, Datadog, etc.).

Once registered, every component run, generator call, retriever query, and pipeline execution is captured as a structured OpenTelemetry span — no per-component wiring required.

## Installation

```bash
pip install traceAI-haystack
```

For the example pipeline below, you also need:

```bash
pip install haystack-ai trafilatura
```

## Usage

### Components

This integration introduces one component:

- The `HaystackInstrumentor`: registers OpenTelemetry instrumentation on Haystack's `Pipeline.run`, `Component.run`, and generator/retriever execution paths. Once `instrument()` is called, every Haystack pipeline run produces a trace automatically.

  Set the `FI_API_KEY` and `FI_SECRET_KEY` environment variables to authenticate with Future AGI. These code examples also require an [`OPENAI_API_KEY`](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key). Haystack is model-agnostic; swap the generator for any provider you prefer.

### Set environment variables

```python
import os

os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["FI_API_KEY"] = "your-futureagi-api-key"
os.environ["FI_SECRET_KEY"] = "your-futureagi-secret-key"
```

### Register the tracer provider

```python
from fi_instrumentation import register
from fi_instrumentation.fi_types import ProjectType

trace_provider = register(
    project_type=ProjectType.OBSERVE,
    project_name="haystack_project",
)
```

### Instrument Haystack

```python
from traceai_haystack import HaystackInstrumentor

HaystackInstrumentor().instrument(tracer_provider=trace_provider)
```

### Run a Haystack pipeline

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

fetcher = LinkContentFetcher()
converter = HTMLToDocument()
prompt_builder = ChatPromptBuilder(
    template=[
        ChatMessage.from_user(
            "Answer the question based on the following context.\n"
            "Context: {{ documents[0].content }}\n"
            "Question: {{ query }}"
        )
    ]
)
generator = OpenAIChatGenerator(model="gpt-4o-mini")

pipeline = Pipeline()
pipeline.add_component("fetcher", fetcher)
pipeline.add_component("converter", converter)
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("generator", generator)

pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "generator.messages")

result = pipeline.run(
    {
        "fetcher": {"urls": ["https://haystack.deepset.ai/"]},
        "prompt_builder": {"query": "What is Haystack?"},
    }
)

print(result["generator"]["replies"][0].text)
```

The pipeline run, every component, the LLM call, and token usage are captured as a single trace.

![Future AGI dashboard showing a Haystack pipeline trace](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/future-agi-ui.png)

## Resources

- Sign up at [app.futureagi.com](https://app.futureagi.com) to get your `FI_API_KEY` and `FI_SECRET_KEY`
- [Full integration guide](https://docs.futureagi.com/docs/integrations/traceai/haystack)
- [`traceAI` on GitHub](https://github.com/future-agi/traceAI)
- [Future AGI documentation](https://docs.futureagi.com)

### License

`traceAI-haystack` is released under the [MIT License](https://github.com/future-agi/traceAI/blob/main/LICENSE).
