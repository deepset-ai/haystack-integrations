---
layout: integration
name: Featherless AI
description: Get access to thousands of open source language models hosted by Featherless.ai
authors:
    - name: Featherless AI
      socials:
        github: featherlessai
        twitter: FeatherlessAI
        linkedin: https://www.linkedin.com/company/feather-serverless-ai/
        
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/featherless.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

**Featherless AI** is a serverless AI inference platform. Our goal is to make all AI models available for serverless inference and we’ve started with large language models (e.g. Qwen, Llama, Mistral, DeepSeek, RWKV). We provide inference via API to a continually expanding library of open-weight models, including the most popular models for role-playing, creative writing, coding assistance, and more. 

To start using Featherless, sign up for an API key [here](https://featherless.ai/).

## Usage

Featherless AI is OpenAI compatible, making it easy to use in Haystack via OpenAI Generators.



### Using `ChatGenerator`

See an example of engaging in a multi-turn conversation with `mistralai/Mistral-Small-24B-Instruct-2501`
You need to set the environment variable `FEATHERLESS_API_KEY` and choose a model from our [catalog](https://featherless.ai/models).

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
import os

os.environ["FEATHERLESS_API_KEY"] = "YOUR_FEATHERLESS_API_KEY"

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("FEATHERLESS_API_KEY"),
    api_base_url="https://api.featherless.ai/v1",
    model="mistralai/Mistral-Small-24B-Instruct-2501",
    generation_kwargs = {"max_tokens": 512}
)


messages = []

while True:
    msg = input("Enter your message or Q to exit\n🧑 ")
    if msg=="Q":
        break
    messages.append(ChatMessage.from_user(msg))
    response = generator.run(messages=messages)
    assistant_resp = response['replies'][0]
    print("🤖 "+assistant_resp.text)
    messages.append(assistant_resp)
```
