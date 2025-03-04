---
layout: integration
name: Weights & Biases Weave Tracer
description: Send Haystack traces to Weights & Biases for monitoring and visualization
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/weights_biases-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/weights_biases
type: Monitoring Tool
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/weighs_and_bias.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This integration allows you to use Weights & Biases Weave framework for tracing and monitoring Haystack pipeline 
components. It provides a connector that sends Haystack traces to Weights & Biases for monitoring and visualization.
 

## Installation

```bash
pip install weights_biases-haystack
```

## Usage

### Components
This integration introduces one new component, a connector named `WeaveConnector` whose only responsibility is to send
traces to Weights & Biases.

Note that you need to have the `WANDB_API_KEY` environment variable set to your Weights & Biases API key.

NOTE: If you don't have a Weights & Biases account, it will interactively ask you to set one and your input will then 
be stored in ~/.netrc

In addition, you need to set the `HAYSTACK_CONTENT_TRACING_ENABLED` environment variable to `true` in order to
enable Haystack tracing in your pipeline.

To use this connector, simply add it to your pipeline without any connections, and it will automatically start
sending traces to Weights & Biases.


```python
import os

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.connectors import WeaveConnector

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder())
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipe.connect("prompt_builder.prompt", "llm.messages")

connector = WeaveConnector(pipeline_name="test_pipeline")
pipe.add_component("weave", connector)

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
print(response["llm"]["replies"][0])
```

### License

Info about your integration license
