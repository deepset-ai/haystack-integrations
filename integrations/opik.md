---
layout: integration
name: Opik
description: Trace and evaluate your Haystack pipelines with Opik
authors:
    - name: Comet ML
      socials:
        github: comet-ml
        twitter: Cometml
        linkedin: https://www.linkedin.com/company/comet-ml/
pypi: https://pypi.org/project/opik/
repo: https://github.com/comet-ml/opik
type: Monitoring Tool
report_issue: https://github.com/comet-ml/opik/issues
logo: /logos/opik.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Opik](https://www.comet.com/site/products/opik/) is an open source tool that helps you to trace, evaluate and monitor your LLM applications. With the Opik platform, you can:

- Debug your pipelines
- Automatically evaluate your pipelines with built-in metrics like hallucinations or context relevance
- Track the latency and cost of your pipeline runs
- Monitor your pipelines in production

You can learn more about the Haystack and Opik integration in Opik's [Haystack integration guide](https://www.comet.com/docs/opik/tracing/integrations/haystack).

## Installation

To use the Opik integration with Haystack, install the `opik` package:

```bash
pip install opik haystack-ai
```

## Usage

To use Opik, you will need to:

1. Enable content tracing in Haystack by setting the environment variable `HAYSTACK_CONTENT_TRACING_ENABLED` to `True`
2. Add the `OpikConnector` to your pipeline

An example pipeline that uses Opik is shown below:

```python
# Enable content tracing
import os
os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from opik.integrations.haystack import OpikConnector


pipe = Pipeline()

# Add the OpikConnector component to the pipeline
pipe.add_component(
    "tracer", OpikConnector("Chat example")
)

# Continue building the pipeline
pipe.add_component("prompt_builder", ChatPromptBuilder())
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-3.5-turbo"))

pipe.connect("prompt_builder.prompt", "llm.messages")
```

The `OpikConnector` component will automatically trace the pipeline and log it in Opik. It will also augment the response to include a `tracer` key that will contain the Opik `traceId`:

```python
messages = [
    ChatMessage.from_system(
        "Always respond in German even if some input data is in other languages."
    ),
    ChatMessage.from_user("Tell me about {{location}}"),
]

response = pipe.run(
    data={
        "prompt_builder": {
            "template_variables": {"location": "Berlin"},
            "template": messages,
        }
    }
)

print(response)
```

![Opik Gif](/images/opik-demo.gif)

## License

Opik is fully open source and is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
