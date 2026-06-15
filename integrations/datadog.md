---
layout: integration
name: Datadog
description: Send Haystack traces to Datadog for monitoring and visualization
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/datadog-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/datadog
type: Monitoring Tool
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/datadog.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This integration lets you use [Datadog](https://www.datadoghq.com/) to trace and monitor your Haystack
pipelines and agents. It relies on [Datadog's tracing library `ddtrace`](https://ddtrace.readthedocs.io/en/stable/)
and provides a `DatadogConnector` component that, once added to your pipeline, sends Haystack traces to Datadog.

## Installation

```bash
pip install datadog-haystack
```

## Usage

Add the `DatadogConnector` to your pipeline without connecting it to any other component. It enables Datadog
tracing for all pipeline operations.

You also need to set the `HAYSTACK_CONTENT_TRACING_ENABLED` environment variable to `true` to trace the content
(inputs and outputs) of the pipeline components.

Datadog itself is configured through the standard `ddtrace` mechanisms, for example the `DD_SERVICE`, `DD_ENV` and
`DD_VERSION` environment variables, or by running your application with the `ddtrace-run` command. See the
[ddtrace documentation](https://ddtrace.readthedocs.io/en/stable/) for more details.

```python
import os

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.connectors.datadog import DatadogConnector

pipe = Pipeline()
pipe.add_component("tracer", DatadogConnector("Chat example"))
pipe.add_component("prompt_builder", ChatPromptBuilder())
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))

pipe.connect("prompt_builder.prompt", "llm.messages")

messages = [
    ChatMessage.from_system("Always respond in German even if some input data is in other languages."),
    ChatMessage.from_user("Tell me about {{location}}"),
]

response = pipe.run(
    data={"prompt_builder": {"template_variables": {"location": "Berlin"}, "template": messages}}
)
print(response["llm"]["replies"][0])
```

Your traces will then be available in your Datadog dashboard under the configured service.

If you prefer not to use the connector, you can also enable the tracer manually:

```python
import ddtrace
from haystack import tracing
from haystack_integrations.tracing.datadog import DatadogTracer

tracing.enable_tracing(DatadogTracer(ddtrace.tracer))
```

## License

`datadog-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
