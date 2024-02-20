---
layout: integration
name: Azure
description: Use OpenAI models deployed through Azure services with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/azure.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Haystack 2.0](#haystack-20)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Embedding Models](#embedding-models)
    - [Generative Models (LLMs)](#generative-models-llms)

## Overview

[Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview) provides REST API access to OpenAI's powerful language models including the GPT-4, GPT-4 Turbo with Vision, GPT-3.5-Turbo, and Embeddings model series. To get access to Azure OpenAI endpoints, visit [Azure OpenAI Service REST API reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference).

## Installation

Install Haystack 2.0:

```bash
pip install haystack-ai
```

## Usage

To work with Azure components, you will need an Azure OpenAI API key, an [Azure Active Directory Token](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id) as well as an Azure OpenAI Endpoint.

### Components

- [AzureOpenAIGenerator](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaigenerator)
- [AzureOpenAIChatGenerator](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaichatgenerator)
- [AzureOpenAITextEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaitextembedder)
- [AzureOpenAIDocumentEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaidocumentembedder)

All components use `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_AD_TOKEN` environment variables by default. Otherwise, you can pass `api_key` and `azure_ad_token` at initialization using `Secret` class. Read more about [Secret Handling](https://docs.haystack.deepset.ai/v2.0/docs/secret-management#structured-secret-handling).

### Embedding Models

You can leverage embedding models from Azure OpenAI through two components: [AzureOpenAITextEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaitextembedder) and [AzureOpenAIDocumentEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaidocumentembedder).

To create semantic embeddings for documents, use `AzureOpenAIDocumentEmbedder` in your indexing pipeline. For generating embeddings for queries, use `AzureOpenAITextEmbedder`. Once you've selected the suitable component for your specific use case, initialize the component with required parameters.

Below is the example indexing pipeline with `InMemoryDocumentStore`, `AzureOpenAIDocumentEmbedder` and  `DocumentWriter`:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import AzureOpenAITextEmbedder, AzureOpenAIDocumentEmbedder
from haystack.components.writers import DocumentWriter

os.environ["AZURE_OPENAI_API_KEY"] = "Your Azure OpenAI API key"
os.environ["AZURE_OPENAI_AD_TOKEN"] = "Your Azure Active Directory Token"

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", AzureOpenAIDocumentEmbedder(azure_endpoint="https://example-resource.azure.openai.com/", azure_deployment="text-embedding-ada-002"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

### Generative Models (LLMs)

You can leverage Azure OpenAI models through two components: [AzureOpenAIGenerator](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaigenerator) and [AzureOpenAIChatGenerator](https://docs.haystack.deepset.ai/v2.0/docs/azureopenaichatgenerator).

To use OpenAI models deployed through Azure services for text generation, initialize a `AzureOpenAIGenerator` with `azure_deployment` and `azure_endpoint`. You can then use the `AzureOpenAIGenerator` instance in a pipeline after the `PromptBuilder`.  

Below is the example of generative questions answering pipeline using RAG with `PromptBuilder` and  `AzureOpenAIGenerator`:

```python
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import AzureOpenAIGenerator

os.environ["AZURE_OPENAI_API_KEY"] = "Your Azure OpenAI API key"
os.environ["AZURE_OPENAI_AD_TOKEN"] = "Your Azure Active Directory Token"

template = """
Given the following information, answer the question.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: What's the official language of {{ country }}?
"""
pipe = Pipeline()

pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", AzureOpenAIGenerator(azure_endpoint="https://example-resource.azure.openai.com/", azure_deployment="gpt-35-turbo"))
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

pipe.run({
    "prompt_builder": {
        "country": "France"
    }
})   



