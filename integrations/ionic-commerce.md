---
layout: integration
name: Ionic Commerce tool for Haystack
description: Ionic is a plug and play ecommerce marketplace for AI Assistants.
authors:
    - name: Ionic Commerce
      socials:
        github: ioniccommerce
        twitter: ioniccommerce
        linkedin: ionic-commerce
pypi: https://pypi.org/project/ionic-haystack/
repo: https://github.com/ioniccommerce/ionic_haystack
type: Agent Tool
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/ionic.png
---


# **Table of Contents**
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)


## Installation

```bash
pip install ionic-haystack
```

## Usage
Get started quickly using Ionic Commerce with Haystack by creating an IonicShoppingTool and adding it to your agent's tools.
```python
import os
from haystack.agents import Tool
from haystack.agents.conversational import ConversationalAgent
from haystack.agents.memory import ConversationMemory
from haystack.nodes import PromptNode

from ionic_haystack.prompt_templates import ionic_template
from ionic_haystack.tool import IonicShoppingTool

ionic_node = IonicShoppingTool(api_key="my_ionic_api_key")
ionic_tool = Tool(
    name="Ionic",
    pipeline_or_node=ionic_node,
    description=ionic_template
)

memory = ConversationMemory()
prompt_node = PromptNode("gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY") , max_length=256, stop_words=["Observation:"])
agent = ConversationalAgent(prompt_node, tools=[ionic_tool],  memory=memory, prompt_template="deepset/conversational-agent")
```

## Examples
- Example Ionic Agent: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ioniccommerce/ionic_haystack/blob/main/examples/example_ionic_agent.ipynb)