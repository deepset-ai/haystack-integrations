---
layout: integration
name: Inferrail
description: Give each Haystack pipeline or agent run its own dollar budget, enforced before model calls, with a per-run cost record.
authors:
    - name: Inferrail
      socials:
        github: domondi1
pypi: https://pypi.org/project/inferrail/
repo: https://github.com/domondi1/inferrail
report_issue: https://github.com/domondi1/inferrail/issues
type: Custom Component
version: Haystack 3.2
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Start Inferrail](#start-inferrail)
- [Give each pipeline run a budget](#give-each-pipeline-run-a-budget)
- [When a run reaches its budget](#when-a-run-reaches-its-budget)
- [Limitations](#limitations)
- [License](#license)

## Overview

[Inferrail](https://github.com/domondi1/inferrail) is a self-hosted,
OpenAI- and Anthropic-compatible gateway. One pipeline or agent run can
make many model calls. With Inferrail you give that run a dollar budget:
calls are admitted while the run's budget has room and refused before
they reach the model provider once it doesn't. Afterwards you can read
the run's total cost. Prompts and responses aren't stored.

Haystack's built-in
[`OpenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/openaichatgenerator)
works with it as-is, so no Haystack-specific package is needed. You
point the generator at Inferrail and attach two headers to each run.

The example below was validated with Haystack 3.2.0 and Inferrail
0.4.7.

## Installation

```bash
pip install haystack-ai inferrail==0.4.7
```

## Start Inferrail

Inferrail holds the provider key; the Haystack process only needs the
gateway URL. Save as `inferrail.yaml`:

```yaml
providers:
  openai: {type: openai, api_key_env: OPENAI_API_KEY}
routes:
  default: {provider: openai, model: gpt-4o-mini}
receipts: {sink: sqlite, path: ./receipts.db}
budgets: {enabled: true, path: ./budgets.db}
```

```bash
export OPENAI_API_KEY=...              # only the gateway process sees it
inferrail serve --config inferrail.yaml
```

In the Haystack process:

```bash
export INFERRAIL_BASE_URL="http://127.0.0.1:8000"
export INFERRAIL_GATEWAY_TOKEN="unused"   # or your INFERRAIL_GATEWAY_TOKEN, if you set one
```

## Give each pipeline run a budget

Build the pipeline once. Each `pipeline.run(...)` passes its own run id
and budget as request headers through `generation_kwargs`:

```python
import os

from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

document_store = InMemoryDocumentStore()
document_store.write_documents([
    Document(content="Refunds are processed within 5 business days."),
    Document(content="Orders over $100 ship free."),
])

template = [
    ChatMessage.from_system("Answer only from the supplied documents."),
    ChatMessage.from_user(
        "Documents:\n{% for document in documents %}- {{ document.content }}\n{% endfor %}"
        "Question: {{ question }}"
    ),
]

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store, top_k=1))
pipeline.add_component(
    "prompt_builder",
    ChatPromptBuilder(template=template, required_variables={"documents", "question"}),
)
pipeline.add_component(
    "llm",
    OpenAIChatGenerator(
        api_key=Secret.from_env_var("INFERRAIL_GATEWAY_TOKEN"),
        model="default",  # an Inferrail route name
        api_base_url=f"{os.environ['INFERRAIL_BASE_URL'].rstrip('/')}/v1",
        generation_kwargs={"max_tokens": 300},
    ),
)
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.messages")


def run_with_budget(question: str, run_id: str, budget_usd: str) -> str:
    """One pipeline run = one Inferrail work unit with its own dollar budget."""
    result = pipeline.run({
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
        "llm": {"generation_kwargs": {"max_tokens": 300, "extra_headers": {
            "X-Inferrail-Attribute-Work-Id": run_id,
            "X-Inferrail-Budget-Usd": budget_usd,
        }}},
    })
    return result["llm"]["replies"][0].text


print(run_with_budget("How long do refunds take?", run_id="support-ticket-4812", budget_usd="0.05"))
```

The first call of a run creates its budget. There's no budget object to
set up beforehand. Every call made with the same run id, including
calls from an agent loop, shares that budget.

Read the run's total cost afterwards:

```bash
inferrail work support-ticket-4812 --config inferrail.yaml
```

## When a run reaches its budget

When the run's remaining budget can't cover a call, Inferrail refuses it
with HTTP 402 before it reaches the provider. `OpenAIChatGenerator`
raises it as `openai.APIStatusError` with `status_code == 402`, so you
can stop the run or return a fallback answer:

```python
from openai import APIStatusError

try:
    answer = run_with_budget(question, run_id, budget_usd="0.05")
except APIStatusError as e:
    if e.status_code != 402:
        raise
    answer = "This request reached its budget."
```

Calls from one run that are in flight at the same time are admitted
against the same budget atomically, so parallel calls can't all spend
the same remaining dollars.

## Limitations

- Each call reserves an estimate (roughly prompt size plus `max_tokens`
  at list price). Set `max_tokens`: without it, Inferrail assumes 4,096
  output tokens. A call whose actual cost exceeds its reservation still
  completes; the overrun is recorded and the run's later calls are
  refused.
- Only calls that go through Inferrail are counted.
- More details and the full list:
  [Give one AI agent run a dollar budget](https://github.com/domondi1/inferrail/blob/main/docs/recipes/agent-run-budget.md?ref=haystack-integrations).

## License

Inferrail is distributed under the
[Apache License 2.0](https://github.com/domondi1/inferrail/blob/main/LICENSE).
