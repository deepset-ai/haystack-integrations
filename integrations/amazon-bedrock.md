---
layout: integration
name: Amazon Bedrock
description: Use Models from AI21 Labs, Anthropic, Cohere, Meta, and Amazon via Amazon Bedrock with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/amazon-bedrock-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/amazon_bedrock
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aws.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[Amazon Bedrock](https://aws.amazon.com/bedrock/) is a fully managed service that makes high-performing foundation models from leading AI startups and Amazon available for your use through a unified API. You can choose from various foundation models to find the one best suited for your use case. More information can be found on the [Amazon Bedrock documentation page](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html).

## Installation

Install the Amazon Bedrock integration:
```bash
pip install amazon-bedrock-haystack
```

## Usage

Once installed, you will have access to [AmazonBedrockGenerator](https://docs.haystack.deepset.ai/docs/amazonbedrockgenerator) and [AmazonBedrockChatGenerator](https://docs.haystack.deepset.ai/docs/amazonbedrockchatgenerator) components that support generative language models on Amazon Bedrock.
You will also have access to the [AmazonBedrockTextEmbedder](https://docs.haystack.deepset.ai/docs/amazonbedrocktextembedder) and [AmazonBedrockDocumentEmbedder](https://docs.haystack.deepset.ai/docs/amazonbedrockdocumentembedder), which can be used to compute embeddings.

### AmazonBedrockGenerator

To use this integration for text generation, initialize an `AmazonBedrockGenerator` with the model name, the AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`) should be set as environment variables or passed as [Secret](https://docs.haystack.deepset.ai/docs/secret-management) arguments. 
Note, make sure the region you set supports Amazon Bedrock. 

Currently, the following models are supported: 

- AI21 Labs' Jurassic-2
- Amazon Titan language models
- Anthropic's Claude
- Cohere's Command
- Meta's Llama 2

```python
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockGenerator

generator = AmazonBedrockGenerator(model="anthropic.claude-v2")
result = generator.run("Who is the best American actor?")
for reply in result["replies"]:
    print(reply)
```
Output: 
```shell
'There is no definitive "best" American actor, as acting skill and talent a# re subjective. However, some of the most acclaimed and influential American act# ors include Tom Hanks, Daniel Day-Lewis, Denzel Washington, Meryl Streep, Rober# t De Niro, Al Pacino, Marlon Brando, Jack Nicholson, Leonardo DiCaprio and John# ny Depp. Choosing a single "best" actor comes down to personal preference.'
```

### AmazonBedrockChatGenerator

To use this integration for chat models, initialize an `AmazonBedrockChatGenerator` with the model name and AWS credentials:

Currently, the following models are supported: 
- Anthropic's Claude 2, Claude 3 Sonnet
- Meta's Llama 2

```python
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator
from haystack.dataclasses import ChatMessage
    
generator = AmazonBedrockChatGenerator(model="meta.llama2-70b-chat-v1")
messages = [ChatMessage.from_system("You are a helpful assistant that answers question in Spanish only"), 
            ChatMessage.from_user("What's Natural Language Processing? Be brief.")]
    
response = generator.run(messages)
print(response)

```
Output: 
```shell
{'replies': [ChatMessage(content='  Procesamiento del Lenguaje Natural (PLN) es una rama de la inteligencia artificial que se enfoca en el desarrollo de algoritmos y modelos que permiten a las computadoras comprender y procesar el lenguaje natural, como el hablado o escrito por los humanos.', role=<ChatRole.ASSISTANT: 'assistant'>, name=None, meta={'stop_reason': 'stop', 'usage': {'prompt_tokens': 44, 'completion_tokens': 71}})]}
```

### AmazonBedrockTextEmbedder and AmazonBedrockDocumentEmbedder

These two components can be used to compute embeddings for text and Documents respectively. 
Supported models are "amazon.titan-embed-text-v1", "cohere.embed-english-v3" and "cohere.embed-multilingual-v3".

See them in action:

```python
from haystack import Pipeline
from haystack.dataclasses import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.amazon_bedrock import (
    AmazonBedrockDocumentEmbedder,
    AmazonBedrockTextEmbedder,
)
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder", AmazonBedrockDocumentEmbedder(model="cohere.embed-english-v3"))
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})


query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", AmazonBedrockTextEmbedder(model="cohere.embed-english-v3"))
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

query = "Who lives in Berlin?"

result = query_pipeline.run({"text_embedder":{"text": query}})

print(result['retriever']['documents'][0])

# Document(id=..., content: 'My name is Wolfgang and I live in Berlin')
