---
layout: integration
name: send21
description: Prepare a non-custodial crypto pay link from a Haystack pipeline and verify send21's signed webhooks. The payer signs in their own wallet.
authors:
    - name: send21
      socials:
        github: send21io
        website: https://send21.io/
pypi: https://pypi.org/project/send21-haystack/
repo: https://github.com/send21io/send21-haystack
type: Tool Integration
report_issue: https://github.com/send21io/send21-haystack/issues
logo: /logos/send21.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [Use Send21PaymentRequest in a pipeline](#use-send21paymentrequest-in-a-pipeline)
  - [Try it offline](#try-it-offline)
  - [Verify a webhook](#verify-a-webhook)
- [License](#license)

## Overview

[send21](https://send21.io/) prepares payment instructions: crypto pay links priced in a fiat currency and paid straight to the receiver's own wallet. A person opens the pay link and signs in their own wallet. send21 never holds keys or funds, never signs and never broadcasts.

`send21-haystack` adds a `Send21PaymentRequest` component that asks send21 to prepare a payment request (amount, fiat currency, receiving address, order id, memo) and returns its id and pay link. It calls the `create_payment_request` tool on the send21 MCP server (`https://send21.io/mcp`, Streamable HTTP). The package also includes `verify_send21_webhook` for checking send21's signed webhooks, and `MockSend21Client` for running the component offline.

Use an API key with the `drafts:write` scope only. That key can prepare a payment request but cannot move funds. New send21 accounts only accept receiving addresses the owner approved in send21; any other address is refused with `422 address_not_approved` and nothing is created.

Supported currencies and networks (API values): `Btc` on `Mainnet` (on-chain and Lightning), `Usdc` on `Solana`, `Ethereum`, `Base`, `Arbitrum` and `Polygon`, `Usdt` on `Solana` and `Ethereum`, `Eurc` on `Solana`, `Ethereum` and `Base`, `Sol` on `Solana`, and `Eth` on `Ethereum`, `Base` and `Arbitrum`.

This is a community integration maintained by send21. It is not an official deepset integration. See the [send21 MCP docs](https://send21.io/docs/mcp) for the server and its tools.

## Installation

```bash
pip install send21-haystack
```

## Usage

### Components

This integration introduces 1 component and a webhook helper:

- `Send21PaymentRequest`: creates a send21 payment request and outputs `id`, `pay_link` and `raw` (the full tool result). It reads the API key from the `SEND21_API_KEY` environment variable through Haystack's `Secret`.
- `verify_send21_webhook(raw_body, headers, secret)`: checks a send21 webhook delivery and returns `(valid, scheme)`, where `scheme` is `"v2"`, `"v1"` or `None`.

### Use Send21PaymentRequest in a pipeline

Create an API key with the `drafts:write` scope at [send21](https://send21.io/api-keys) and set it as `SEND21_API_KEY`. Approve your receiving address in send21 first.

```python
from haystack import Pipeline
from send21_haystack import Send21PaymentRequest

# reads SEND21_API_KEY from the environment (scope: drafts:write)
payment = Send21PaymentRequest(currency="Usdc", network="Base", address="0xYourReceivingAddress")

p = Pipeline()
p.add_component("payment", payment)
out = p.run({"payment": {"amount": 1.50, "fiat_currency": "USD",
                         "order_id": "run-42", "memo": "agent top-up"}})
print(out["payment"]["pay_link"])   # https://send21.io/p/...
```

### Try it offline

Pass `client=MockSend21Client()` to get deterministic ids with no network call:

```python
from haystack import Pipeline
from send21_haystack import MockSend21Client, Send21PaymentRequest

payment = Send21PaymentRequest(currency="Usdc", network="Base", address="0xYourReceivingAddress",
                               client=MockSend21Client())

p = Pipeline()
p.add_component("payment", payment)
out = p.run({"payment": {"amount": 1.50, "fiat_currency": "USD", "order_id": "run-42"}})
print(out["payment"]["pay_link"])   # https://send21.io/p/demo-0001
```

### Verify a webhook

`verify_send21_webhook` checks `X-Send21-Signature-V2` first: `t=<timestamp>,v1=<lowercase hex HMAC-SHA256 of "<timestamp>.<delivery id>.<raw body>">`, keyed with the endpoint signing secret. It compares in constant time and refuses deliveries more than 5 minutes old, so a copied delivery cannot be replayed. The legacy `X-Send21-Signature` (HMAC of the raw body only) is used only when no V2 header is present; pass `allow_legacy=False` to turn it off.

```python
from send21_haystack import verify_send21_webhook

# raw_body: the request bytes before JSON parsing; headers: the request headers
valid, scheme = verify_send21_webhook(raw_body, headers, signing_secret)
if not valid:
    raise PermissionError("invalid, expired or missing signature")
```

send21 retries failed deliveries, so the same delivery can arrive more than once, and deliveries can arrive out of order. Store `X-Send21-Delivery` and ignore repeats.

### License

`send21-haystack` is distributed under the terms of the [MIT](https://github.com/send21io/send21-haystack/blob/main/LICENSE) license.
