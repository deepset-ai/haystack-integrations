---
layout: integration
name: Kolibri
description: Use Aleph Alpha Kolibri open-weight German–English models with Haystack for generation, reasoning, and agents
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/vllm-haystack/
repo: https://huggingface.co/Aleph-Alpha/Kolibri-1
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/kolibri.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
  - [Generative chat (German)](#generative-chat-german)
  - [Reasoning mode](#reasoning-mode)
  - [Agentic tool calling](#agentic-tool-calling)

## Overview

**[Kolibri](https://aleph-alpha.com/en/kolibri/)** is Aleph Alpha’s open-weight model for German and English. Serve it with vLLM, then use it in Haystack for chat, reasoning, and agents.

Key capabilities:

<div class="styled-table">

| Capability | Details |
| --- | --- |
| **Generative** | Chat completion for drafting, Q&A, coding, and long-document work |
| **German & English** | Native bilingual model; German is a first-class language (≈24% of pre-training mix) |
| **Reasoning** | Controllable thinking via `reasoning_effort` (`none` / `low` / `medium` / `high`) |
| **Agentic** | Hermes-style tool calling with vLLM’s `kolibri1` parser |
| **Long context** | Native 262,144 tokens; validated up to 1,048,576 (recommend ≤256k for complex tasks) |

</div>

## Setup

Kolibri needs Aleph Alpha’s vLLM plugin (`aleph-alpha-inference`). Stock vLLM alone cannot load `Kolibri1ForCausalLM` or the `kolibri1` parsers.

**Option A — pip (pins a supported vLLM, currently 0.29):**

```bash
pip install 'aleph-alpha-inference>=1'
```

**Option B — container:**

```bash
docker pull ghcr.io/aleph-alpha/aleph-alpha-inference
```

Serve with reasoning and tool calling enabled:

```bash
vllm serve Aleph-Alpha/Kolibri-1 \
  --kv-cache-dtype fp8 \
  --reasoning-parser kolibri1 \
  --tool-call-parser kolibri1 \
  --enable-auto-tool-choice
```

For BF16 weights, serve `Aleph-Alpha/Kolibri-1-BF16` and omit `--kv-cache-dtype fp8`. For contexts beyond 262,144 tokens, add `--max-model-len 1048576 --hf-overrides '{"max_position_embeddings": 1048576}'`.

Recommended sampling defaults from the model card: `temperature=1.0`, `top_p=0.97`, `top_k=128`.

Install the Haystack client for the OpenAI-compatible vLLM server:

```bash
pip install vllm-haystack
```

See also the [vLLM](/integrations/vllm) integration.

## Usage

Once Kolibri is serving (default `http://localhost:8000/v1`), use [`VLLMChatGenerator`](https://docs.haystack.deepset.ai/docs/vllmchatgenerator) for generation, reasoning, and Haystack [`Agent`](https://docs.haystack.deepset.ai/docs/agent) agent loops.

### Generative chat (German)

Kolibri is specialized for German. This example asks for a short explanation entirely in German:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.vllm import VLLMChatGenerator

chat = VLLMChatGenerator(
    model="Aleph-Alpha/Kolibri-1",
    api_base_url="http://localhost:8000/v1",
    generation_kwargs={
        "temperature": 1.0,
        "top_p": 0.97,
        "extra_body": {
            "top_k": 128,
            "chat_template_kwargs": {
                "enable_thinking": False,
                "reasoning_effort": "none",
            },
        },
    },
)

result = chat.run(
    messages=[
        ChatMessage.from_user(
            "Erkläre kurz, was ein Mixture-of-Experts-Modell ist und warum es für deutsche Verwaltungstexte hilfreich sein kann."
        )
    ]
)
print(result["replies"][0].text)
```

### Reasoning mode

Thinking is on by default when the server is started with `--reasoning-parser kolibri1`. Control effort per request with `chat_template_kwargs`. When thinking is enabled, Haystack exposes the reasoning trace on the reply’s `.reasoning` field:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.vllm import VLLMChatGenerator

chat = VLLMChatGenerator(
    model="Aleph-Alpha/Kolibri-1",
    api_base_url="http://localhost:8000/v1",
    generation_kwargs={
        "temperature": 1.0,
        "top_p": 0.97,
        "extra_body": {
            "top_k": 128,
            "chat_template_kwargs": {
                "enable_thinking": True,
                "reasoning_effort": "high",  # none | low | medium | high
            },
        },
    },
)

result = chat.run(
    messages=[
        ChatMessage.from_user(
            "Ein Amt hat 3 Anträge: A braucht 2 Tage, B 5 Tage, C 1 Tag. "
            "In welcher Reihenfolge minimiert man die mittlere Wartezeit? Begründe."
        )
    ]
)
reply = result["replies"][0]
print(reply.reasoning)  # thinking trace (when enabled)
print(reply.text)       # final answer
```

Set `reasoning_effort` to `"none"` or `enable_thinking` to `False` for a direct reply without a thinking block.

### Agentic tool calling

Serve with `--tool-call-parser kolibri1 --enable-auto-tool-choice`, then plug Kolibri into a Haystack `Agent`. Tool calling can be combined with reasoning. This agent looks up a mock product price in German:

```python
from typing import Annotated

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack_integrations.components.generators.vllm import VLLMChatGenerator


@tool
def preis_abrufen(produkt: Annotated[str, "Produktname für die Preissuche"]) -> str:
    """Sucht einen Beispielpreis für ein Produkt."""
    preise = {"laptop": "999 €", "tastatur": "99 €", "monitor": "349 €"}
    return preise.get(produkt.lower(), "Unbekanntes Produkt")


agent = Agent(
    chat_generator=VLLMChatGenerator(
        model="Aleph-Alpha/Kolibri-1",
        api_base_url="http://localhost:8000/v1",
        generation_kwargs={
            "temperature": 1.0,
            "top_p": 0.97,
            "extra_body": {
                "top_k": 128,
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "reasoning_effort": "medium",
                },
            },
        },
    ),
    tools=[preis_abrufen],
    system_prompt=(
        "Du hilfst Nutzern auf Deutsch und rufst die bereitgestellten Tools auf, wenn sie relevant sind. Antworte klar und knapp."
    ),
)

result = agent.run(messages=[ChatMessage.from_user("Was kostet ein Laptop?")])
print(result["last_message"].text)
```

For English-only assistants, the same pattern works — keep tools and prompts in English. For RAG pipelines, use Kolibri as the generator after retrieval the same way you would any other chat model behind vLLM.
