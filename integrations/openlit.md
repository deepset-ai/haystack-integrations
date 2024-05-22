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
[OpenLIT](https://openlit.io/) is an OpenTelemetry-native GenAI and LLM Application Observability tool. 
It simplifies the integration of observability into GenAI and LLM using Haystack with just a single line of code.

OpenLIT allows you to monitor detailed information about LLM operations, such as API calls, content, prompts, costs, and more. This enables you to gain insights into your models’ performance, identify improvement areas, and reduce costs.

Check out the [Official documentation](https://docs.openlit.io/) for more information.

### ⚡ Features
- **OpenTelemetry-native**: Native support ensures that integrating OpenLIT into your projects feels more like a natural extension rather than an additional layer of complexity.
- **Granular Usage Insights of your LLM Applications**: Assess your LLM's performance and costs with fine-grained control, breaking down metrics by environment (such as staging or production) or application, to optimize for efficiency and scalability.
- **Vendor-Neutral SDKs**: In the spirit of OpenTelemetry, OpenLIT's SDKs are agnostic of the backend vendors. This means you can confidently use OpenLIT with various telemetry backends, like Prometheus + Jaeeger or even platforms like Grafana Cloud, without worrying about compatibility issues.

## Installation

```bash
pip install openlit
```

## Usage
Adding Monitoring to your application is as simple as adding one line to your code:

```python
openlit.init()
```

When you execute your code, traces and metrics will appear directly in your console, which is ideal for immediate debugging. 

However, to store and track this data over time, you should send these traces and metrics to OpenLIT. For guidance on how to do this, [refer to this quickstart guide](https://docs.openlit.io/latest/quickstart). 

If you wish to integrate LLM Monitoring data with your existing Observability Stack, such as Grafana, explore [OpenLIT connections](https://docs.openlit.io/latest/connections/intro) to get started.

### Example: Trace Haystack Pipelines

The following code snippet illustrates how to utilize OpenLIT to trace a Haystack pipeline, enabling you to monitor and optimize the performance of your LLM applications:

```python
import os
from haystack import Pipeline, PredefinedPipeline
import urllib.request
import openlit         # Import the OpenLIT Library

openlit.init()         # Initialize OpenLIT for monitoring

os.environ["OPENAI_API_KEY"] = "Your OpenAI API Key"
urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/7785/pg7785.txt", "davinci.txt")  

indexing_pipeline =  Pipeline.from_template(PredefinedPipeline.INDEXING)
indexing_pipeline.run(data={"sources": ["davinci.txt"]})

rag_pipeline =  Pipeline.from_template(PredefinedPipeline.RAG)

query = "How old was he when he died?"
result = rag_pipeline.run(data={"prompt_builder": {"query":query}, "text_embedder": {"text": query}})
print(result["llm"]["replies"][0])
```

## License

`OpenLIT` is distributed under the terms of the [Apache-2.0](https://github.com/openlit/openlit/blob/main/LICENSE) license.
