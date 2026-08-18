---
layout: integration
name: HPC-AI
description: Use HPC-AI's OpenAI-compatible API for chat generation models in Haystack.
authors:
    - name: HPC-AI
      socials:
        website: https://www.hpc-ai.com/
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/hpc-ai-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/hpc_ai
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/hpc_ai.svg
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

[HPC-AI](https://www.hpc-ai.com/) provides an OpenAI-compatible chat completion API that you can use from Haystack through `HPCAIChatGenerator`.

This integration is built on top of Haystack's OpenAI-compatible chat generation flow and currently officially supports these models:

- `minimax/minimax-m2.5`
- `moonshotai/kimi-k2.5`

Requests are sent to the default HPC-AI base URL `https://api.hpc-ai.com/inference/v1`.

To follow along with the examples below, set:

- `HPC_AI_API_KEY`
- `HPC_AI_BASE_URL` if you need to override the default endpoint

You can find the component reference in the Haystack docs here:

- [`HPCAIChatGenerator`](https://docs.haystack.deepset.ai/docs/hpcaichatgenerator)

## Installation

```bash
pip install hpc-ai-haystack
```

## Usage

You can use `HPCAIChatGenerator` on its own, inside a [pipeline](https://docs.haystack.deepset.ai/docs/pipelines), or together with Haystack agents.

Here's a minimal standalone example:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.hpc_ai import HPCAIChatGenerator

os.environ["HPC_AI_API_KEY"] = "YOUR_HPC_AI_API_KEY"

chat = HPCAIChatGenerator(model="minimax/minimax-m2.5")
result = chat.run([
    ChatMessage.from_user("What's the capital of France?")
])

print(result["replies"][0].text)
```

You can also use the second officially supported model:

```python
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.hpc_ai import HPCAIChatGenerator

chat = HPCAIChatGenerator(model="moonshotai/kimi-k2.5")
result = chat.run([
    ChatMessage.from_user("Summarize RAG in two lines.")
])

print(result["replies"][0].text)
```

The integration also supports:

- Streaming via `streaming_callback`
- Tool calling through the `tools` parameter
- Structured outputs via `generation_kwargs["response_format"]`

For a full tool-calling example, see:

- [`hpc_ai_with_tools_example.py`](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/hpc_ai/examples/hpc_ai_with_tools_example.py)

## License

This integration is distributed under the [Apache 2.0 License](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/hpc_ai/LICENSE.txt).
