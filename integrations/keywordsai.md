---
layout: integration
name: Keywords AI
description: Monitor, trace, and optimize your Haystack pipelines with Keywords AI
authors:
    - name: Keywords AI
      socials:
        github: Keywords-AI
        twitter: keywordsai
        linkedin: https://www.linkedin.com/company/keywordsai/
pypi: https://pypi.org/project/keywordsai-exporter-haystack/
repo: https://github.com/Keywords-AI/keywordsai/tree/main/python-sdks/keywordsai-exporter-haystack
type: Gateway & Monitoring Tool
report_issue: https://github.com/Keywords-AI/keywordsai/issues
logo: /logos/keywordsai.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Tracing](#tracing)
  - [Gateway](#gateway)
  - [Prompt Management](#prompt-management)
- [License](#license)

## Overview

[Keywords AI](https://keywordsai.co) is an LLM monitoring and optimization platform that provides two powerful integrations for Haystack:

**[Tracing](https://docs.keywordsai.co/integration/development-frameworks/tracing/haystack)**: Monitor multi-step Haystack pipelines with full workflow visibility. Track how data flows through retrievers, prompt builders, LLMs, and custom components with detailed timing, costs, and input/output at each step.

![Keywords AI Tracing](/images/keywordsai_tracing.png)

**[Gateway](https://docs.keywordsai.co/integration/development-frameworks/llm_framework/haystack)**: Route your LLM calls through Keywords AI's intelligent gateway for automatic logging, model fallbacks, load balancing, cost optimization, and prompt management.

![Keywords AI Gateway](/images/keywordsai_gateway.png)

### Features

- **Full Pipeline Tracing**: Capture complete execution flow with parent-child relationships between components
- **Automatic Gateway Logging**: Monitor all LLM requests without manual instrumentation
- **Cost & Token Tracking**: Real-time visibility into usage and spending across models
- **Prompt Management**: Store and version prompts on the Keywords AI platform
- **Model Fallbacks**: Automatic failover between LLM providers
- **Analytics Dashboard**: Visualize traces, metrics, and performance insights

Sign up for free at [keywordsai.co](https://keywordsai.co) to get started.

## Installation

```bash
pip install keywordsai-exporter-haystack
```

## Usage

### Tracing

Use `KeywordsAIConnector` to trace your entire Haystack pipeline execution. This works with any LLM provider (OpenAI, Anthropic, etc.).

#### Set Environment Variables

```bash
export KEYWORDSAI_API_KEY="your-keywords-ai-key"
export OPENAI_API_KEY="your-openai-key"
export HAYSTACK_CONTENT_TRACING_ENABLED="true"
```

The `HAYSTACK_CONTENT_TRACING_ENABLED` variable activates Haystack's tracing system.

#### Use `KeywordsAIConnector` in a Pipeline

```python
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from keywordsai_exporter_haystack import KeywordsAIConnector

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with tracing
pipeline = Pipeline()
pipeline.add_component("tracer", KeywordsAIConnector("My Workflow"))
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("prompt", "llm")

# Run pipeline
result = pipeline.run({"prompt": {"topic": "artificial intelligence"}})
print(result["llm"]["replies"][0])
print(f"\nTrace URL: {result['tracer']['trace_url']}")
```

The `KeywordsAIConnector` automatically captures all components in your pipeline. Note that the tracer component doesn't need to be connected to other components to work.

#### Use `KeywordsAIConnector` in a RAG Pipeline

First, install additional dependencies:

```bash
pip install sentence-transformers datasets
```

```python
from datasets import load_dataset
from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from keywordsai_exporter_haystack import KeywordsAIConnector

# Setup document store
document_store = InMemoryDocumentStore()
dataset = load_dataset("bilgeyucel/seven-wonders", split="train")
embedder = SentenceTransformersDocumentEmbedder("sentence-transformers/all-MiniLM-L6-v2")
embedder.warm_up()
docs_with_embeddings = embedder.run([Document(**ds) for ds in dataset]).get("documents") or []
document_store.write_documents(docs_with_embeddings)

# Build RAG pipeline
template = """
Given the following information, answer the question.
Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}
Question: {{question}}
Answer:
"""

pipeline = Pipeline()
pipeline.add_component("tracer", KeywordsAIConnector("RAG Pipeline"))
pipeline.add_component(
    "text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
)
pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store, top_k=2))
pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))

# Connect components (note: tracer doesn't need connections)
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
pipeline.connect("retriever", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

# Run pipeline
question = "What does Rhodes Statue look like?"
response = pipeline.run({
    "text_embedder": {"text": question},
    "prompt_builder": {"question": question}
})

print(response["llm"]["replies"][0])
print(f"\nTrace URL: {response['tracer']['trace_url']}")
```

View your traces at [platform.keywordsai.co/platform/traces](https://platform.keywordsai.co/platform/traces).

### Gateway

Use `KeywordsAIGenerator` to route LLM calls through the Keywords AI gateway for automatic logging and optimization features.

#### Simple Gateway Usage

```python
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from keywordsai_exporter_haystack import KeywordsAIGenerator

# Create pipeline with gateway
pipeline = Pipeline()
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", KeywordsAIGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))
pipeline.connect("prompt", "llm")

# Run pipeline
result = pipeline.run({"prompt": {"topic": "machine learning"}})
print(result["llm"]["replies"][0])
```

All requests are automatically logged to your Keywords AI dashboard at [platform.keywordsai.co/platform/dashboard](https://platform.keywordsai.co/platform/dashboard).

#### Combined Gateway + Tracing

For complete observability, combine both gateway and tracing:

```python
import os
from haystack import Pipeline
from keywordsai_exporter_haystack import KeywordsAIConnector, KeywordsAIGenerator

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

# Create pipeline with both gateway and tracing
pipeline = Pipeline()
pipeline.add_component("tracer", KeywordsAIConnector("Gateway + Tracing"))
pipeline.add_component("prompt", PromptBuilder(template="Tell me about {{topic}}."))
pipeline.add_component("llm", KeywordsAIGenerator(
    model="gpt-4o-mini",
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))
pipeline.connect("prompt", "llm")

# Run pipeline
result = pipeline.run({"prompt": {"topic": "deep learning"}})
print(result["llm"]["replies"][0])
print(f"\nTrace URL: {result['tracer']['trace_url']}")
```

### Prompt Management

Store and manage prompts on the Keywords AI platform, then reference them by ID:

```python
import os
from haystack import Pipeline
from keywordsai_exporter_haystack import KeywordsAIGenerator

# Create pipeline with platform-managed prompt
pipeline = Pipeline()
pipeline.add_component("llm", KeywordsAIGenerator(
    prompt_id="your-prompt-id",  # Get from Keywords AI platform
    api_key=os.getenv("KEYWORDSAI_API_KEY")
))

# Run with prompt variables
result = pipeline.run({
    "llm": {
        "prompt_variables": {
            "user_input": "The quick brown fox"
        }
    }
})

print(result["llm"]["replies"][0])
```

When using `prompt_id`, the model is configured on the Keywords AI platform, so you don't need to specify it in the code.

## License

`keywordsai-exporter-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
