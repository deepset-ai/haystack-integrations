---
layout: integration
name: Mobilebox
description: Give a Haystack agent cloud Android phones over MCP. It creates a phone, reads the screen, taps, types, swipes and installs APKs, then parks or deletes the phone.
authors:
    - name: Mobilebox
      socials:
        github: fifteenA
pypi: https://pypi.org/project/mcp-haystack/
repo: https://github.com/fifteenA/mobilebox
type: Tool Integration
report_issue: https://github.com/fifteenA/mobilebox/issues
logo: /logos/mobilebox.png
version: Haystack 2.0
toc: true
mcp: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Mobilebox](https://mobilebox.dev) runs cloud Android phones that an AI agent controls through a hosted [MCP](https://modelcontextprotocol.io/) server at `https://mobilebox.dev/mcp`. The agent reads the screen as a numbered list of elements, acts with taps, typing and swipes, installs apps from an APK URL, and parks the phone to keep its apps, data and logins. Typical uses are testing your own Android app (install a build, walk a flow, check each screen) and running tasks in apps that have no web version or API.

This integration doesn't ship its own package. It uses `mcp-haystack`'s `MCPToolset` to connect a Haystack `Agent` to the server over Streamable HTTP. The 15 tools include `create_phone`, `observe`, `act`, `screenshot`, `install_app`, `park_phone` and `delete_phone`; the [Android MCP server page](https://mobilebox.dev/android-mcp-server) lists them all.

## Installation

```bash
pip install mcp-haystack
```

## Usage

Create an API key in the Mobilebox dashboard after you [sign up](https://mobilebox.dev/signup), and set it as `MOBILESANDBOX_API_KEY`. The example uses `OpenAIChatGenerator`, so it also needs `OPENAI_API_KEY`; any chat generator that supports tools works.

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo

toolset = MCPToolset(
    server_info=StreamableHttpServerInfo(
        url="https://mobilebox.dev/mcp",
        token=Secret.from_env_var("MOBILESANDBOX_API_KEY"),
    ),
    invocation_timeout=120,  # create_phone waits until the phone is ready
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=toolset,
    system_prompt=(
        "You control cloud Android phones. Create one phone per task, read the "
        "screen before you act, and delete the phone when the task is done."
    ),
)

result = agent.run(
    messages=[ChatMessage.from_user("Open Settings > Display on a new phone and tell me the brightness level.")]
)
print(result["last_message"].text)
toolset.close()
```

`create_phone` waits until the phone is ready, which usually takes about 20 seconds, so the example raises `invocation_timeout` from the default 30 seconds. Phones are billed per minute while they run ([pricing](https://mobilebox.dev/pricing)), which is why the system prompt asks the agent to delete its phone at the end. To give the agent fewer tools, pass `tool_names`, for example `tool_names=["create_phone", "observe", "act", "delete_phone"]`.

## License

`mcp-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license. The Mobilebox examples in [fifteenA/mobilebox](https://github.com/fifteenA/mobilebox) are MIT licensed. Mobilebox itself is a hosted service governed by its [terms](https://mobilebox.dev/terms).
