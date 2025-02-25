---
layout: integration
name: vLLM Invocation Layer
description: Use the vLLM inference engine with Haystack
authors:
  - name: Lukas Kreussel
    socials:
      github: LLukas22
pypi: https://pypi.org/project/vllm-haystack/
repo: https://github.com/LLukas22/vLLM-haystack-adapter
type: Model Provider
report_issue: https://github.com/LLukas22/vLLM-haystack-adapter/issues
logo: /logos/vllm.png
version: Haystack 2.0
toc: true
---
[![PyPI - Version](https://img.shields.io/pypi/v/vllm-haystack.svg)](https://pypi.org/project/vllm-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vllm-haystack.svg)](https://pypi.org/project/vllm-haystack)

Simply use [vLLM](https://github.com/vllm-project/vllm) in your haystack pipeline, to utilize fast, self-hosted LLMs. 

<p align="center">
    <img alt="vLLM" src="https://raw.githubusercontent.com/vllm-project/vllm/main/docs/source/assets/logos/vllm-logo-text-light.png" width="45%" style="vertical-align: middle;">
    <a href="https://www.deepset.ai/haystack/">
        <img src="https://raw.githubusercontent.com/deepset-ai/haystack/main/docs/img/haystack_logo_colored.png" alt="Haystack" width="45%" style="vertical-align: middle;">
    </a>
</p>

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

[vLLM](https://github.com/vllm-project/vllm) is a high-throughput and memory-efficient inference and serving engine for LLMs.
It is an open-source project that allows serving open models in production, when you have GPU resources available.

vLLM can be deployed as a server that implements the OpenAI API protocol and integration with Haystack comes out-of-the-box.
This allows vLLM to be used with the [`OpenAIGenerator`](https://docs.haystack.deepset.ai/docs/openaigenerator) and [`OpenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/openaichatgenerator) components in Haystack.

For an end-to-end example of [vLLM + Haystack, see this notebook](https://colab.research.google.com/github/deepset-ai/haystack-cookbook/blob/main/notebooks/vllm_inference_engine.ipynb).


## Installation
vLLM should be installed.
- you can use `pip`: `pip install vllm` (more information in the [vLLM documentation](https://docs.vllm.ai/en/latest/getting_started/installation.html))
- for production use cases, there are many other options, including Docker ([docs](https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html))

## Usage
You first need to run an vLLM OpenAI-compatible server. You can do that using [Python](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-compatible-server) or [Docker](https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html). 

Then, you can use the `OpenAIGenerator` and `OpenAIChatGenerator` components in Haystack to query the vLLM server.

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_token("VLLM-PLACEHOLDER-API-KEY"),  # for compatibility with the OpenAI API, a placeholder api_key is needed
    model="mistralai/Mistral-7B-Instruct-v0.1",
    api_base_url="http://localhost:8000/v1",
    generation_kwargs = {"max_tokens": 512}
)

response = generator.run(messages=[ChatMessage.from_user("Hi. Can you help me plan my next trip to Italy?")])
```
