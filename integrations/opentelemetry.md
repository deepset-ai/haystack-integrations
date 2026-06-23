---
layout: integration
name: OpenTelemetry
description: Trace and monitor your Haystack pipelines with OpenTelemetry.

authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: haystack_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/opentelemetry-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/opentelemetry
type: Monitoring Tool
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/opentelemetry.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This integration lets you use [OpenTelemetry](https://opentelemetry.io/) to trace and monitor your Haystack
pipelines and agents. It builds on the [OpenTelemetry SDK](https://opentelemetry.io/docs/languages/python/) and
provides an `OpenTelemetryConnector` component that, once added to your pipeline, sends Haystack traces to any
OpenTelemetry-compatible backend.

## Installation

```bash
pip install opentelemetry-haystack
```

## Usage

Configure an OpenTelemetry `TracerProvider` with an exporter, then add the `OpenTelemetryConnector` to your
pipeline without connecting it to any other component. It enables OpenTelemetry tracing for all pipeline
operations.

You also need to set the `HAYSTACK_CONTENT_TRACING_ENABLED` environment variable to `true` to trace the content
(inputs and outputs) of the pipeline components.

```python
import os

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

# Configure the OpenTelemetry SDK. A service name is required for most backends.
resource = Resource(attributes={ResourceAttributes.SERVICE_NAME: "haystack"})
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")))
trace.set_tracer_provider(tracer_provider)

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.connectors.opentelemetry import OpenTelemetryConnector

pipe = Pipeline()
pipe.add_component("tracer", OpenTelemetryConnector("Chat example"))
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

Your traces will then be available in the OpenTelemetry backend you configured (for example, Jaeger, Grafana
Tempo, or any OTLP-compatible collector).

To capture even more detailed traces of the libraries used in your pipeline, you can combine the connector with the
available [OpenTelemetry instrumentations](https://opentelemetry.io/ecosystem/registry/?s=python), such as
`opentelemetry-instrumentation-openai-v2` for OpenAI requests.

If you prefer not to use the connector, you can also enable the tracer manually:

```python
from opentelemetry import trace
from haystack import tracing
from haystack_integrations.tracing.opentelemetry import OpenTelemetryTracer

tracing.enable_tracing(OpenTelemetryTracer(trace.get_tracer("my_application")))
```

## License

`opentelemetry-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
