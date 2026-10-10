---
layout: integration
name: send21
description: Let a Haystack pipeline or agent prepare a non-custodial payment request and get a pay link a person signs in their own wallet
authors:
    - name: send21
      socials:
        github: send21io
repo: https://github.com/send21io/send21-haystack
report_issue: https://github.com/send21io/send21-haystack/issues
type: Tool Integration
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[send21](https://send21.io) prepares payment instructions. `send21-haystack` adds a component that asks send21 to create a payment request (amount, fiat currency, receiving address, memo, order id) and returns a pay link. A person opens the link and signs in their own wallet; funds go straight from the payer's wallet to the receiver's wallet. send21 never holds keys or funds, never signs and never broadcasts.

Use an API key with the `drafts:write` scope only. That key can prepare a payment request but cannot move funds, so an agent using this component can ask for a payment but cannot make one.

The package also includes `verify_send21_signature` for checking send21 webhooks (`X-Send21-Signature`, HMAC-SHA256 of the raw body), so a pipeline can continue once a payment is confirmed.

This is a community integration maintained by send21. See the [repository](https://github.com/send21io/send21-haystack) for details and open questions.

## Installation

```bash
pip install git+https://github.com/send21io/send21-haystack
```

## Usage
### Components
This integration introduces 1 component and a helper:

- `Send21PaymentRequest`: calls the `create_payment_request` tool on the send21 MCP server (`https://send21.io/mcp`) and outputs `id`, `pay_link` and `raw`.
- `verify_send21_signature(raw_body, signature_header, secret)`: constant-time check of a send21 webhook signature.

### Use Send21PaymentRequest in a pipeline

Set `SEND21_API_KEY` (scope `drafts:write`). To try it offline, pass `client=MockSend21Client()`.

```python
from haystack import Pipeline
from send21_haystack import Send21PaymentRequest

payment = Send21PaymentRequest(currency="USDC", network="base", address="0xYourReceivingAddress")

p = Pipeline()
p.add_component("payment", payment)
out = p.run({"payment": {"amount": 1.50, "fiat_currency": "USD",
                         "order_id": "run-42", "memo": "agent top-up"}})
print(out["payment"]["pay_link"])
```

### Verify a webhook

```python
from send21_haystack import verify_send21_signature

if not verify_send21_signature(raw_body, headers.get("X-Send21-Signature"), signing_secret):
    raise PermissionError("invalid signature")
```

### License

`send21-haystack` is distributed under the terms of the [MIT](https://github.com/send21io/send21-haystack/blob/main/LICENSE) license.
