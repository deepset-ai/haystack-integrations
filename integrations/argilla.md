---
layout: integration
name: Argilla
description: Use Argilla as a collaboration platform for AI engineers and domain experts!
authors:
    - name: Argilla Team
      socials:
        github: argilla-io
        twitter: argilla_io
        linkedin: argilla-io
pypi: https://pypi.org/project/argilla-haystack
repo: https://github.com/argilla-io/argilla-haystack
type: Monitoring
report_issue: https://github.com/argilla-io/argilla-haystack/issues
logo: /logos/argilla.png
version: Haystack 1.x
---

Argilla is an open-source platform for data-centric LLM development. Integrates human and model feedback loops for continuous LLM refinement and oversight.

With Argilla's Python SDK and adaptable UI, you can create human and model-in-the-loop workflows for:

- Supervised fine-tuning
- Preference tuning (RLHF, DPO, RLAIF, and more)
- Small, specialized NLP models
- Scalable evaluation.

## Getting Started

You first need to install argilla and argilla-haystack as follows:

```bash
pip install argilla argilla-haystack['haystack-v1']
```

You will need an Argilla Server running to monitor the LLM. You can either install the server locally or have it on HuggingFace Spaces. For a complete guide on how to install and initialize the server, you can refer to the [Quickstart Guide](https://docs.argilla.io/en/latest/getting_started/quickstart_installation.html).

## Usage

You can use your Haystack agent with Argilla with just a simple step. After the agent is created, we will need to call the handler to log the data into Argilla.

Let us create a simple pipeline with a conversational agent. Also, we will use GPT3.5 from OpenAI as our LLM. For this, you will need a valid API key from OpenAI.

```python
import os
from getpass import getpass

openai_api_key = os.getenv("OPENAI_API_KEY", None)
```

With the code snippet below, let us create the conversational agent.

```python
from haystack.nodes import PromptNode
from haystack.agents.memory import ConversationSummaryMemory
from haystack.agents.conversational import ConversationalAgent

prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo-instruct", api_key=openai_api_key, max_length=256, stop_words=["Human"]
    )

summary_memory = ConversationSummaryMemory(prompt_node)

conversational_agent = ConversationalAgent(prompt_node=prompt_node, memory=summary_memory)
```

Let us import the `ArgillaCallbackHandler` with the standard arguments and run it. Note that the dataset with the given name will be pulled from Argilla server. If the dataset does not exist, it will be created with the given name. For more customization, you can refer to the [tutorial](https://github.com/argilla-io/argilla-haystack/blob/main/docs/use_argilla_callback_in_haystack-v1.ipynb).

```python
from argilla_haystack import ArgillaCallbackHandler

dataset_name = "conversational_ai"
api_url = "http://localhost:6900/"
api_key = "argilla.apikey"

argilla_callback = ArgillaCallbackHandler(agent=conversational_agent, dataset_name=dataset_name, api_url=api_url, api_key=api_key)
```

Now, let us run the agent to obtain a response. The prompt given and the response obtained will be logged in to Argilla server.

```python
conversational_agent.run("Tell me three most interesting things about Istanbul, Turkey")
```

## Other Use Cases

Please refer to this [notebook](https://github.com/argilla-io/argilla-haystack/blob/main/docs/use_argilla_callback_in_haystack-v1.ipynb) for a more detailed example.
