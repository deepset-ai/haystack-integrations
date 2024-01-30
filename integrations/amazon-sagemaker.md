---
layout: integration
name: Amazon Sagemaker
description: Use Models from Huggingface, Anthropic, AI21 Labs, Cohere, Meta, and Amazon via Amazon Sagemaker with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/amazon-sagemaker-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/amazon_sagemaker
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aws.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Haystack 2.x]
    - [Installation](#installation)
    - [Usage](#usage)
- [Haystack 1.x]
    - [Installation (1.x)](#installation-1x)
    - [Usage (1.x)](#usage-1x)

## Overview

[Amazon Sagemaker](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html) is a comprehensive, fully managed machine learning service 
that allows data scientists and developers to build, train, and deploy ML models efficiently. More information can be found on the 
[documentation page](#).

## Haystack 2.x

### Installation

Install the Amazon Sagemaker integration:
```bash
pip install amazon-sagemaker-haystack
```

### Usage

Once installed, you will have access to a [SagemakerGenerator](#) that supports models from various providers. To know more
about which models are supported, check out [Sagemaker's documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models.html).

To use this integration for text generation, initialize a `SagemakerGenerator` with the model name and aws credentials: 

```python
import os
haystack_integrations.components.generators.amazon_sagemaker import SagemakerGenerator

os.environ["AWS_ACCESS_KEY_ID"] = "..."
os.environ["AWS_SECRET_ACCESS_KEY"] = "..."
# This one is optional
os.environ["AWS_REGION_NAME"] = "..."

model = # Your Sagemaker endpoint name, such as "jumpstart-dft-hf-llm-falcon-7b-instruct-bf16"

generator = SagemakerGenerator(model=model)
result = generator.run("Who is the best American actor?")
for reply in result["replies"]:
    print(reply)
```
Output: 
```shell
'There is no definitive "best" American actor, as acting skill and talent are subjective.
However, some of the most acclaimed and influential American actors include Tom Hanks,
Daniel Day-Lewis, Denzel Washington, Meryl Streep, Rober# t De Niro, Al Pacino, Marlon Brando,
Jack Nicholson, Leonardo DiCaprio and John# ny Depp. Choosing a single "best" actor comes
down to personal preference.'
```

Note that different models may require different parameters. One notable example is the Llama2 family of models,
which should be initialized with `{'accept_eula': True}` as a custom attribute:

```python
generator = SagemakerGenerator(model="jumpstart-dft-meta-textgenerationneuron-llama-2-7b", aws_custom_attributes={"accept_eula": True})
```

## Haystack 1.x  

### Installation (1.x)

```bash
pip install farm-haystack
```

### Usage (1.x)

To use Sagemaker models in Haystack 1.x, initialize a `PromptNode` with the model name, AWS credentials and the prompt template. You can then use this `PromptNode` in a question answering pipeline to generate answers based on the given context.  

Below is the example of generative questions answering pipeline using RAG with an `EmbeddingRetriever` using Cohere models and a Sagemaker-powered `PromptNode`:

```python
from haystack.nodes import PromptNode, EmbeddingRetriever
from haystack.pipelines import Pipeline

retriever = EmbeddingRetriever(
    embedding_model="embed-english-v2.0", document_store=document_store, api_key=COHERE_API_KEY
)
prompt_node = PromptNode(model_name_or_path="sagemaker-model-endpoint-name", model_kwargs={"aws_profile_name": "my_aws_profile_name","aws_region_name": "your-aws-region"})

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
query_pipeline.run("YOUR_QUERY")
```
