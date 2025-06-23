---
layout: integration
name: OpenLIT
description: Monitor, evaluate & improve GenAI and LLM applications
authors:
    - name: OpenLIT Team
      socials:
        github: openlit
        twitter: openlit_io
pypi: https://pypi.org/project/openlit
repo: https://github.com/openlit/openlit
type: Monitoring Tool
report_issue: https://github.com/openlit/openlit/issues
logo: /logos/openlit.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
[OpenLIT](https://openlit.io/) is an OpenTelemetry-native GenAI and LLM application observability tool. 
It simplifies the integration of observability into GenAI and LLM using Haystack with just a single line of code.

OpenLIT allows you to monitor detailed information about LLM operations, such as API calls, content, prompts, costs, and more. This enables you to gain insights into your models’ performance, identify improvement areas, and reduce costs.

Check out the [official documentation](https://docs.openlit.io/) for more information.

### ⚡ Features
- **OpenTelemetry-native**: Native support ensures that integrating OpenLIT into your projects feels more like a natural extension rather than an additional layer of complexity.
- **Granular Usage Insights of your LLM Applications**: Assess your LLM's performance and costs with fine-grained control, breaking down metrics by environment (such as staging or production) or application, to optimize efficiency and scalability.
- **Vendor-Neutral SDKs**: In the spirit of OpenTelemetry, OpenLIT's SDKs are agnostic of the backend vendors. This means you can confidently use OpenLIT with various telemetry backends, like Prometheus + Jaeeger or even platforms like Grafana Cloud, without worrying about compatibility issues.

## Installation

```bash
pip install openlit
```

## Usage
Adding monitoring to your application is as simple as adding one line to your code:

```python
openlit.init()
```

When you execute your code, traces and metrics will appear directly in your console, which is ideal for immediate debugging. 

However, to store and track this data over time, you should send these traces and metrics to OpenLIT. For guidance on how to do this, [refer to this quickstart guide](https://docs.openlit.io/latest/quickstart). 

If you wish to integrate LLM monitoring data with your existing observability stack, such as Grafana, explore [OpenLIT connections](https://docs.openlit.io/latest/connections/intro) to get started.

### Example: Trace Haystack Pipelines

The following code snippet illustrates how to utilize OpenLIT to trace a Haystack pipeline, enabling you to monitor and optimize the performance of your LLM applications:

```python
import os

from haystack import Pipeline
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

import openlit         # Import the OpenLIT Library

openlit.init()         # Initialize OpenLIT for monitoring

os.environ["OPENAI_API_KEY"] = "Your OpenAI API Key"

fetcher = LinkContentFetcher()
converter = HTMLToDocument()
prompt_template = [
    ChatMessage.from_user(
      """
      According to the contents of this website:
      {% for document in documents %}
        {{document.content}}
      {% endfor %}
      Answer the given question: {{query}}
      Answer:
      """
    )
]

prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables="*")
llm = OpenAIChatGenerator()

pipeline = Pipeline()
pipeline.add_component("fetcher", fetcher)
pipeline.add_component("converter", converter)
pipeline.add_component("prompt", prompt_builder)
pipeline.add_component("llm", llm)

pipeline.connect("fetcher.streams", "converter.sources")
pipeline.connect("converter.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm")

result = pipeline.run({"fetcher": {"urls": ["https://haystack.deepset.ai/overview/quick-start"]},
              "prompt": {"query": "Which components do I need for a RAG pipeline?"}})

print(result["llm"]["replies"][0].text)

```

## License

`OpenLIT` is distributed under the terms of the [Apache-2.0](https://github.com/openlit/openlit/blob/main/LICENSE) license.
