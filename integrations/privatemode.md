---
# SPDX-License-Identifier: CC0-1.0
layout: integration
name: Privatemode
description: Use open-weight models from Privatemode in Haystack, end-to-end encrypted and based on confidential computing
authors:
    - name: Edgeless Systems
      socials:
        github: edgelesssys
        linkedin: https://www.linkedin.com/company/edgeless-systems
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/edgelesssys/privatemode-public
type: Model Provider
report_issue: https://github.com/edgelesssys/privatemode-public/issues
logo: /logos/privatemode.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)

## Overview

[Privatemode](https://www.privatemode.ai/) is an inference API for open-weight models with end-to-end encryption.
Privatemode processes prompts and responses only inside hardware-isolated Confidential Computing Environments.
By design, neither Edgeless Systems as the operator nor the infrastructure provider can access them.
Before any data leaves your environment, the client verifies the service through remote attestation.
Edgeless Systems, a company based in Germany, operates Privatemode on infrastructure in the EU.

The API is OpenAI-compatible, so Haystack's OpenAI components work with Privatemode for chat generation, embeddings, and agents with tool calling.
Privatemode serves chat models such as GLM, and the Qwen3 embedding model.
For the current lineup, see the [models page](https://docs.privatemode.ai/models/overview).

## Setup

The [Privatemode proxy](https://docs.privatemode.ai/api/proxy-configuration) runs next to your application.
It verifies the service through remote attestation, encrypts your prompts, and decrypts the responses.
Haystack talks to the proxy like it would to any OpenAI-compatible endpoint.

1. Create an API key in the [Privatemode portal](https://portal.privatemode.ai).
2. Start the proxy with your API key:

    ```bash
    docker run -p 127.0.0.1:8080:8080 ghcr.io/edgelesssys/privatemode/privatemode-proxy:latest --api-key <your-api-key>
    ```

3. Install Haystack:

    ```bash
    pip install haystack-ai
    ```

The proxy adds your API key to each request.
Haystack's OpenAI components still require an `api_key` value, so the examples pass a placeholder.

## Usage

The examples use [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) with `reasoning_effort` set to `high`.
See [Choose a model and reasoning effort](#choose-a-model-and-reasoning-effort) to change either.

### Chat generation with `OpenAIChatGenerator`

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_token("placeholder"),  # The proxy adds your API key.
    api_base_url="http://localhost:8080/v1",
    model="glm-flash-latest",
    generation_kwargs={"reasoning_effort": "high"},
)

messages = [ChatMessage.from_user("Explain confidential computing in one sentence.")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
```

### Retrieval-augmented generation with embeddings

Embedding documents and queries through Privatemode keeps the documents encrypted as well, not only the prompts.

```python
from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

PRIVATEMODE_URL = "http://localhost:8080/v1"
API_KEY = Secret.from_token("placeholder")  # The proxy adds your API key.

document_store = InMemoryDocumentStore()
document_embedder = OpenAIDocumentEmbedder(
    api_key=API_KEY, api_base_url=PRIVATEMODE_URL, model="qwen3-embedding-4b"
)
documents = [
    Document(content="Employees may work remotely for up to three days per week."),
    Document(content="Travel expenses must be submitted within 30 days."),
    Document(content="The office is closed on public holidays in Berlin."),
]
document_store.write_documents(document_embedder.run(documents)["documents"])
```

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def weather(city: str) -> str:
    """Return the weather for a city."""
    return f"The weather in {city} is sunny and 22 degrees"


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_token("placeholder"),  # The proxy adds your API key.
        api_base_url="http://localhost:8080/v1",
        model="glm-flash-latest",
        generation_kwargs={"reasoning_effort": "high"},
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Munich?")])
print(result["last_message"].text)
```

### Choose a model and reasoning effort

Set `model="glm-latest"` to use the larger GLM-5.3 model instead of GLM-5.3-Flash.

GLM models accept `none`, `low`, `high`, and `max` for `reasoning_effort` and default to `max`.
Lower values reduce latency, and `none` switches reasoning off.
See [reasoning](https://docs.privatemode.ai/models/overview#reasoning) for details.

### Evaluate without the proxy

To try Privatemode without running the proxy, use the [proxyless API](https://docs.privatemode.ai/api/proxyless-api).
Set `api_base_url="https://proxyless-api.privatemode.ai/v1"` and pass your API key with `Secret.from_env_var("PRIVATEMODE_API_KEY")`.

Use the proxy if you need cryptographically verifiable protection against access by Edgeless Systems.
