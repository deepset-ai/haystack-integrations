---
layout: integration
name: Screwtape.ai
description: Check whether a seller is safe to pay before an agent pays, and return a signed receipt.
authors:
  - name: Screwtape.ai
    socials:
      github: screwtapeai
pypi: https://pypi.org/project/screwtape-pay-safely/
repo: https://github.com/screwtapeai/pay-safely
type: Tool Integration
report_issue: https://github.com/screwtapeai/pay-safely/issues
version: Haystack 2.0
toc: true
---

# Screwtape.ai

[Screwtape.ai](https://screwtape.ai) provides a pre-payment safety check for AI agents. The Haystack component calls `POST /v1/payment-check` and returns **allow**, **review** or **block**, with reasons and a signed receipt you can verify later. The check advises and records; it does not hold funds and does not independently stop a payment your code still makes.

## Installation

```bash
pip install "screwtape-pay-safely[haystack]"
```

## Components

This integration introduces one component:

- `SellerCheck`: takes a seller URL (and optional amount in US dollars) and returns a result string. Only treat the payment as allowed when the result starts with `Safe to pay`.

## Usage

```python
from pay_safely import PaySafely
from pay_safely.haystack import SellerCheck

check = SellerCheck(guard=PaySafely(agent_id="haystack-buyer"))
result = check.run(
    seller_url="https://seller.example/pay",
    amount_usd=0.05,
)
print(result["result"])
```

You can also place `SellerCheck` in a Haystack pipeline as any other component.

Free use is 3 calls per UTC day with no key, or 10 with a free key from [https://screwtape.ai/signup/](https://screwtape.ai/signup/). Then $0.005 per call. Pass `PaySafely(api_key="...")` when you have a key.

## License

The package is released under the MIT license. See [https://github.com/screwtapeai/pay-safely](https://github.com/screwtapeai/pay-safely).

## Support

support@screwtape.ai · [https://screwtape.ai](https://screwtape.ai)
