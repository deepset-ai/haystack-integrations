---
layout: integration
name: Monster API
description: Use MonsterAPI with HeyStack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/haystack-ai
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: [[https://github.com/yout-repo/issues](https://github.com/deepset-ai/haystack/issues)](https://github.com/deepset-ai/haystack/issues)
logo: /logos/monsterapi.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
The MonsterAPI integration allows you to leverage the powerful language models provided by MonsterAPI within the Haystack framework. This integration enables text generation using Monster AI generative models, designed to work seamlessly with the MonsterAPI Chat Completion endpoint. It supports streaming responses and customizability through various parameters.

For more information, visit the [MonsterAPI documentation](https://developer.monsterapi.ai/).

## Installation

```bash
pip install haystack-ai
```

## Usage
### Components
This integration introduces the `MonsterChatGeneraor` component:

- **MonsterChatGeneraor**: Enables the use of MonsterAPI's language models within a Haystack pipeline.

### Use MonsterAPI with Haystack

Here's an example of how to use the `MonsterChatGeneraor` integration:

```python
from haystack import Pipeline
from haystack.components.generators.chat import MonsterChatGeneraor
from haystack.dataclasses import ChatMessage

# Create chat messages
messages = [ChatMessage.from_user("What's Natural Language Processing?")]

# Initialize the MonsterChatGeneraor with your API key
client = MonsterChatGeneraor(api_key="YOUR_MONSTER_API_KEY")

# Run the client to get responses
response = client.run(messages)
print(response)

# Example output:
# {'replies': [ChatMessage(content='Natural Language Processing (NLP) is a branch of artificial intelligence
# that focuses on enabling computers to understand, interpret, and generate human language in a way that is
# meaningful and useful.', role=<ChatRole.ASSISTANT: 'assistant'>, name=None,
# meta={'model': 'meta-llama/Meta-Llama-3-8B-Instruct', 'index': 0, 'finish_reason': 'stop',
# 'usage': {'prompt_tokens': 15, 'completion_tokens': 36, 'total_tokens': 51}})]}
```

Replace `YOUR_MONSTER_API_KEY` with your actual MonsterAPI key.
