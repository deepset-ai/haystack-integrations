---
layout: integration
name: Soofi
description: Use Soofi S open foundation models with Haystack
authors:
    - name: Soofi
      socials:
        github: Soofi-Project
        linkedin: https://www.linkedin.com/company/ki-verband/
        
pypi: https://pypi.org/project/ollama-haystack/
repo: https://huggingface.co/Soofi-Project
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/soofi.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)

## Overview

**Soofi** ([Sovereign Open Source Foundation Models](https://www.soofi.info/)) is a German research consortium building open European foundation models for industrial AI. The first model family, **Soofi S**, is a ~30B-parameter hybrid Mamba-2 / Mixture-of-Experts model (about 3.5B active parameters) with a strong focus on English and German.

Preview checkpoints are on the [Soofi-Project Hugging Face organization](https://huggingface.co/Soofi-Project). Three models are available:

| Model | Role |
| --- | --- |
| [`Soofi-S-Instruct-Preview`](https://huggingface.co/Soofi-Project/Soofi-S-Instruct-Preview) | Instruct model |
| [`Soofi-S-Isar-Preview`](https://huggingface.co/Soofi-Project/Soofi-S-Isar-Preview) | Reasoning model |
| [`Soofi-S-Rhine-Preview`](https://huggingface.co/Soofi-Project/Soofi-S-Rhine-Preview) | Reasoning model |

Each model ships in several quantization variants:

| Quantization | Approx. size | Typical runtime |
| --- | --- | --- |
| FP16 | ~64 GB | Hugging Face Transformers / vLLM |
| FP8 | ~34 GB | vLLM |
| FP8@4bit | ~19 GB | vLLM (EntQuant) |
| FP8@3bit | ~16 GB | vLLM (EntQuant) |
| FP8@2bit | ~14 GB | vLLM (EntQuant) |
| GGUF Q8_0 | ~34 GB | Ollama / llama.cpp |
| GGUF Q5_K_M | ~26 GB | Ollama / llama.cpp |

> **Access:** Preview weights are gated (closed beta). Request access on the model card, then authenticate before downloading.

## Setup

Serve a Soofi checkpoint first, then connect Haystack to that server:

- **Ollama / llama.cpp (GGUF):** follow the instructions on the [`Soofi-S-Instruct-Preview-GGUF`](https://huggingface.co/Soofi-Project/Soofi-S-Instruct-Preview-GGUF) model card (and the matching Isar / Rhine GGUF cards). See also the [Ollama](/integrations/ollama) integration.
- **vLLM (FP8):** follow the serve commands on the [`Soofi-S-Instruct-Preview-FP8`](https://huggingface.co/Soofi-Project/Soofi-S-Instruct-Preview-FP8) model card (and the matching Isar / Rhine FP8 cards). See also the [vLLM](/integrations/vllm) integration.
- **vLLM (EntQuant):** follow the Docker / plugin setup on the [`Soofi-S-Instruct-Preview-EntQuant-2bit`](https://huggingface.co/Soofi-Project/Soofi-S-Instruct-Preview-EntQuant-2bit) model card (sibling 3-bit / 4-bit and reasoning variants work the same way).

Install the Haystack package for the runtime you use:

```bash
pip install ollama-haystack   # Ollama
pip install vllm-haystack     # vLLM
```

## Usage

Once a model is serving, use it as the chat generator for a Haystack [`Agent`](https://docs.haystack.deepset.ai/docs/agent).

### Agent with Ollama

Soofi S is strong in German as well as English. This example runs the agent entirely in German:

```python
from typing import Annotated

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack_integrations.components.generators.ollama import OllamaChatGenerator


@tool
def price_lookup(product: Annotated[str, "Produktname für die Preissuche"]) -> str:
    """Sucht einen Beispielpreis für ein Produkt."""
    mock_prices = {"laptop": "999 €", "tastatur": "99 €", "monitor": "349 €"}
    return mock_prices.get(product.lower(), "Unbekanntes Produkt")


agent = Agent(
    chat_generator=OllamaChatGenerator(
        model="huggingface.co/Soofi-Project/Soofi-S-Instruct-Preview-GGUF:Q5_K_M",
        url="http://localhost:11434",
        generation_kwargs={"temperature": 0.6, "top_p": 0.95, "num_ctx": 8192},
    ),
    tools=[price_lookup],
    system_prompt="Du hilfst Nutzern und rufst die bereitgestellten Tools auf, wenn sie relevant sind.",
)

result = agent.run(messages=[ChatMessage.from_user("Was kostet ein Laptop?")])
print(result["last_message"].text)
```

Adjust `model` to match `ollama list` (or a local Modelfile tag).

### Agent with vLLM

```python
from typing import Annotated

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack_integrations.components.generators.vllm import VLLMChatGenerator


@tool
def price_lookup(product: Annotated[str, "Product name to look up"]) -> str:
    """Look up a mock product price."""
    mock_prices = {"laptop": "$999", "keyboard": "$99", "monitor": "$349"}
    return mock_prices.get(product.lower(), "Unknown product")


agent = Agent(
    chat_generator=VLLMChatGenerator(
        # Use the served model name, e.g. Soofi-S-Instruct-Preview-EntQuant-2bit for EntQuant
        model="Soofi-Project/Soofi-S-Instruct-Preview-FP8",
        api_base_url="http://localhost:8000/v1",
        generation_kwargs={"temperature": 0.6, "top_p": 0.95},
    ),
    tools=[price_lookup],
    system_prompt="You help users by calling the provided tools when they are relevant.",
)

result = agent.run(messages=[ChatMessage.from_user("How much is a laptop?")])
print(result["last_message"].text)
```

For llama.cpp with an OpenAI-compatible server, use Haystack’s [`OpenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/openaichatgenerator) against that endpoint the same way — see the GGUF model card for `llama-server` flags such as `--jinja`.
