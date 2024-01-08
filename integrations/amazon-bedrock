---
layout: integration
name: Amazon Bedrock
description: Use Models from AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via Amazon Bedrock with Haystack
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
    - [AmazonBedrockGenerator](#AmazonBedrockGenerator)

## Overview

[Amazon Bedrock](https://aws.amazon.com/bedrock/) is a fully managed service that makes high-performing foundation models from leading AI startups and Amazon available for your use through a unified API. 
You can choose from various foundation models to find the one best suited for your use case.

## Installation

Install the Amazon Bedrock integration:
```bash
pip install amazon-bedrock-haystack
```

## Usage

Once installed, you will have access to an AmazonBedrockGenerator that supports models from various providers: 
- Anthropic's Claude
- AI21 Labs' Jurassic-2
- Stability AI's Stable Diffusion
- Cohere's Command and Embed
- Meta's Llama 2
- Amazon Titan language and embeddings models

### AmazonBedrockGenerator

To use this integration for text generation, initialize a `AmazonBedrockGenerator` with the model name and aws credentials: 

```python
from amazon_bedrock_haystack import AmazonBedrockGenerator

aws_access_key_id="..."
aws_secret_access_key="..."
aws_region_name="eu-central-1"

generator = AmazonBedrockGenerator(model_name="anthropic.claude-v2", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_region_name=aws_region_name)
result = generator.run("Who is the best American actor?")
for reply in result["replies"]:
    print(reply)
```
Output: 
```shell
'There is no definitive "best" American actor, as acting skill and talent a# re subjective. However, some of the most acclaimed and influential American act# ors include Tom Hanks, Daniel Day-Lewis, Denzel Washington, Meryl Streep, Rober# t De Niro, Al Pacino, Marlon Brando, Jack Nicholson, Leonardo DiCaprio and John# ny Depp. Choosing a single "best" actor comes down to personal preference.'
```
