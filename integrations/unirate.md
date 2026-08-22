---
layout: integration
name: UniRate
description: Currency exchange rates, conversion, and currency listings for Haystack pipelines via the UniRate API.
authors:
    - name: UniRate Team
      socials:
        github: UniRate-API
pypi: https://pypi.org/project/haystack-unirate/
repo: https://github.com/UniRate-API/haystack-unirate
type: Custom Component
report_issue: https://github.com/UniRate-API/haystack-unirate/issues
logo: /logos/unirate.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`haystack-unirate` integrates the [UniRate API](https://unirateapi.com) into
Haystack 2.x pipelines. It ships three `@component`-decorated building blocks:

- **`UniRateExchangeRate`** — latest rate for a currency pair (or all targets).
- **`UniRateConverter`** — convert a monetary amount between two currencies.
- **`UniRateCurrencies`** — list every supported currency code.

UniRate covers 593+ fiat, crypto, and commodity instruments. Latest rates,
conversion, and currency listings are available on the free tier; historical
data requires a Pro plan.

## Installation

```bash
pip install haystack-unirate
```

## Usage

Set your API key in the `UNIRATE_API_KEY` environment variable (get one free at
[unirateapi.com](https://unirateapi.com)).

The components are most useful when wired alongside other Haystack building
blocks. Here a live rate is pulled with `UniRateExchangeRate`, injected into a
prompt, and handed to a chat generator so the model can answer using up-to-date
FX data:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_unirate import UniRateExchangeRate

pipeline = Pipeline()
pipeline.add_component(
    "rate", UniRateExchangeRate(api_key=Secret.from_env_var("UNIRATE_API_KEY"))
)
pipeline.add_component(
    "prompt",
    ChatPromptBuilder(
        template=[
            ChatMessage.from_user(
                "The current USD to EUR exchange rate is {{ rate }}. "
                "In one sentence, tell a traveler what 100 USD is worth in EUR."
            )
        ],
        required_variables=["rate"],
    ),
)
pipeline.add_component("llm", OpenAIChatGenerator())  # any Haystack chat generator

# Feed the live rate into the prompt, then the prompt into the chat model.
pipeline.connect("rate.rate", "prompt.rate")
pipeline.connect("prompt.prompt", "llm.messages")

result = pipeline.run({"rate": {"from_currency": "USD", "to_currency": "EUR"}})
print(result["llm"]["replies"][0].text)
```

`UniRateConverter` (amount conversion) and `UniRateCurrencies` (list supported
codes) slot into pipelines the same way. All three components support
`to_dict` / `from_dict` for pipeline serialization and use Haystack `Secret`
for API-key handling.

## License

`haystack-unirate` is distributed under the terms of the
[MIT license](https://github.com/UniRate-API/haystack-unirate/blob/main/LICENSE).
