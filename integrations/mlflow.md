---
layout: integration
name: MLflow
description: Trace, evaluate, and monitor your Haystack applications with MLflow.
authors:
    - name: MLflow
      socials:
        github: mlflow
        twitter: MLflow
        linkedin: https://www.linkedin.com/company/mlflow-org/
pypi: https://pypi.org/project/mlflow/
repo: https://github.com/mlflow/mlflow
type: Monitoring Tool
report_issue: https://github.com/mlflow/mlflow/issues
logo: /logos/mlflow.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[MLflow](https://mlflow.org/) is an [open-source](https://github.com/mlflow/mlflow) platform for managing the end-to-end machine learning and AI lifecycle. MLflow provides native tracing support for Haystack through its autolog integration, giving you full visibility into your Haystack pipeline execution.

MLflow Tracing offers:

- Hierarchical trace visualization of every component, LLM call, retriever step, and pipeline execution
- Automatic token usage and cost tracking for each LLM call
- Built-in evaluation framework with LLM judges and custom scorers
- Prompt versioning and management across your AI applications
- Fully open-source with no vendor lock-in, self-host or use [Managed MLflow](https://mlflow.org/docs/latest/genai/getting-started/databricks-trial/) in the cloud

You can learn more about the integration in MLflow's [Haystack integration guide](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/haystack.html).

## Installation

```bash
pip install mlflow haystack-ai
```

To start the MLflow tracking server:

```bash
mlflow server --port 5000
```

The MLflow UI will be available at `http://localhost:5000`.

## Usage

Enable tracing for Haystack with a single line of code. This automatically captures traces from all Haystack pipelines and components.

### Trace a RAG Pipeline

```python
import mlflow

from haystack import Document, Pipeline
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

# Enable MLflow tracing for Haystack
mlflow.haystack.autolog()
mlflow.set_experiment("Haystack")

# Write documents to InMemoryDocumentStore
document_store = InMemoryDocumentStore()
document_store.write_documents(
    [
        Document(content="My name is Jean and I live in Paris."),
        Document(content="My name is Mark and I live in Berlin."),
        Document(content="My name is Giorgio and I live in Rome."),
    ]
)

# Build a RAG pipeline
prompt_template = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user(
        "Given these documents, answer the question.\n"
        "Documents:\n{% for doc in documents %}{{ doc.content }}{% endfor %}\n"
        "Question: {{question}}\n"
        "Answer:"
    ),
]

prompt_builder = ChatPromptBuilder(
    template=prompt_template, required_variables={"question", "documents"}
)

retriever = InMemoryBM25Retriever(document_store=document_store)
llm = OpenAIChatGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"))

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm.messages")

# Ask a question
question = "Who lives in Paris?"
results = rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)

print(results["llm"]["replies"])
```

Open the MLflow UI at `http://localhost:5000` and navigate to the **Traces** tab to see detailed traces of your pipeline execution, including component spans, LLM calls, and token usage.

### Disable Tracing

Auto-tracing for Haystack can be disabled by calling:

```python
mlflow.haystack.autolog(disable=True)
```

## License

MLflow is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
