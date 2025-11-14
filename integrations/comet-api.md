---
layout: integration
name: Comet API
description: Use the Comet API for text generation models.
authors:
    - name: deepset 
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
    - name: Gary Badwal
      socials:
        website: garybadwal.com
        github: garybadwal
        twitter: garybadwal_
        linkedin: https://www.linkedin.com/in/garybadwal/
pypi: https://pypi.org/project/cometapi-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/cometapi
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/cometapi.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`CometAPIChatGenerator` lets you call any LLMs available on [Comet API](https://cometapi.com), including:

- OpenAI variants such as `gpt-5`
- Anthropic’s `claude-4.5-haiku`
- Community-hosted open-source models (Llama 2, Mixtral, etc.)

For more information on models available via the Comet API API, see [the Comet API docs](https://www.cometapi.com/model/).


In order to follow along with this guide, you'll need a Comet API key. Add it as an environment variable, `COMET_API_KEY`.

## Installation

```bash
pip install cometapi-haystack
```

## Usage
You can use `CometAPIChatGenerator` as standalone, within a [pipeline](https://docs.haystack.deepset.ai/docs/pipelines) or with the [Agent component](https://docs.haystack.deepset.ai/docs/agent).

Here's an example of using it as a standalone component:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.cometapi import CometAPIChatGenerator

os.environ["COMET_API_KEY"] = "YOUR_COMET_API_KEY"

client = CometAPIChatGenerator() # defaults to gpt-4o-mini
response = client.run(
    [ChatMessage.from_user("What are Agentic Pipelines? Be brief.")]
)
print(response["replies"])

```
```bash
{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='Agentic Pipelines refer to processes or frameworks that enable individuals or groups to take proactive control over their learning, decision-making, or actions in a systematic way. They emphasize agency, allowing participants to navigate pathways that reflect their interests, goals, and capabilities, often leveraging technology and resources to facilitate this empowerment. In various contexts, such as education or organizational development, Agentic Pipelines can foster greater engagement, autonomy, and outcomes.')], _name=None, _meta={'model': 'gpt-4o-mini-2024-07-18', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 87, 'prompt_tokens': 17, 'total_tokens': 104, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}})]}
```
`CometAPIChatGenerator` also support streaming responses if you pass a streaming callback:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.cometapi import CometAPIChatGenerator

os.environ["COMET_API_KEY"] = "YOUR_COMET_API_KEY"

def show(chunk):                              # simple streaming callback
    print(chunk.content, end="", flush=True)

client = CometAPIChatGenerator(
    model="grok-3-mini",
    streaming_callback=show,
)

response = client.run([ChatMessage.from_user("Summarize RAG in two lines.")])

print(response)

```

### License

`cometapi-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
