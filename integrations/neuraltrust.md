---
layout: integration
name: NeuralTrust
description: Evaluate text and chat messages with NeuralTrust TrustGuard to enforce security policies in Haystack pipelines.
authors:
    - name: NeuralTrust
      socials:
        github: NeuralTrust
pypi: https://pypi.org/project/neuraltrust-haystack/
repo: https://github.com/NeuralTrust/neuraltrust-haystack
report_issue: https://github.com/NeuralTrust/neuraltrust-haystack/issues
type: Custom Component
version: Haystack 2.31+ and 3.x
toc: true
---

## Overview

[NeuralTrust](https://neuraltrust.ai) provides TrustGuard policies for evaluating application input and output. The `neuraltrust-haystack` package adds two native Haystack components:

| Component | Input | Purpose |
| --- | --- | --- |
| `NeuralTrustGuard` | `text: str` | Evaluate a text input or completed output. |
| `NeuralTrustChatGuard` | `messages: list[ChatMessage]` | Evaluate text-only chat messages while preserving names and metadata. |

Read the [official Haystack integration guide](https://docs.neuraltrust.ai/integrations/haystack) for setup and usage documentation.

Both support synchronous and asynchronous execution and Haystack pipeline serialization. TrustGuard collector policies determine which checks run and whether content is allowed, reported, transformed, blocked, or held for approval.

## Installation

Requires Python 3.10+ and Haystack 2.31 or 3.x.

```bash
pip install neuraltrust-haystack
export TRUSTGUARD_API_KEY="your-collector-api-key"
```

Use a collector configured with the desired TrustGuard policy. The API key selects that collector. The default API origin is `https://trustguard.neuraltrust.ai`; use `api_base` for your deployment's public HTTPS origin.

## Text evaluation

```python
from haystack_integrations.components.guardrails.neuraltrust import NeuralTrustGuard

with NeuralTrustGuard() as guard:
    result = guard.run(text="What is the capital of France?")
    print(result["text"])
    print(result["verdict"]["status"])
```

By default, `block` and `ask` raise `NeuralTrustBlockedError`. `allow` and `report` forward the original content; `transform` forwards validated transformed content. Invalid responses and service errors stop execution.

## Pipeline usage

Set `on_violation="route"` to handle a stopped request through its verdict. Only passing content receives a `text` output:

```python
from haystack import Pipeline, component

from haystack_integrations.components.guardrails.neuraltrust import NeuralTrustGuard


@component
class AcceptText:
    @component.output_types(accepted=str)
    def run(self, text: str) -> dict[str, str]:
        return {"accepted": text}


with NeuralTrustGuard(on_violation="route") as guard:
    pipeline = Pipeline()
    pipeline.add_component("guard", guard)
    pipeline.add_component("accept", AcceptText())
    pipeline.connect("guard.text", "accept.text")

    result = pipeline.run(
        {"guard": {"text": "What is the capital of France?"}},
        include_outputs_from={"guard"},
    )
    print(result["guard"]["verdict"]["status"])
    if "accept" in result:
        print(result["accept"]["accepted"])
```

For `block` or `ask`, the guard returns only `verdict`. The connected component's required input receives no value, so it does not run. `ask` remains stopped because this integration does not implement human approval.

## Chat and output evaluation

```python
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.guardrails.neuraltrust import NeuralTrustChatGuard

with NeuralTrustChatGuard(direction="output") as guard:
    result = guard.run(messages=[ChatMessage.from_assistant("Paris is the capital of France.")])
    print(result["messages"][0].text)
```

In a chat pipeline, connect the generator's `replies` output to `guard.messages`. Use `async with guard` around direct `await guard.run_async(...)` calls or asynchronous pipeline execution, and close each pool in its owning event loop before shutdown. Haystack 3.x runs async pipelines through `Pipeline.run_async`; Haystack 2.31 uses `AsyncPipeline.run_async`.

The chat component accepts a nonempty list of system, user, and assistant messages, each containing exactly one nonempty text part. Multiple content parts, reasoning, multimodal data, and tool calls/results are rejected. Evaluation covers completed replies; it does not intercept streamed tokens or an Agent's internal tool actions.

## Configuration and serialization

Optional constructor settings include `api_base`, `direction`, `on_violation`, `timeout`, `max_retries`, and the `collector_key` identifier for service-token authentication. Run calls accept `session_id`, `consumer_id`, and JSON-compatible `attributes`.

The default environment-based Haystack Secret supports `Pipeline.dumps()` and `Pipeline.loads()` without serializing the API key value. Configure the same credential environment in the restoring process. Token-based Secrets are intentionally not serializable.

Verdicts can include findings and request/trace IDs. Findings may contain sensitive content evidence; avoid logging them indiscriminately. See the [official integration guide](https://docs.neuraltrust.ai/integrations/haystack) and [package README](https://github.com/NeuralTrust/neuraltrust-haystack#readme) for the full configuration and error contract.

## License

`neuraltrust-haystack` is distributed under the [MIT License](https://github.com/NeuralTrust/neuraltrust-haystack/blob/main/LICENSE).
