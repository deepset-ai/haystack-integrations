---
layout: integration
name: Context AI
description: A component to log conversations for analytics by Context.ai - built for Haystack 2.0.
authors:
    - name: Alec Barber
      socials:
        github: BarberAlec
        linkedin: https://www.linkedin.com/in/alec-barber/
    - name: Alex Gamble
      socials:
        github: agamble
        linkedin: https://www.linkedin.com/in/alex-gamble-13682086/
    - name: Henry Scott-Green
      socials:
        linkedin: https://www.linkedin.com/in/hcscottgreen/
    - name: Amishapriya Singh
      socials:
        github: amisha29sh
        linkedin: https://www.linkedin.com/in/amisha29/
pypi: https://pypi.org/project/context-haystack/
repo: https://github.com/contextco/context-haystack
type: Monitoring Tool
report_issue: https://github.com/contextco/context-haystack/issues
logo: /logos/context.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
[Context.ai](https://context.ai)  is an evaluations and analytics tool for products powered by LLMs.

With Context.ai, you can understand how your users are interacting with natural language interfaces. This helps you know where your customers are having great experiences, but also proactively detect potential areas of improvement. You can test the performance impact of changes before you ship them to production with evaluations, and can identify where inappropriate conversations taking place.

Login to [Context Dashboard](https://with.context.ai) to create a token and see your analytics.

## Installation

```bash
pip install --upgrade context-haystack
```

## Usage
### Components
The `ContextAIAnalytics` component allows you to seamlessly integrate with Context.ai, uploading your messages to the Context AI platform.

When running your pipeline you must include `thread_id` in the parameters where each unique `thread_id` identifies a conversation. You can optionally include `metadata` with `user_id` and `model` reserved for special analytics. 

Use an instance of the `ContextAIAnalytics` component at each stage of your pipeline where you wish to log a message. In the example below the output of the `prompt_builder` and the `llm` components are captured.

### Example
```python
import uuid
import os

from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders import ChatPromptBuilder
from haystack import Pipeline
from haystack.dataclasses import ChatMessage

from context_haystack.context import ContextAIAnalytics


model = "gpt-3.5-turbo"
os.environ["GETCONTEXT_TOKEN"] = "GETCONTEXT_TOKEN"
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

prompt_builder = ChatPromptBuilder()
llm = OpenAIChatGenerator(model=model)
prompt_analytics = ContextAIAnalytics()
assistant_analytics = ContextAIAnalytics()

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", llm)
pipe.add_component("prompt_analytics", prompt_analytics)
pipe.add_component("assistant_analytics", assistant_analytics)

pipe.connect("prompt_builder.prompt", "llm.messages")
pipe.connect("prompt_builder.prompt", "prompt_analytics")
pipe.connect("llm.replies", "assistant_analytics")

# thread_id is unique to each conversation
context_parameters = {"thread_id": uuid.uuid4(), "metadata": {"model": model, "user_id": "1234"}}
location = "Berlin"
messages = [ChatMessage.from_system("Always respond in German even if some input data is in other languages."),
            ChatMessage.from_user("Tell me about {{location}}")]

response = pipe.run(
    data={
        "prompt_builder": {"template_variables":{"location": location}, "prompt_source": messages},
        "prompt_analytics": context_parameters,
        "assistant_analytics": context_parameters,
    }
)

print(response)
```

## License
`context-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
