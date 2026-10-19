---
# SPDX-License-Identifier: CC0-1.0
layout: integration
name: TrustedTokens
description: Use EU data-sovereign open-weight models from TrustedTokens in Haystack
authors:
    - name: TNG Technology Consulting GmbH
      socials:
        github: tngtech
        twitter: tngtech
        linkedin: https://de.linkedin.com/company/tng-technology-consulting
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/trustedtokens.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[TrustedTokens](https://trustedtokens.eu/) serves leading open-weight models
from GPU servers that [TNG Technology Consulting GmbH](https://www.tngtech.com/en/)
operates itself, colocated in a German datacenter. Inference runs on a vLLM and
SGLang stack behind an OpenAI-compatible API, with no US cloud at any hop and
no third-party CDN or WAF in the request path. There is no CLOUD Act exposure.

TrustedTokens never stores prompts or completions and never uses them for
training; only operational metadata such as token counts and latency is
retained for billing. A data processing agreement under Art. 28 GDPR is
available.

New model releases go live within hours of their weights appearing on Hugging Face;
for the current lineup, see the [models page](https://trustedtokens.eu/models).
Open weights mean no vendor lock-in. The API supports streaming, tool calling,
structured outputs and prompt caching.

## Usage

The [TrustedTokens API](https://trustedtokens.eu/docs/) is OpenAI compatible, so it works in Haystack through the OpenAI generators by pointing them at the TrustedTokens endpoint.

Set your API key as an environment variable:

```bash
export TRUSTEDTOKENS_API_KEY="your-api-key"
```

### Using `OpenAIChatGenerator`

```python
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_env_var("TRUSTEDTOKENS_API_KEY"),
    api_base_url="https://api.trustedtokens.eu/v1",
    model="zai-org/GLM-5.3",
)

messages = [ChatMessage.from_user("Summarise the following contract clause: ...")]
response = generator.run(messages=messages)
print(response["replies"][0].text)
```

### Use with a Haystack Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from haystack.utils import Secret


@tool
def weather(city: str) -> str:
    """Return the weather for a city."""
    return f"The weather in {city} is sunny and 22 degrees"


agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_env_var("TRUSTEDTOKENS_API_KEY"),
        api_base_url="https://api.trustedtokens.eu/v1",
        model="zai-org/GLM-5.3",
    ),
    tools=[weather],
)
result = agent.run(messages=[ChatMessage.from_user("What's the weather in Munich?")])
print(result["last_message"].text)
```
