---
layout: integration
name: MAQAMI Travel
description: Search hotels and flights, read hotel details, then prebook and book from a Haystack agent through the hosted MAQAMI Travel MCP server
authors:
    - name: MAQAMI
      socials:
        github: negm17111995
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/negm17111995/mcp-server
type: Tool Integration
report_issue: https://github.com/negm17111995/mcp-server/issues
logo: /logos/maqami.png
version: Haystack 2.0
toc: true
mcp: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Overview

[MAQAMI](https://maqami.co) is a hotel and flight booking platform with 3M+ hotels. The [MAQAMI Travel MCP server](https://github.com/negm17111995/mcp-server) is hosted at `https://mcp.maqami.co/` over Streamable HTTP and needs no API key. It lets an agent:

- resolve places and airports,
- search live hotel rates and flights,
- read hotel details and reviews,
- prebook a rate to confirm availability and the final price, and
- book the prebooked rate.

Prebook and book hold or create real reservations, and booking needs guest and payment details. The example below asks the user before any of those calls run.

This integration doesn't ship its own package. It uses the `MCPToolset` from `mcp-haystack` to connect a Haystack agent to the server.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Connect to the server and load the tools you need. The server also exposes tools for managing existing bookings, so use `tool_names` to keep the agent focused on search and booking:

```python
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

server_info = StreamableHttpServerInfo(url="https://mcp.maqami.co/")

toolset = MCPToolset(
    server_info=server_info,
    tool_names=[
        "get_data_places",
        "post_hotels_rates",
        "get_data_hotel",
        "post_rates_prebook",
        "post_rates_book",
    ],
    eager_connect=True,
)

for tool in toolset.tools:
    print(tool.name)
```

The tool names above are the ones the server published in October 2026. Print `toolset.tools` without `tool_names` to see the full current list with descriptions and input schemas.

A hotel search with `post_hotels_rates` needs `checkin`, `checkout`, `occupancies`, `currency`, `guestNationality` and one location field (for example `placeId`, `cityName` with `countryCode`, `hotelIds` or `aiSearch`). A flight search with `post_flights_rates` needs `legs` (each with `origin`, `destination` and `date`), `adults` and `currency`.

## Examples

This travel assistant can search hotels and flights. The prebook and book tools go through a `ConfirmationHook`, so the agent shows the tool call and waits for `y`, `n` or `m` (modify) in the terminal before it runs:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.hooks.human_in_the_loop import (
    AlwaysAskPolicy,
    BlockingConfirmationStrategy,
    ConfirmationHook,
    SimpleConsoleUI,
)
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

# Read-only search and details tools, plus the prebook and book steps.
HOTEL_TOOLS = [
    "get_data_places",
    "post_hotels_rates",
    "get_data_hotel",
    "get_data_reviews",
    "post_rates_prebook",
    "post_rates_book",
]
FLIGHT_TOOLS = [
    "get_data_flights_airports",
    "post_flights_rates",
    "post_flights_verify",
    "post_flights_prebooks",
    "post_flights_bookings",
]
# These steps hold or create real reservations, so the agent asks before running them.
NEEDS_APPROVAL = ("post_rates_prebook", "post_rates_book", "post_flights_prebooks", "post_flights_bookings")

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(url="https://mcp.maqami.co/"),
    tool_names=HOTEL_TOOLS + FLIGHT_TOOLS,
    eager_connect=True,
)

confirmation = ConfirmationHook(
    confirmation_strategies={
        NEEDS_APPROVAL: BlockingConfirmationStrategy(
            confirmation_policy=AlwaysAskPolicy(),
            confirmation_ui=SimpleConsoleUI(),
        )
    }
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-5.4-mini"),
    tools=toolset,
    system_prompt=(
        "You are a travel assistant. Use the MAQAMI Travel tools to search hotels and flights and "
        "answer with concrete options: name, dates, price with currency, and cancellation terms when "
        "available. Ask for missing details such as dates, number of guests, the guest's nationality "
        "and the currency instead of guessing. Prebook and book create real reservations: only call "
        "them after the user has chosen an option and confirmed the final price."
    ),
    hooks={"before_tool": [confirmation]},
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Find 4-star hotels in Lisbon for 2 adults from 12 to 15 May, paying in EUR. "
            "We are both Portuguese citizens."
        )
    ]
)
print(result["last_message"].text)
```

In a web or chat app, replace `SimpleConsoleUI` with your own confirmation UI.

The typical flow is:

1. **Hotels**: `get_data_places` → `post_hotels_rates` → `get_data_hotel` and `get_data_reviews` → `post_rates_prebook` → user confirmation → `post_rates_book`.
2. **Flights**: `get_data_flights_airports` → `post_flights_rates` → `post_flights_verify` → user confirmation → `post_flights_prebooks` → `post_flights_bookings`.

For setup in other clients and frameworks, see the [server repository](https://github.com/negm17111995/mcp-server).

## License

`mcp-haystack` is distributed under the terms of the Apache-2.0 license.

The MAQAMI Travel MCP server repository is [MIT licensed](https://github.com/negm17111995/mcp-server/blob/main/LICENSE). Searches and bookings are processed by MAQAMI under the policies published at [maqami.co](https://maqami.co).
