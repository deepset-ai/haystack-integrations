---
layout: integration
name: Anthropic
description: Use Anthropic Models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/farm-haystack
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/anthropic.png
---

You can use [Anhtropic Claude](https://docs.anthropic.com/claude/reference/getting-started-with-the-api) in your Haystack pipelines with the [PromptNode](https://docs.haystack.deepset.ai/v1.25/docs/prompt_node#using-anthropic-generative-models), which can also be used with and [Agent](https://docs.haystack.deepset.ai/v1.25/docs/agent).

## Installation

```bash
pip install farm-haystack[inference]
```

## Usage

You can use Anthropic models in various ways:

### Using Claude with PromptNode

To use Claude for prompting and generating answers, initialize a `PromptNode` with the model name, your Anthrpic API key and a prompt template. You can then use this `PromptNode` in a question answering pipeline to generate answers based on the given context.  

Below is the example of a `PromptNode` that uses a custom `PromptTemplate`

```python
from haystack.nodes import PromptTemplate, PromptNode

prompt_text = """
Answer the following question.
Question: {query}
Answer:
"""

prompt_template = PromptTemplate(prompt=prompt_text)

prompt_node = PromptNode(
    model_name_or_path = "claude-2",
    default_prompt_template=PromptTemplate(prompt_text),
    api_key='YOUR_ANTHROPIC_API_KEY',
    max_length=768,
    model_kwargs={"stream": True},
)
```

### Using Claude for Agents

To use Calude for an `Agent`, simply provide a `PromptNode` that uses Claude to the `Agent`:

```python
from haystack.agents import Agent
from haystack.nodes import PromptNode

prompt_node = PromptNode(model_name_or_path="YOUR_ANTHROPIC_API_KEY", api_key=anthropic_key, stop_words=["Observation:"])
agent = Agent(prompt_node=prompt_node)
```