---
layout: integration
name: Respan
description: Trace, monitor, and route Haystack pipelines with Respan observability, gateway, and prompt management.
authors:
  - name: Respan Team
    socials:
      github: respanai
pypi: https://pypi.org/project/respan-instrumentation-haystack/
repo: https://github.com/respanai/respan/tree/main/python-sdks/instrumentations/respan-instrumentation-haystack
type: Monitoring Tool
report_issue: https://github.com/respanai/respan/issues
logo: /logos/respan.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Prompt management](#prompt-management)
- [Screenshots](#screenshots)
- [License](#license)

## Overview

[Respan](https://respan.ai) is an observability and AI gateway platform for LLM applications. The `respan-instrumentation-haystack` package instruments Haystack pipelines through OpenTelemetry and exports pipeline, component, and LLM spans to Respan.

With Respan and Haystack, you can:

- Trace Haystack pipeline runs, component calls, prompt content, responses, token usage, latency, and cost
- Route Haystack's OpenAI-compatible generators through the Respan gateway with only a Respan API key
- Use Respan-managed prompts from Haystack by passing a managed `prompt_id` and variables through `generation_kwargs.extra_body.prompt`

## Installation

```bash
pip install respan-ai respan-instrumentation-haystack haystack-ai
```

Create a Respan API key in the [Respan platform](https://platform.respan.ai/platform/api/api-keys), then set:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export HAYSTACK_CONTENT_TRACING_ENABLED="true"
```

`HAYSTACK_CONTENT_TRACING_ENABLED` lets Haystack include prompt and response content in spans.

## Usage

### Trace and route a Haystack pipeline

The example below uses the Respan gateway, so Haystack's OpenAI-compatible generator uses `RESPAN_API_KEY` instead of a separate OpenAI provider key.

```python
import os

from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from respan import Respan
from respan_instrumentation_haystack import HaystackInstrumentor

os.environ.setdefault("HAYSTACK_CONTENT_TRACING_ENABLED", "true")
os.environ["OPENAI_API_KEY"] = os.environ["RESPAN_API_KEY"]
os.environ["OPENAI_BASE_URL"] = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")

respan = Respan(instrumentations=[HaystackInstrumentor()])

pipeline = Pipeline()
pipeline.add_component(
    "prompt_builder",
    PromptBuilder(template="Answer the following question: {{question}}"),
)
pipeline.add_component("generator", OpenAIGenerator(model="gpt-5-mini"))
pipeline.connect("prompt_builder", "generator")

result = pipeline.run(
    {"prompt_builder": {"question": "What is the capital of France?"}}
)
print(result["generator"]["replies"][0])

respan.flush()
```

After the run, open the [Respan traces page](https://platform.respan.ai/platform/traces) to inspect the Haystack pipeline, component, and LLM spans.

## Prompt management

Use Respan prompt management when you want to store and version prompt templates on the platform instead of hardcoding them in your Haystack application.

Create and deploy a prompt in Respan first, then pass only the managed `prompt_id` and variables in Haystack's `generation_kwargs.extra_body.prompt`.

```python
import os

from haystack import Pipeline
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from respan import Respan
from respan_instrumentation_haystack import HaystackInstrumentor

PROMPT_ID = "YOUR_RESPAN_PROMPT_ID"

os.environ.setdefault("HAYSTACK_CONTENT_TRACING_ENABLED", "true")
os.environ["OPENAI_API_KEY"] = os.environ["RESPAN_API_KEY"]
os.environ["OPENAI_BASE_URL"] = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")

respan = Respan(instrumentations=[HaystackInstrumentor()])

pipeline = Pipeline()
pipeline.add_component(
    "generator",
    OpenAIChatGenerator(model="gpt-5-mini"),
)

result = pipeline.run(
    {
        "generator": {
            "messages": [
                ChatMessage.from_user("Who created Python?"),
            ],
            "generation_kwargs": {
                "temperature": 0.0,
                "extra_body": {
                    "prompt": {
                        "prompt_id": PROMPT_ID,
                        "schema_version": 2,
                        "variables": {
                            "question": "Who created Python?",
                            "context": "Python was created by Guido van Rossum and first released in 1991.",
                        },
                        "override": True,
                    }
                },
            },
        }
    }
)

print(result["generator"]["replies"][0].text)
respan.flush()
```

Haystack still requires a runtime message for `OpenAIChatGenerator`. The Respan gateway reads `extra_body.prompt`, renders the managed prompt from the platform, and applies the prompt variables to the final model request.

For a runnable example that creates and deploys the managed prompt from code with `RESPAN_API_KEY`, see the [Respan Haystack examples](https://github.com/respanai/respan-example-projects/tree/main/python/tracing/haystack).

## Screenshots

After a Haystack pipeline run, Respan shows the trace tree with Haystack workflow, component, and LLM spans.

![Respan trace view for a Haystack pipeline](/images/respan-observability-tracing-result.png)

The managed prompt can be created programmatically and then referenced by `prompt_id` in the Haystack run.

![Managed prompt created from the Haystack example](/images/respan-managed-prompt-created-by-code.png)

Managed prompts are visible in the Respan prompt management page.

![Respan managed prompts page](/images/respan-managed-prompts-page.png)

## License

`respan-instrumentation-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
