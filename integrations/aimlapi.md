---
layout: integration
name: AIMLAPI
description: Call AIMLAPI's OpenAI-compatible chat models from Haystack pipelines and agents.
authors:
    - name: AI/ML API
      socials:
        github: aimlapi
        twitter: aimlapi
        linkedin: https://www.linkedin.com/company/aimlapi/
pypi: https://pypi.org/project/aimlapi-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/aimlapi
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aimlapi.svg
type: Model Provider
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[`AIMLAPIChatGenerator`](https://docs.haystack.deepset.ai/docs/aimlapichatgenerator) lets you call any of the models that AIMLAPI serves behind an OpenAI-compatible `/chat/completions` endpoint. AIMLAPI routes the request to the requested provider while maintaining the familiar OpenAI payload schema, so you can reuse existing Haystack pipelines or agents with minimal changes.

AIMLAPI extends the base OpenAI integration with:

- **Direct AIMLAPI routing** – requests are sent to `https://api.aimlapi.com/v1` and can target any model AIMLAPI exposes by passing the `model` name.
- **Tool calling support** – pass Haystack [`Tool`](https://docs.haystack.deepset.ai/reference/tool) objects to the generator to enable function calling workflows.
- **Streaming callbacks** – supply `streaming_callback` to receive tokens as they are generated.
- **Flexible extras** – forward provider-specific parameters by using `generation_kwargs` and `extra_body`.

To follow along with the example below, set the `AIMLAPI_API_KEY` environment variable to your API token.

## Installation

```bash
pip install aimlapi-haystack
```

## Usage

You can use `AIMLAPIChatGenerator` on its own or as part of a larger pipeline. The snippet below shows a minimal chat interaction that asks the model a question and prints the assistant reply.

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.aimlapi import AIMLAPIChatGenerator

os.environ["AIMLAPI_API_KEY"] = "YOUR_AIMLAPI_KEY"

chat = AIMLAPIChatGenerator(model="openai/gpt-4o")
result = chat.run([
    ChatMessage.from_user("What's the capital of France?")
])

print(result["replies"][0].text)
```

If you want the model to call tools, pass the tool definitions to the generator. AIMLAPI will return tool call information that you can route to the relevant function and then send back to the model. The example in [`examples/aimlapi_with_tools_example.py`](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/aimlapi/examples/aimlapi_with_tools_example.py) demonstrates the full round-trip.

## License

This integration is distributed under the [Apache 2.0 License](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/aimlapi/LICENSE.txt).