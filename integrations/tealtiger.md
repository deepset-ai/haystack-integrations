---
layout: integration
name: TealTiger
description: Deterministic governance, cost tracking, and PII detection for Haystack pipelines and agents. Supports Haystack 3.0 Agent Hooks. No LLM in the governance path.
authors:
    - name: TealTiger
      socials:
        github: agentguard-ai
        twitter: TealtigerAI
        linkedin: https://www.linkedin.com/company/tealtiger
pypi: https://pypi.org/project/tealtiger-haystack
repo: https://github.com/agentguard-ai/tealtiger
type: Custom Component
report_issue: https://github.com/agentguard-ai/tealtiger/issues
logo: /logos/tealtiger.png
version: Haystack 2.0+
toc: true
---

### Table of Contents

- Overview
- Installation
- Usage
- Features
- Support
- License

## Overview

[![PyPI - Version](https://img.shields.io/pypi/v/tealtiger-haystack)](https://pypi.org/project/tealtiger-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tealtiger-haystack)](https://pypi.org/project/tealtiger-haystack)

Add deterministic governance to any Haystack pipeline or agent. No LLM in the governance path — all policy evaluation is deterministic, adding <2ms latency.

**v0.2.0** adds native support for Haystack 3.0 Agent Hooks (`before_tool`).

## Installation

```bash
pip install tealtiger-haystack
```

## Usage

### Agent Hooks (Haystack 3.0+) — Recommended for Agents

Use `TealTigerGovernanceHook` as a `before_tool` hook to enforce governance on every tool call an agent makes:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools import tool
from typing import Annotated
from haystack_integrations.components.connectors.tealtiger import TealTigerGovernanceHook

@tool
def search(query: Annotated[str, "The search query"]) -> str:
    """Search the web."""
    return "Results for: " + query

@tool
def delete_account(account_id: Annotated[str, "The account ID"]) -> str:
    """Delete a customer account."""
    return "Deleted"

# Create governance hook
governance = TealTigerGovernanceHook(
    mode="ENFORCE",
    allowed_tools=["search"],           # Only search is allowed
    pii_categories=["ssn", "credit_card", "email"],
    budget_limit=5.0,                   # $5 max per session
)

# Attach to agent
agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[search, delete_account],
    hooks={"before_tool": [governance]},
)

result = agent.run(messages=[ChatMessage.from_user("Delete account 12345")])
# → delete_account is DENIED (not in allowlist)

# Inspect audit trail
for decision in governance.decisions:
    print(f"{decision.action}: {decision.tool_name} — {decision.reason}")
```

### Zero-Config Mode (Observe) — Pipeline Component

No policies needed — just add the component and get instant visibility into cost, PII, and tool usage:

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.connectors.tealtiger import TealTigerGovernanceComponent

pipeline = Pipeline()
pipeline.add_component("governance", TealTigerGovernanceComponent())
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("governance.text", "llm.prompt")

result = pipeline.run({"governance": {"text": "What is the capital of France?"}})

# Access governance decision
decision = result["governance"]["decision"]
print(decision["action"])         # "ALLOW"
print(decision["cost_tracked"])   # 0.0023
print(decision["pii_detected"])   # []
```

### Policy Mode (Enforce)

Add a TealEngine with policies for full governance enforcement:

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from tealtiger import TealEngine
from haystack_integrations.components.connectors.tealtiger import TealTigerGovernanceComponent

engine = TealEngine(policies=[
    {"type": "cost_limit", "max_per_session": 5.00},
    {"type": "pii_block", "categories": ["ssn", "credit_card"]},
])

pipeline = Pipeline()
pipeline.add_component(
    "governance",
    TealTigerGovernanceComponent(engine=engine, mode="ENFORCE"),
)
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.connect("governance.text", "llm.prompt")

result = pipeline.run({"governance": {"text": "Process payment for card 4111-1111-1111-1111"}})
# PII detected → action: "DENY"
```

## Features

- **Deterministic** — Same input + same policy = same decision, every time
- **<2ms overhead** — No LLM in the governance path
- **Agent Hooks (3.0+)** — Native `before_tool` hook for agent-level governance
- **Pipeline Component (2.x+)** — Standalone governance component for pipelines
- **Zero-config mode** — Observe cost, PII, and behavior without writing policies
- **Policy enforcement** — ALLOW, DENY, REQUIRE_APPROVAL, REVISE decisions
- **Cost tracking** — Per-request and cumulative session cost with hard stop
- **PII detection** — Email, phone, SSN, credit card, IP address patterns
- **Secret detection** — API keys, passwords, tokens, private keys
- **Tool authorization** — Allowlist/denylist which tools an agent can call
- **Audit trail** — Every decision produces a structured evidence record
- **TEEC receipts** — Compliance-grade execution receipts with correlation IDs
- **Serializable** — Hooks support `to_dict`/`from_dict` for Agent persistence

## Support

- [GitHub Issues](https://github.com/agentguard-ai/tealtiger/issues)
- [TealTiger Documentation](https://tealtiger.ai/)
- [OWASP ASI Coverage](https://github.com/agentguard-ai/tealtiger) — 8/10 Agentic Security Index categories

## License

`tealtiger-haystack` is distributed under the [Apache 2.0 License](https://opensource.org/licenses/Apache-2.0).
