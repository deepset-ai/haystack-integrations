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
type: Monitoring
report_issue: https://github.com/traceloop/openllmetry/issues
logo: /logos/traceloop.png
---

# OpenLLMetry

OpenLLMetry is an open-source Python package built and maintained by Traceloop that instruments your Haystack-based applications with OpenTelemetry. This gives you full visibility to your LLM app, right in your existing observability stack. You can also connect this to Traceloop to get quality evaluation metrics and LLM-specific capabilities like Prompt Playground.

![Traceloop screenshot](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/traceloop-monitoring.png)

More info on the [documentation](https://traceloop.com/docs/python-sdk).

# Installation

```
pip install traceloop-sdk
```

# Integration

Basic integration is as simple as adding one line to your code:

```python
Traceloop.init(app_name="your_app_name")
```

When you run your code, you'll get a link to the Traceloop UI where you can see your app's traces.
If you want to connect to a different observability platform, [follow the guide for exporting your traces](https://traceloop.com/docs/python-sdk/exporting).

## Use a Traceloop API Key

If you have an account with Traceloop and would like to see your traces on your account dashboard:

- Create an API key on Traceloop
- Export the API key in an environment variable called `TRACELOOP_API_KEY`

## Trace Haystack Pipelines

Once you've initialized a Traceloop app, any Haystack pipeline that you run in the same environment will get logged in the dashboard provided by the generated Traceloop URL.
For example, below is a simple Haystack pipeline and its traceloop logs:

```python
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser
from haystack.pipelines import Pipeline
from traceloop.sdk import Traceloop

Traceloop.init(app_name="haystack_app")

prompt = PromptTemplate(
    prompt="Tell me a joke about {query}\n",
    output_parser=AnswerParser(),
)

prompt_node = PromptNode(
    model_name_or_path="gpt-4",
    api_key=api_key,
    default_prompt_template=prompt,
)

pipeline = Pipeline()
pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Query"])
result = pipeline.run("Haystack")
```

<img width="1798" alt="image" src="https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/traceloop-tracing.png">

## About Traceloop

Traceloop is a platform for monitoring, evaluating and debugging LLM apps and agents. Deploy changes with confidence and get insights into your LLM executions.

### Key features

- Manage your prompts in a single place with version support, gradual rollout, A/B testing, and more.
- Evaluate your prompts and models quality with auto-generated test sets.
- Monitor your LLM app's performance and get alerts when it's not behaving as expected.
