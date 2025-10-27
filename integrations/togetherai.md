---
layout: integration
name: TogetherAI
description: Use the Together API for text generation models.
authors:
    - name: deepset 
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/togetherai-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/togetherai
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/togetherai.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

Once installed you will have access to [TogetherAIGenerator] and [TogetherAIChatGenerator] that allow
you to call any LLMs available on [TogetherAI](https://www.together.ai/), including:

- OpenAI variants such as `oopenai/gpt-oss-120B`
- deepseek-ai's `deepseek-ai/DeepSeek-R1`
- Other open-source models (Llama 2, Mixtral, etc.)

For more information on models available via the TogetherAI API, see [the TogetherAI docs](https://www.together.ai/models).

In order to follow along with this guide, you'll need a TogetherAI API key. Add it as an environment variable, `TOGETHER_API_KEY`.

## Installation

```bash
pip install togetherai-haystack
```

## Usage
You can use [TogetherAIChatGenerator](https://docs.haystack.deepset.ai/docs/togetheraichatgenerator) as standalone, within a [pipeline](https://docs.haystack.deepset.ai/docs/pipelines) or with the [Agent component](https://docs.haystack.deepset.ai/docs/agent).

Here's an example of using it as a standalone component:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.togetherai import TogetherAIChatGenerator

os.environ["TOGETHER_API_KEY"] = "YOUR_TOGETHER_API_KEY"

client = TogetherAIChatGenerator() # defaults to "meta-llama/Llama-3.3-70B-Instruct-Turbo",
response = client.run(
    [ChatMessage.from_user("What are Agentic Pipelines? Be brief.")]
)
print(response["replies"])

```
```bash
{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='The capital of Vietnam is Hanoi.')], _name=None, _meta={'model': 'meta-llama/Llama-3.3-70B-Instruct-Turbo', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 8, 'prompt_tokens': 13, 'total_tokens': 21, 'completion_tokens_details': CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=0, rejected_prediction_tokens=None), 'prompt_tokens_details': PromptTokensDetails(audio_tokens=None, cached_tokens=0)}})]}
```
`TogetherAIChatGenerator` also support streaming responses if you pass a streaming callback:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.togetherai import TogetherAIChatGenerator

os.environ["TOGETHER_API_KEY"] = "YOUR_TOGETHER_API_KEY"

def show(chunk):                              # simple streaming callback
    print(chunk.content, end="", flush=True)

client = TogetherAIChatGenerator(
    model="deepseek-ai/DeepSeek-R1",
    streaming_callback=show,
    generation_kwargs={"max_tokens": 100, "temperature": 0.7, "top_p": 0.9},
)

response = client.run([ChatMessage.from_user("Summarize RAG in two lines.")])

print (response)

```

### License

`togetherai-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
