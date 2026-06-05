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
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
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
pip install haystack-ai "transformers[torch,sentencepiece]"
```

## Usage

### Components

Haystack provides several components that run Transformers models locally:
- [`HuggingFaceLocalChatGenerator`](https://docs.haystack.deepset.ai/docs/huggingfacelocalchatgenerator): chat generation with local LLMs.
- [`ExtractiveReader`](https://docs.haystack.deepset.ai/docs/extractivereader): extracts answers from documents using question answering models.
- [`TransformersTextRouter`](https://docs.haystack.deepset.ai/docs/transformerstextrouter) and [`TransformersZeroShotTextRouter`](https://docs.haystack.deepset.ai/docs/transformerszeroshottextrouter): route text to different pipeline branches based on classification.
- [`TransformersZeroShotDocumentClassifier`](https://docs.haystack.deepset.ai/docs/transformerszeroshotdocumentclassifier): classifies documents with zero-shot classification models.
- [`NamedEntityExtractor`](https://docs.haystack.deepset.ai/docs/namedentityextractor): annotates named entities in documents (with the `hugging_face` backend).

### Chat Generation

Use [`HuggingFaceLocalChatGenerator`](https://docs.haystack.deepset.ai/docs/huggingfacelocalchatgenerator) to run a chat model locally:

```python
from haystack.components.generators.chat import HuggingFaceLocalChatGenerator
from haystack.dataclasses import ChatMessage

generator = HuggingFaceLocalChatGenerator(model="Qwen/Qwen3-0.6B")

messages = [ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
print(generator.run(messages))
```

### Extractive Question Answering

Use [`ExtractiveReader`](https://docs.haystack.deepset.ai/docs/extractivereader) to extract answers from the relevant context:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.readers import ExtractiveReader

docs = [Document(content="Paris is the capital of France."),
        Document(content="Berlin is the capital of Germany."),
        Document(content="Rome is the capital of Italy."),
        Document(content="Madrid is the capital of Spain.")]
document_store = InMemoryDocumentStore()
document_store.write_documents(docs)

retriever = InMemoryBM25Retriever(document_store=document_store)
reader = ExtractiveReader(model="deepset/roberta-base-squad2-distilled")

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
from haystack.components.classifiers import TransformersZeroShotDocumentClassifier

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

Use [`NamedEntityExtractor`](https://docs.haystack.deepset.ai/docs/namedentityextractor) to annotate named entities in documents:

```python
from haystack import Document
from haystack.components.extractors.named_entity_extractor import NamedEntityExtractor

documents = [
    Document(content="I'm Merlin, the happy pig!"),
    Document(content="My name is Clara and I live in Berkeley, California."),
]
extractor = NamedEntityExtractor(backend="hugging_face", model="dslim/bert-base-NER")

results = extractor.run(documents=documents)["documents"]
annotations = [NamedEntityExtractor.get_stored_annotations(doc) for doc in results]
print(annotations)
```
