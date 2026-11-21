---
layout: integration
name: viaSocket
description: "Give a Haystack Agent the apps each of your end users connected (Slack, Google Sheets, HubSpot, Notion and 2,300+ more) as tools, run on that user's own connection"
authors:
    - name: viaSocket
      socials:
        github: Walkover-Web-Solution
pypi: https://pypi.org/project/viasocket/
repo: https://github.com/Walkover-Web-Solution/viasocket-apps
type: Tool Integration
report_issue: https://github.com/Walkover-Web-Solution/viasocket-apps/issues
logo: /logos/viasocket.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[viaSocket](https://viasocket.com) connects 2,300+ apps. The `viasocket` package turns the apps an end user connected through viaSocket into Haystack [`Tool`](https://docs.haystack.deepset.ai/docs/tool)s: one tool per app action (Slack's Send Message, Google Sheets' Add New Row, HubSpot's Create Deal...), with the action's own JSON Schema as its parameters. Each call runs on that end user's own connection, so an app built on Haystack can let its users act in their own accounts without writing connectors or handling OAuth.

- Picker fields (such as a Slack channel) come with an `<app>_list-options` tool, so the model can look up the id it needs.
- Errors (the app is not connected, a run failed) come back to the model as text instead of raising, so one bad call does not end the agent's run.

Docs: [viasocket-apps on GitHub](https://github.com/Walkover-Web-Solution/viasocket-apps/tree/main/python#haystack).

## Installation

```bash
pip install "viasocket[haystack]"
```

You need a viaSocket embed project (create one at [flow.viasocket.com](https://flow.viasocket.com)) and its three keys: `VIASOCKET_ORG_ID`, `VIASOCKET_PROJECT_ID` and `VIASOCKET_EMBED_SECRET`. Each end user connects an app once, either through viaSocket's embed in your app or, for a quick test, from the terminal:

```bash
npx viasocket-apps connect slack --user user_123
```

## Usage

### Components

This integration provides:

- `viasocket_toolset(viasocket, user, apps, actions=None)`: a Haystack `Toolset` with one `Tool` per chosen action of the user's connected apps.
- `viasocket_tools(...)`: the same tools as a list.

### Use with an Agent

```python
import os

from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from viasocket import ViaSocket
from viasocket.haystack import viasocket_toolset

viasocket = ViaSocket(
    org_id=os.environ["VIASOCKET_ORG_ID"],
    project_id=os.environ["VIASOCKET_PROJECT_ID"],
    secret=os.environ["VIASOCKET_EMBED_SECRET"],
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4.1-mini"),
    system_prompt="Keep the team updated in Slack.",
    tools=viasocket_toolset(viasocket, user="user_123", apps=["slack"], actions={"slack": ["send-message"]}),
)

result = agent.run(messages=[ChatMessage.from_user("Post 'Q3 numbers are in' in #general")])
print(result["last_message"].text)
```

## License

`viasocket` is distributed under the terms of the [MIT](https://github.com/Walkover-Web-Solution/viasocket-apps/blob/main/LICENSE) license.
