---
layout: integration
name: Hugging Face Transformers
description: Run Transformers models locally in your Haystack pipelines
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/transformers-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/transformers
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/transformers.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Transformers](https://huggingface.co/docs/transformers/index) is Hugging Face's library for state-of-the-art machine learning models. With this integration, you can run models from the [Hugging Face Hub](https://huggingface.co/models) **locally**, on your own machine, in your Haystack pipelines.

Haystack supports Hugging Face models in other ways too:
- [Sentence Transformers](https://haystack.deepset.ai/integrations/sentence-transformers) for local embedding and ranking models
- [Hugging Face API](https://haystack.deepset.ai/integrations/huggingface-api) to call models via Inference Providers, Inference Endpoints, or self-hosted TGI/TEI
- [Optimum](https://haystack.deepset.ai/integrations/optimum) for high-performance inference with ONNX Runtime

## Installation

```bash
pip install transformers-haystack
```

## Usage

### Components

This integration provides several components that run Transformers models locally:
- [`TransformersChatGenerator`](https://docs.haystack.deepset.ai/docs/transformerschatgenerator): chat generation with local LLMs.
- [`TransformersExtractiveReader`](https://docs.haystack.deepset.ai/docs/transformersextractivereader): extracts answers from documents using question answering models.
- [`TransformersTextRouter`](https://docs.haystack.deepset.ai/docs/transformerstextrouter) and [`TransformersZeroShotTextRouter`](https://docs.haystack.deepset.ai/docs/transformerszeroshottextrouter): route text to different pipeline branches based on classification.
- [`TransformersZeroShotDocumentClassifier`](https://docs.haystack.deepset.ai/docs/transformerszeroshotdocumentclassifier): classifies documents with zero-shot classification models.
- [`TransformersNamedEntityExtractor`](https://docs.haystack.deepset.ai/docs/transformersnamedentityextractor): annotates named entities in documents.

### Chat Generation

Use [`TransformersChatGenerator`](https://docs.haystack.deepset.ai/docs/transformerschatgenerator) to run a chat model locally:

```python
from haystack_integrations.components.generators.transformers import TransformersChatGenerator
from haystack.dataclasses import ChatMessage

generator = TransformersChatGenerator(model="Qwen/Qwen3-0.6B")

messages = [ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
print(generator.run(messages))
```

### Extractive Question Answering

Use [`TransformersExtractiveReader`](https://docs.haystack.deepset.ai/docs/transformersextractivereader) to extract answers from the relevant context:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack_integrations.components.readers.transformers import TransformersExtractiveReader

docs = [Document(content="Paris is the capital of France."),
        Document(content="Berlin is the capital of Germany."),
        Document(content="Rome is the capital of Italy."),
        Document(content="Madrid is the capital of Spain.")]
document_store = InMemoryDocumentStore()
document_store.write_documents(docs)

retriever = InMemoryBM25Retriever(document_store=document_store)
reader = TransformersExtractiveReader(model="deepset/roberta-base-squad2-distilled")

extractive_qa_pipeline = Pipeline()
extractive_qa_pipeline.add_component(instance=retriever, name="retriever")
extractive_qa_pipeline.add_component(instance=reader, name="reader")
extractive_qa_pipeline.connect("retriever.documents", "reader.documents")

query = "What is the capital of France?"
extractive_qa_pipeline.run(data={"retriever": {"query": query, "top_k": 3},
                                 "reader": {"query": query, "top_k": 2}})
```

### Zero-Shot Document Classification

Use [`TransformersZeroShotDocumentClassifier`](https://docs.haystack.deepset.ai/docs/transformerszeroshotdocumentclassifier) to classify documents with labels of your choice, without fine-tuning:

```python
from haystack import Document
from haystack_integrations.components.classifiers.transformers import TransformersZeroShotDocumentClassifier

documents = [Document(content="Today was a nice day!"),
             Document(content="Yesterday was a bad day!")]

classifier = TransformersZeroShotDocumentClassifier(
    model="cross-encoder/nli-deberta-v3-xsmall",
    labels=["positive", "negative"],
)

result = classifier.run(documents=documents)
print([doc.meta["classification"]["label"] for doc in result["documents"]])
# ['positive', 'negative']
```

### Named Entity Recognition

Use [`TransformersNamedEntityExtractor`](https://docs.haystack.deepset.ai/docs/transformersnamedentityextractor) to annotate named entities in documents:

```python
from haystack import Document
from haystack_integrations.components.extractors.transformers import TransformersNamedEntityExtractor

documents = [
    Document(content="I'm Merlin, the happy pig!"),
    Document(content="My name is Clara and I live in Berkeley, California."),
]
extractor = TransformersNamedEntityExtractor(model="dslim/bert-base-NER")

results = extractor.run(documents=documents)["documents"]
annotations = [TransformersNamedEntityExtractor.get_stored_annotations(doc) for doc in results]
print(annotations)
```
