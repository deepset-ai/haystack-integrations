---
layout: integration
name: Adanos Market Sentiment
description: Stock and crypto market sentiment from Reddit, X / FinTwit, financial news, and Polymarket
authors:
    - name: Adanos
      socials:
        github: adanos-software
repo: https://github.com/adanos-software/adanos-haystack
report_issue: https://github.com/adanos-software/adanos-haystack/issues
type: Tool Integration
logo: /logos/adanos.svg
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Component](#component)
  - [Investment Research Agent](#investment-research-agent)
- [License](#license)

## Overview

[Adanos](https://adanos.org/) provides structured market sentiment for stocks and crypto. The
`AdanosMarketSentiment` component makes signals from Reddit, X / FinTwit, financial news, and
Polymarket available to Haystack pipelines and agents without adding trading or portfolio logic.

The community-maintained integration supports sentiment lookups, trending assets, aggregate market
sentiment, asset comparisons, search, and dataset statistics. Stock requests can use Reddit, X,
news, or Polymarket; crypto requests use Reddit.

Create an API key at [adanos.org/register](https://adanos.org/register). Free, Hobby, and
Professional accounts use the same component; the API applies the quota and historical access
available to the key's plan.

## Installation

Install the released component from PyPI:

```bash
pip install "adanos-haystack==0.1.1"
```

Provide the API key through the `ADANOS_API_KEY` environment variable.

## Usage

### Component

```python
from haystack_integrations.components.tools.adanos import AdanosMarketSentiment

sentiment = AdanosMarketSentiment()
result = sentiment.run(
    operation="sentiment",
    asset_type="stock",
    source="news",
    symbol="NVDA",
)

print(result["result"])
```

Both synchronous `run` and asynchronous `run_async` calls are supported.

### Investment Research Agent

A research agent can combine private investment notes retrieved by Haystack with current external
sentiment from Adanos. In this example, the agent searches an internal document store, calls Adanos
for relevant stock sentiment, and keeps the two evidence sources distinct in its assessment:

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.tools import ComponentTool
from haystack_integrations.components.tools.adanos import AdanosMarketSentiment

document_store = InMemoryDocumentStore()
document_store.write_documents(
    [
        Document(
            content=(
                "NVDA research note: data-center demand remains the main growth driver, "
                "while customer concentration is a material risk."
            ),
            meta={"ticker": "NVDA"},
        )
    ]
)

research_tool = ComponentTool(
    component=InMemoryBM25Retriever(document_store=document_store, top_k=3),
    name="internal_research",
    description="Search approved internal investment research and return relevant documents.",
)
adanos_tool = ComponentTool(
    component=AdanosMarketSentiment(),
    name="market_sentiment",
    description=(
        "Get current and historical stock or crypto market sentiment from Reddit, "
        "X / FinTwit, financial news, and Polymarket."
    ),
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[research_tool, adanos_tool],
    system_prompt=(
        "You are an investment research assistant. Use internal_research for private notes "
        "and market_sentiment for external sentiment evidence. Clearly distinguish the two "
        "sources, mention conflicting signals, and do not present the result as financial advice."
    ),
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "Assess NVDA using our internal research and external sentiment from "
            "2026-07-21 through 2026-07-28."
        )
    ]
)
print(result["last_message"].text)
```

See the [Adanos API reference](https://api.adanos.org/docs) and the
[integration repository](https://github.com/adanos-software/adanos-haystack) for all operations and
parameters.

## License

`adanos-haystack` is distributed under the terms of the Apache-2.0 license.
