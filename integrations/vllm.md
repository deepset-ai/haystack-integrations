---
layout: integration
name: vLLM
description: Use the vLLM inference engine with Haystack
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
logo: /logos/vllm.png
version: Haystack 2.0
toc: true
---
Simply use [vLLM](https://github.com/vllm-project/vllm) in your haystack pipeline, to utilize fast, self-hosted LLMs. 

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
```bash
pip install haystack-ai vllm
```

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
