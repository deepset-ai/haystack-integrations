---
layout: integration
name: ParlayAPI MCP
description: "Sports, sportsbook coverage and private odds research through ParlayAPI's MCP server."
authors:
    - name: ParlayAPI
      socials:
        github: JacobiusMakes
pypi: https://pypi.org/project/parlayapi-mcp/
repo: https://github.com/JacobiusMakes/parlay-api-mcp
type: Tool Integration
report_issue: https://github.com/JacobiusMakes/parlay-api-mcp/issues
version: Haystack 2.0
toc: true
mcp: true
---

## Overview

[ParlayAPI](https://parlay-api.com/docs) provides sports-data tools through a
published MCP server. Discover sport keys and event counts, inspect sportsbook
coverage metadata, or connect private account data to a Haystack workflow.
This integration uses `mcp-haystack`'s `MCPToolset` without a separate wrapper.
The examples expose only selected read-only tools, excluding signup, email,
billing and preference changes.

## Installation

Use Python 3.10 or newer in a private virtual environment:

```bash
pip install "haystack-ai==2.31.0" "mcp-haystack==1.5.1" "parlayapi-mcp==0.3.7"
```

## Discover tools without an account or model

Save this complete example as `parlayapi_discovery.py` and run it with Python.
It starts the installed server locally, lists only the allowed tool names, and
closes the connection. It calls no ParlayAPI endpoint or model, even if account
keys already exist in your environment. Haystack telemetry is disabled.

```python
import os
import sys


def make_toolset():
    os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "false"
    from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

    allowed = [
        "parlayapi_live_sports",
        "parlayapi_source_quality",
        "parlayapi_book_coverage",
    ]
    server = StdioServerInfo(
        command=sys.executable,
        args=["-m", "parlayapi_mcp"],
        env={
            "PARLAYAPI_BASE_URL": "https://parlay-api.com",
            "PARLAYAPI_KEY": "",
            "PARLAY_API_KEY": "",
        },
        max_retries=0,
    )
    return MCPToolset(
        server_info=server,
        tool_names=allowed,
        connection_timeout=20,
        invocation_timeout=20,
    )


if __name__ == "__main__":
    toolset = make_toolset()
    try:
        toolset.warm_up()
        print(
            "Available read-only tools:",
            ", ".join(sorted(tool.name for tool in toolset.tools)),
        )
        print("Discovery only: no API data request or model call was made.")
    finally:
        toolset.close()
```

## Read public sport counts with one explicit call

After saving the first example, save the following alongside it and run it when
you want current public metadata. It makes one no-key call, prints only sport
keys and reported event counts, and closes the server. No model is involved.

```python
import json

from parlayapi_discovery import make_toolset

toolset = make_toolset()
try:
    toolset.warm_up()
    tool = next(tool for tool in toolset.tools if tool.name == "parlayapi_live_sports")
    result = json.loads(tool.invoke())
    if result.get("isError") is not False or not isinstance(
        result.get("content"), list
    ):
        raise RuntimeError("Public metadata request failed")
    rows = []
    for block in result["content"]:
        if block.get("type") != "text":
            raise RuntimeError("Unexpected metadata content")
        row = json.loads(block["text"])
        if not isinstance(row, dict) or not isinstance(row.get("key"), str):
            raise RuntimeError("Unexpected sport metadata")
        if type(row.get("event_count")) is not int or row["event_count"] < 0:
            raise RuntimeError("Unknown event count")
        rows.append((row["key"], row["event_count"]))
    for sport, count in rows:
        print(f"{sport}: {count} reported events")
finally:
    toolset.close()
```

The public metadata call was tested through the published MCP server. Counts
describe that endpoint's response, not exhaustive coverage or price freshness.
Discovery alone does not validate API access. Tested versions: Python 3.12,
Haystack 2.31.0, `mcp-haystack` 1.5.1 and `parlayapi-mcp` 0.3.7.

## Use the toolset in private research

Once you choose to make API calls, use the initialized toolset with a Haystack
[Agent](https://docs.haystack.deepset.ai/docs/agent) or
[ToolInvoker](https://docs.haystack.deepset.ai/docs/toolinvoker) before closing it.
Each tool exposes its input schema; only invoke the specific operation your
workflow needs.

For account data, create your own [account](https://parlay-api.com/signup), store
its key privately, and explicitly configure `Secret.from_env_var("PARLAYAPI_KEY")`
from `haystack.utils` as the server's `PARLAYAPI_KEY` value. Keep the alternate
`PARLAY_API_KEY` value empty. Add only the data tools you need, such as
`parlayapi_list_sports` and `parlayapi_get_odds`, to `tool_names`; never expose the
whole server by omitting the allowlist. Account calls consume the applicable
[plan allowance](https://parlay-api.com/pricing).

Keep credentials out of tool arguments, prompts and source code. Keep account
results and pipeline storage private. Connecting a model may send raw tool
results to that provider; choose one appropriate for your data-use agreement.
Review the allowlist when upgrading the server. This example does not place bets.

## License

The [ParlayAPI MCP server](https://github.com/JacobiusMakes/parlay-api-mcp) is MIT
licensed. `mcp-haystack` uses the
[Apache-2.0 license](https://github.com/deepset-ai/haystack-core-integrations/blob/main/LICENSE).
Software licensing is separate from [API service terms](https://parlay-api.com/terms).
An API account does not grant public odds redisplay, redistribution or white-label
data rights.
