---
layout: integration
name: Hetzner
description: Use the Hetzner Inference API for open-weight LLMs hosted in Europe.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/hetzner-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/hetzner
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/hetzner.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The [Hetzner Inference API](https://docs.hetzner.com/general/company-and-policy/experiments/inference/) serves open-weight LLMs from Hetzner's European data centers behind an OpenAI-compatible REST API. Once installed, you get access to the `HetznerChatGenerator`, which lets you call any of the models Hetzner serves.

At the time of writing, two models are available, both with a 262,144-token context window and both accepting images alongside text:

- `Qwen/Qwen3.6-35B-A3B-FP8` (mixture-of-experts, 35B total / 3B active) — the default
- `Qwen3.8-27B` (dense)

The selection changes while the service is in its experimental phase, and the `/v1/models` endpoint of the API is definitive. To see the current list:

```bash
curl -s https://inference.hetzner.com/api/v1/models -H "Authorization: Bearer $HETZNER_API_KEY"
```

In order to follow along with this guide, you'll need a Hetzner API token for the Inference API. Add it as an environment variable, `HETZNER_API_KEY`.

Note that the Inference API is offered as an experiment: it is free of charge while it keeps that status, its availability is not guaranteed, and it is rate-limited per API key (4M input tokens, 100k output tokens and 10 requests per 60 seconds).

## Installation

```bash
pip install hetzner-haystack
```

## Usage

You can use `HetznerChatGenerator` as a standalone component, within a [pipeline](https://docs.haystack.deepset.ai/docs/pipelines) or with the [Agent component](https://docs.haystack.deepset.ai/docs/agent).

Here's an example of using it as a standalone component:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.hetzner import HetznerChatGenerator

os.environ["HETZNER_API_KEY"] = "YOUR_HETZNER_API_KEY"

client = HetznerChatGenerator()  # defaults to "Qwen/Qwen3.6-35B-A3B-FP8"
response = client.run(
    [ChatMessage.from_user("What are Agentic Pipelines? Be brief.")]
)
print(response["replies"][0].text)
```

`HetznerChatGenerator` also supports streaming responses if you pass a streaming callback:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.hetzner import HetznerChatGenerator

os.environ["HETZNER_API_KEY"] = "YOUR_HETZNER_API_KEY"

def show(chunk):                              # simple streaming callback
    print(chunk.content, end="", flush=True)

client = HetznerChatGenerator(
    model="Qwen3.8-27B",
    streaming_callback=show,
    generation_kwargs={"max_tokens": 100, "temperature": 0.7, "top_p": 0.9},
)

client.run([ChatMessage.from_user("Summarize RAG in two lines.")])
```

The served models are multimodal, so you can pass images along with your prompt:

```python
import os
from haystack.dataclasses import ChatMessage, ImageContent
from haystack_integrations.components.generators.hetzner import HetznerChatGenerator

os.environ["HETZNER_API_KEY"] = "YOUR_HETZNER_API_KEY"

image = ImageContent.from_url(
    "https://cdn.hetzner.de/cdn/public/Uploads/Finnland_Luftaufnahme-v2.jpg"
)

client = HetznerChatGenerator()
response = client.run(
    [ChatMessage.from_user(content_parts=["Describe this image in one sentence.", image])]
)
print(response["replies"][0].text)
```

And here's how to use it in a pipeline:

```python
import os
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.hetzner import HetznerChatGenerator

os.environ["HETZNER_API_KEY"] = "YOUR_HETZNER_API_KEY"

pipe = Pipeline()
pipe.add_component("builder", ChatPromptBuilder())
pipe.add_component("llm", HetznerChatGenerator())
pipe.connect("builder.prompt", "llm.messages")

messages = [
    ChatMessage.from_system("Give brief answers."),
    ChatMessage.from_user("Tell me about {{city}}"),
]

response = pipe.run(
    data={"builder": {"template": messages, "template_variables": {"city": "Nuremberg"}}},
)
print(response["llm"]["replies"][0].text)
```

### License

`hetzner-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
