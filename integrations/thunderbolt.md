---
layout: integration
name: Thunderbolt
description: Use Thunderbolt as a cross-platform AI client for your Haystack pipelines through Hayhooks
authors:
  - name: Thunderbird
    socials:
      github: thunderbird
repo: https://github.com/thunderbird/thunderbolt
type: UI
report_issue: https://github.com/thunderbird/thunderbolt/issues
logo: /logos/thunderbolt.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [License](#license)

## Overview

[Thunderbolt](https://github.com/thunderbird/thunderbolt) is an open-source, cross-platform AI client developed by MZLA Technologies (Thunderbird). It runs on web, iOS, Android, Mac, Linux, and Windows, and works with any OpenAI-compatible model endpoint — including self-hosted ones.

By exposing your Haystack pipeline through [Hayhooks](https://github.com/deepset-ai/hayhooks) as an OpenAI-compatible endpoint, you can connect Thunderbolt to your pipeline and interact with it from any device — without building a frontend yourself.

Thunderbolt is designed for enterprise on-prem deployments but can be self-hosted locally for development and testing.

## Setup

### 1. Expose your Haystack pipeline with Hayhooks

Install Hayhooks:

```bash
pip install hayhooks
```

Create a pipeline wrapper that implements `run_chat_completion`:

```python
# pipelines/my_rag/pipeline_wrapper.py
from typing import Generator

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from hayhooks import BasePipelineWrapper, streaming_generator


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        self.system_message = ChatMessage.from_system("You are a helpful assistant.")
        prompt_builder = ChatPromptBuilder()
        llm = OpenAIChatGenerator(model="gpt-4o-mini")

        self.pipeline = Pipeline()
        self.pipeline.add_component("prompt_builder", prompt_builder)
        self.pipeline.add_component("llm", llm)
        self.pipeline.connect("prompt_builder.prompt", "llm.messages")

    def run_chat_completion(self, model: str, messages: list[dict], body: dict) -> Generator:
        chat_messages = [self.system_message] + [
            ChatMessage.from_openai_dict_format(msg) for msg in messages
        ]
        return streaming_generator(
            pipeline=self.pipeline,
            pipeline_run_args={"prompt_builder": {"template": chat_messages}},
        )
```

Start Hayhooks:

```bash
hayhooks run --pipelines-dir ./pipelines
```

This exposes your pipeline at `http://localhost:1416/v1` as an OpenAI-compatible endpoint. See [Hayhooks OpenAI compatibility docs](https://deepset-ai.github.io/hayhooks/features/openai-compatibility) for details.

### 2. Deploy Thunderbolt

Follow the [Thunderbolt deployment guide](https://github.com/thunderbird/thunderbolt/blob/main/deploy/README.md) to self-host Thunderbolt with Docker Compose or Kubernetes, or run it locally for development. See the [development guide](https://github.com/thunderbird/thunderbolt/blob/main/docs/development.md) to get started quickly.

## Usage

Once Hayhooks is running and Thunderbolt is deployed:

1. Open Thunderbolt and go to **Settings → Model Providers**.
2. Add a new provider with a custom **OpenAI-compatible** base URL pointing to your Hayhooks server (e.g. `http://localhost:1416/v1`).
3. Select your Haystack pipeline as the model.
4. Start chatting — your messages are routed through Hayhooks to your Haystack pipeline.

This gives you a polished, cross-platform chat interface backed by whatever Haystack pipeline you choose — RAG, agents, or a custom workflow.

## License

Thunderbolt is licensed under the [Mozilla Public License 2.0](https://github.com/thunderbird/thunderbolt/blob/main/LICENSE).
Hayhooks is licensed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
