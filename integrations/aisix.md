---
layout: integration
name: AISIX AI Gateway
description: Route Haystack model calls through the open-source AISIX AI Gateway using OpenAI-compatible endpoints.
authors:
    - name: Yilia Lin
      socials:
        github: Yilialinn
repo: https://github.com/api7/aisix
type: AI Gateway
report_issue: https://github.com/api7/aisix/issues
version: Haystack 3.1
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Configure AISIX](#configure-aisix)
- [Use AISIX in a RAG Pipeline](#use-aisix-in-a-rag-pipeline)
- [Retry Ownership](#retry-ownership)
- [License](#license)

## Overview

[AISIX AI Gateway](https://github.com/api7/aisix) is an Apache-2.0-licensed open-source AI gateway maintained by API7.ai. It is an independent project and is not an Apache Software Foundation project.

AISIX exposes OpenAI-compatible endpoints, so Haystack applications can use the built-in [`OpenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/openaichatgenerator) without installing an AISIX-specific component. The Haystack application authenticates with a gateway caller key and selects a caller-facing model alias. AISIX keeps the upstream provider credential and resolves that alias to a direct model or routing group.

The examples below were validated with Haystack 3.1.1 and AISIX 1.2.0.

## Installation

Install Haystack:

```bash
pip install haystack-ai==3.1.1
```

Deploy AISIX by following the [open-source AISIX gateway quickstart](https://docs.api7.ai/ai-gateway/getting-started/gateway-quickstart), using the `ghcr.io/api7/aisix:1.2.0` image tag to reproduce this example. No additional Haystack integration package is required.

## Configure AISIX

The following AISIX resources define two direct upstream models and expose them to Haystack as one `rag-model` [failover alias](https://docs.api7.ai/ai-gateway/routing/routing-and-failover). Replace the provider endpoint and model identifiers with values available in your environment.

```yaml
_format_version: "1"

provider_keys:
  - display_name: haystack-provider
    provider: openai
    adapter: openai
    api_key: ${UPSTREAM_API_KEY}
    api_base: ${UPSTREAM_API_BASE}

models:
  - display_name: rag-primary
    provider: openai
    model_name: ${UPSTREAM_PRIMARY_MODEL}
    provider_key: haystack-provider
  - display_name: rag-backup
    provider: openai
    model_name: ${UPSTREAM_BACKUP_MODEL}
    provider_key: haystack-provider
  - display_name: rag-model
    routing:
      strategy: failover
      retries: 0
      max_fallbacks: 1
      targets:
        - model: rag-primary
        - model: rag-backup

api_keys:
  - display_name: haystack-caller
    key_env: HAYSTACK_CALLER_KEY
    allowed_models:
      - rag-model
```

Set the referenced environment variables in the AISIX process and validate the resources before starting or reloading the gateway:

```bash
aisix validate --resources /etc/aisix/resources.yaml
```

The Haystack process needs only the gateway URL and caller key:

```bash
export AISIX_BASE_URL="http://localhost:3000"
export HAYSTACK_CALLER_KEY="replace-with-a-gateway-caller-key"
```

Do not expose `UPSTREAM_API_KEY` to the Haystack application.

## Use AISIX in a RAG Pipeline

This example uses in-memory BM25 retrieval so that the only external request is the generation call through AISIX.

```python
import os

from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

document_store = InMemoryDocumentStore()
document_store.write_documents(
    [
        Document(
            content=(
                "If the checkout service returns HTTP 503, fail over to the "
                "secondary region and page the on-call engineer."
            )
        ),
        Document(
            content=(
                "If checkout latency exceeds two seconds, inspect the payment "
                "provider dashboard before scaling the application."
            )
        ),
    ]
)

template = [
    ChatMessage.from_system(
        "Answer only from the supplied runbook documents."
    ),
    ChatMessage.from_user(
        "Runbook documents:\n"
        "{% for document in documents %}"
        "- {{ document.content }}\n"
        "{% endfor %}"
        "Question: {{ question }}"
    ),
]

pipeline = Pipeline()
pipeline.add_component(
    "retriever",
    InMemoryBM25Retriever(document_store=document_store, top_k=1),
)
pipeline.add_component(
    "prompt_builder",
    ChatPromptBuilder(
        template=template,
        required_variables={"documents", "question"},
    ),
)
pipeline.add_component(
    "llm",
    OpenAIChatGenerator(
        api_key=Secret.from_env_var("HAYSTACK_CALLER_KEY"),
        model="rag-model",
        api_base_url=f"{os.environ['AISIX_BASE_URL'].rstrip('/')}/v1",
        max_retries=0,
        generation_kwargs={"temperature": 0},
    ),
)

pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "What should we do when checkout returns HTTP 503?"
result = pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)

print(result["llm"]["replies"][0].text)
```

A response grounded in the retrieved runbook should instruct the operator to fail over to the secondary region and page the on-call engineer.

## Retry Ownership

The example sets `max_retries=0` on `OpenAIChatGenerator` because the displayed AISIX routing model owns failover. This makes one Haystack generation call correspond to one gateway request while AISIX tries the configured targets within that request.

You can keep client-side retries for a different failure policy, but size the Haystack/OpenAI client retry budget and the AISIX retry/failover budget together. Otherwise, one application-level call can create more upstream attempts than expected.

## License

AISIX is distributed under the [Apache License 2.0](https://github.com/api7/aisix/blob/main/LICENSE).
