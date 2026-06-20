---
layout: integration
name: Skim
description: Turn any URL into clean, LLM-ready Markdown — paid per call over x402, no API key or signup
authors:
    - name: Skim
      socials:
        github: JessieJanie
        twitter: skim402
pypi: https://pypi.org/project/skim-haystack
repo: https://github.com/JessieJanie/skim402
type: Data Ingestion
report_issue: https://github.com/JessieJanie/skim402/issues
logo: /logos/skim.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Example](#basic-example)
  - [In a Pipeline](#in-a-pipeline)
  - [Parameters](#parameters)
- [License](#license)

## Overview

[Skim](https://skim402.com) is the canonical [x402](https://x402.org) clean reader API for AI agents. Give it a URL and it returns the page as clean, agent-ready Markdown plus structured metadata — no ads, no nav, no boilerplate.

This integration provides one component:

- `SkimReader`: Fetches one or more URLs and returns the extracted content as Haystack `Document` objects (cleaned Markdown in `content`, page metadata in `meta`).

Skim requires no signup and no API key. Each call costs $0.002 in USDC on Base, paid automatically by a wallet you control over the HTTP 402 payment protocol. The private key never leaves your machine — it only signs an EIP-3009 USDC authorization locally. Fund a dedicated Base wallet with a little USDC and set its private key in the `SKIM_WALLET_PRIVATE_KEY` environment variable. Step-by-step wallet setup (written for non-crypto-native developers): [skim402.com/wallet](https://skim402.com/wallet).

## Installation

```bash
pip install skim-haystack
```

This pulls in the x402 client with EVM support, so there is nothing else to install.

## Usage

### Basic Example

```python
import os
from skim_haystack import SkimReader

os.environ["SKIM_WALLET_PRIVATE_KEY"] = "0x..."  # a dedicated Base wallet, funded with USDC

reader = SkimReader()  # reads SKIM_WALLET_PRIVATE_KEY from the environment

result = reader.run(urls="https://en.wikipedia.org/wiki/HTTP_402")
print(result["documents"][0].content)
```

You can also pass the key explicitly with a Haystack `Secret`:

```python
from haystack.utils import Secret
from skim_haystack import SkimReader

reader = SkimReader(
    private_key=Secret.from_token("0x..."),
    max_price_usd=0.005,
    include_metadata=True,
)
```

### In a Pipeline

`SkimReader` is a standard Haystack component, so it drops straight into a `Pipeline`. Here it fetches a page and feeds the cleaned Markdown into a prompt:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from skim_haystack import SkimReader

pipe = Pipeline()
pipe.add_component("reader", SkimReader())
pipe.add_component("prompt", PromptBuilder(
    template="Summarize this article in 5 bullets:\n\n{{ documents[0].content }}"
))
pipe.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))

pipe.connect("reader.documents", "prompt.documents")
pipe.connect("prompt.prompt", "llm.prompt")

result = pipe.run({"reader": {"urls": "https://en.wikipedia.org/wiki/HTTP_402"}})
print(result["llm"]["replies"][0])
```

The wallet pays per read, and your pipeline gets clean Markdown instead of raw HTML.

### Parameters

`SkimReader` takes the following parameters (all optional except the wallet key):

- **`private_key`**: A Haystack `Secret` holding the Base wallet's hex private key. Defaults to `Secret.from_env_var("SKIM_WALLET_PRIVATE_KEY")`. Pass `Secret.from_token("0x...")` for an explicit key. Use a dedicated wallet, never your personal one.
- **`base_url`**: Skim API base URL. Defaults to `https://skim402.com`.
- **`max_price_usd`**: Hard per-call price cap in USD. The wallet refuses to sign for anything above this. Defaults to `0.01` (Skim is `$0.002`).
- **`include_metadata`**: When `True` (default), populate each `Document`'s `meta` with page metadata (title, byline, published date, language, excerpt).
- **`timeout`**: Per-request timeout in seconds. Defaults to `60`.

The component output is `{"documents": [...]}` — one `Document` per URL, with cleaned Markdown in `content` and metadata in `meta` (always including `source`, the URL). It also supports pipeline serialization (`to_dict`/`from_dict`); when the key comes from an environment variable, it is stored as a reference to that variable name, never the raw value.

## License

`skim-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
