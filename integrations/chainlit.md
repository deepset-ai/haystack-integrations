---
layout: integration
name: Chainlit Agent UI
description: Visualise and debug your agent's intermediary steps!
authors:
    - name: Chainlit Team
      socials:
        github: Chainlit
        twitter: chainlit_io
pypi: https://pypi.org/project/chainlit/
repo: https://github.com/Chainlit/chainlit
type: Monitoring Tool
report_issue: https://github.com/Chainlit/chainlit/issues
logo: /logos/chainlit.png
---

Chainlit is an open-source Python package that makes it incredibly fast to build, test and share LLM apps. Integrate the Chainlit API in your existing code to spawn a ChatGPT-like interface in minutes. With a simple line of code, you can leverage Chainlit to interact with your agent, visualise intermediary steps, debug them in an advanced prompt playground and share your app to collect human feedback. More info on the [documentation](https://docs.chainlit.io/).

![Chainlit screenshot](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/chainlit-haystack.png)

## Installation

```bash
pip install chainlit
```

## Usage

Create a new Python file named `app.py` with the code below. This code adds the Chainlit callback handler to the Haystack callback manager. The callback handler is responsible for listening to the Agent’s intermediate steps and sending them to the UI.

```python
from haystack.agents.conversational import ConversationalAgent
import chainlit as cl

## Agent Code

agent = ConversationalAgent(
  prompt_node=conversational_agent_prompt_node,
  memory=memory,
  prompt_template=agent_prompt,
  tools=[search_tool],
)

cl.HaystackAgentCallbackHandler(agent)

@cl.on_message
async def main(message: str):
    response = await cl.make_async(agent.run)(message)
    await cl.Message(author="Agent", content=response["answers"][0].answer).send()
```

To kick off your LLM app, open a terminal, navigate to the directory containing `app.py`, and run the following command:

```bash
chainlit run app.py
```

## Example
Check out this full example from [the cookbook](https://github.com/Chainlit/cookbook/tree/main/haystack). 

## About Chainlit
Chainlit is an open-source Python package that makes it incredibly fast to build, test and share LLM apps. Integrate the Chainlit API in your existing code to spawn a ChatGPT-like interface in minutes!

### Key features
- Build LLM Apps fast: Integrate seamlessly with an existing code base or start from scratch in minutes
- Visualize multi-steps reasoning: Understand the intermediary steps that produced an output at a glance
- Iterate on prompts: Deep dive into prompts in the Prompt Playground to understand where things went wrong and iterate
- Collaborate with teammates: Invite your teammates, create annotated datasets and run experiments together
- Share your app: Publish your LLM app and share it with the world (coming soon)
