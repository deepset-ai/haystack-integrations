---
layout: integration
name: vLLM Invocation Layer
description: Use a vLLM server or locally hosted instance in your Prompt Node
authors:
  - name: Lukas Kreussel
    socials:
      github: LLukas22
pypi: https://pypi.org/project/vllm-haystack/
repo: https://github.com/LLukas22/vLLM-haystack-adapter
type: Custom Node
report_issue: https://github.com/LLukas22/vLLM-haystack-adapter/issues
logo: /logos/vllm.png
---

# vLLM Invocation Layer
[![PyPI - Version](https://img.shields.io/pypi/v/vllm-haystack.svg)](https://pypi.org/project/vllm-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vllm-haystack.svg)](https://pypi.org/project/vllm-haystack)

Simply use [vLLM](https://github.com/vllm-project/vllm) in your haystack pipeline, to utilize fast, self-hosted LLMs. 

<p align="center">
    <img alt="vLLM" src="https://raw.githubusercontent.com/vllm-project/vllm/main/docs/source/assets/logos/vllm-logo-text-light.png" width="45%" style="vertical-align: middle;">
    <a href="https://www.deepset.ai/haystack/">
        <img src="https://raw.githubusercontent.com/deepset-ai/haystack/main/docs/img/haystack_logo_colored.png" alt="Haystack" width="45%" style="vertical-align: middle;">
    </a>
</p>

## Installation
Install the wrapper via pip:  `pip install vllm-haystack`

## Usage
To utilize the wrapper the `vLLMInvocationLayer` has to be used. 

Here is a simple example of how a `PromptNode` can be created with the wrapper.

```python
from haystack.nodes import PromptNode, PromptModel
from vllm_haystack import vLLMInvocationLayer


model = PromptModel(model_name_or_path="", invocation_layer_class=vLLMInvocationLayer, max_length=256, api_key="EMPTY", model_kwargs={
        "api_base" : API, # Replace this with your API-URL
        "maximum_context_length": 2048,
    })

prompt_node = PromptNode(model_name_or_path=model, top_k=1, max_length=256)
```
For more configuration examples, take a look at the unit-tests.

## Hosting a vLLM Server

To create an *OpenAI-Compatible Server* via vLLM you can follow the steps in the 
Quickstart section of their [documentation](https://vllm.readthedocs.io/en/latest/getting_started/quickstart.html#openai-compatible-server).

##  Running Locally

If you don't want to use an API-Server this wrapper also provides a `vLLMLocalInvocationLayer` which executes the vLLM on the same node Haystack is running on. 

Here is a simple example of how a `PromptNode` can be created with the `vLLMLocalInvocationLayer`.
```python
from haystack.nodes import PromptNode, PromptModel
from vllm_haystack import vLLMLocalInvocationLayer

model = PromptModel(model_name_or_path=MODEL, invocation_layer_class=vLLMLocalInvocationLayer, max_length=256, model_kwargs={
        "maximum_context_length": 2048,
    })

prompt_node = PromptNode(model_name_or_path=model, top_k=1, max_length=256)
```
⚠️To run `vLLM` locally you need to have `vLLM` installed and a supported GPU.