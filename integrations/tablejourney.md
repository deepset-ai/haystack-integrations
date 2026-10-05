---
layout: integration
name: TableJourney
description: Search verified restaurants, food festivals and food day plans across 214 cities from a Haystack Agent.
authors:
    - name: TableJourney
      socials:
        github: lewismvaughan
repo: https://github.com/lewismvaughan/tablejourney-mcp/tree/main/haystack
type: Tool Integration
report_issue: https://github.com/lewismvaughan/tablejourney-mcp/issues
logo: /logos/tablejourney.png
version: Haystack 3.2
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[TableJourney](https://tablejourney.com) is a free REST API and MCP server over editorially verified food travel data: restaurants, cafes, markets and street food in 214 cities, each with a source URL and a last-checked date, food festivals with resolved dates, and bookable food tours, stays and car hire. OpenAPI document: https://tablejourney.com/api/v1/openapi.json. Guide for agents: https://tablejourney.com/agents/.

This integration provides three Haystack `Tool`s:

- `search_food_places`: search verified venues by text, city, cuisine or dietary need.
- `plan_food_day`: a one-day food itinerary of open, verified venues for a city.
- `find_food_festivals`: food festivals with resolved next dates.

No API key is required.

## Installation

```bash
pip install haystack-ai requests
```

Copy [`tablejourney_tools.py`](https://github.com/lewismvaughan/tablejourney-mcp/tree/main/haystack) into your project.

## Usage

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from tablejourney_tools import (
    tablejourney_festivals_tool,
    tablejourney_plan_tool,
    tablejourney_search_tool,
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=[tablejourney_search_tool, tablejourney_plan_tool, tablejourney_festivals_tool],
)

result = agent.run(messages=[ChatMessage.from_user("Plan a vegan food day in Lisbon, Portugal.")])
print(result["messages"][-1].text)
```

Each tool returns the API's JSON, so the agent sees venue names, addresses, cuisines, price tiers, hours and source URLs.

## License

`tablejourney_tools.py` is MIT licensed. The data is free to use under TableJourney's agent terms (https://tablejourney.com/agents/#terms).
