---
layout: integration
name: IsMalicious
description: Inspect selected Agent fetch URLs and complete text results with the IsMalicious Gate API.
authors:
  - name: IsMalicious
    socials:
      github: hexablob
repo: https://github.com/hexablob/ismalicious-haystack
report_issue: https://github.com/hexablob/ismalicious-haystack/issues
type: Tool Integration
version: Haystack 3.3
toc: true
---

[IsMalicious](https://ismalicious.com/) provides URL reputation and content checks for selected Agent tools. This integration installs native `before_tool` and `after_tool` hooks: the first checks the original URL before the selected tool runs, and the second scans its complete string result before the Agent's next model call

## Installation

```bash
python -m pip install "ismalicious-haystack @ git+https://github.com/hexablob/ismalicious-haystack.git@v0.1.1"
```

The repository also publishes a wheel with the tagged GitHub release. Haystack 3.3 or later is required

## Credentials and policy

Set `ISMALICIOUS_API_KEY` and `ISMALICIOUS_API_SECRET` from [your account](https://ismalicious.com/app/account) in your secret manager. Environment variable names, rather than secret values, are serialized with the hook

Top-level `warn` and `block`, service errors, timeouts, quota errors, redirects, malformed responses, incomplete link inspection and serialized request bodies over 1 MiB refuse. Requests use TLS, a 15-second timeout and no retries. Allowed text is unchanged. `allow` means the Gate did not refuse under its current rules; it does not prove a URL or its content benign, and an unknown link reputation can still be allowed. These endpoints consume the separate scan quota

## Example

This complete example uses a deterministic native Haystack generator to show the tool path without an LLM provider charge. It sends real reputation/content requests when credentials are configured and restricts the fetch to `https://example.com/`. Replace the generator with a chat generator and adapt the fetch allowlist and SSRF controls for your application

```python
import os

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "false"
os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "false"

import httpx
from haystack import component
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage, ToolCall
from haystack.tools import Tool

from ismalicious_haystack import GateRefusal, IsMaliciousGateHook
from ismalicious_haystack.gate import REFUSAL


def fetch_page(url: str) -> str:
    if url != "https://example.com/":
        raise GateRefusal()
    with httpx.stream("GET", url, follow_redirects=False, timeout=15, trust_env=False) as response:
        response.raise_for_status()
        parts = []
        size = 0
        for part in response.iter_bytes():
            size += len(part)
            if size > 512 * 1024:
                raise GateRefusal()
            parts.append(part)
        return b"".join(parts).decode("utf-8", errors="strict")


@component
class DemoGenerator:
    @component.output_types(replies=list[ChatMessage])
    def run(self, messages: list[ChatMessage], tools: list[Tool] | None = None) -> dict[str, object]:
        if messages[-1].tool_call_results:
            return {"replies": [ChatMessage.from_assistant("The allowed page was received.")]}
        return {
            "replies": [
                ChatMessage.from_assistant(
                    tool_calls=[ToolCall(tool_name="fetch_page", arguments={"url": "https://example.com/"}, id="demo")]
                )
            ]
        }


def main() -> None:
    fetch = Tool(
        name="fetch_page",
        description="Read the example.com demonstration page",
        parameters={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        function=fetch_page,
    )
    agent = Agent(
        chat_generator=DemoGenerator(),
        tools=[fetch],
        hooks={
            "before_tool": [IsMaliciousGateHook(phase="before_tool", tool_name="fetch_page")],
            "after_tool": [IsMaliciousGateHook(phase="after_tool", tool_name="fetch_page")],
        },
        streaming_callback=None,
        tool_streaming_callback_passthrough=False,
        raise_on_tool_invocation_failure=True,
    )
    try:
        result = agent.run(messages=[ChatMessage.from_user("Read the example page.")])
        print(result["last_message"].text)
    except GateRefusal:
        print(REFUSAL)


if __name__ == "__main__":
    main()
```

Use the same hooks with `await agent.run_async(messages=...)` for asynchronous Agents

## Scope and safety boundaries

Only the named tool is inspected. URL reputation does not fetch the destination. This first release supports complete string results. Binary, multipart and streaming results are excluded. Disable content tracing and all generator/Agent/tool streaming callbacks, and do not configure `outputs_to_state` on the selected fetch tool. Register these gates first at their hook points and avoid other hooks that expose or rewrite uninspected results

Native tool-result streaming can happen before `after_tool`, so these hooks do not protect an independently streaming tool or callback. Content necessarily exists in memory before scanning; side effects cannot be undone. Network calls hidden inside other tools and model-native search are outside this integration

The hook removes the current tool-result messages on refusal and raises a fixed exception without raw content, URLs or credentials. The caller must return that refusal and must not recover or continue from the rejected State. See the [repository](https://github.com/hexablob/ismalicious-haystack) for sync/async native Agent tests and the full API policy
