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
[unirateapi.com](https://unirateapi.com)), then:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack_unirate import UniRateConverter

pipeline = Pipeline()
pipeline.add_component(
    "convert", UniRateConverter(api_key=Secret.from_env_var("UNIRATE_API_KEY"))
)

result = pipeline.run(
    {"convert": {"from_currency": "USD", "to_currency": "EUR", "amount": 100}}
)
print(result["convert"]["result"])  # e.g. 92.5
```

All components support `to_dict` / `from_dict` for pipeline serialization and
use Haystack `Secret` for API-key handling.

## License

`haystack-unirate` is distributed under the terms of the
[MIT license](https://github.com/UniRate-API/haystack-unirate/blob/main/LICENSE).
