---
layout: integration
name: OpenZoo
description: Use OpenZoo's pay-per-call OpenAI-compatible API in Haystack via the local npx openzoo proxy
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
no account or signup: a small local proxy (`npx openzoo`, serving
`http://localhost:8402/v1`) pays for each request via the x402 protocol from a
local burner wallet. The proxy ignores the API key, so any non-empty value
works.

Because the API is OpenAI-compatible, it works with Haystack's built-in
`OpenAIGenerator` and `OpenAIChatGenerator` — no extra package is needed.

The model catalog at `http://localhost:8402/v1/models` is free to fetch and
includes per-model pricing and context metadata. Model ids are bare model
names, e.g. `claude-sonnet-5` or `gpt-4o-mini`; `auto` lets the proxy pick a
model per request.

## Usage

Install Haystack and start the OpenZoo proxy:

```bash
pip install haystack-ai
npx openzoo   # serves http://localhost:8402/v1
```

`npx openzoo address` prints the proxy's wallet — fund it with USDC on Solana
or Base; `npx openzoo balance` shows what is left.

Use OpenZoo with `OpenAIChatGenerator` by pointing `api_base_url` at the
proxy. The API key can be any non-empty value (the proxy ignores it):

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

generator = OpenAIChatGenerator(
    api_key=Secret.from_token("sk-openzoo"),  # ignored by the proxy
    api_base_url="http://localhost:8402/v1",
    model="auto",
)

response = generator.run(messages=[ChatMessage.from_user("Explain x402 in one sentence.")])
print(response["replies"][0].text)
```

The hosted endpoint `https://api.openzoo.fun/v1` answers HTTP 402 unless the
caller pays x402 or presents an OpenZoo subscription key (`ozk_live_…`);
Haystack cannot pay x402 itself, so use the local proxy.

Streaming works through the standard `streaming_callback` parameter, since the
endpoint supports SSE.
