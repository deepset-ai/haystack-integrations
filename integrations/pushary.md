---
layout: integration
name: Pushary
description: Customer phone approvals and one-use execution permits for Haystack actions.
authors:
  - name: Aadil Abdul Ghani
    socials:
      github: aadilghani1
repo: https://github.com/Pushary/pushary-haystack
type: Custom Component
report_issue: https://github.com/Pushary/pushary-haystack/issues
version: Haystack 3.0
toc: true
---

## Overview

Pushary sends an approval request to an enrolled customer's phone.
`PusharyProtectedAction` executes an application-owned action only after the
customer approves and the component consumes a one-use execution permit. It uses
the existing Pushary Python SDK and is maintained by Pushary.

The component supports Haystack 3.1+ and Python 3.10+. Its repository includes
a serialized-pipeline example that stops the worker before the customer answers
and resumes in another process, plus offline checks for refusal and retry behavior.

## Installation

Install the versioned PyPI package:

```bash
pip install pushary-haystack==0.1.0
```

Phone delivery requires a Pushary Partner account, a server-side `PUSHARY_API_KEY`,
and a customer enrolled by your application. The package's offline checks require
neither an account nor a real key.

## Usage

### Components

- `PusharyProtectedAction`: protects its registered handler with customer
  approval. It emits `result` after execution or `blocked` on a refusal.
  Haystack's `ComponentTool` can expose it to an Agent without exposing the
  recipient or operation identity as model-controlled tool arguments.

### Request an order approval

The following example uses an enrolled `customer-1` and a configured
`PUSHARY_API_KEY`. Replace the demonstration handler with your application's
idempotent order service.

```python
import time

from haystack import Pipeline
from pushary_haystack import PusharyProtectedAction


def release_order(parameters, idempotency_key):
    return {"order_id": parameters["order_id"], "status": "released"}


pipeline = Pipeline()
pipeline.add_component("approve", PusharyProtectedAction(
    release_order,
    tenant_id="store-1", external_id="customer-1",
    run_id="persisted-order-workflow-1", call_id="release-1",
    action="order.release", target="order-1", revision="release-v1",
    expires_at=int(time.time()) + 3600,
))
result = pipeline.run({"approve": {"parameters": {
    "order_id": "order-1", "amount_cents": 1900,
}}})
print(result)
```

By default, the component does not wait for a phone response. Persist the
pipeline configuration, input and deadline once, then re-enter that saved
operation after the customer answers. Do not regenerate IDs or extend the
deadline on retry. The [complete restart demonstration](https://github.com/Pushary/pushary-haystack/blob/main/examples/order_approval.py)
does this with an application-owned state file and a local SQLite order record.

Changed arguments require fresh approval. Duplicate workers cannot reuse a spent
permit. A crash after consumption requires reconciliation with the business
service; it does not guarantee exactly-once business effects. Only the registered
handler is protected: do not expose an alternative ungated action tool.

See the [package documentation](https://github.com/Pushary/pushary-haystack#readme)
for supported inputs, trusted snapshot loading, agent usage, and offline checks.

## License

[MIT](https://github.com/Pushary/pushary-haystack/blob/main/LICENSE).
