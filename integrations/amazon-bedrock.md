---
layout: integration
name: Amazon Bedrock
description: Use Models from AI21 Labs, Anthropic, Cohere, Meta, and Amazon via Amazon Bedrock with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
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
    - [AmazonBedrockGenerator](#amazonbedrockgenerator)
    - [AmazonBedrockChatGenerator](#amazonbedrockchatgenerator)

## Overview

[Amazon Bedrock](https://aws.amazon.com/bedrock/) is a fully managed service that makes high-performing foundation models from leading AI startups and Amazon available for your use through a unified API. You can choose from various foundation models to find the one best suited for your use case. More information can be found on the [Amazon Bedrock documentation page](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html).

## Installation

Install the Amazon Bedrock integration:
```bash
pip install amazon-bedrock-haystack
```

## Usage

Once installed, you will have access to [AmazonBedrockGenerator](https://docs.haystack.deepset.ai/v2.0/docs/amazonbedrockgenerator) and [AmazonBedrockChatGenerator](https://docs.haystack.deepset.ai/v2.0/docs/amazonbedrockchatgenerator) components that support foundation models on Amazon Bedrock. 

### AmazonBedrockGenerator

To use this integration for text generation, initialize an `AmazonBedrockGenerator` with the model name and aws credentials: 

Currently, the following models are supported: 
- Anthropic's Claude
- AI21 Labs' Jurassic-2
- Cohere's Command
- Meta's Llama 2
- Amazon Titan language models

```python
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockGenerator

aws_access_key_id="..."
aws_secret_access_key="..."
aws_region_name="eu-central-1"

generator = AmazonBedrockGenerator(model="anthropic.claude-v2", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_region_name=aws_region_name)
result = generator.run("Who is the best American actor?")
for reply in result["replies"]:
    print(reply)
```
Output: 
```shell
'There is no definitive "best" American actor, as acting skill and talent a# re subjective. However, some of the most acclaimed and influential American act# ors include Tom Hanks, Daniel Day-Lewis, Denzel Washington, Meryl Streep, Rober# t De Niro, Al Pacino, Marlon Brando, Jack Nicholson, Leonardo DiCaprio and John# ny Depp. Choosing a single "best" actor comes down to personal preference.'
```

### AmazonBedrockChatGenerator

To use this integration for chat models, initialize an `AmazonBedrockChatGenerator` with the model name and aws credentials:

Currently, the following models are supported: 
- Anthropic's Claude
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
{'replies': [ChatMessage(content='  Procesamiento del Lenguaje Natural (PLN) es una rama de la inteligencia artificial que se enfoca en el desarrollo de algoritmos y modelos computacionales para analizar, comprender y generar texto y lenguaje humano.', role=<ChatRole.ASSISTANT: 'assistant'>, name=None, meta={'prompt_token_count': 46, 'generation_token_count': 60, 'stop_reason': 'stop'})]}
```



