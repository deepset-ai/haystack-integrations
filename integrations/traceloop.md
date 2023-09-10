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

OpenLLMetry is an open-source Python package built and maintained by Traceloop that instruments your haystack-based applications with OpenTelemetry. This gives you full visibility to your LLM app, right in your existing observability stack. You can also connect this to Traceloop to get quality evaluation metrics and LLM-specific capabilities like Prompt Playground.

![Traceloop screenshot](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/traceloop-haystack.png)

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

## About Traceloop

Traceloop is a platform for monitoring, evaluating and debugging LLM apps and agents. Deploy changes with confidence and get insights into your LLM executions.

### Key features

- Manage your prompts in a single place with version support, gradual rollout, A/B testing, and more.
- Evaluate your prompts and models quality with auto-generated test sets.
- Monitor your LLM app's performance and get alerts when it's not behaving as expected.
