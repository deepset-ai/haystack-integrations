---
layout: integration
name: LurkAPI
description: Give Haystack agents live public social media data (posts, profiles, comments, ads and transcripts from 16 platforms) through LurkAPI's remote MCP server
authors:
    - name: Mesmer Lord
      socials:
        github: mesmerlord
repo: https://github.com/mesmerlord/lurkapi-claude-plugin
type: Tool Integration
report_issue: https://github.com/mesmerlord/lurkapi-claude-plugin/issues
logo: /logos/lurkapi.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Connect to the server](#connect-to-the-server)
  - [Use the tools in an Agent](#use-the-tools-in-an-agent)
- [Pricing](#pricing)
- [License](#license)

## Overview

[LurkAPI](https://lurkapi.com) is a social media data API. Its remote MCP server at `https://api.lurkapi.com/mcp` (Streamable HTTP) exposes one tool per endpoint: public posts, profiles, comments and video transcripts from TikTok, Instagram, YouTube, Reddit, X, LinkedIn, Threads, Bluesky, Telegram and more, plus the ads in Meta's, Google's, TikTok's and LinkedIn's ad libraries. With Haystack's [MCP integration](https://haystack.deepset.ai/integrations/mcp), an `Agent` can call those tools to answer with today's data.

Tools are named `<platform>_<endpoint>`, for example `facebook_search_ads`, `tiktok_profile`, `youtube_transcript` or `reddit_search`. The [docs](https://lurkapi.com/docs) list every endpoint with its parameters and a real response.

LurkAPI reads public data only. It never logs in to anyone's account, can't see private profiles or messages, and can't post or message anyone.

## Installation

```bash
pip install mcp-haystack
```

Sign in at [lurkapi.com/login](https://lurkapi.com/login) to get an API key (new accounts get 100 free credits, no card), then set it:

```bash
export LURKAPI_API_KEY="lk_live_..."
```

## Usage

### Connect to the server

`MCPToolset` loads the server's tools. Pass `tool_names` to keep the list your model sees short; without it, the toolset loads all of them.

```python
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

lurkapi = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.lurkapi.com/mcp",
        headers={"x-api-key": Secret.from_env_var("LURKAPI_API_KEY")},
    ),
    tool_names=["facebook_search_ads", "tiktok_profile", "youtube_transcript", "reddit_search"],
)
```

`https://api.lurkapi.com/mcp?platforms=tiktok,youtube` lists only those platforms' tools, and `https://api.lurkapi.com/mcp?compact` gives two tools instead of one per endpoint (`find_endpoints` and `call_endpoint`).

### Use the tools in an Agent

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

lurkapi = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://api.lurkapi.com/mcp",
        headers={"x-api-key": Secret.from_env_var("LURKAPI_API_KEY")},
    ),
    tool_names=["facebook_search_companies", "facebook_company_ads"],
)

agent = Agent(chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"), tools=lurkapi)
agent.warm_up()

result = agent.run(
    messages=[ChatMessage.from_user("What ads is Allbirds running on Facebook right now? Summarize the main angles.")]
)
print(result["messages"][-1].text)
```

The agent can look up the advertiser with `facebook_search_companies` and read its ads from Meta's Ad Library with `facebook_company_ads`: each ad's copy, media, landing page and run dates. Results leave out empty fields and keep one URL per image or video, to save tokens.

## Pricing

Most tool calls cost 1 credit. New accounts get 100 free credits with no card, and once a day a balance under 25 is topped back up to 25. Packs start at $9 for 10,000 credits, and credits never expire. Calls that fail on bad arguments, rate limits or server errors are free. See [pricing](https://lurkapi.com/pricing).

## License

LurkAPI is a hosted commercial service ([terms](https://lurkapi.com/terms)). `mcp-haystack` is licensed under Apache 2.0.
