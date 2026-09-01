---
layout: integration
name: OpenZoo
description: Use OpenZoo's signup-free, pay-per-call OpenAI-compatible API in Haystack
authors:
    - name: OpenZoo
      socials:
        github: staccDOTsol
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/staccDOTsol/openzoo-mcp-server
type: Model Provider
report_issue: https://github.com/staccDOTsol/openzoo-mcp-server/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Usage](#usage)

## Overview

[OpenZoo](https://openzoo.fun) is an OpenAI-compatible inference provider with
no account or signup: any API key value is accepted, and usage is paid per
request — by card, or automatically via the x402 protocol when running the
local gateway (`npx openzoo`, serving `http://localhost:8402/v1`).

Because the API is OpenAI-compatible, it works with Haystack's built-in
`OpenAIGenerator` and `OpenAIChatGenerator` — no extra package is needed.

The model catalog at
[`https://api.openzoo.fun/v1/models`](https://api.openzoo.fun/v1/models) is
free to fetch and includes per-model pricing and context metadata. Model ids
are namespaced, e.g. `z-ai/glm-5.3-flash`.

## Usage

Install Haystack:

```bash
pip install haystack-ai
```

Use OpenZoo with `OpenAIChatGenerator` by pointing `api_base_url` at the
endpoint. The API key can be any value (there is no signup):

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_token("sk-openzoo"),  # any value works
    api_base_url="https://api.openzoo.fun/v1",
    model="z-ai/glm-5.3-flash",
)

response = generator.run(messages=[ChatMessage.from_user("Explain x402 in one sentence.")])
print(response["replies"][0].text)
```

For a fully local setup, run `npx openzoo` and set
`api_base_url="http://localhost:8402/v1"` — the gateway pays per call from a
local burner wallet.

Streaming works through the standard `streaming_callback` parameter, since the
endpoint supports SSE.
