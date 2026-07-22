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
  - [Pipeline](#pipeline)
  - [Agent Tool](#agent-tool)
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

Install the component directly from its public repository:

```bash
pip install "adanos-haystack @ git+https://github.com/adanos-software/adanos-haystack.git"
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

### Pipeline

```python
from haystack import Pipeline
from haystack_integrations.components.tools.adanos import AdanosMarketSentiment

pipeline = Pipeline()
pipeline.add_component("sentiment", AdanosMarketSentiment())

result = pipeline.run(
    {
        "sentiment": {
            "operation": "trending",
            "asset_type": "stock",
            "source": "reddit",
            "limit": 5,
        }
    }
)
```

### Agent Tool

Use Haystack's `ComponentTool` to expose all supported operations to an agent:

```python
from haystack.tools import ComponentTool
from haystack_integrations.components.tools.adanos import AdanosMarketSentiment

adanos_tool = ComponentTool(
    component=AdanosMarketSentiment(),
    name="market_sentiment",
    description=(
        "Get current and historical stock or crypto market sentiment from Reddit, "
        "X / FinTwit, financial news, and Polymarket."
    ),
)
```

See the [Adanos API reference](https://api.adanos.org/docs) and the
[integration repository](https://github.com/adanos-software/adanos-haystack) for all operations and
parameters.

## License

`adanos-haystack` is distributed under the terms of the Apache-2.0 license.
