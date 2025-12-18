---
layout: integration
name: PraisonAI
description: Integrate PraisonAI multi-agent workflows into your Haystack pipelines
authors:
    - name: Mervin Praison
      socials:
        github: MervinPraison
        twitter: MervinPraison
pypi: https://pypi.org/project/haystack-praisonai
repo: https://github.com/MervinPraison/haystack-praisonai
type: Custom Component
report_issue: https://github.com/MervinPraison/haystack-praisonai/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

This integration provides a Haystack 2.0 component for PraisonAI, enabling you to run multi-agent AI workflows within your Haystack pipelines. PraisonAI orchestrates multiple AI agents to collaboratively solve complex tasks.

## Installation

```bash
pip install haystack-praisonai
```

## Usage

### Components

This integration introduces the `PraisonAIComponent`:

- **PraisonAIComponent**: Sends queries to a PraisonAI server and returns agent responses.

### Basic Usage

```python
from haystack import Pipeline
from haystack_praisonai import PraisonAIComponent

# Create the component
praisonai = PraisonAIComponent(api_url="http://localhost:8080")

# Use in a pipeline
pipeline = Pipeline()
pipeline.add_component("praisonai", praisonai)

# Run
result = pipeline.run({"praisonai": {"query": "Research the latest AI trends"}})
print(result["praisonai"]["response"])
```

### Using a Specific Agent

```python
from haystack_praisonai import PraisonAIComponent

component = PraisonAIComponent(api_url="http://localhost:8080")
result = component.run(query="Write an article about AI", agent="writer")
print(result["response"])
```

### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_url` | str | `http://localhost:8080` | PraisonAI server URL |
| `timeout` | int | `300` | Request timeout in seconds |

## Prerequisites

Start a PraisonAI server:

```bash
pip install praisonai
praisonai serve agents.yaml --port 8080
```

## License

MIT License
