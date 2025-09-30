---
layout: integration
name: Anthropic
description: Use Anthropic Models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/anthropic-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/anthropic
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/anthropic.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

This integration supports Anthropic Claude models such as Claude Haiku 3.5, Claude Sonnet 3.7, and Claude Sonnet 4.5 through Anthropic’s inference infrastructure. For a complete list of available models, check out [the Anthropic Claude documentation](https://docs.claude.com/en/docs/about-claude/models/overview).

You can use Anthropic models with [`AnthropicGenerator`](https://docs.haystack.deepset.ai/docs/anthropicgenerator) and [`AnthropicChatGenerator`](https://docs.haystack.deepset.ai/docs/anthropicchatgenerator).

## Installation

```bash
pip install anthropic-haystack
```

## Usage

Based on your use case, you can choose between [`AnthropicGenerator`](https://docs.haystack.deepset.ai/docs/anthropicgenerator) or [`AnthropicChatGenerator`](https://docs.haystack.deepset.ai/docs/anthropicchatgenerator) to work with Anthropic models. To learn more about the difference, visit the [Generators vs Chat Generators](https://docs.haystack.deepset.ai/docs/generators-vs-chat-generators) guide.  
Before using, make sure to set the `ANTHROPIC_API_KEY` environment variable.

### Using `AnthropicChatGenerator`

Below is an example RAG Pipeline where we answer a predefined question using the contents of the URL pointing to the Anthropic prompt engineering guide. We fetch the URL's contents and generate an answer with the `AnthropicChatGenerator`.

```python
# To run this example, you need to set the `ANTHROPIC_API_KEY` environment variable.
# !pip install trafilatura

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator

messages = [
    ChatMessage.from_system("You are a prompt expert who answers questions based on the given documents."),
    ChatMessage.from_user(
        "Here are the documents:\n"
        "{% for d in documents %} \n"
        "    {{d.content}} \n"
        "{% endfor %}"
        "\nAnswer: {{query}}"
    ),
]

rag_pipeline = Pipeline()
rag_pipeline.add_component("fetcher", LinkContentFetcher())
rag_pipeline.add_component("converter", HTMLToDocument())
rag_pipeline.add_component("prompt_builder", ChatPromptBuilder(variables=["documents"]))
rag_pipeline.add_component(
    "llm",
    AnthropicChatGenerator(
        api_key=Secret.from_env_var("ANTHROPIC_API_KEY"),
        streaming_callback=print_streaming_chunk,
    ),
)


rag_pipeline.connect("fetcher", "converter")
rag_pipeline.connect("converter", "prompt_builder")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "When should we use prompt engineering and when should we fine-tune?"
rag_pipeline.run(
    data={
        "fetcher": {"urls": ["https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview"]},
        "prompt_builder": {"template_variables": {"query": question}, "template": messages},
    }
)
```

### Using `AnthropicGenerator`

Below is an example of using `AnthropicGenerator`:

```python
from haystack_integrations.components.generators.anthropic import AnthropicGenerator

client = AnthropicGenerator()
response = client.run("What's Natural Language Processing? Be brief.")
print(response)

>>{'replies': ['Natural language processing (NLP) is a branch of artificial intelligence focused on enabling
>>computers to understand, interpret, and manipulate human language. The goal of NLP is to read, decipher,
>> understand, and make sense of the human languages in a manner that is valuable.'], 'meta': {'model':
>> 'claude-2.1', 'index': 0, 'finish_reason': 'end_turn', 'usage': {'input_tokens': 18, 'output_tokens': 58}}}
```
