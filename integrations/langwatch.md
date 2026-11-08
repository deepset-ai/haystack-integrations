---
layout: integration
name: LangWatch
description: Trace your Haystack pipelines and agents with LangWatch
authors:
    - name: LangWatch
      socials:
        github: langwatch
        linkedin: https://www.linkedin.com/company/langwatch/
pypi: https://pypi.org/project/langwatch/
repo: https://github.com/langwatch/langwatch
type: Monitoring Tool
report_issue: https://github.com/langwatch/langwatch/issues
logo: /logos/langwatch.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[LangWatch](https://langwatch.ai) is an open source LLM observability platform. LangWatch integrates with Haystack through OpenInference instrumentation to capture traces from your Haystack pipelines and components, including:

- Pipeline operations
- Component executions
- Model interactions

You can learn more about the Haystack and LangWatch integration in LangWatch's [Haystack integration guide](https://langwatch.ai/docs/integration/python/integrations/haystack).

## Installation

To use the LangWatch integration with Haystack, install the `langwatch` package together with the OpenInference Haystack instrumentation:

```bash
pip install langwatch openinference-instrumentation-haystack haystack-ai
```

## Usage

To use LangWatch, you will need to:

1. Set your LangWatch API key in the `LANGWATCH_API_KEY` environment variable
2. Pass `HaystackInstrumentor` to `langwatch.setup()`

An example agent traced with LangWatch is shown below:

```python
import os
import langwatch

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from openinference.instrumentation.haystack import HaystackInstrumentor

langwatch.setup(instrumentors=[HaystackInstrumentor()])

basic_agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-5-mini"),
    system_prompt="You are a helpful web agent.",
    tools=[],
)

result = basic_agent.run(messages=[ChatMessage.from_user("Tell me a joke")])

print(result["last_message"].text)
```

The `HaystackInstrumentor` automatically captures Haystack pipeline operations, component executions, and model interactions. Use `@langwatch.trace()` to create a parent trace under which Haystack operations will be nested.

## License

LangWatch is open source and is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
