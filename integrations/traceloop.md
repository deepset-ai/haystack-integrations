---
layout: integration
name: Traceloop
description: Evaluate and monitor the quality of your LLM apps and agents
authors:
  - name: Traceloop Team
    socials:
      github: traceloop
      twitter: traceloopdev
pypi: https://pypi.org/project/traceloop-sdk/
repo: https://github.com/traceloop/openllmetry
type: Monitoring Tool
report_issue: https://github.com/traceloop/openllmetry/issues
logo: /logos/traceloop.png
version: Haystack 2.0
toc: true
---

- [OpenLLMetry](#openllmetry)
  - [Installation](#installation)
  - [Example](#example)
  - [About Traceloop](#about-traceloop)

# OpenLLMetry

OpenLLMetry is an open-source Python package built and maintained by Traceloop that instruments your Haystack-based applications with OpenTelemetry. This gives you full visibility to your LLM app, right in your existing observability stack. You can also connect this to Traceloop to get quality evaluation metrics and LLM-specific capabilities like Prompt Playground.

![Traceloop screenshot](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/traceloop-monitoring.png)

More info on the [documentation](https://traceloop.com/docs/python-sdk).

## Installation

```
pip install traceloop-sdk
```

## Example

Basic integration is as simple as adding one line to your code:

```python
Traceloop.init(app_name="your_app_name")
```

When you run your code, you'll get a link to the Traceloop UI where you can see your app's traces.
If you want to connect to a different observability platform, [follow the guide for exporting your traces](https://traceloop.com/docs/python-sdk/exporting).

### Use a Traceloop API Key

If you have an account with Traceloop and would like to see your traces on your account dashboard:

- Create an API key on Traceloop
- Export the API key in an environment variable called `TRACELOOP_API_KEY`

### Trace Haystack Pipelines

Once you've initialized a Traceloop app, any Haystack pipeline that you run in the same environment will get logged in the dashboard provided by the generated Traceloop URL.
For example, below is a simple Haystack pipeline and its traceloop logs. It requires an OPENAI_API_KEY to be set. 

```python
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack import Pipeline

from traceloop.sdk import Traceloop

Traceloop.init(app_name="haystack_app")

prompt_builder = ChatPromptBuilder()
llm = OpenAIChatGenerator()

location = "Berlin"
messages = [ChatMessage.from_system("Always respond in German even if some input data is in other languages."),
            ChatMessage.from_user("Tell me about {{location}}")]

pipe = Pipeline()
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", llm)
pipe.connect("prompt_builder.prompt", "llm.messages")

pipe.run(data={"prompt_builder": {"template_variables":{"location": location}, "template": messages}})
```
```bash
>> {'llm': {'replies': [ChatMessage(content='Berlin ist die Hauptstadt Deutschlands und die größte Stadt des Landes.
>> Es ist eine lebhafte Metropole, die für ihre Geschichte, Kultur und einzigartigen Sehenswürdigkeiten bekannt ist.
>> Berlin bietet eine vielfältige Kulturszene, beeindruckende architektonische Meisterwerke wie den Berliner Dom
>> und das Brandenburger Tor, sowie weltberühmte Museen wie das Pergamonmuseum. Die Stadt hat auch eine pulsierende
>> Clubszene und ist für ihr aufregendes Nachtleben berühmt. Berlin ist ein Schmelztiegel verschiedener Kulturen und
>> zieht jedes Jahr Millionen von Touristen an.', role=<ChatRole.ASSISTANT: 'assistant'>, name=None,
>> metadata={'model': 'gpt-4o-mini', 'index': 0, 'finish_reason': 'stop', 'usage': {'prompt_tokens': 32,
>> 'completion_tokens': 153, 'total_tokens': 185}})]}}
```

<img width="1798" alt="image" src="https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/traceloop-tracing.png">

## About Traceloop

Traceloop is a platform for monitoring, evaluating and debugging LLM apps and agents. Deploy changes with confidence and get insights into your LLM executions.

### Key features

- Manage your prompts in a single place with version support, gradual rollout, A/B testing, and more.
- Evaluate your prompts and models quality with auto-generated test sets.
- Monitor your LLM app's performance and get alerts when it's not behaving as expected.
