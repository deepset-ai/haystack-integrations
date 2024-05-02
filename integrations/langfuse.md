---
layout: integration
name: langfuse
description: langfuse-haystack integrates tracing capabilities into [Haystack](https://github.com/deepset-ai/haystack) (2.x) pipelines using [Langfuse](https://langfuse.com/). This package enhances the visibility of pipeline runs by capturing comprehensive details of the execution traces, including API calls, context data, prompts, and more. Whether you're monitoring model performance, pinpointing areas for improvement, or creating datasets for fine-tuning and testing from your pipeline executions, langfuse-haystack is the right tool for you.

authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/langfuse-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/langfuse
type: Evaluation Framework
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/your-logo.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
### Features

- Easy integration with Haystack pipelines
- Capture the full context of the execution
- Track model usage and cost
- Collect user feedback
- Identify low-quality outputs
- Build fine-tuning and testing datasets

In order to use this integration, [sign up for a Langfuse account](https://langfuse.com/). See [the Langfuse docs](https://langfuse.com/docs) for the most up-to-date information about features and pricing. 

## Installation

```bash
pip install langfuse-haystack
```

## Usage
### Components
This integration introduces one component:

- The `LangfuseConnector`: 
  
    `LangfuseConnector`` connects Haystack LLM framework with Langfuse in order to enable the tracing of operations
    and data flow within various components of a pipeline.
    Simply this component to your pipeline, but *do not* connect it to any other component. The `LangfuseConnector`
    will automatically trace the operations and data flow within the pipeline.

    Note that you need to set the `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY` environment variables in order
    to use this component. The `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY` are the secret and public keys provided
    by Langfuse. You can get these keys by signing up for an account [on the Langfuse website](https://langfuse.com/).
    In addition, you need to set the `HAYSTACK_CONTENT_TRACING_ENABLED` environment variable to `true` in order to
    enable Haystack tracing in your pipeline.

### Using `LangfuseConnector` in a RAG pipeline:
```python
from datasets import load_dataset
from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.connectors.langfuse import LangfuseConnector


def get_pipeline(document_store: InMemoryDocumentStore):
    retriever = InMemoryEmbeddingRetriever(document_store=document_store, top_k=2)

    template = """
    Given the following information, answer the question.
    Context:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}
    Question: {{question}}
    Answer:
    """

    prompt_builder = PromptBuilder(template=template)

    basic_rag_pipeline = Pipeline()
    # Add components to your pipeline
    basic_rag_pipeline.add_component("tracer", LangfuseConnector("Basic RAG Pipeline"))
    basic_rag_pipeline.add_component(
        "text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
    )
    basic_rag_pipeline.add_component("retriever", retriever)
    basic_rag_pipeline.add_component("prompt_builder", prompt_builder)
    basic_rag_pipeline.add_component("llm", OpenAIGenerator(model="gpt-3.5-turbo", generation_kwargs={"n": 2}))

    # Now, connect the components to each other
    # NOTE: the tracer component doesn't need to be connected to anything in order to work
    basic_rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    basic_rag_pipeline.connect("retriever", "prompt_builder.documents")
    basic_rag_pipeline.connect("prompt_builder", "llm")

    return basic_rag_pipeline

document_store = InMemoryDocumentStore()
dataset = load_dataset("bilgeyucel/seven-wonders", split="train")
embedder = SentenceTransformersDocumentEmbedder("sentence-transformers/all-MiniLM-L6-v2")
embedder.warm_up()
docs_with_embeddings = embedder.run([Document(**ds) for ds in dataset]).get("documents") or []  # type: ignore
document_store.write_documents(docs_with_embeddings)

pipeline = get_pipeline(document_store)
question = "What does Rhodes Statue look like?"
response = pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
# {'tracer': {'name': 'Basic RAG Pipeline', 'trace_url': 'https://cloud.langfuse.com/trace/3d52b8cc-87b6-4977-8927-5e9f3ff5b1cb'}, 'llm': {'replies': ['The Rhodes Statue was described as being about 105 feet tall, with iron tie bars and brass plates forming the skin. It was built on a white marble pedestal near the Rhodes harbour entrance. The statue was filled with stone blocks as construction progressed.', 'The Rhodes Statue was described as being about 32 meters (105 feet) tall, built with iron tie bars, brass plates for skin, and filled with stone blocks. It stood on a 15-meter-high white marble pedestal near the Rhodes harbor entrance.'], 'meta': [{'model': 'gpt-3.5-turbo-0125', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 100, 'prompt_tokens': 453, 'total_tokens': 553}}, {'model': 'gpt-3.5-turbo-0125', 'index': 1, 'finish_reason': 'stop', 'usage': {'completion_tokens': 100, 'prompt_tokens': 453, 'total_tokens': 553}}]}}
```

### License

Info about your integration license
